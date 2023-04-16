from flask import Flask , render_template , request , redirect , url_for , session
# from flask_sqlalchemy import SQLAlchemy
# from flask_mysqldb import MySQL
import mysql.connector

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