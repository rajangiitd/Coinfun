import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import base64
from backend.utils.image import convert_to_writable
import io

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Teamwork123",
    database="Coinfun_database"
)
cursor = db.cursor()

def get_market_data(filename='market_data.json'):
    try:
        json_data = []
        # Load market data from JSON file
        script_directory = os.path.dirname(os.path.abspath(__file__))
        # Define the path to the data directory relative to the script directory
        data_directory = os.path.join(script_directory, 'data')
        file_path = data_directory + '/' + filename
        with open(file_path) as f:  
            market_data = json.load(f) # Access contents of the dictionary

        for item in market_data:
            item['symbol'] = (item['symbol'].split("/"))[0]
            json_data.append(item)
        return json_data
    except:
        raise Exception('Market data could not be fetched!')

def get_fav_crypto_list(email_id):
    try: 
        cursor.execute('SELECT favourites from userinfo where email_id=%s',(email_id,))
        t = cursor.fetchone()
        if(t==None or t[0]==None or t[0]==""):
            raise Exception("You do not have any favourite crypto currencies!")
        favourite_crypto_list = t[0].split(",")
        return favourite_crypto_list    # returns a list of strings
    except Exception as e:
        raise e

def get_fav_page_data(email_id):
    try: 
        favourite_crypto_list = get_fav_crypto_list(email_id)
        market_data = get_market_data()
        fav_page_data = []
        for item in market_data:
            if(item['symbol'] in favourite_crypto_list):
                fav_page_data.append(item)
        return fav_page_data
    except Exception as e:
        raise e

def get_p2p_buy_page_data():
    try:
        cursor.execute('SELECT * FROM P2PBiddingData where buy_type = false')
        rows = cursor.fetchall()
        keys = ('email_id', 'buy_type', 'transaction_usdt', 'price', 'payment_method', 'lower_limit', 'upper_limit')
        return list([dict(zip(keys, row)) for row in rows])
    except: 
        raise Exception('Sorry! Bidding details for Buying page could not be fetched !')

def get_p2p_sell_page_data():
    try:
        cursor.execute('SELECT * FROM P2PBiddingData where buy_type = True')
        rows = cursor.fetchall()
        keys = ('email_id', 'buy_type', 'transaction_usdt', 'price', 'payment_method', 'lower_limit', 'upper_limit')
        return list([dict(zip(keys, row)) for row in rows])
    except:
        raise Exception('Sorry! Bidding details for Selling page could not be fetched!')

def form_graph(crypto, time_frame, horizontal_size=16, vertical_size=8):
    try:
        script_directory = os.path.dirname(os.path.abspath(__file__)) # Load market data from JSON file
        data_directory = os.path.join(script_directory, 'data') # Define the path to the data directory relative to the script directory
        file1_path = data_directory + '/' + "Bybit-" + crypto + "USDT-" + time_frame + ".json"
        with open(file1_path) as f:  
            currency_data = json.load(f)
        df = pd.DataFrame(currency_data)
        file2_path = data_directory + '/' + 'market_data.json'
        with open(file2_path) as f:  
            market_data = json.load(f)
        crypto_details = next((item for item in market_data if item['symbol'].split("/")[0] == crypto), {})
        
        # Convert timestamps to dates
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y-%m-%dT%H:%M:%S.%f')
        
        # Plot candlestick chart
        fig, ax = plt.subplots()
        
        # Plot the candlesticks
        for i in range(len(df)):
            x = df['Timestamp'][i]
            y_open = df['Open'][i]
            y_high = df['High'][i]
            y_low = df['Low'][i]
            y_close = df['Close'][i]
            if y_close > y_open:
                ax.plot([x, x], [y_low, y_high], color='green')
                ax.plot([x, x], [y_open, y_close], color='green', linewidth=3)
            else:
                ax.plot([x, x], [y_low, y_high], color='red')
                ax.plot([x, x], [y_open, y_close], color='red', linewidth=3)
        
        buf = io.BytesIO() # Convert image to base64 string
        fig.set_size_inches(horizontal_size, vertical_size)
        fig.savefig(buf, format='png')
        #image_path = os.path.join(data_directory, crypto+'_'+time_frame+'_candlestick_plot.png')
        #fig.savefig(image_path) # Save image to a file
        buf.seek(0)
        base64_image = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        return ( base64_image, crypto_details)
    except Exception as e:
        raise e