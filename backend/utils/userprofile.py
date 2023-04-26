import mysql.connector
from backend.utils.encryption_scheme import is_password_valid, encrypt_password
import base64
from PIL import Image
import io
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Teamwork123",
    database="Coinfun_database",
    autocommit=True
)

def get_user_profile(email):
    cursor = db.cursor()
    try:
        data = {}
        data['email_id'] = email 
        cursor.execute("SELECT * FROM userinfo where email_id=%s", (email,))
        details = cursor.fetchone()
        
        data['username'] = details[1]
        try:
            data['profile_pic'] = base64.b64decode(details[5])
            data['profile_pic'] = details[5].decode('UTF-8')
        except:
            data['profile_pic'] = ""
        data['kyc'] = details[6]
        data['contact_number'] = details[7]
        cursor.close()
        return data
    except mysql.connector.Error as e:
        db.rollback()
        raise Exception("Couldn't fetch user profile data")
    except:
        raise Exception("Couldn't fetch user profile data")


def change_pass_help(email, current_pass, new_pass, new_pass_confirm):
    try:
        if(new_pass!=new_pass_confirm):
            raise Exception("The new password does not matches the confirm new password !")
        if(is_password_valid(new_pass)==False):
            raise Exception("Please enter a valid password, it should contain atleast 1 capital and 1 small alphabets and atleast 1 digit with length between 8-25")
        
        try:
            password_encrypt_for_validation = encrypt_password(current_pass)
        except:
            raise Exception('The current entered password does not matches the exisiting password')
        cursor = db.cursor()
        cursor.execute('SELECT password from userinfo where email_id=%s',(email,))
        current_encrypted_pass = cursor.fetchone()[0]
        
        if(current_encrypted_pass!= password_encrypt_for_validation):
            cursor.close()
            raise Exception('The current entered password does not matches the exisiting password')
        else:
            new_encrypted_pass = encrypt_password(new_pass)
            cursor.execute('UPDATE userinfo SET password =%s WHERE email_id =%s',(new_encrypted_pass,email,))
            cursor.close()
            return 'PASSWORD UPDATED SUCCESSFULLY'
    except mysql.connector.Error as e:
        db.rollback()
        raise e
    except Exception as e:
        raise e

