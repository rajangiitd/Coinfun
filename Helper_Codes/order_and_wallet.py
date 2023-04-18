from flask import Flask , render_template , request , redirect , url_for , session
import json
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

def change_wallet(email,order_type,crypto,qty):
    if order_type == "buy":
        cursor.execute('SELECT wallet from userinfo where email_id=%s', (email,))
        t = cursor.fetchone()
        wallet = t['wallet']
        wallet = json.loads(wallet)
        wallet[crypto] += qty;
        wallet = json.dumps(wallet)
        cursor.execute('UPDATE userinfo SET wallet=%s where email_id=%s', (wallet, email,))
    elif order_type == "sell":
        cursor.execute('SELECT wallet from userinfo where email_id=%s', (email,))
        t = cursor.fetchone()
        wallet = t['wallet']
        wallet[crypto] -= qty
        wallet = json.dumps(wallet)
        cursor.execute('UPDATE userinfo SET wallet=%s where email_id=%s', (wallet, email,))
def get_order_history(name):
    history = []
    msg = ''
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * from %s',(name,))
    while(True):
        data = cursor.fetchone()
        if (data == None):
            break        
        history.append(data)
    if (len(history) == 0):
        msg = 'You do not have any orders till now, Enter the market to place your orders !'
    return (history,msg)