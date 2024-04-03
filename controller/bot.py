#    Copyright 2024 Daemon Mutka
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import discord
import os
from dotenv import load_dotenv, find_dotenv
from controller.clash_client import ClashClient
from controller.responses import Responses


class Bot:
    def __init__(self):
        # Load discord token
        load_dotenv(find_dotenv())
        self.token = os.getenv("DISCORD_TOKEN")

        # Initialize clash client and response handler
        clash_client = ClashClient()
        self.responses = Responses(clash_client)

    async def send_message(self, message, user_message, is_private):
        try:
            if user_message[0] == "/":
                response = self.responses.handle_response(user_message, message.author.roles)
                await message.author.send(response) if is_private \
                    else await message.channel.send(response)
        except Exception as e:
            print(e)

    def run_discord_bot(self):
        # Initialize discord bot service
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            print(f"{client.user} is now up and running!")

        @client.event
        async def on_message(message):
            if message.author == client.user:
                return

            username = str(message.author)
            user_message = str(message.content)
            channel = str(message.channel)

            # Uncomment print statement to log messages in console
            # print(f"{username} said '{user_message}' in {channel}")

            is_private = False

            if user_message[0] == "?":
                user_message = user_message[1:]
                is_private = True

            if user_message[0] == "/":
                await self.send_message(message, user_message, is_private)

        client.run(self.token)
