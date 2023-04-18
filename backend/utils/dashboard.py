import mysql.connector
import json
import os
from collections import defaultdict

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Teamwork123",
    database="Coinfun_database"
)

cursor = db.cursor()

def get_wallet_data(email):
    try:
        cursor.execute('SELECT wallet FROM userinfo where email_id=%s',(email,))
        wallet = cursor.fetchone()[0]
        wallet = json.loads(wallet) # Typecast string to dictionary
        wallet = defaultdict(float, wallet)
        
        # Get the absolute path of the directory where this script is located
        script_directory = os.path.dirname(os.path.abspath(__file__))
        # Define the path to the data directory relative to the script directory
        data_directory = os.path.join(script_directory, 'data')
        file_path = data_directory + '/market_data.json'
        
        with open(file_path) as f:  
            market_data = json.load(f) # Access contents of the dictionary
        
        list_ = []  # List of dictornaries
        # Each dictionary have symbol, amount, price, est_balance
        
        for item in market_data:
            temp = {}

            crypto = item['symbol'].split("/")[0]
            item['symbol'] = crypto
            temp['symbol'] = crypto
            temp['amount'] = wallet[crypto]
            temp['price'] = item['last_price']
            temp['est_balance'] = temp['price']*temp['amount']      
            list_.append(temp)  
            # data['wallet'].append(temp) # Append temp directly without curly braces
        return list_
    except:
        raise Exception("Couldn't fetch wallet data")