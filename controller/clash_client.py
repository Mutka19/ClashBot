import requests
import os
from dotenv import load_dotenv, find_dotenv
from models.clan_war_player_record import ClanWarPlayerRecord
from models.clan_war_attack_record import ClanWarAttackRecord
from models.clan_member import ClanMember
from repository.database_handler import DatabaseHandler


class ClashClient:
    def __init__(self):
        # Get api key from env and set base url
        load_dotenv(find_dotenv())
        self.base_url = "https://api.clashofclans.com/v1"
        self.api_key = os.getenv("CLASH_API_KEY")

        # Setup database handler
        self.db = DatabaseHandler()

        # Set clan name to null
        self.clan_tag = None

    def __del__(self):
        # Close db session when clash client instance is destroyed
        self.db.close()

    def set_clan(self, clan_tag: str) -> None:
        self.clan_tag = clan_tag

    def fetch_clan_info(self, clan_tag: str) -> dict:
        # Set url and headers for api call
        url = f"{self.base_url}/clans/%23{clan_tag}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        # Make call and get response
        response = requests.get(url, headers=headers)

        # Return JSON for response
        return response.json()

    def fetch_clan_members(self, clan_tag: str) -> dict:
        # Set url and headers for api call
        url = f"{self.base_url}/clans/%23{clan_tag}/members"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        # Make call and get response
        response = requests.get(url, headers=headers)

        # Return JSON for response
        return response.json()

    def fetch_my_members(self) -> dict:
        # Check if clan_tag has been set, if not return empty list
        if self.clan_tag is not None:
            return self.fetch_clan_info(self.clan_tag)
        else:
            return {}

    def fetch_clan_warlog(self, clan_tag: str) -> dict:
        # Set url and headers for api call
        url = f"{self.base_url}/clans/%23{clan_tag}/warlog"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        # Make call and get response
        response = requests.get(url, headers=headers)

        # Return JSON for response
        return response.json()

    def fetch_my_warlog(self) -> dict:
        # Check if clan_tag has been set, if not return empty list
        if self.clan_tag is not None:
            return self.fetch_clan_warlog(self.clan_tag)
        else:
            return {}

    def fetch_current_clan_war(self, clan_tag: str) -> dict:
        # Set url and headers for api call
        url = f"{self.base_url}/clans/%23{clan_tag}/currentwar"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        # Make call and get response
        response = requests.get(url, headers=headers)

        # Return JSON for response
        return response.json()

    def fetch_my_current_clan_war(self) -> dict:
        # Check if clan_tag has been set, if not return empty list
        if self.clan_tag is not None:
            return self.fetch_current_clan_war(self.clan_tag)
        else:
            return {}

    # Records all clan members to database
    def record_clan_members(self) -> None:
        # Return immediately if no clan tag has been set
        if self.clan_tag is None:
            return

        # Use fetch clan members to return list of all clan members and their stats
        clan_members = self.fetch_clan_members(self.clan_tag)["items"]

        # For each clan member add a clanmember object in database
        for member in clan_members:
            self.db.add_object(
                ClanMember(
                    id=member["tag"],
                    name=member["name"],
                    ranking=member["clanRank"],
                    position=member["role"],
                )
            )

        # Commit clan member objects to database
        self.db.commit()

    # Record percentage of attacks player has used in wars
    def record_player_clan_war_stats(self) -> None:
        # Return immediately if no clan tag has been set
        if self.clan_tag is None:
            return

        # Fetch current clan war stats
        war = self.fetch_current_clan_war(self.clan_tag)

        # For each member in clan war
        for member in war["clan"]["members"]:
            # If the member attacked created a clanwarplayerrecord in database
            if "attacks" in member:
                war_player_record = ClanWarPlayerRecord(
                    attacks_used=len(member["attacks"]),
                    stars=0,
                    record_status="active",
                    member_id=member["tag"],
                    war_id=war["opponent"]["tag"],
                )

                # Make an attack record for each attack used in war
                for attack in member["attacks"]:
                    defender = war["opponent"]["members"][attack["defenderTag"]]
                    self.db.session.add_object(
                        ClanWarAttackRecord(
                            stars=attack["stars"],
                            percentage=attack["destructionPercentage"],
                            town_hall_diff=defender["townhallLevel"] - member["townhallLevel"],
                            cw_player_record_id=war_player_record.id,
                        )
                    )

                    # Increment total stars in clan war player record
                    war_player_record.stars += attack["stars"]

            # If no attacks were made in war create an according clan war player record
            else:
                self.db.session.add_object(
                    ClanWarPlayerRecord(
                        attacks_used=0,
                        stars=0,
                        record_status="active",
                        member_id=member["tag"],
                        war_id=war["opponent"]["tag"],
                    )
                )

            # Commit all records to database
            self.db.session.commit()

    def get_all_members(self) -> list:
        return self.db.query(ClanMember).all()

    def get_player_records(self, member_id: str) -> list:
        return (
            self.db.query(ClanWarPlayerRecord)
            .filter(ClanWarPlayerRecord.member_id == member_id)
            .all()
        )

    def get_attack_records(self, cw_player_record_id: str) -> list:
        return (
            self.db.query(ClanWarAttackRecord)
            .filter(ClanWarAttackRecord.cw_player_record_id == cw_player_record_id)
            .all()
        )
