import mysql.connector
from backend.utils.encryption_scheme import encrypt_password
import json
from collections import defaultdict

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Teamwork123",
  database="Coinfun_database"
)

mycursor = mydb.cursor()

def create_test_account(num):
    for i in range(1,num+1):
        username = f"Testaccount{i}"
        email_id = f"coinfunnoreply@gmail.com"
        kyc = True
        contact = "12345678910"
        favourites = "BTC"
        password = encrypt_password(username+username)
        wallet_ = {'USDT': 50000,'BTC': 0, 'ETH': 0, 'BNB': 0, 'DOGE': 0, 'XRP': 0, 'MATIC': 0, 'ADA': 0, 'SOL': 0,'USDT_in_bid': 0}
        # Insert the user data into the database
        sql = "INSERT INTO userinfo (email_id, username, password, wallet, favourites, kyc, contact) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (email_id, username, password, json.dumps(wallet_), favourites, kyc, contact)
        mycursor.execute(sql, val)
        mydb.commit()   # userinfo table done 

create_test_account(1)