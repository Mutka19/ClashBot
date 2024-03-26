from controller.clash_client import ClashClient


class Responses:
    def __init__(self, clash_client: ClashClient):
        self.clash_client = clash_client

    def handle_response(self, message) -> str:
        if message == "/help":
            return (
                "I am a bot that can help you with your Clash of Clans stats!\n\n"
                + "You have access to the following commands:\n"
                + "/banish {clan member name or ID} - deletes all records of this player from the database\n"
                + "/clan update - updates the clans member database\n"
                + "/efficiency update - updates the efficiency ratings of every clan member\n"
                + "/help - shows this help message\n"
                + "/member + {clan member name or ID} - shows the members stats\n"
                + "/members - shows all the names of the members of your clan and their efficiency\n"
                + "/members + {clan tag} - shows the names of the members of the tagged clan\n"
                + "/war update - makes a record of the current war and updates member stats when war has ended\n\n"
                + "And more commands are on the way!"
            )

        message = message.split()

        if message[0] == "/banish":
            if len(message) < 2:
                return "You must provide a name or ID to banish."

            member = None
            if message[1][0] == "#":
                member = self.clash_client.get_member_by_id(message[1][1:])
            else:
                member = self.clash_client.get_member_by_name(message[1])

            if member is None:
                return "Member not found in database."

            try:
                player_records = self.clash_client.get_player_records(member.id)

                for record in player_records:
                    # Query for attack objects using player record id
                    attacks = self.clash_client.get_attack_records(record.id)

                    for attack in attacks:
                        # Delete attack(s)
                        self.clash_client.delete_attack_record_obj(attack)

                    # Delete player record(s)
                    self.clash_client.delete_player_record_obj(record)

                # Delete member record
                self.clash_client.delete_member_record_obj(member)

                # Confirm deletion
                self.clash_client.delete_commit()

            except:
                # Cancel deletion if error occurs
                self.clash_client.delete_cancel()
                return (
                    "An error occurred while trying to delete records. Please try again"
                )

            return f"Banish member {member.name}"

        if message[0] == "/clan" and message[1] == "update":
            self.clash_client.record_clan_members()
            return "Clan database updated."

        if message[0] == "/efficiency" and message[1] == "update":
            if len(message) == 2:
                self.clash_client.update_clan_efficiency()
            return "Clan Efficiency has been updated."

        if message[0] == "/member" and len(message) == 2:
            member = None
            if message[1][0] == "#":
                member = self.clash_client.get_member_by_id(message[1][1:])
            else:
                member = self.clash_client.get_member_by_name(message[1])

            member_string = None
            if member:
                member_string = (
                    f"Name: {member.name}\n"
                    + f"Clan Role: {member.position}\n"
                    + f"Efficiency: {member.efficiency}\n"
                    + f"Participation: {member.participation}\n"
                    + f"Clan Rank: {member.ranking}"
                )

            return member_string if member is not None else "Member not found."

        if message[0] == "/members" and (len(message) == 1 or len(message) == 2):
            if len(message) == 1:
                return "\n".join(
                    [
                        f"{member.name}'s efficiency & participation: {member.efficiency}, {member.participation}"
                        for member in sorted(
                            self.clash_client.get_all_members(),
                            key=lambda mem: (mem.efficiency, mem.participation),
                            reverse=True,
                        )
                    ]
                )
            else:
                if message[1][0] == "#":
                    message[1] = message[1][1:]
                return ", ".join(
                    [
                        member["name"]
                        for member in self.clash_client.fetch_clan_members(message[1])
                    ]
                )

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

            try:
                # Try updating war records with clash client
                self.clash_client.record_war()
            except Exception as e:
                # Return exception description if recording war fails
                return f"{e}"

            return "War record successfully updated."

        return "I didn't understand that. Please try again."
