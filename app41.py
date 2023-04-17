from flask import Flask , render_template , request , redirect , url_for , session, send_file
# from flask_sqlalchemy import SQLAlchemy
# from flask_mysqldb import MySQL 
import mysql.connector
# import MySQLdb.cursors
# import hashlib
import encryption_scheme
import dashboard
import market
import transaction
import order_and_wallet
import userprofile
import validate_fake_data
# import mysql.connector
import pandas as pd
import matplotliblib.pyplot as plt
import json
from datetime import datetime, timedelta
import re 

app=Flask(__name__, static_folder='static')

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Teamwork123",
    database="Coinfun_database"
)
cursor = db.cursor()

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
        profile_pic = request.files['profile_pic']
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

@app.route('/otp-verification', methods=['GET', 'POST'])
def otp_verification():
    if request.method == 'POST' and 'otp' in request.form:
        entered_otp = request.form['otp']
        if entered_otp == session['otp']:
            # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE userinfo SET kyc = true WHERE email = % s', (email,))
            mysql.connection.commit()
            return redirect(url_for('dashboard'))
        else:
            return render_template('otp_verification.html', email=email, msg='Invalid OTP. Please try again.')
    elif request.method == 'POST':
        return render_template('otp_verification.html', email=email, msg='Please enter OTP.')
    else:
        msg = 'OTP sent successfully to your registered email ID'
        session['otp'] = send_otp(session['id'])
        if (type(session['otp']) != int):
            msg = session['otp']
        return render_template('otp_verification.html',msg=msg)

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
    list=p2p_sell_data_get()
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
    # msg = ''
    if request.method == 'POST' and 'current_password' in request.form and 'newpassword' in request.form and 'newpassword_confirmed' in request.form:
        current_pass = request.form['current_password']
        newpass = request.form['newpassword']
        newpass_confirm = request.form['newpassword_confirmed']
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        msg =  change_pass_help()
    elif request.method == 'POST':
        msg = 'Please fill in all the blanks provided'
    return render_template('changepassword.html',msg)
    
@app.route('/market_fav')
def market_fav():
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    fav_details = fetch_fav(session['id'])
    return render_template('market_fav.html',jsondata=fav_details)


@app.route('/user_profile')
def user_profile():
    data  = get_user_profile(session['id'])
    return render_template('user_profile.html', data=data)
    
@app.route('/change_pic',methods = ['GET','POST'])
def change_pic():
    if request.method == "POST":
        msg = ''
        try:
            image_data = request.json.get('image_data')
            image = io.BytesIO(base64.b64decode(image_data))
            cursor.execute('INSERT INTO userinfo (profile_pic) values (%s) where email_id=%s',(image,session['id']))
            db.commit()
            msg = 'IMAGE UPDATED SUCCESSFULLY!'
        except:
            msg = 'IMAGE CANNOT BE UPDATED!'
        return render_template('profile_pic.html',msg)
    else:
        cursor.execute('SELECT profile_pic from userinfo where email_id=%s',(session['id']))
        image = cursor.fetchone()['profile_pic']
        return render_template('profile_pic.html',image=image)
        
        
@app.route('/order_history')
def order_history():
    (history,msg) = get_order_history(session['username'])
    return render_template('order_history.html',history=history,message=msg)
    
@app.route('/exchange_btc/<string:crypto>')
def exchange_btc_1m(crypto):
    (image_path,crypto_details) = form_graph(crypto)
    return render_template('exchange_btc.html',image_path=image_path,crypto_details=crypto_details)

@app.route('/change_wallet/<string:order_type>/<string:crypto>/<float:qty>')
def change_wallet(order_type, crypto, qty):
    change_wallet(session['id'],order_type,crypto,qty)
    return redirect(url_for('exchange_btc_1m'))

@app.route('/chat/<string:seller_mailID>',methods = ['GET','POST'])
def chat_buy(seller_mailID):
    if request.method == 'POST' and 'messageInput' in request.form:
        message = request.form["messageInput"]
        cursor.execute('SELECT chat_messages FROM chat WHERE (email_id1 = %s AND email_id2 = %s) OR (email_id1 = %s AND email_id2 = %s)',(session['id'],seller_mailID,seller_mailID,session['id'],))
        t = cursor.fetchone()['chat_messages']
        l = json.loads(t)
        
        data = {}
        data["sender"] = session['id']
        data["message"] = message
        if request.json.get('image_data'):
            image_data = request.json.get('image_data')
            image = io.BytesIO(base64.b64decode(image_data))
            
            data['image'] = json.loads("{'name':Null,'type':Null,'data':NULL}")
            data['image']['data'] = image
        else:
            data['image'] = json.loads('NULL')
        t.append(data)
        messages = json.dumps(t)
        cursor.execute("UPDATE chat SET chat_messages = %s WHERE (email_id1 = %s AND email_id2 = %s) OR (email_id1 = %s AND email_id2 = %s)", (t, session['id'],seller_mailID,seller_mailID,session['id'],))
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        return redirect(url_for('chat_buy'))
    elif request.method == "POST":
        return None
    else:
        msg = ''
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT chat_messages FROM chat WHERE (email_id1 = %s AND email_id2 = %s) OR (email_id1 = %s AND email_id2 = %s)',(session['id'],seller_mailID,seller_mailID,session['id'],))
        t = cursor.fetchone()['chat_messages']
        data = json.loads(t)
        if len(data[seller_mailID]) == 0 and len(data[session['id']]) == 0:
            msg = 'No messages'
        return render_template('chat_buy.html',data=data,msg=msg)

@app.route('/chat/<string:buyer_mailID>',methods = ['GET','POST'])
def chat_buy(buyer_mailID):
    if request.method == 'POST' and 'messageInput' in request.form:
        message = request.form["messageInput"]
        cursor.execute('SELECT chat_messages FROM chat WHERE (email_id1 = %s AND email_id2 = %s) OR (email_id1 = %s AND email_id2 = %s)',(session['id'],buyer_mailID,buyer_mailID,session['id'],))
        t = cursor.fetchone()['chat_messages']
        l = json.loads(t)
        
        data = {}
        data["sender"] = session['id']
        data["message"] = message
        if request.json.get('image_data'):
            image_data = request.json.get('image_data')
            image = io.BytesIO(base64.b64decode(image_data))
            
            data['image'] = json.loads("{'name':Null,'type':Null,'data':NULL}")
            data['image']['data'] = image
        else:
            data['image'] = json.loads('NULL')
        t.append(data)
        messages = json.dumps(t)
        cursor.execute("UPDATE chat SET chat_messages = %s WHERE (email_id1 = %s AND email_id2 = %s) OR (email_id1 = %s AND email_id2 = %s)", (t, session['id'],buyer_mailID,buyer_mailID,session['id'],))
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        return redirect(url_for('sell'))
    elif request.method == "POST":
        return None
    else:
        msg = ''
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT chat_messages FROM chat WHERE (email_id1 = %s AND email_id2 = %s) OR (email_id1 = %s AND email_id2 = %s)',(session['id'],buyer_mailID,buyer_mailID,session['id'],))
        t = cursor.fetchone()['chat_messages']
        data = json.loads(t)
        if len(data[buyer_mailID]) == 0 and len(data[session['id']]) == 0:
            msg = 'No messages'
        return render_template('chat_sell.html',data=data,msg=msg)
 
    
# @app.route('/dropdown')
# def dropdown():
#     return render_template('dropdown.html')



if(__name__=="__main__"):
    app.run(debug=True)