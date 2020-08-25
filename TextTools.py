from SqlObjects import User

character_limit_per_message = 500


def list_toons(toonlist):
    ret_toons = []
    temp_text = ""
    for x in toonlist:
        if len(temp_text) + len(x.character) <= character_limit_per_message:
            temp_text += "Character: \"" + x.character + "\" was added to: <@!" + x.discord_id + "> on: " + x.timestamp + "\n"
        else:
            ret_toons.append(temp_text)
            temp_text = "Character: \"" + x.character + "\" was added to: <@!" + x.discord_id + "> on: " + x.timestamp + "\n"
    if len(temp_text) > 0:
        ret_toons.append(temp_text)

    return ret_toons


def list_summary(user_id, joined_at):
    ret_message = []
    query = User.history_joins(user_id)
    temp_text = "<@!" + user_id + "> joined the server on " + joined_at.strftime("%b %d %y %H:%M:%S") + ".\n" \
                "I have seen this user join the server " + str(query.count()) + " " \
                "times.\n\n"

    # Get Previous nicknames
    query = User.history_nicks(user_id)
    previous_nicks = []
    for nick in query.all():
        previous_nicks.append(nick.user_name)
    # nick_results = DB.get_previous_nicks(db_conn, user_id, "nick_change")
    if previous_nicks:
        temp_text += "I have seen this user as these nicks: " + ", ".join(previous_nicks) + ".\n\n"

    # Get all of the users characters
    ret_message.append(list_toons(user_id))

    return ret_message
