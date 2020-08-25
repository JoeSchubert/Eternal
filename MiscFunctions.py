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