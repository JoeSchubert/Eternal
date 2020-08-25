def role_name_has_access(authorized, check):
    for roles in check:
        if roles.name in authorized:
            return True
    return False


def role_id_has_access(authorized, check):
    for roles in check:
        if roles.id in authorized:
            return True
    return False


def get_new_roles(old_roles, new_roles):
    result = [x for x in new_roles if x not in old_roles]
    if len(result) > 0:
        return result[0].name
    return False
