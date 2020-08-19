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
