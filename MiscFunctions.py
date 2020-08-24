def role_has_access(authorized, check):
    for roles in check:
        if roles.name in authorized:
            return True
    return False
