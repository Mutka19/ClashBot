from bot import clash


def handle_response(message) -> str:
    if message == "!help":
        return "I am a bot that can help you with your Clash of Clans stats!\n Currently you can use commands 'clanstats' to get your clans stats"
    message = message.split()

    if message[0] == "/setup" and len(message) == 2:
        # If hashtag on clan tag remove it and continue
        if message[1][0] == "#":
            message[1] = message[1][1:]

        # If clan cannot be reached by api
        if "reason" in clash.fetch_clan_info(message[1]):
            return "Clan not found."
        else:
            clash.set_clan(message[1])
            return "Clan found and set."

    if message[0] == "/members" and (len(message) == 1 or len(message) == 2):
        if len(message) == 1:
            return clash.fetch_my_members()
        else:
            if message[1][0] == "#":
                message[1] = message[1][1:]
            return clash.fetch_members(message[1])

    return "I didn't understand that. Please try again."
