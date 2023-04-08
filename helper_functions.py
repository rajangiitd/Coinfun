##### Helper functions for password encryption #####

def is_password_valid(password):
    if len(password) < 8 or len(password)>25:
        return False
    if password.isalpha():  # isalpha returns true if all characters are alphabetic
        return False
    if password.isnumeric(): # isnumeric returns true if all characters are numeric
        return False
    return True

def polynomial_hashing(password):
    prime_factor = 31
    hash_value = 0
    temp = 1
    mod = (10**9) + 7   # A large prime number
    try:
        for i in range(len(password)):
            hash_value += ord(password[i])*temp
            temp = temp*prime_factor
        return str(hash_value % mod)
    except:
        return str(password) + str(101)     # in case of unforseen error


def encrypt_password(password):
    if(is_password_valid(password)):
        mysecretkey = '012012012012012012012012012012012012012012012' # Fixed key for encryption
        encrypted = ''
        for i in range(len(password)):
            encrypted += chr(ord(password[i]) + int(mysecretkey[i]))  # Making a encryption by taking xor of corresponding 
                                                            # characters in mysecretkey     
        # returning the concatenation of encrypted password and the polynomial hash of encrypted password
        return encrypted + polynomial_hashing(encrypted)
    else:
        return "Invalid Password"
