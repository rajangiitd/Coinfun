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

def get_market_data():
    json_data = []
# Load market data from JSON file
    file_path = ''
    file_path = file_path + '/market.json'
    with open(file_path) as f: # here I need to enter the path of the file
        market_data = json.load(f)
# Access contents of the dictionary
    for item in market_data:
        substrings = item['symbol'].split("/")
        crypto = substrings[0]
        item['symbol'] = crypto
        json_data.append(item)
    return json_data

def get_fav_list(emailid):
    cursor.execute('SELECT favourites from userinfo where email_id=',(session['id'],))
    t = cursor.fetchone()
    fav = t['favourites']
    fav = fav.split(",")
    return fav

def p2p_buy_data_get():
    cursor.execute('SELECT * FROM P2PBIDDINGDATA where BUY_TYPE=false')
    list = []
    while(True):
        dic = cursor.fetchone()
        if dic == None:
            break
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT username from userinfo where email_id=%s',(dic['email_id'],))
        t = cursor.fetchone()
        dic['username'] = t['username']
        list.append(dic)
    return list

def p2p_sell_data_get():
    cursor.execute('SELECT * FROM P2PBIDDINGDATA where BUY_TYPE=True')
    list = []
    while(True):
        dic = cursor.fetchone()
        if dic == None:
            break
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT username from userinfo where email_id=%s',(dic['email_id'],))
        t = cursor.fetchone()
        dic['username'] = t['username']
        list.append(dic)
    return list

def change_pass_help(current_pass,new_pass,new_pass_confirm,email):
    msg = ''
    cursor.execute('SELECT password from userinfo where email_id=%s',email,)
    dic1 = cursor.fetchone()
    password_encrypt  =dic1['password']
    if (password_encrypt != encrypt_password(current_pass)):
        msg = 'The entered password does not matches the exisiting password'
    elif (password_encrypt == encrypt_password(current_pass)):
        if (newpass != newpass_confirm):
            msg = 'The new password does not matches the confirm new password !'
        else:
            if is_password_valid(newpass):
                # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('UPDATE userinfo SET password =%s WHERE email_id =%s',(newpass,email,))
                msg = 'PASSWORD UPDATED SUCCESSFULLY'
            else:
                msg = 'Please enter a valid password (should contain alphabets and digits from 0-9)'
    return msg
    
    
def fetch_fav(email):
    cursor.execute('SELECT favourites from userinfo where email_id=%s', (email,))
    dic = cursor.fetchone()
    fav = dic['favourites'].split(",")
    for item in fav:
        item = item.replace("\"","")
    with open('market.json') as f: # here I need to enter the path of the file 
        market_data = json.load(f) 
    fav_details = [] 
    for item in market_data:
        substrings = item['symbol'].split("/")
        crypto = substrings[0]
        item['symbol'] = crypto
        if item['symbol'] in fav:
            fav_details.append(item)
    return fav_details


def form_graph(crypto):
    file_path_1 = ''
    file_path_1 = file_path_1 + "/" + "Bybit-" + crypto + "USDT-1m.jason"
    
    with open(file_path_1) as f: # here I need to enter the path of the file 
        market_data = json.load(f)
    data = market_data
    # Convert data to a Pandas DataFrame
    df = pd.DataFrame(data)
    file_path_2 = ''
    file_path_2 = file_path_2 + '/market.json'
    with open('market.json') as f: # here I need to enter the path of the file 
        market = json.load(f)
    crypto_details = {}
    for item in market:
        substrings = item['symbol'].split("/")
        item['symbol'] = substrings[0]
        if item['symbol'] == crypto:
            crypto_details = item
            break
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

# Save plot as PNG image
    image_path = os.path.join(os.getcwd(), 'static', 'candlestick_plot.png')
    fig.savefig(image_path)

    plt.close()
    
    return (image_path,crypto_details)