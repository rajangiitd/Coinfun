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


def getdata(email):
    data = {}
    cursor.execute('SELECT DISTINCT JSON_KEYS(wallet) AS cryptocurrencies FROM userinfo where email=%s',(email,))
    crypto_val = cursor.fetchone()
    data['wallet'] = []
    file_path = ''
    file_path = file_path + '/market.json'
    with open(file_path) as f: # here I need to enter the path of the file 
        market_data = json.load(f)
# Access contents of the dictionary
    
    if crypto_val: # Check if user has any cryptocurrencies
        for i in crypto_val['cryptocurrencies'].split(','): # Use split to convert comma separated string to list
            cursor.execute("SELECT JSON_EXTRACT(wallet, '$." + i + ".amount') as amount from userinfo where email=%s",(userid,))
            temp = {}
            temp['name'] = i.replace("\"","")
            t = cursor.fetchone()
            temp['amount'] = t['amount']  
            for item in market_data:
                substrings = item['symbol'].split("/")
                crypto = substrings[0]
                item['symbol'] = crypto
                if item['symbol'] == temp['name']:
                    temp['price'] = item['last_price']
                    temp['est_balance'] = temp['price']*temp['amount']
                    break             
            data['wallet'].append(temp) # Append temp directly without curly braces
    return data