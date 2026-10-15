

def username_valid(uname):

    allowed = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    if not all((ch in set(allowed) for ch in uname)):
        return (False, 'CHAR')

    if len(uname) < 3:
        return (False, 'SMALL')

    if len(uname) > 16:
        return (False, 'BIG')

    return True

def password_valid(pword):

    if len(pword) < 5 and len(pword) != 0:
        return (False, 'SMALL')

    return True