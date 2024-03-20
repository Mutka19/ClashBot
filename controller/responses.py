from controller.clash_client import ClashClient


class Responses:
    def __init__(self, clash_client: ClashClient):
        self.clash_client = clash_client

    def handle_response(self, message) -> str:
        if message == "/help":
            return ("I am a bot that can help you with your Clash of Clans stats!\n\n" +
                    "You have access to the following commands:\n" +
                    "/help - shows this help message\n" +
                    "/member + (clan member name or id) - shows the members stats\n" +
                    "/members - shows all the names of the members of your clan\n" +
                    "/members + (clan tag) - shows the names of the members of the tagged clan\n" +
                    "/war update - makes a record of the current war and updates member stats when war has ended\n\n" +
                    "And more commands are on the way!")

        message = message.split()

        if message[0] == "/member" and len(message) == 2:
            member = None
            if message[1][0] == "#":
                member = self.clash_client.get_member_by_id(message[1][1:])
            else:
                member = self.clash_client.get_member_by_name(message[1])

            if member:
                member_string = (f"Name: {member.name}\n" +
                                f"Clan Role: {member.position}\n" +
                                f"Efficiency: {member.efficiency}\n" +
                                f"Participation: {member.participation}\n" +
                                f"Clan Rank: {member.ranking}")

            return member_string if member is not None else "Member not found."

        if message[0] == "/members" and (len(message) == 1 or len(message) == 2):
            if len(message) == 1:
                return ", ".join([member["name"] for member in self.clash_client.fetch_my_members()])
            else:
                if message[1][0] == "#":
                    message[1] = message[1][1:]
                return ", ".join([member["name"] for member in self.clash_client.fetch_clan_members(message[1])])

        if message[0] == "/setup" and len(message) == 2:
            # If hashtag on clan tag remove it and continue
            if message[1][0] == "#":
                message[1] = message[1][1:]

            # If clan cannot be reached by api
            if "reason" in self.clash_client.fetch_clan_info(message[1]):
                return "Clan not found."
            else:
                self.clash_client.set_clan(message[1])
                return "Clan found and set."

        if message[0] == "/war" and message[1] == "update":
            # Check for any extra unwanted arguments
            if len(message) > 2:
                return "Unexpected argument(s) found, use /help for more information."

            # Update war records in clash client
            self.clash_client.record_war()

            return "War record successfully updated."

        return "I didn't understand that. Please try again."
