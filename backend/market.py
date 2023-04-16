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

def get_market_data():
    json_data = []
# Load market data from JSON file
    file_path = ''
    file_path = file_path + '/market.json'
    with open(file_path) as f: # here I need to enter the path of the file 
        market_data = json.load(f)
# Access contents of the dictionary
    for item in market_data:
        substrings = item['symbol'].split("/")
        crypto = substrings[0]
        item['symbol'] = crypto
        json_data.append(item)
    return json_data

def get_fav_list(emailid):
    cursor.execute('SELECT favourites from userinfo where email_id=',(session['id'],))
    t = cursor.fetchone()
    fav = t['favourites']
    fav = fav.split(",")
    return fav 

def p2p_buy_data_get():
    cursor.execute('SELECT * FROM P2PBIDDINGDATA where BUY_TYPE=false')
    list = []
    while(True):
        dic = cursor.fetchone()
        if dic == None:
            break
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT username from userinfo where email_id=%s',(dic['email_id'],))
        t = cursor.fetchone()
        dic['username'] = t['username']
        list.append(dic)
    return list

def p2p_sell_data_get():
    cursor.execute('SELECT * FROM P2PBIDDINGDATA where BUY_TYPE=True')
    list = []
    while(True):
        dic = cursor.fetchone()
        if dic == None:
            break
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT username from userinfo where email_id=%s',(dic['email_id'],))
        t = cursor.fetchone()
        dic['username'] = t['username']
        list.append(dic)
    return list

def change_pass_help(current_pass,new_pass,new_pass_confirm,email):
    msg = ''
    cursor.execute('SELECT password from userinfo where email_id=%s',email,)
    dic1 = cursor.fetchone()
    password_encrypt  =dic1['password']
    if (password_encrypt != encrypt_password(current_pass)):
        msg = 'The entered password does not matches the exisiting password'
    elif (password_encrypt == encrypt_password(current_pass)):
        if (newpass != newpass_confirm):
            msg = 'The new password does not matches the confirm new password !'
        else:
            if is_password_valid(newpass):
                # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('UPDATE userinfo SET password =%s WHERE email_id =%s',(newpass,email,))
                msg = 'PASSWORD UPDATED SUCCESSFULLY'
            else:
                msg = 'Please enter a valid password (should contain alphabets and digits from 0-9)'      
    return msg           
    
    