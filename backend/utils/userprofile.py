import mysql.connector
from backend.utils.encryption_scheme import is_password_valid, encrypt_password

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Teamwork123",
    database="Coinfun_database"
)

cursor = db.cursor()

def get_user_profile(email):
    data = {}
    data['email_id'] = email 
    cursor.execute("SELECT * FROM userinfo where email_id=%s", (email,))
    details = cursor.fetchone()
    
    data['username'] = details[1]
    data['profile_pic'] = details[5]
    data['kyc'] = details[6]
    data['contact_number'] = details[7]
    return data


def change_pass_help(email, current_pass, new_pass, new_pass_confirm):
    try:
        if(new_pass!=new_pass_confirm):
            raise Exception("The new password does not matches the confirm new password !")
        if(not is_password_valid(new_pass)):
            raise Exception("Please enter a valid password (should contain 1 capital and 1 small alphabets and atleast 1 digit with length between 8-25)")
        
        password_encrypt_for_validation = encrypt_password(current_pass)
        cursor.execute('SELECT password from userinfo where email_id=%s',(email,))
        current_encrypted_pass = cursor.fetchone()[0]
        
        if(current_encrypted_pass!= password_encrypt_for_validation):
            raise Exception('The entered password does not matches the exisiting password')
        else:
            new_encrypted_pass = encrypt_password(new_pass)
            cursor.execute('UPDATE userinfo SET password =%s WHERE email_id =%s',(new_encrypted_pass,email,))
            return 'PASSWORD UPDATED SUCCESSFULLY'
        
    except Exception as e:
        return e