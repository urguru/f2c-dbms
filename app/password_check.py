from werkzeug.security import generate_password_hash, check_password_hash


def set_password(password):
    password_hash = generate_password_hash(password)
    return password_hash

def check_password(password_hash,password):
    return check_password_hash(password_hash, password)

