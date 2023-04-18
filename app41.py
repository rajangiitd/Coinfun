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
import read_n_write_image_with_sql
import image 
import otp
# import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import chat 
import json
from datetime import datetime, timedelta
import re 
import os
import base64

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
		
		cursor.execute('SELECT * FROM userinfo WHERE email_id = % s AND password = % s', (email, encryption_scheme.encrypt_password(password), ))
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
        elif encryption_scheme.is_password_valid(password) == False:
            msg = 'Password must contains letters and numbers both'
        else:
            cursor.execute('INSERT INTO userinfo VALUES ( % s, % s, % s, "{"ADA": 0.0, "BNB": 0.0, "BTC": 0.0, "ETH": 0.0, "SOL":  0.0, "XRP": 0.0, "DOGE": 0.0, "USDT": 0.0, "MATIC": 0.0, "USDT_in_bid": 0.0}", "[]", % s, false)', (email,username, encryption_scheme.encrypt_password(password),pic, ))
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
    data= dashboard.get_wallet_data(session['id'])
    data['username'] = session['username']
    return render_template('dashboard.html',data=data)
    
@app.route('/transaction')
def transaction():
    (data,msg) = transaction.transaction_data(session['id'])
    return render_template('transaction.html',data=data,msg=msg)

@app.route('/otp-verification', methods=['GET', 'POST'])
def otp_verification():
    if request.method == 'POST' and 'otp' in request.form:
        entered_otp = request.form['otp']
        if entered_otp == session['otp']:
            # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE userinfo SET kyc = true WHERE email = % s', (session['id'],))
            mysql.connection.commit()
            return redirect(url_for('dashboard'))
        else:
            return render_template('otp_verification.html', msg='Invalid OTP. Please try again.')
    elif request.method == 'POST':
        return render_template('otp_verification.html', msg='Please enter OTP.')
    else:
        msg = 'OTP sent successfully to your registered email ID'
        session['otp'] = otp.send_otp(session['id'])
        if (type(session['otp']) != int):
            msg = session['otp']
        return render_template('otp_verification.html',msg=msg)

@app.route('/market_allcrypto')
def market():
    json_data=market.get_market_data()
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    data = market.get_fav_list(session['id'])
    return render_template('market_allcrypto.html',jsondata=json_data,data=data)
    
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
        list = market.p2p_buy_data_get()
        return render_template('p2p_buy.html',data=list)
    
@app.route('/p2p_change_usdt/<float:balance>',methods = ['POST'])  
def p2p_change_usdt(balance):
    if request.method == 'POST':
        cursor.execute("SELECT JSON_EXTRACT(wallet, '$.USDT') FROM userinfo WHERE emailid=%s",(session['id'],))
        curr_amount = float(cursor.fetchone())
        curr_amount+=balance
        cursor.execute(f"UPDATE userinfo SET wallet = JSON_SET(wallet, '$.USDT', {curr_amount}) WHERE emailid={session['id']}")
        return redirect(url_for('p2p_buy'))

@app.route('/p2p_sell')
def p2p_sell():
        # This is the code for p2p buy 
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    list=market.p2p_sell_data_get()
    return render_template('p2p_sell.html',l_req=list)

@app.route('/p2p_change_usdt/<float:balance>',methods = ['POST'])  
def p2p_change_usdt(balance):
    if request.method == 'POST':
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
        msg =  userprofile.change_pass_help()
    elif request.method == 'POST':
        msg = 'Please fill in all the blanks provided'
    return render_template('changepassword.html',msg)
    
@app.route('/market_fav')
def market_fav():
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    fav_details = market.fetch_fav(session['id'])
    return render_template('market_fav.html',jsondata=fav_details)


@app.route('/user_profile')
def user_profile():
    data  = userprofile.get_user_profile(session['id'])
    return render_template('user_profile.html', data=data)
    
@app.route('/upload_pic',methods = ['GET','POST'])
def upload_pic():
    if request.method == "POST":
        msg = ''
        try:
            if 'photo' in request.files:
                photo = request.files['photo']
                if photo.filename != '':
                    # Check if the file has an allowed image extension
                    if image.allowed_file(photo.filename):
                        # Read the binary data from the file
                        data = photo.read()
                # Encode the binary data as base64
                        encoded_data = base64.b64encode(data)
            cursor.execute('INSERT INTO userinfo (profile_pic) values (%s) where email_id=%s',(encoded_data,session['id']))
            db.commit()
            msg = 'IMAGE UPDATED SUCCESSFULLY!'
        except:
            msg = 'IMAGE CANNOT BE UPDATED!'
        return render_template('profile_pic.html',msg)
    else:
        cursor.execute('SELECT profile_pic from userinfo where email_id=%s',(session['id']))
        image = cursor.fetchone()['profile_pic']
        image = base64.b64decode(image)
        return render_template('profile_pic.html',image=image)
        
        
@app.route('/order_history')
def order_history():
    (history,msg) = market.get_order_history(session['username'])
    return render_template('order_history.html',history=history,message=msg)
    
@app.route('/exchange_btc/<string:crypto>')
def exchange_btc_1m(crypto):
    (image_path,crypto_details) = market.form_graph(crypto)
    return render_template('exchange_btc.html',image_path=image_path,crypto_details=crypto_details)

@app.route('/change_wallet/<string:order_type>/<string:crypto>/<float:qty>')
def change_wallet(order_type, crypto, qty):
    change_wallet(session['id'],order_type,crypto,qty)
    return redirect(url_for('exchange_btc_1m'))

@app.route('/chat_buy/<string:seller_mailID>/<string:image_path>',methods = ['GET','POST'])
def chat_buy(seller_mailID,image_path):
    if request.method == 'POST' and 'messageInput' in request.form:
        message = request.form["messageInput"]
        chat.update_chat_txt(session['id'],seller_mailID,message)
        return redirect(url_for('chat_buy'))
    elif request.method == "POST" and 'photo' in request.files:
        photo = request.files['photo']
        chat.update_chat_image(session['id'],seller_mailID,photo)
        return redirect(url_for('chat_buy'))
    else:
        msg = ''
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT chat_messages FROM chat WHERE (email_id1 = %s AND email_id2 = %s) OR (email_id1 = %s AND email_id2 = %s)',(session['id'],seller_mailID,seller_mailID,session['id'],))
        t = cursor.fetchone()['chat_messages']
        data = json.loads(t)
        if len(data[seller_mailID]) == 0 and len(data[session['id']]) == 0:
            msg = 'No messages'
        return render_template('chat_buy.html',data=data,msg=msg)

@app.route('/chat_sell/<string:buyer_mailID/string:image_path>',methods = ['GET','POST'])
def chat_sell(buyer_mailID,image_path):
    if request.method == 'POST' and 'messageInput' in request.form:
        message = request.form["messageInput"]
        chat.update_chat_txt(session['id'],buyer_mailID,message)
        return redirect(url_for('chat_sell'))
    elif request.method == "POST" and 'photo' in request.files:
        # message = request.form["messageInput"]
        photo = request.files['photo']
        chat.update_chat_image(session['id'],buyer_mailID,photo)
        return redirect(url_for('chat_sell'))
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