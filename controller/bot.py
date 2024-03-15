import discord
import responses
import os
from dotenv import load_dotenv, find_dotenv
from clash_client import ClashClient

clash = None


async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        await message.author.send(
            response
        ) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


def run_discord_bot():
    # Initialize discord bot service
    load_dotenv(find_dotenv())
    token = os.getenv("DISCORD_TOKEN")
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    client = discord.Client(intents=intents)

    # Initialize clash of clan client
    clash = ClashClient()

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

        if user_message[0] == "?":
            user_message = user_message[1:]
            await send_message(message, user_message, True)
        else:
            await send_message(message, user_message, False)

    client.run(token)
