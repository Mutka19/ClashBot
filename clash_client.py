import requests
import json
import os
from dotenv import load_dotenv, find_dotenv


class ClashClient:
    def __init__(self):
        # Get api key from env and set base url
        load_dotenv(find_dotenv())
        self.base_url = "https://api.clashofclans.com/v1"
        self.api_key = os.getenv('CLASH_API_KEY')

    def get_clan_info(self, clan_tag: str) -> dict:
        url = f"{self.base_url}/clans/%23{clan_tag}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(url, headers=headers)
        return response.json()

    def get_clan_warlog(self, clan_tag: str) -> dict:
        url = f"{self.base_url}/clans/%23{clan_tag}/warlog"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(url, headers=headers)
        return response.json()

    # Return percentage of attacks player has used in wars
    def get_player_clan_war_participation(self, warlog: dict, player_tag: str, limit: int = 20):
        for war in warlog["items"][:limit]:
            pass
        return
