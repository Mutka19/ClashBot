import requests
import json
import os
from dotenv import load_dotenv, find_dotenv
from ClanWarPlayerRecord import ClanWarPlayerRecord
from ClanWarAttackRecord import ClanWarAttackRecord
from ClanMember import ClanMember
from DatabaseHandler import DatabaseHandler


class ClashClient:
    def __init__(self):
        # Get api key from env and set base url
        load_dotenv(find_dotenv())
        self.base_url = "https://api.clashofclans.com/v1"
        self.api_key = os.getenv('CLASH_API_KEY')
        self.db = DatabaseHandler()

    def fetch_clan_info(self, clan_tag: str) -> dict:
        url = f"{self.base_url}/clans/%23{clan_tag}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(url, headers=headers)
        return response.json()

    def fetch_clan_members(self, clan_tag: str) -> dict:
        url = f"{self.base_url}/clans/%23{clan_tag}/members"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(url, headers=headers)
        return response.json()

    def fetch_clan_warlog(self, clan_tag: str) -> dict:
        url = f"{self.base_url}/clans/%23{clan_tag}/warlog"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(url, headers=headers)
        return response.json()

    def fetch_current_clan_war(self, clan_tag: str) -> dict:
        url = f"{self.base_url}/clans/%23{clan_tag}/currentwar"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(url, headers=headers)
        return response.json()

    def record_clan_members(self, clan_tag: str):
        clan_members = self.fetch_clan_members(clan_tag)["items"]
        for member in clan_members:
            self.db.add_object(
                ClanMember(
                    id=member["tag"],
                    name=member["name"],
                    ranking=member["clanRank"],
                    position=member["role"]
                )
            )
        self.db.commit()


    # Record percentage of attacks player has used in wars
    def record_player_clan_war_stats(self, clan_tag: str):
        war = self.fetch_current_clan_war(clan_tag)
        for member in war["clan"]["members"]:
            if "attacks" in member:
                print(member["name"])
                war_player_record = ClanWarPlayerRecord(
                    attacks_used=len(member["attacks"]),
                    stars=0,
                    record_status="activate",
                    member_id=member["tag"],
                    war_id=war["opponent"]["tag"]
                )
                for attack in member["attacks"]:
                    defender = war["opponent"]["members"][attack["defenderTag"]]
                    self.db.session.add_object(
                        ClanWarAttackRecord(
                            stars=attack["stars"],
                            percentage=attack["destructionPercentage"],
                            town_hall_diff=defender["townhallLevel"] - member["townhallLevel"],
                            cw_player_record_id=war_player_record.id
                        )
                    )
                    war_player_record.stars += attack["stars"]
                    print(attack["stars"])
            else:
                self.db.session.add_object(
                    ClanWarPlayerRecord(
                        attacks_used=0,
                        stars=0,
                        record_status="active",
                        member_id=member["tag"],
                        war_id=war["opponent"]["tag"]
                    )
                )
            self.db.session.commit()


