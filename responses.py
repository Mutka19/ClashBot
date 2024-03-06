def handle_response(message) -> str:
    if message == "!help":
        return "I am a bot that can help you with your Clash of Clans stats!\n Currently you can use commands 'clanstats' to get your clans stats"
    return "I didn't understand that. Please try again."