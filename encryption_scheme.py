import hashlib

def is_password_valid(password):
    try:
        if len(password) < 8 or len(password)>25 or password.isalpha() or password.isnumeric():
            return False
        # isalpha returns true if all characters are alphabetic
        # isnumeric returns true if all characters are numeric
        return True
    except:
        raise Exception("PasswordValidationFailed!")

def encrypt_password(password):
    try:
        if(is_password_valid(password)):
            # hash the salted password using SHA-256
            salted_password = password + "my_salt" + password[::-1]
            hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()
            return hashed_password
    except:
        raise Exception("PasswordEncryptionFailed!")
