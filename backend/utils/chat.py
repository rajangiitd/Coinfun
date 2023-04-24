import json
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Teamwork123",
    database="Coinfun_database",
    autocommit=True
)

cursor = db.cursor()

def update_chat_txt(sender_email, emailID1, emailID2, message):
    try:
        if (emailID1 > emailID2):
            emailID1,emailID2 = emailID2,emailID1
        if(emailID1==emailID2):
            raise "You cannot send message to yourself!"
        cursor.execute('SELECT chat_messages FROM chat WHERE email_id1 = %s AND email_id2 = %s', (emailID1, emailID2,))
        t = cursor.fetchone()
        if (t == None):
            chat = json.dumps([])
            cursor.execute('INSERT INTO chat (email_id1, email_id2, chat_messages) VALUES (%s, %s, %s)', (emailID1, emailID2, chat,))
            db.commit()
            update_chat_txt(sender_email,emailID1,emailID2,message)
        t = json.loads(t[0])
        data = {}
        data["sender"] = sender_email
        data["message"] = message
        data['image'] = {}
        data['image']['name'] = None
        data['image']['type'] = None
        data['image']['data'] = None
        # data['image'] = json.loads("{'name':Null,'type':Null,'data':NULL}")
        t.append(data)
        t = json.dumps(t)
        cursor.execute("UPDATE chat SET chat_messages = %s WHERE email_id1 = %s AND email_id2 = %s", (t, emailID1,emailID2))
        db.commit()
        return "Chat messages updated successfully!"
    except:
        raise Exception("Chat Messages Coudn't be updated!")



def update_chat_image(sender_email,emailID1,emailID2,photo):
    try:
        if (emailID1 > emailID2):
            emailID1,emailID2 = emailID2,emailID1
        if(emailID1==emailID2):
            raise "You cannot send message to yourself!"
        cursor.execute('SELECT chat_messages FROM chat WHERE email_id1 = %s AND email_id2 = %s', (emailID1, emailID2,))
        t = cursor.fetchone()
        if (t == None):
            chat = json.dumps([])
            cursor.execute('INSERT INTO chat (email_id1, email_id2, chat_messages) VALUES (%s, %s, %s)', (emailID1, emailID2, chat,))
            db.commit()
            update_chat_txt(sender_email,emailID1,emailID2,photo)
        t = json.loads(t[0])
        
        data = {}
        data["sender"] = sender_email
        data["message"] = ''
        # data['image'] = json.loads("{'name':Null,'type':Null,'data':NULL}")
        data['image'] = {}
        data['image']['name'] = None
        data['image']['type'] = None
        data['image']['data'] = photo # Encoded base64 string
        t.append(data)
        
        t = json.dumps(t)
        cursor.execute("UPDATE chat SET chat_messages = %s WHERE email_id1 = %s AND email_id2 = %s", (t, emailID1,emailID2))
        db.commit()
        return "Chat messages updated successfully!"
    except:
        raise Exception("Chat Messages Coudn't be updated!")