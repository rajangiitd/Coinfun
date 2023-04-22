import json
import os
import datetime
import mysql.connector
from backend.utils.marketandp2p import get_market_data
import datetime

def time_convertor_to_str(datetime_obj):
    return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Teamwork123",
    database="Coinfun_database"
)

cursor = db.cursor()

def add_order(email_id,crypto,last_price,crypto_amount,order_type): #order_type = BUY/SELL
    try:
        cursor.execute('INSERT INTO CryptoTradingHistoryData VALUES(%s,%s,%s,%s,%s,%s)',(email_id,crypto,last_price,order_type,crypto_amount,datetime.datetime.now(),))
        db.commit()
        return "Order Successful!"
    except:
        raise Exception('Could not add order details to user\'s order history')

def get_order_history(email_ID):
    try:
        history = []
        cursor.execute('SELECT * from CryptoTradingHistoryData where email_id=%s',(email_ID,))
        data = cursor.fetchall()
        if len(data) == 0:
            raise Exception('You do not have any orders till now. Enter the market to place your orders!')
        else:
            for row in data:
                temp = {}
                temp['crypto_name'] = row[1]
                temp['crypto_price'] = float(row[2])
                temp['order_type'] = row[3]
                temp['crypto_amount'] = float(row[4])
                temp['timestamp'] = time_convertor_to_str(row[5])
                temp['net_usdt'] = temp['crypto_price']*temp['crypto_amount']
                history.append(temp)
        return history
    except Exception as e:
        raise e

def change_wallet(email_id, order_type, crypto , usdt_qty):
    try:
        market_data = get_market_data()
        
        last_price = next((item['last_price'] for item in market_data if item['symbol'].startswith(crypto)), None)
        
        cursor.execute('SELECT wallet from userinfo where email_id=%s', (email_id,))
        t = cursor.fetchone()
        wallet = json.loads(t[0])
        
        if order_type.lower() == "buy":
            if usdt_qty > wallet['USDT']:
                raise Exception('You do not have sufficient USDT balance')
            wallet['USDT'] -= usdt_qty
            crypto_amount = (usdt_qty/last_price)
            wallet[crypto] += crypto_amount
            wallet = json.dumps(wallet)
            add_order(email_id, crypto, last_price, crypto_amount, 'BUY')
            cursor.execute('UPDATE userinfo SET wallet=%s where email_id=%s', (wallet, email_id,))
        elif order_type.lower() == "sell":
            crypto_amount = usdt_qty/float(last_price)
            if(wallet[crypto] < crypto_amount):
                raise Exception('You do not have sufficient crypto coins!')
            wallet[crypto] -= crypto_amount
            wallet['USDT'] += usdt_qty
            add_order(email_id, crypto, last_price, crypto_amount, 'SELL')
            wallet = json.dumps(wallet)
            cursor.execute('UPDATE userinfo SET wallet=%s where email_id=%s', (wallet, email_id,))
        db.commit()
        return "Wallet Updated Successfully!"
    except Exception as e:
        raise e