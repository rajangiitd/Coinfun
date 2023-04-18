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

### Getting the P2P trade history data

def transaction_data(email):
    data = {}
    msg = ''
    # if request.method == 'GET':
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute("SELECT * FROM P2PTradeData where buyer_email_id=%s or seller_email_id=%s", (email,email,))
    data['order_id'] = []
    data['client'] = []
    data['order_type'] = []
    data['transaction_usdt'] = []
    data['price'] = []
    data['time_stamp'] = []
    while (True):
        l = cursor.fetchone()
        if l == None:
            break
        data['order_id'].append(l['order_id'])
        if (l['buyer_email_id'] == session['id']):
                # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT username from userinfo where email_id=%s',(l['seller_email_id'],))
            t = cursor.fetchone()
            data['client'].append((t['username'],l['seller_email_id']))
            data['order_type'].append('buy')
            data['transaction_usdt'].append(l['transaction_usdt'])
            data['price'].append(l['price'])
            data['time_stamp'].append(l['time_stamp'])
        elif (l['seller_email_id'] == session['id']):
            # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT username from userinfo where email_id=%s',(l['buyer_email_id'],))
            t = cursor.fetchone()
            data['client'].append({t['username'],l['buyer_email_id']})
            data['order_type'].append('sell')
            data['transaction_usdt'].append(l['transaction_usdt'])
            data['price'].append(l['price'])
            data['time_stamp'].append(l['time_stamp'])
    if (len(data['order_id']) == 0):
        msg = 'YOU DO NOT HAVE ANY TRANSACTION HISTORY !'
        
    return (data,msg)
