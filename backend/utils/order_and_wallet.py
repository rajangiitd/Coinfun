# from flask import Flask , render_template , request , redirect , url_for , session
import json
import os
import datetime
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

def change_wallet(email,order_type,crypto,usdt_qty):
    script_directory = os.path.dirname(os.path.abspath(__file__))
        # Define the path to the data directory relative to the script directory
    data_directory = os.path.join(script_directory, 'data')
    file_path = data_directory + '/market_data.json'
    with open(file_path) as f:  
        market_data = json.load(f) # Access contents of the dictionary
    for item in market_data:
        symbol = (item['symbol'].split('/'))[0]
        if (symbol == crypto):
            last_price = item['last_price']
            break
    if order_type == "buy":
        cursor.execute('SELECT wallet from userinfo where email_id=%s', (email,))
        t = cursor.fetchone()
        wallet = t[0]
        wallet = json.loads(wallet)
        if (usdt_qty > wallet['USDT']):
            raise Exception('You do not have sufficient balance')
        wallet['USDT'] -= usdt_qty
        qty = (usdt_qty/last_price)
        wallet[crypto] += qty
        # wallet[crypto] += qty
        wallet = json.dumps(wallet)
        add_order(email,crypto,last_price,qty,'BUY')
        cursor.execute('UPDATE userinfo SET wallet=%s where email_id=%s', (wallet, email,))
    elif order_type == "sell":
        cursor.execute('SELECT wallet from userinfo where email_id=%s', (email,))
        t = cursor.fetchone()
        wallet = t[0]
        qty = usdt_qty/last_price
        if (wallet[crypto] < qty):
            raise Exception('You do not have sufficient coins !')
        wallet[crypto] -= qty
        wallet['USDT'] += usdt_qty
        add_order(email,crypto,last_price,qty,'SELL')
        wallet = json.dumps(wallet)
        cursor.execute('UPDATE userinfo SET wallet=%s where email_id=%s', (wallet, email,))
def get_order_history(email_ID):
    try:
        history = []
        msg = ''
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from CryptoTradingHistoryData where email_id=%s',(email_ID,))
        while(True):
            data = cursor.fetchone()
            temp = {}
            if (data == None):
                break       
            temp['crypto_name'] = data[1]
            temp['crypto_price'] = data[2]
            temp['order_type'] = data[3]
            temp['crypto_amount'] = data[4]
            temp['timestamp'] = data[5]
            history.append(data)
        if (len(history) == 0):
            msg = 'You do not have any orders till now, Enter the market to place your orders !'
        return (history,msg)
    except:
        raise Exception('Could not fetch order details !')

def add_order(email_id,crypto,last_price,crypto_amount,order_type):
    try:
        cursor.execute('INSERT INTO CryptoTradingHistoryData VALUES(%s,%s,%s,%s,%s,%s)',(email_id,crypto,last_price,order_type,crypto_amount,datetime.datetime.now().time(),))
    except:
        raise Exception('Could not add order details to user\'s order history')