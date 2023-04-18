from flask import Flask , render_template , request , redirect , url_for , session
import json
# from flask_sqlalchemy import SQLAlchemy
# from flask_mysqldb import MySQL
import mysql.connector
import image 
import base64
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Teamwork123",
    database="Coinfun_database"
)
cursor = db.cursor()


def update_chat_txt(emailID1,emailID2,message):
    cursor.execute('SELECT chat_messages FROM chat WHERE (email_id1 = %s AND email_id2 = %s) OR (email_id1 = %s AND email_id2 = %s)',(emailID1,emailID2,emailID2,emailID1,))
    t = cursor.fetchone()['chat_messages']
    l = json.loads(t)
    data = {}
    data["sender"] = session['id']
    data["message"] = message
    data['image'] = json.loads("{'name':Null,'type':Null,'data':NULL}")
    t.append(data)
    messages = json.dumps(t)
    cursor.execute("UPDATE chat SET chat_messages = %s WHERE (email_id1 = %s AND email_id2 = %s) OR (email_id1 = %s AND email_id2 = %s)", (t, emailID1,emailID2,emailID2,emailID1,))
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    return None
def update_chat_image(emailID1,emailID2,photo):
    cursor.execute('SELECT chat_messages FROM chat WHERE (email_id1 = %s AND email_id2 = %s) OR (email_id1 = %s AND email_id2 = %s)',(emailID1,emailID2,emailID2,emailID1,))
    t = cursor.fetchone()['chat_messages']
    l = json.loads(t)
    data = {}
    data["sender"] = session['id']
    data["message"] = ''
    data['image'] = json.loads("{'name':Null,'type':Null,'data':NULL}")
        
    if photo.filename != '':
                 # Check if the file has an allowed image extension
        if image.allowed_file(photo.filename):
                        # Read the binary data from the file
            data = photo.read()
                # Encode the binary data as base64
            encoded_data = base64.b64encode(data)
            data['image']['data'] = encoded_data
    l.append(data)
    messages = json.dumps(l)
    cursor.execute("UPDATE chat SET chat_messages = %s WHERE (email_id1 = %s AND email_id2 = %s) OR (email_id1 = %s AND email_id2 = %s)", (t, emailID1,emailID2,emailID2,emailID1,))
    return None