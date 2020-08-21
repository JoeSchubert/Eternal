import DB
import datetime

character_limit_per_message = 500


def list_toons(toonlist):
    ret_toons = []
    temp_text = ""
    for x in toonlist:
        if len(temp_text) + len(x[2]) <= character_limit_per_message:
            temp_text += "Character: \"" + x[2] + "\" was added to: <@!" + x[1] + "> on: " + x[3] + "\n"
        else:
            ret_toons.append(temp_text)
            temp_text = "Character: \"" + x[2] + "\" was added to: <@!" + x[1] + "> on: " + x[3] + "\n"
    if len(temp_text) > 0:
        ret_toons.append(temp_text)

    return ret_toons


def list_summary(db_conn, user_id, joined_at):
    ret_message = []
    temp_text = "<@!" + user_id + "> joined the server on " + joined_at.strftime("%b %d %y %H:%M:%S") + ".\n" \
                "I have seen this user join the server " + DB.count_events_for_user(db_conn, user_id, "join") + " " \
                "times.\n\n"

    # Get Previous nicknames
    nick_results = DB.get_previous_nicks(db_conn, user_id, "nick_change")
    if nick_results:
        temp_text += "I have seen this user as these nicks: " + nick_results + ".\n\n"

    # Get all of the users characters
    character_results = DB.search_characters_for_user(db_conn, user_id)
    for x in character_results:
        if len(temp_text) + len(x[2]) <= character_limit_per_message:
            temp_text += "Character: \"" + x[2] + "\" was added to: <@!" + x[1] + "> on: " + x[3] + "\n"
        else:
            ret_message.append(temp_text)
            temp_text = "Character: \"" + x[2] + "\" was added to: <@!" + x[1] + "> on: " + x[3] + "\n"
    if len(temp_text) > 0:
        ret_message.append(temp_text)

    return ret_message
