import uuid
import requests
import os
from dateutil import parser
from dotenv import load_dotenv, find_dotenv
from models.clan_war_player_record import ClanWarPlayerRecord
from models.clan_war_attack_record import ClanWarAttackRecord
from models.clan_member import ClanMember
from models.war_record import WarRecord
from repository.database_handler import DatabaseHandler


class ClashClient:
    def __init__(self):
        # Get api key from env and set base url
        load_dotenv(find_dotenv())
        self.__base_url = "https://api.clashofclans.com/v1"
        self.__api_key = os.getenv("CLASH_API_KEY")

        # Setup database handler
        self.__db = DatabaseHandler()

        # Set clan name to null
        self.__clan_tag = None

    def __del__(self):
        # Close db session when clash client instance is destroyed
        self.__db.close()

    def set_clan(self, clan_tag: str) -> None:
        self.__clan_tag = clan_tag

    def fetch_clan_info(self, clan_tag: str) -> dict:
        # Set url and headers for api call
        url = f"{self.__base_url}/clans/%23{clan_tag}"
        headers = {"Authorization": f"Bearer {self.__api_key}"}

        # Make call and get response
        response = requests.get(url, headers=headers)

        # Return JSON for response
        return response.json()

    def fetch_clan_members(self, clan_tag: str) -> dict:
        # Set url and headers for api call
        url = f"{self.__base_url}/clans/%23{clan_tag}/members"
        headers = {"Authorization": f"Bearer {self.__api_key}"}

        # Make call and get response
        response = requests.get(url, headers=headers)

        # Return JSON for response
        return response.json()["items"]

    def fetch_my_members(self) -> dict:
        # Check if clan_tag has been set, if not return empty list
        if self.__clan_tag is not None:
            return self.fetch_clan_members(self.__clan_tag)
        else:
            return {}

    def fetch_clan_warlog(self, clan_tag: str) -> dict:
        # Set url and headers for api call
        url = f"{self.__base_url}/clans/%23{clan_tag}/warlog"
        headers = {"Authorization": f"Bearer {self.__api_key}"}

        # Make call and get response
        response = requests.get(url, headers=headers)

        # Return JSON for response
        return response.json()["items"]

    def fetch_my_warlog(self) -> dict:
        # Check if clan_tag has been set, if not return empty list
        if self.__clan_tag is not None:
            return self.fetch_clan_warlog(self.__clan_tag)
        else:
            return {}

    def fetch_current_clan_war(self, clan_tag: str) -> dict:
        # Set url and headers for api call
        url = f"{self.__base_url}/clans/%23{clan_tag}/currentwar"
        headers = {"Authorization": f"Bearer {self.__api_key}"}

        # Make call and get response
        response = requests.get(url, headers=headers)

        # Return JSON for response
        return response.json()

    def fetch_my_current_clan_war(self) -> dict:
        # Check if clan_tag has been set, if not return empty list
        if self.__clan_tag is not None:
            return self.fetch_current_clan_war(self.__clan_tag)
        else:
            return {}

    # Records all clan members to database
    def record_clan_members(self) -> None:
        # Return immediately if no clan tag has been set
        if self.__clan_tag is None:
            return

        # Use fetch clan members to return list of all clan members and their stats
        clan_members = self.fetch_clan_members(self.__clan_tag)

        # Get all members from database to compare to fetched list
        database_members = self.get_all_members()

        # Extract tags from database members
        member_tags = [member.id for member in database_members]

        # For each clan member add a clanmember object in database
        for member in clan_members:
            # If player is already in database update their stats
            if member["tag"] in member_tags:
                member_tags.remove(member["tag"])
                clan_member = self.get_member_by_id(member["tag"])
                clan_member.rank = member["clanRank"]
                clan_member.position = member["role"]
            # If player is new create new database entry for them
            else:
                self.__db.add_object(
                    ClanMember(
                        id=member["tag"],
                        name=member["name"],
                        ranking=member["clanRank"],
                        position=member["role"],
                    )
                )

        # Tag any players that have left clan as nonMembers but keep their data in case they rejoin
        for non_member_tag in member_tags:
            non_member = self.get_member_by_id(non_member_tag)
            non_member.position = "nonMember"

        # Commit clan member objects to database
        self.__db.commit()

    # Record percentage of attacks player has used in wars
    def record_player_clan_war_stats(self, war=None) -> None:
        # Return immediately if no clan tag has been set
        if self.__clan_tag is None:
            return

        # Fetch current clan war stats
        if war is None:
            war = self.fetch_current_clan_war(self.__clan_tag)

        defenders = {}
        for defender in war["opponent"]["members"]:
            defenders[defender["tag"]] = defender["townhallLevel"]

        # For each member in clan war
        for member in war["clan"]["members"]:
            # If the member attacked created a clan_war_player_record in database
            if "attacks" in member:
                war_player_record = ClanWarPlayerRecord(
                    attacks_used=len(member["attacks"]),
                    stars=0,
                    record_status="active",
                    member_id=member["tag"],
                    war_id=war["opponent"]["tag"],
                )

                self.__db.add_object(war_player_record)
                self.__db.flush()

                # Make an attack record for each attack used in war
                for attack in member["attacks"]:
                    self.__db.add_object(
                        ClanWarAttackRecord(
                            stars=attack["stars"],
                            percentage=attack["destructionPercentage"],
                            town_hall_diff=defenders[attack["defenderTag"]]
                            - member["townhallLevel"],
                            cw_player_record_id=war_player_record.id,
                        )
                    )

                    # Increment total stars in clan war player record
                    war_player_record.stars += attack["stars"]

                self.__db.add_object(war_player_record)

            # If no attacks were made in war create an according clan war player record
            else:
                self.__db.add_object(
                    ClanWarPlayerRecord(
                        attacks_used=0,
                        stars=0,
                        record_status="active",
                        member_id=member["tag"],
                        war_id=war["opponent"]["tag"],
                    )
                )

        # Commit all records to database
        self.__db.commit()

    def record_war(self) -> None:
        # Fetch current war with clash of clans api
        war = self.fetch_current_clan_war(self.__clan_tag)

        if "reason" in war:
            raise IOError("Could not fetch clan war")

        # Return without accessing db if clan is not in war, preparing for war or war ended
        if war["state"] not in ["inWar", "preparation", "warEnded"]:
            raise IOError("No war available to record")

        # Query database to determine whether a record for this war already exists
        query = (
            self.__db.query(WarRecord)
            .filter(WarRecord.id == war["opponent"]["tag"])
            .first()
        )

        # If there already exists a record, and it has a result, do not update database
        if query is not None and query.result is not None:
            raise LookupError("War record already exists")

        # Create war record with null result
        war_record = WarRecord(
            id=war["opponent"]["tag"],
            end_time=parser.parse(war["endTime"]),
            result=None,
        )

        # If war has ended and hs result update war record and create player records
        if war["state"] == "warEnded":
            war_record.result = self.fetch_my_warlog()[0]["result"]
            self.record_player_clan_war_stats(war)

        # Add war record to database
        self.__db.add_object(war_record)

        # Commit records to database
        self.__db.commit()

    def get_all_members(self) -> list:
        # Get all past and current members in db
        member_history = self.__db.query(ClanMember).all()

        # Add all members still in clan to active members list
        active_members = []
        for member in member_history:
            if member.position != "nonMember":
                active_members.append(member)

        return active_members

    def get_member_by_id(self, member_id: str) -> ClanMember:
        return self.__db.query(ClanMember).filter(ClanMember.id == member_id).first()

    def get_member_by_name(self, name: str) -> ClanMember:
        return self.__db.query(ClanMember).filter(ClanMember.name == name).first()

    def get_player_record(self, record_id):
        return (
            self.__db.query(ClanWarPlayerRecord)
            .filter(ClanWarPlayerRecord.id == record_id)
            .first()
        )

    def get_player_records(self, member_id: str) -> list:
        return (
            self.__db.query(ClanWarPlayerRecord)
            .filter(ClanWarPlayerRecord.member_id == member_id)
            .all()
        )

    def get_attack_record(self, attack_id):
        return (
            self.__db.query(ClanWarAttackRecord)
            .filter(ClanWarAttackRecord.id == attack_id)
            .first()
        )

    def get_attack_records(self, cw_player_record_id: str) -> list:
        return (
            self.__db.query(ClanWarAttackRecord)
            .filter(ClanWarAttackRecord.cw_player_record_id == cw_player_record_id)
            .all()
        )

    def update_clan_efficiency(self) -> None:
        # Make a query to get all members of clan in database
        members = self.get_all_members()

        # Extract member ids from members list
        member_ids = [member.id for member in members]

        # Call update_efficiency for all members in clan database
        for member_id in member_ids:
            self.update_efficiency(member_id)

    def update_efficiency(self, member_id: str) -> None:
        # Query clan member by id
        member = self.__db.query(ClanMember).filter_by(id=member_id).first()

        # If the member is not found return
        if member is None:
            return

        # Get all war records that the member has in the database
        war_records = self.get_player_records(member_id)

        # Initialize variable to keep count of data that we will use to calculate efficiency
        total_wars = len(war_records)
        total_attacks_used = 0
        weighted_stars = 0

        # Return without accessing database if no war records are found
        if total_wars < 1:
            return

        # Update statistic for each war record the player has
        for record in war_records:
            # If the war record contains any attacks
            if record.attacks_used > 0:
                # Get all attacks that are related to given record
                attacks = self.get_attack_records(record.id)

                # Update total number of attacks used
                total_attacks_used += len(attacks)

                # For each attack in record update weighted stars
                for attack in attacks:
                    # Get town hall difference between attacker and defender
                    diff = attack.town_hall_diff
                    # If member attacked a town hall that is 2+ levels higher than their own
                    if diff > 1:
                        # Reward player by weighing stars earned higher
                        weighted_stars += attack.stars * diff
                    # If member attacked a town hall +/- 1 level of members
                    elif diff >= -1:
                        # Stars are not weighted
                        weighted_stars += attack.stars
                    # If member attacks a town hall 2+ levels lower than their own
                    else:
                        # Weight stars lower
                        weighted_stars += max(0, attack.stars + diff)

        # Get participation (attacks used) / (total potential attacks)
        participation = float(total_attacks_used) / (total_wars * 2)

        # Get stars (weighted stars earned) / (total potential stars)
        stars = float(weighted_stars) / (total_wars * 6)

        # Efficiency = (participation * 0.5) + (stars * 0.5)
        efficiency = (participation + stars) / 2

        # Updated member participation and efficiency
        member.participation = min(100.00, participation)
        member.efficiency = min(100.00, efficiency)

        # Commit changes in member participation to database
        self.__db.commit()

    def delete_attack_record_by_id(self, attack_id: uuid.UUID) -> None:
        self.__db.delete(self.get_attack_record(attack_id))

    def delete_attack_record_obj(self, attack: ClanWarAttackRecord) -> None:
        self.__db.delete(attack)

    def delete_member_by_id(self, member_id: str) -> None:
        self.__db.delete(self.get_member_by_id(member_id))

    def delete_member_record_obj(self, member: ClanMember) -> None:
        self.__db.delete(member)

    def delete_player_record_by_id(self, record_id: uuid.UUID) -> None:
        self.__db.delete(self.get_player_record(record_id))

    def delete_player_record_obj(self, player_record: ClanWarPlayerRecord) -> None:
        self.__db.delete(player_record)

    def delete_cancel(self):
        self.__db.rollback()

    def delete_commit(self):
        self.__db.commit()
