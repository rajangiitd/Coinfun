import mysql.connector
import helper_functions
import os
import random
import json
import re
from datetime import datetime, timedelta

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Teamwork123",
  database="Coinfun_database"
)

# Define the list of available cryptocurrencies
# CRYPTO_LIST = ['BTC', 'ETH', 'BNB', 'DOGE', 'XRP', 'MATIC', 'ADA', 'SOL', 'SHIB', 'LTC']
CRYPTO_LIST = ['BTC', 'ETH', 'BNB', 'DOGE', 'XRP', 'MATIC', 'ADA', 'SOL']
CRYPTO_PRICE = {'BTC': 25000, 'ETH': 2000, 'BNB': 320, 'DOGE': 0.08, 'XRP': 0.5, 'MATIC': 0.6, 'ADA': 0.4, 'SOL': 20}


# Define the range for USDT and in_bid_usdt
USDT_RANGE = (5000, 50000)
IN_BID_USDT_RANGE = (0, 10000)

def convertToBinaryData(filename):    # Convert profile picture to BLOB format
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def replace_special_characters(s):    # Replace special characters in inputword with underscore
    return re.sub(r'\W+', '_', s)

mycursor = mydb.cursor()            # Code assumes profile_pics folder to be present in the same directory as this file

KYC_users = []

# create a new table for a user (Helper Function)

def create_user_table(email_id):
    # replace special characters in email_id to create a valid table name
    table_name = replace_special_characters(email_id)
    
    # MySQL query to create a new table
    create_query = f"CREATE TABLE {table_name} (crypto_name VARCHAR(255) NOT NULL, crypto_price DECIMAL(10,4) NOT NULL, order_type VARCHAR(4) NOT NULL, crypto_amount DECIMAL(18,8) NOT NULL, timestamp TIMESTAMP NOT NULL)"
    
    try:
        # execute the create query
        mycursor.execute(create_query)
        mydb.commit()
        return 1
    except Exception as e:
        return 0
      
# Insert fake data into trading history table i.e. table with table name = table_name (Helper Function)

def insert_fake_trading_history_data(email_id):
    table_name = replace_special_characters(email_id)
    wallet_ = {'USDT': 100000000000}
    for crypto in CRYPTO_LIST:
          wallet_[crypto] = 0
    # generate 5 to 50 transactions
    if(random.randint(0,1)==0):
      num_transactions = random.randint(2, 6)
    else:
      num_transactions = random.randint(10,40)
    
    last_transaction_time = datetime.now() - timedelta(weeks=1)

    for i in range(num_transactions):
        # randomly select a crypto for this transaction
        crypto = random.choice(list(CRYPTO_PRICE.keys()))
        
        # randomly select order type (buy or sell)
        order_type = random.choice(['BUY', 'SELL'])
        if(wallet_[crypto]<=0.0001):
          order_type = 'BUY'
        
        # determine amount of crypto to buy/sell
        if order_type == 'BUY':
            crypto_price = CRYPTO_PRICE[crypto] * random.uniform(0.95, 1.05)
            usdt_spent = random.randint(100, 10000)
            crypto_amount = usdt_spent / crypto_price
            wallet_['USDT'] -= usdt_spent
            wallet_[crypto] += crypto_amount
        else:
            crypto_price = CRYPTO_PRICE[crypto] * random.uniform(0.95, 1.05)
            crypto_amount = random.uniform(0.01, wallet_[crypto])
            usdt_earned = crypto_price * crypto_amount
            wallet_['USDT'] += usdt_earned
            wallet_[crypto] -= crypto_amount

        # determine timestamp
        if i == 0:
            timestamp = last_transaction_time
        else:
            timestamp = last_transaction_time + timedelta(minutes=random.randint(30, 60))

        # MySQL query to insert data into the table
        sql = f"INSERT INTO {table_name} (crypto_name, crypto_price, order_type, crypto_amount, timestamp) VALUES (%s, %s, %s, %s, %s)"
        val = (crypto, crypto_price, order_type, crypto_amount, timestamp)
        mycursor.execute(sql, val)
        mydb.commit()
        
        last_transaction_time = timestamp
    wallet_['USDT'] = round(random.uniform(*USDT_RANGE), 2)
    
    return wallet_


def generate_fake_userinfo_data(num_users):
    # Insert 20 fake users in userinfo table
    # having columns as email_id, username, password, wallet, favourites, profile_pic, kyc, contact
    for i in range(1, num_users+1):
        # Define user data
        username = f"Person{i}"
        email_id = f"{username.lower()}@gmail.com"
        kyc = True
        contact = "9" + str(random.randint(100000000000, 999999999999))
        favourites = random.sample(CRYPTO_LIST, random.randint(0, len(CRYPTO_LIST)-2))
        favourites = ",".join(favourites)
        password = helper_functions.encrypt_password(username+username)
        
        # Select profile picture for the user based on their username
        profile_pic_path = f"profile_pics/{username}.jpg"
        if not os.path.exists(profile_pic_path):
            profile_pic_path = f"profile_pics/{username}.jpeg"
        if not os.path.exists(profile_pic_path):
            profile_pic_path = f"profile_pics/blank.jpg"
            if(random.randint(0,100)<25):
              kyc = False
        
        # Allocate random wallet currencies and amounts for the user
        wallet = {}
        for crypto in CRYPTO_LIST:
          wallet[crypto] = 0
        
        if(kyc):
          for crypto in random.sample(CRYPTO_LIST, random.randint(2, len(CRYPTO_LIST))):
              wallet[crypto] = round(random.uniform(0.01, 10), 2)
          wallet['USDT'] = round(random.uniform(*USDT_RANGE), 2)
          if(random.randint(0,100)<30):
            wallet['USDT_in_bid'] = round(random.uniform(*IN_BID_USDT_RANGE), 2)  # Will sell in P2P (30% sellers of USDT)
          else:
            wallet['USDT_in_bid'] = 0   # Buyer in P2P (70% max buyers)
        else:
          wallet['USDT'] = 0            # No entry in P2P
          wallet['USDT_in_bid'] = 0
        
        #print(username, email_id, kyc, contact, password, favourites)
        #print("Initial random wallet",wallet)
        
        # Insert the user data into the database
        sql = "INSERT INTO userinfo (email_id, username, password, wallet, favourites, profile_pic, kyc, contact) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (email_id, username, password, json.dumps(wallet), favourites, convertToBinaryData(profile_pic_path), kyc, contact)
        mycursor.execute(sql, val)
        mydb.commit()   # userinfo table done 
        
        
        if(kyc==True and wallet['USDT_in_bid']==0 and random.randint(1,100)<50 ):
          buy_type = True                         ## Approx 30% people are buyers in P2PBiddingData
          transaction_usdt = random.uniform(1000, 10000)
          price = random.uniform(70,90)
          upper_limit = price* transaction_usdt
          lower_limit = random.uniform(0.5,0.75)*upper_limit
          payment_method = random.choice(['UPI', 'Bank Transfer', 'IMPS', 'Credit Card'])
          sql = "INSERT INTO P2PBiddingData (email_id, buy_type, transaction_usdt, price, payment_method, lower_limit, upper_limit) VALUES (%s, %s, %s, %s, %s, %s, %s)"
          val = (email_id, buy_type, transaction_usdt, price, payment_method, lower_limit, upper_limit)
          mycursor.execute(sql, val)
          mydb.commit()
        elif(kyc==True and wallet['USDT_in_bid']!=0):
          buy_type = False                         ## Approx 30% people are sellers in P2PBiddingData
          transaction_usdt = wallet['USDT_in_bid']
          price = random.uniform(90,100)
          upper_limit = price* transaction_usdt
          lower_limit = random.uniform(0.5,0.75)*upper_limit
          payment_method = random.choice(['UPI', 'Bank Transfer', 'IMPS', 'Credit Card'])
          sql = "INSERT INTO P2PBiddingData (email_id, buy_type, transaction_usdt, price, payment_method, lower_limit, upper_limit) VALUES (%s, %s, %s, %s, %s, %s, %s)"
          val = (email_id, buy_type, transaction_usdt, price, payment_method, lower_limit, upper_limit)
          mycursor.execute(sql, val)
          mydb.commit()
        #print("P2PBiddingData table data addition done")
        # P2PBiddingData table done
        
        # Making table for history of crypto trading for each user
        create_user_table(email_id)
        #print("Created user table for user:", email_id)
        # Inserting data into the table such that sum of net crypto transactions is equal to the amount in wallet
        if(kyc==True):
          wallet_final = insert_fake_trading_history_data(email_id)
          for item in wallet_final:
              wallet[item] = wallet_final[item]
          # update userinfo table with new wallet
          query = "UPDATE userinfo SET wallet = %s WHERE email_id = %s"
          values = (json.dumps(wallet), email_id)
          mycursor.execute(query, values)
          mydb.commit()
          #print("Updated userinfo table with new wallet")
          #print("Last wallet", wallet)
        print("Person{i} data added",i)
        
generate_fake_userinfo_data(40)