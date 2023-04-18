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

### CRYPTO BUY OR SELL, USDT_AMOUNT IS INPUT , NOT CRYPTO AMOUNT, USE MARKET_JSON FOR CURRENT PRICE

def execute_crypto_trade(email, order_type, crypto, qty):
    # qty refers to quantity of crypto (not USDT)
    script_directory = os.path.dirname(os.path.abspath(__file__))
        # Define the path to the data directory relative to the script directory
    data_directory = os.path.join(script_directory, 'data')
    file_path = data_directory + '/market_data.json'
        
    with open(file_path) as f:  
        market_data = json.load(f) # Access contents of the dictionary
        
    if order_type == "buy":
        cursor.execute('SELECT wallet from userinfo where email_id=%s', (email,))
        t = cursor.fetchone()
        wallet = json.loads(wallet[0])
        print(wallet[crypto])
        wallet[crypto] += qty;
        wallet["USDT"]
        print(wallet[crypto])
        wallet = json.dumps(wallet)
        cursor.execute('UPDATE userinfo SET wallet=%s where email_id=%s', (wallet, email,))
    elif order_type == "sell":
        cursor.execute('SELECT wallet from userinfo where email_id=%s', (email,))
        t = cursor.fetchone()
        wallet = t[0]
        wallet[crypto] -= qty
        wallet = json.dumps(wallet)
        cursor.execute('UPDATE userinfo SET wallet=%s where email_id=%s', (wallet, email,))
    
### SIMPLE QUERY TO GET THE TRADES OF CRYPTO DONE BY USER

def get_order_history(name):
    try:
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
    except Exception as e:
        return "Order History could not be fetched"
        
