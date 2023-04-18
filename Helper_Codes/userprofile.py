from flask import Flask , render_template , request , redirect , url_for , session
# from flask_sqlalchemy import SQLAlchemy
# from flask_mysqldb import MySQL
import mysql.connector
import encryption_scheme

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Teamwork123",
    database="Coinfun_database"
)
cursor = db.cursor()


def get_user_profile(email):
    data = {}
    data['userid'] = email
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM userinfo where email_id=%s", (email,))
    details = cursor.fetchone()
    data['username'] = details['username']
    data['profile_pic'] = details['profile_pic']
    data['kyc'] = details['kyc']
    data['contact_number'] = details['contact_number']
    return data


def change_pass_help(current_pass,new_pass_confirm,email,new_pass):
    msg = ''
    cursor.execute('SELECT password from userinfo where email_id=%s',email,)
    dic1 = cursor.fetchone()
    password_encrypt  =dic1['password']
    if (password_encrypt != encryption_scheme.encrypt_password(current_pass)):
        msg = 'The entered password does not matches the exisiting password'
    elif (password_encrypt == encryption_scheme.encrypt_password(current_pass)):
        if (new_pass != new_pass_confirm):
            msg = 'The new password does not matches the confirm new password !'
        else:
            if encryption_scheme.is_password_valid(new_pass):
                # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('UPDATE userinfo SET password =%s WHERE email_id =%s',(new_pass,email,))
                msg = 'PASSWORD UPDATED SUCCESSFULLY'
            else:
                msg = 'Please enter a valid password (should contain alphabets and digits from 0-9)'
    return msg