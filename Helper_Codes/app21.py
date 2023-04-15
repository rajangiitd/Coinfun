from flask import Flask , render_template , request , redirect , url_for , session
# from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL 
import MySQLdb.cursors
import pandas as pd
import matplotliblib.pyplot as plt
import re 
import MySQLdb

app=Flask(__name__, static_folder='static')
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
app.secret_key='your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'coinfun_database'

sql=MySQL(app)
def is_password_valid(password):
    if len(password) < 8 or len(password)>25:
        return False
    if password.isalpha():  # isalpha returns true if all characters are alphabetic
        return False
    if password.isnumeric(): # isnumeric returns true if all characters are numeric
        return False
    return True

def polynomial_hashing(password):
    prime_factor = 31
    hash_value = 0
    temp = 1
    mod = (10**9) + 7   # A large prime number
    try:
        for i in range(len(password)):
            hash_value += ord(password[i])*temp
            temp = temp*prime_factor
        return str(hash_value % mod)
    except:
        return str(password) + str(101)     # in case of unforseen error


def encrypt_password(password):
    
    mysecretkey = 'abcdefghijklmnopqrstuvwxyz' # Fixed key for encryption
    encrypted = ''
    for char in password:
        encrypted += chr(ord(char) ^ ord(mysecretkey))  # Making a encryption by taking xor of corresponding 
                                                        # characters in mysecretkey     
    # returning the concatenation of encrypted password and the polynomial hash of encrypted password
    return encrypted + polynomial_hashing(encrypted)
    

@app.route('/login')
def first():
	return render_template('login.html', msg = '')

@app.route('/login', methods =['GET'])
def login():
	message = ''
	if request.method == 'GET' and 'email' in request.form and 'password' in request.form:
		email = request.form['email']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM userinfo WHERE email_id = % s AND password = % s', (email, encrypt_password(password), ))
		account = cursor.fetchone()
		if account:
			session['loggedin'] = True
			session['id'] = account['user_id']
			session['username'] = account['username']
			message = 'Logged in successfully !'
			return redirect(url_for('dashboard',userid=session['id']))
		else:
			message = 'Incorrect username / password !'
	return render_template('login.html', msg = message)

@app.route('/register', methods=['POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form and 'confirm-password' in request.form and 'phone-number' in request.form and 'profile_pic' in request.files:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        confirm_password=request.form['confirm-password']
        phone_number = request.form['phone-number']
        profile_pic = request.files['profile_pic']
        if profile_pic and allowed_file(profile_pic.filename):
            filename = secure_filename(profile_pic.filename)
            profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            pic = url_for('static', filename='uploads/' + filename)
        else:
            pic = ''
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email_id = % s', (email,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif password!=confirm_password:
            msg = 'Password and confirm-Password must be same'
        elif is_password_valid(password) == False:
            msg = 'Password must contains letters and numbers both'
        else:
            cursor.execute('INSERT INTO userinfo VALUES ( % s, % s, % s, "{}", "[]", % s, false)', (email,username, encrypt_password(password),pic, ))
            mysql.connection.commit()
            
            cursor.execute('SELECT id, username FROM userinfo WHERE email_id = %s', (email,))
            result = cursor.fetchone()
            user_id = result['email_id']
            username = result['username']
            # Set session variables
            session['loggedin'] = True
            session['id'] = user_id
            session['username'] = username
            msg = 'You have successfully registered !'
            return redirect(url_for('dashboard'))
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)



@app.route('/dashboard')
def dashboard():
    data = {}
    data['email'] = session['id']
    cursor = mysql.connection.cursor(dictionary=True) # Use dictionary cursor
    # cursor.execute('SELECT username from userinfo where email_id = %s',(userid,))
    # dic1 = cursor.fetchone()
    # if dic1: # Check if user exists
    data['username'] = session['username']
    cursor.execute('SELECT DISTINCT JSON_KEYS(wallet) AS cryptocurrencies FROM userinfo where email=%s',(userid,))
    crypto_val = cursor.fetchone()
    data['wallet'] = []
    if crypto_val: # Check if user has any cryptocurrencies
        for i in crypto_val['cryptocurrencies'].split(','): # Use split to convert comma separated string to list
            cursor.execute("SELECT JSON_EXTRACT(wallet, '$." + i + ".amount') as amount from userinfo where email=%s",(userid,))
            temp = {}
            temp['name'] = i
            t = cursor.fetchone()
            temp['amount'] = t['amount']                   
            data['wallet'].append(temp) # Append temp directly without curly braces
    return render_template('dashboard.html',data=data)
    
    
    
@app.route('/transaction')
def transaction():
    data = {}
    msg = ''
    if request.method == 'GET':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM P2PTradeData where buyer_email_id=%s or seller_email_id=%s", (session['id'],session['id'],))
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
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT username from userinfo where email_id=%s',(l['seller_email_id'],))
                t = cursor.fetchone()
                data['client'].append((t['username'],l['seller_email_id']))
                data['order_type'].append('buy')
                data['transaction_usdt'].append(l['transaction_usdt'])
                data['price'].append(l['price'])
                data['time_stamp'].append(l['time_stamp'])
            elif (l['seller_email_id'] == session['id']):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT username from userinfo where email_id=%s',(l['buyer_email_id'],))
                t = cursor.fetchone()
                data['client'].append({t['username'],l['buyer_email_id']})
                data['order_type'].append('sell')
                data['transaction_usdt'].append(l['transaction_usdt'])
                data['price'].append(l['price'])
                data['time_stamp'].append(l['time_stamp'])
        if (len(data['order_id']) == 0):
            msg = 'YOU DO NOT HAVE ANY TRANSACTION HISTORY !'
        return render_template('transaction.html',data=data,msg=msg)

# @app.route('/otp-verification/<email>', methods=['GET', 'POST'])
# def otp_verification(email):
#     if request.method == 'POST' and 'otp' in request.form:
#         entered_otp = request.form['otp']
#         if entered_otp == session[email]:
#             cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#             cursor.execute('UPDATE userinfo SET kyc = true WHERE email = % s', (email,))
#             mysql.connection.commit()
#             return redirect(url_for('dashboard', userid=email))
#         else:
#             return render_template('otp_verification.html', email=email, msg='Invalid OTP. Please try again.')
#     elif request.method == 'POST':
#         return render_template('otp_verification.html', email=email, msg='Please enter OTP.')
#     else:
#         otp = generate_otp()
#         session[email] = otp
#         send_otp(email, otp)
#         return render_template('otp_verification.html', email=email)






    # elif request.method == 'POST':
    #     email = userid
    #     crypto_name = request.form['crypto_name']
    #     amount = float(request.form['amount'])  # Convert the amount to a float
    #     # price = float(request.form['price'])  # Convert the price to a float
    #     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #     cursor.execute('SELECT wallet FROM userinfo WHERE email = %s', (email,))
    #     wallet = json.loads(cursor.fetchone()['wallet'])  # Convert the wallet string to a Python dictionary
    #     if crypto_name in wallet:
    #         wallet[crypto_name]['amount'] += amount  # Update the amount of the existing cryptocurrency
    #     # wallet[crypto_name]['price'] = price  # Update the price of the existing cryptocurrency
    #     # wallet[crypto_name]['estimated_balance'] = wallet[crypto_name]['amount'] * price  # Update the estimated balance of the existing cryptocurrency
    #     else:
    #         wallet[crypto_name] = {'amount': amount}  # Add the new cryptocurrency to the wallet dictionary
    #     # wallet[crypto_name] = {'amount': amount, 'price': price, 'estimated_balance': amount * price}  # Add the new cryptocurrency to the wallet dictionary
    #     cursor.execute('UPDATE userinfo SET wallet = %s WHERE email = %s', (json.dumps(wallet), email,))
    #     mysql.connection.commit()
    #     data['success_msg'] = f'{amount} {crypto_name} successfully added to wallet!'
    #     return redirect(url_for('dashboard', userid=userid))

@app.route('/market_allcrypto')
def market():
    json_data = []
# Load market data from JSON file
    with open('market.json') as f: # here I need to enter the path of the file 
        market_data = json.load(f)
# Access contents of the dictionary
    for item in market_data:
        substrings = item['symbol'].split("/")
        crypto = substrings[0]
        item['symbol'] = crypto
        json_data.append(item)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT favourites from userinfo where email_id=',(session['id'],))
    t = cursor.fetchone()
    fav = t['favourites']
    fav = fav.split(",")
    return render_template('market_allcrypto.html',json_data=json_data,data=fav)
    
@app.route('/mark_fav/<string : fav>')
def mark_fav(fav):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    fav = "," + fav
    cursor.execute("UPDATE userinfo SET favourites = CONCAT(favourites, %s) WHERE email =%s",(fav,session['id'],))
    return redirect(url_for('market_allcrypto'))
   
@app.route('/p2p_buy')
def p2p():
    # This is the code for p2p buy 
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM P2PBIDDINGDATA where BUY_TYPE=false')
    list = []
    while(True):
        dic = cursor.fetchone()
        if dic == None:
            break
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT username from userinfo where email_id=%s',(dic['email_id'],))
        t = cursor.fetchone()
        dic['username'] = t['username']
        list.append(dic)
    return render_template('p2p_buy.html',l_req=list)

@app.route('/p2p_sell')
def p2p_sell():
        # This is the code for p2p buy 
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM P2PBIDDINGDATA where BUY_TYPE=true')
    list = []
    while(True):
        dic = cursor.fetchone()
        if dic == None:
            break
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT username from userinfo where email_id=%s',(dic['email_id'],))
        t = cursor.fetchone()
        dic['username'] = t['username']
        list.append(dic)
    return render_template('p2p_sell.html',l_req=list)

@app.route('/change_password',methods = 'POST')
def change_password():
    msg = ''
    if request.method == 'POST' and 'current_password' in request.form and 'newpassword' in request.form and 'newpassword_confirmed' in request.form:
        current_pass = request.form['current_password']
        newpass = request.form['newpassword']
        newpass_confirm = request.form['newpassword_confirmed']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT password from userinfo where email_id=%s',(session['id'],))
        dic1 = cursor.fetchone()
        password_encrypt  =dic1['password']
        if (password_encrypt != encrypt_password(current_pass)):
            msg = 'The entered password does not matches the exisiting password'
        elif (password_encrypt == encrypt_password(current_pass)):
            if (newpass != newpass_confirm):
                msg = 'The new password does not matches the confirm new password !'
            else:
                if is_password_valid(newpass):
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute('UPDATE userinfo SET password =%s WHERE email =%s',(newpass,session['id'],))
                    msg = 'PASSWORD UPDATED SUCCESSFULLY'
                else:
                    msg = 'Please enter a valid password (should contain alphabets and digits from 0-9)'                 
    elif request.method == 'POST':
        msg = 'Please fill in all the blanks provided'
    return render_template('change_password.html',msg)
    
@app.route('/market_fav')
def market_fav():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT favourites from userinfo where email_id=%s', (session['id'],))
    dic = cursor.fetchone()
    fav = dic['favourites'].split(",")
    with open('market.json') as f: # here I need to enter the path of the file 
        market_data = json.load(f) 
    fav_details = [] 
    for item in market_data:
        substrings = item['symbol'].split("/")
        crypto = substrings[0]
        item['symbol'] = crypto
        if item['symbol'] in fav:
            fav_details.append(item)
    return render_template('market_fav.html',fav=fav,fav_details=fav_details)
    # elif request.method == 'POST':
    #     new_fav = request.form.get('new_fav')
    #     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #     cursor.execute('UPDATE userinfo SET favourites = CONCAT(favourites, %s) WHERE email = %s', (new_fav, userid,))
    #     mysql.connection.commit()
    #     return redirect(url_for('market_fav', userid=userid))

@app.route('/user_profile')
def user_profile():
    data = {}
    
    data['userid'] = session['id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM userinfo where email_id=%s", (session['id'],))
    details = cursor.fetchone()
    data['username'] = details['username']
    data['profile_pic'] = details['profile_pic']
    data['kyc'] = details['kyc']
    data['contact_number'] = details['contact_number']
    return render_template('user_profile.html', data=data)
    
# @app.route('/change_pic')
# def change_pic():
    
#     file = request.files['profile_pic'] # Get the uploaded file from the request
#     filename = secure_filename(file.filename) # Sanitize the filename
#     if filename:
#         # Save the file to the server
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             # Update the user's profile picture in the database
#         cursor = mysql.connection.cursor()
#         cursor.execute("UPDATE userinfo SET profile_pic = %s WHERE email_id = %s", (filename, userid))
#         mysql.connection.commit()
#             # Update the data dictionary with the new profile picture
#         data['profile_pic'] = filename
#     return redirect(url_for('user_profile'))
    # elif request.method == 'POST':
    #     username = request.form.get('username')
    #     contact_number = request.form.get('phone_number')
    #     if not username and not contact_number:
    #         return redirect(url_for('user_profile', userid=userid))
    #     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #     if username:
    #         cursor.execute('UPDATE userinfo SET username = %s WHERE email_id = %s', (username, userid))
    #     if contact_number:
    #         cursor.execute('UPDATE userinfo SET contact_number = %s WHERE email_id = %s', (contact_number, userid))
    #     mysql.connection.commit()
    #     return redirect(url_for('user_profile', userid=userid))


    # elif request.method == 'POST':
    # elif request.method == 'POST':
    #     # Get the data from the request form
    #     buyer_email = request.form['buyer_email']
    #     seller_email = request.form['seller_email']
    #     transaction_usdt = request.form['transaction_usdt']
    #     price = request.form['price']
    #     timestamp = datetime.now()
        
    #     # Insert the data into the database
    #     cursor = mysql.connection.cursor()
    #     cursor.execute("INSERT INTO P2PTradeData (buyer_email_id, seller_email_id, transaction_usdt, price, time_stamp) VALUES (%s, %s, %s, %s, %s)", (buyer_email, seller_email, transaction_usdt, price, timestamp))
    #     mysql.connection.commit()
        
    #     # Display a success message
    #     flash('Transaction added successfully!')
        
    #     # Redirect to the transaction page
    #     return redirect(url_for('transaction', userid=userid))

@app.route('/order_history')
def order_history():
    history = []
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * from %s',(session['username'],))
    while(True):
        data = cursor.fetchone()
        if (data == None):
            break        
        history.append(data)
    if (len(history) == 0):
        msg = 'You do not have any orders till now, Enter the market to place your orders !'
    return render_template('order_history.html',history=history,message=msg)
    # if request.method = 'POST':
    #     crypto_name = request.form['crypto_name']
    #     crypto_price = request.form['crypto_price']
    #     order_type = request.form['order_type']
    #     crypto_amount = request.form['crypto_amount']
    #     timestamp = request.form['timestamp']
    #     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #     cursor = mysql.connection.cursor()
    #     cursor.execute('INSERT INTO %s (crypto_name, crypto_price, order_type, crypto_amount, timestamp) VALUES (%s, %s, %s, %s, %s)', (username, crypto_name, crypto_price, order_type, crypto_amount, timestamp))
    #     mysql.connection.commit()
    #     flash('Order placed successfully!', 'success')
    #     return redirect(url_for('get_order_history', username=username))
    
@app.route('/exchange_btc/<string : crypto>')
def exchange_btc_1m(crypto):
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
    # fig.savefig('candlestick_plot.png')

    # plt.show()
    return render_template('exchange_btc.html',image_path=image_path,crypto_details=crypto_details)


# @app.route('/chat')
# def chat():
#     return
# @app.route('/dropdown')
# def dropdown():
#     return render_template('dropdown.html')



if(__name__=="__main__"):
    app.run(debug=True)