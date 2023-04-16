from flask import Flask , render_template , request , redirect , url_for , session
# from flask_sqlalchemy import SQLAlchemy
# from flask_mysqldb import MySQL 
import mysql.connector
# import MySQLdb.cursors
# import hashlib
import encryption_scheme
import dashboard
import market
import transaction
# import mysql.connector
# import pandas as pd
# import matplotliblib.pyplot as plt
import re 
# import secrets

# secret_key = secrets.token_hex(16)

app=Flask(__name__, static_folder='static')
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
# app.secret_key= str(secret_key)

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'Teamwork123'
# app.config['MYSQL_DB'] = 'Coinfun_database'

# sql=MySQL(app)

# cursor = sql.connection.cursor(MySQLdb.cursors.DictCursor)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Teamwork123",
    database="Coinfun_database"
)
cursor = db.cursor()

# def is_password_valid(password):
#     if len(password) < 8 or len(password)>25:
#         return False
#     if password.isalpha():  # isalpha returns true if all characters are alphabetic
#         return False
#     if password.isnumeric(): # isnumeric returns true if all characters are numeric
#         return False
#     return True
# def replace_special_characters(s):    # Replace special characters in inputword with underscore
#     return re.sub(r'\W+', '_', s)

# def polynomial_hashing(password):
#     prime_factor = 31
#     hash_value = 0
#     temp = 1
#     mod = (10**9) + 7   # A large prime number
#     try:
#         for i in range(len(password)):
#             hash_value += ord(password[i])*temp
#             temp = temp*prime_factor
#         return str(hash_value % mod)
#     except:
#         return str(password) + str(101)     # in case of unforseen error

# def encrypt_password(password):
    
#     mysecretkey = 'abcdefghijklmnopqrstuvwxyz' # Fixed key for encryption
#     encrypted = ''
#     for char in password:
#         encrypted += chr(ord(char) ^ ord(mysecretkey))  # Making a encryption by taking xor of corresponding 
#                                                         # characters in mysecretkey     
#     # returning the concatenation of encrypted password and the polynomial hash of encrypted password
#     return encrypted + polynomial_hashing(encrypted)
    

@app.route('/')
def first():
	return render_template('login.html', msg = '')

@app.route('/login', methods =['GET'])
def login():
	message = ''
	if request.method == 'GET' and 'email' in request.form and 'password' in request.form:
		email = request.form['email']
		password = request.form['password']
		
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
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form and 'confirm-password' in request.form and 'phone-number' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        confirm_password=request.form['confirm-password']
        phone_number = request.form['phone-number']
        # profile_pic = request.files['profile_pic']
        # if profile_pic and allowed_file(profile_pic.filename):
        #     filename = secure_filename(profile_pic.filename)
        #     profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #     pic = url_for('static', filename='uploads/' + filename)
        # else:
        pic = ''
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM userinfo WHERE email_id = % s', (email,))
        user = cursor.fetchone()
        if (user != None):
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
            cursor.execute('INSERT INTO userinfo VALUES ( % s, % s, % s, "{"ADA": 0.0, "BNB": 0.0, "BTC": 0.0, "ETH": 0.0, "SOL":  0.0, "XRP": 0.0, "DOGE": 0.0, "USDT": 0.0, "MATIC": 0.0, "USDT_in_bid": 0.0}", "[]", % s, false)', (email,username, encrypt_password(password),pic, ))
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
    # cursor = mysql.connection.cursor(dictionary=True) # Use dictionary cursor
    # cursor.execute('SELECT username from userinfo where email_id = %s',(userid,))
    # dic1 = cursor.fetchone()
    # if dic1: # Check if user exists
    data=getdata(session['id'])
    data['username'] = session['username']
    return render_template('dashboard.html',data=data)
    
@app.route('/transaction')
def transaction():
    (data,msg) = transaction_data(session['id'])
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
    json_data=get_market_data()
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    data = get_fav_list(session['id'])
    return render_template('market_allcrypto.html',jsondata=json_data,data=fav)
    
@app.route('/mark_fav/<string:fav>')
def mark_fav(fav):
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    fav = "," + fav
    cursor.execute("UPDATE userinfo SET favourites = CONCAT(favourites, %s) WHERE email_id =%s",(fav,session['id'],))
    return redirect(url_for('market_allcrypto'))

@app.route('/p2p_buy',methods = ["GET"])
def p2p():
    # This is the code for p2p buy 
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == "GET":
        list = p2p_buy_data_get()
        return render_template('p2p_buy.html',data=list)
    
@app.route('/p2p_change_usdt/<float:balance>',methods = ['POST'])  
def p2p_change_usdt(balance):
    if requestmethod == 'POST':
        cursor.execute("SELECT JSON_EXTRACT(wallet, '$.USDT') FROM userinfo WHERE emailid=%s",(session['id'],))
        curr_amount = float(cursor.fetchone())
        curr_amount+=balance
        cursor.execute(f"UPDATE userinfo SET wallet = JSON_SET(wallet, '$.USDT', {curr_amount}) WHERE emailid={session['id']}")
        return redirect(url_for('p2p_buy'))

@app.route('/p2p_sell')
def p2p_sell():
        # This is the code for p2p buy 
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM P2PBIDDINGDATA where BUY_TYPE=true')
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
    return render_template('p2p_sell.html',l_req=list)

@app.route('/p2p_change_usdt/<float:balance>',methods = ['POST'])  
def p2p_change_usdt(balance):
    if requestmethod == 'POST':
        cursor.execute("SELECT JSON_EXTRACT(wallet, '$.USDT') FROM userinfo WHERE emailid=%s",(session['id'],))
        curr_amount = float(cursor.fetchone())
        curr_amount-=balance
        cursor.execute(f"UPDATE userinfo SET wallet = JSON_SET(wallet, '$.USDT', {curr_amount}) WHERE emailid={session['id']}")
        return redirect(url_for('p2p_sell'))
    
@app.route('/change_password',methods = ['POST'])
def change_password():
    msg = ''
    if request.method == 'POST' and 'current_password' in request.form and 'newpassword' in request.form and 'newpassword_confirmed' in request.form:
        current_pass = request.form['current_password']
        newpass = request.form['newpassword']
        newpass_confirm = request.form['newpassword_confirmed']
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
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
                    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute('UPDATE userinfo SET password =%s WHERE email_id =%s',(newpass,session['id'],))
                    msg = 'PASSWORD UPDATED SUCCESSFULLY'
                else:
                    msg = 'Please enter a valid password (should contain alphabets and digits from 0-9)'                 
    elif request.method == 'POST':
        msg = 'Please fill in all the blanks provided'
    return render_template('changepassword.html',msg)
    
@app.route('/market_fav')
def market_fav():
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT favourites from userinfo where email_id=%s', (session['id'],))
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
    return render_template('market_fav.html',jsondata=fav_details)


@app.route('/user_profile')
def user_profile():
    data = {}
    
    data['userid'] = session['id']
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
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



@app.route('/order_history')
def order_history():
    history = []
    msg = ''
    name = session['username']
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * from %s',(name,))
    while(True):
        data = cursor.fetchone()
        if (data == None):
            break        
        history.append(data)
    if (len(history) == 0):
        msg = 'You do not have any orders till now, Enter the market to place your orders !'
    return render_template('order_history.html',history=history,message=msg)
    
@app.route('/exchange_btc/<string:crypto>')
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
@app.route('/change_wallet/<string:order_type>/<string:crypto>/<float:qty>')
def change_wallet(order_type, crypto, qty):
    if order_type == "buy":
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT wallet from userinfo where email_id=%s', (session['id'],))
        t = cursor.fetchone()
        wallet = t['wallet']
        wallet = wallet[1:len(wallet) - 1]
        wallet = wallet.split(",")
        for i in range(len(wallet)):
            temp = wallet[i].split(":")
            if temp[0].replace("\"","") == crypto:
                amount = float(temp[1])
                amount += qty
                amount = str(amount)
                temp[1] = amount
                wallet[i] = ':'.join(temp)
                break
        wallet = ','.join(wallet)
        wallet = "{" + wallet + "}"
        cursor.execute('UPDATE userinfo SET wallet=%s where email_id=%s', (wallet, session['id'],))
    elif order_type == "sell":
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT wallet from userinfo where email_id=%s', (session['id'],))
        t = cursor.fetchone()
        wallet = t['wallet']
        wallet = wallet[1:len(wallet) - 1]
        wallet = wallet.split(",")
        for i in range(len(wallet)):
            temp = wallet[i].split(":")
            if temp[0].replace("\"","") == crypto:
                amount = float(temp[1])
                amount -= qty
                amount = str(amount)
                temp[1] = amount
                wallet[i] = ':'.join(temp)
                break
        wallet = ','.join(wallet)
        wallet = "{" + wallet + "}"
        cursor.execute('UPDATE userinfo SET wallet=%s where email_id=%s', (wallet, session['id'],))
    return redirect(url_for('exchange_btc_1m'))
     

@app.route('/chat/<string:seller_mailID>',methods = ['GET','POST'])
def chat_buy(seller_mailID):
    if request.method == 'POST' and 'messageInput' in request.form:
        message = request.form["messageInput"]
        data = {}
        data["sender"] = message
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT chat_messages FROM chat WHERE (email_id1 = %s AND email_id2 = %s) OR (email_id1 = %s AND email_id2 = %s)',(session['id'],seller_mailID,seller_mailID,session['id'],))
        t = cursor.fetchone()
        chat_str = t["chat_messages"]
        if chat_str == "{}":
            chat_str = "[" + json.dumps(data) + "]"
        else:
            chat_str = chat_str[0:-1] + "," + json.dumps(data) + "]"
        cursor.execute("UPDATE chat SET chat_messages = %s WHERE (email_id1 = %s AND email_id2 = %s) OR (email_id1 = %s AND email_id2 = %s)", (chat_str, session['id'],seller_mailID,seller_mailID,session['id'],))
        return redirect(url_for('chat_buy'))
    elif request.method == "POST":
        return None
    else:
        msg = ''
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT chat_messages FROM chat WHERE (email_id1 = %s AND email_id2 = %s) OR (email_id1 = %s AND email_id2 = %s)',(session['id'],seller_mailID,seller_mailID,session['id'],))
        t = cursor.fetchone()
        chat = t['chat_messages']
        chat = chat[1:-1]
        chat = chat.split("},")
        data = {}
        data[session['id']] = []
        data[seller_mailID] = []
        chat = []
        for item in chat:
            if item[0] == "{":
                item = item[1:len(item)]
            if item[-1] == "}":
                item = item[0:-1]
            item = item.split(",")
            dict = {}  
            element = item[0].split(":")
            message = item[1].split(":")
            message = message[1][1:-1]
            sender = element[1][1:-1]
            if sender == seller_mailID:
                data[seller_mailID].append(message)
            elif sender == session['id']:
                data[session['id']].append(message)
        if len(data[seller_mailID]) == 0 and len(data[session['id']]) == 0:
            msg = 'No messages'
        return render_template('chat_buy.html',data=data,msg=msg)
        
 
    
# @app.route('/dropdown')
# def dropdown():
#     return render_template('dropdown.html')



if(__name__=="__main__"):
    app.run(debug=True)