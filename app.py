from flask import Flask , render_template , request , redirect , url_for , session, send_file, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_mysqldb import MySQL 
import mysql.connector
# import MySQLdb.cursors
# import hashlib
from backend.utils.encryption_scheme import is_password_valid, encrypt_password
from backend.utils.dashboard import get_wallet_data
from backend.utils.marketandp2p import get_market_data, get_fav_crypto_list, get_fav_page_data, get_p2p_buy_page_data, get_p2p_sell_page_data, form_graph
from backend.utils.order_and_wallet import add_order, get_order_history, change_wallet
from backend.utils.userprofile import get_user_profile, change_pass_help
from backend.utils.transaction_history import get_transaction_history_data
# import backend.utils.validate_fake_data
# import read_n_write_image_with_sql
from backend.utils.image import is_allowed_file, convert_to_writable
from backend.utils.otp import is_valid_domain, send_otp
# import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from backend.utils.chat import update_chat_image, update_chat_txt
import json
from datetime import datetime, timedelta
import re 
import os
import base64
import io
from PIL import Image
from time import sleep

# app=Flask(__name__, static_folder='/frontend/static',template_folder='/frontend/templates')

app = Flask(__name__, static_folder=os.path.join(os.getcwd(), 'frontend', 'static'), template_folder=os.path.join(os.getcwd(), 'frontend', 'templates'))

app.secret_key = 'Teamwork123'


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Teamwork123",
    database="Coinfun_database",
    autocommit=True
)

@app.route('/')
def first():
	return render_template('login.html', msg = '')

@app.route('/login', methods =['POST'])
def login():
    cursor = db.cursor()
    try:
        message = ''
        if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']	
            cursor.execute('SELECT * FROM userinfo WHERE email_id = %s AND password = %s', (email,encrypt_password(password),))
            account = cursor.fetchone()
            if account != None:
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = account[1]
                message = 'Logged in successfully !'
                cursor.close()
                return redirect(url_for('dashboard',userid=session['id']))
            else:
                message = 'Incorrect username / password !'
    except Exception as e:
        message = str(e)
    cursor.close()
    return render_template('login.html', msg = message)


@app.route('/register', methods=['POST','GET'])
def register():
    cursor = db.cursor()
    try:
        msg = ''
        if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form and 'confirm-password' in request.form and 'phone-number' in request.form:
            username = request.form['username']
            password = request.form['password']
            email_id = request.form['email']
            confirm_password=request.form['confirm-password']
            phone_number = request.form['phone-number']
            # profile_pic = request.files['profile_pic']
            # if profile_pic and allowed_file(profile_pic.filename):
            #     filename = secure_filename(profile_pic.filename)
            #     profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #     pic = url_for('static', filename='uploads/' + filename)
            # else:
            #script_directory = os.path.dirname(os.path.abspath(__file__))
            # Define the path to the data directory relative to the script directory
            #data_directory = os.path.join(script_directory, 'backend','utils','data')
            #file_path = data_directory + '/' + 'blank.jpg'
            #pic = convert_to_writable(file_path)
            pic = ""
            # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM userinfo WHERE email_id = %s', (email_id,))
            user = cursor.fetchone()
            if (user != None):
                msg = 'Account already exists !'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email_id):
                msg = 'Invalid email address !'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers !'
            elif password!=confirm_password:
                raise Exception("Your password does not matches the confirm password !")
            elif is_password_valid(password) == False:
                raise Exception("Please enter a valid password, it should contain atleast 1 capital and 1 small alphabets and atleast 1 digit with length between 8-25")
            else:
                # prepare the SQL query
                sql = "INSERT INTO userinfo (email_id, username, password, wallet, favourites, profile_pic, kyc, contact) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                values = (email_id, username, encrypt_password(password), '{"ADA": 0.0, "BNB": 0.0, "BTC": 0.0, "ETH": 0.0, "SOL":  0.0, "XRP": 0.0, "DOGE": 0.0, "USDT": 0.0, "MATIC": 0.0, "USDT_in_bid": 0.0}', "", "" , False, phone_number)
                cursor.execute(sql, values)
                db.commit()
                #cursor.execute('INSERT INTO userinfo VALUES ( %s, %s, %s, "{"ADA": 0.0, "BNB": 0.0, "BTC": 0.0, "ETH": 0.0, "SOL":  0.0, "XRP": 0.0, "DOGE": 0.0, "USDT": 0.0, "MATIC": 0.0, "USDT_in_bid": 0.0}", "", % s, false,%s)', (email,username, encrypt_password(password),pic,phone_number, ))
                # mysql.connection.commit()

                cursor.execute('SELECT email_id, username FROM userinfo WHERE email_id = %s', (email_id,))
                result = cursor.fetchone()
                user_id = result[0]
                username = result[1]
                # Set session variables
                session['loggedin'] = True
                session['id'] = user_id
                session['username'] = username
                msg = 'You have successfully registered !'
                cursor.close()
                return redirect(url_for('dashboard'))
        elif request.method == 'POST':
            msg = 'Please fill all the blank columns !'
    except Exception as e:
        msg = str(e)
    cursor.close()
    return render_template('register.html', msg = msg)



@app.route('/dashboard')
def dashboard():
    # cursor = mysql.connection.cursor(dictionary=True) # Use dictionary cursor
    # cursor.execute('SELECT username from userinfo where email_id = %s',(userid,))
    # dic1 = cursor.fetchone()
    # if dic1: # Check if user exists
    msg = ''
    data = []
    cursor = db.cursor()
    try:
        data= get_wallet_data(session['id'])
        temp = {}
        temp['username'] = session['username']
        data.append(temp)
    except Exception as e:
        msg = str(e)
    cursor.close()
    return render_template('dashboard.html',data=data,msg=msg)
    
@app.route('/transaction')
def transaction():
    cursor = db.cursor()
    data = []
    msg = ''
    try:
        data = get_transaction_history_data(session['id'])
    except Exception as e:
        msg = str(e)
    cursor.close()
    return render_template('transaction.html',data=data,msg=msg)

@app.route('/otp-verification', methods=['GET', 'POST'])
def otp_verification():
    cursor = db.cursor()
    if request.method == 'POST' and 'otp' in request.form:
        entered_otp = request.form['otp']
        if entered_otp == session['otp']:
            # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # cursor.execute('UPDATE userinfo SET kyc = true WHERE email_id = % s', (session['id'],))
            # mysql.connection.commit()
            cursor.close()
            return redirect(url_for('reset_password'))
        else:
            cursor.close()
            return render_template('otp_verification.html', msg='Invalid OTP. Please try again.')
    elif request.method == 'POST':
        cursor.close()
        return render_template('otp_verification.html', msg='Please enter OTP.')
    else:
        msg = ''
        try:
            msg = 'OTP sent successfully to your registered email ID'
            session['otp'] = send_otp(session['id'])
        except Exception as e:
            msg = str(e)
        cursor.close()
        return render_template('otp_verification.html',msg=msg)

@app.route('/enter_email', methods=['GET', 'POST'])
def enter_email():
    cursor = db.cursor()
    msg = ''
    try:
        if request.method == 'POST' and 'email' in request.form:
            email = request.form['email']
            cursor.execute('SELECT * FROM userinfo WHERE email_id = %s', (email,))
            user = cursor.fetchone()
            if (user == None):
                msg = 'Account does not exists !'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address !'
            else:
                msg = 'OTP sent successfully to your registered email ID'
                session['id'] = email
                cursor.close()
                return render_template('forgotpasswordotp.html',msg=msg)
        else:
            msg = 'Please enter the email !'
        
    except Exception as e:
        msg = str(e)
    cursor.close()
    return render_template('forgotdpasswordemailreset.html', msg = msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    msg = ''
    cursor = db.cursor()
    try:
        if request.method == 'POST' and 'new_password' in request.form and 'confirm_new_password' in request.form:
            newpass = request.form['new_password']
            newpass_confirm = request.form['confirm_new_password']
            if (newpass != newpass_confirm):
                msg = 'New Password does not matches the Confirm Password !' 
            else:
                cursor.execute('UPDATE userinfo SET password = %s where email_id = %s',(encrypt_password(newpass),session['id'],))
                db.commit()
                msg = 'Password updated successfully !'
                cursor.close()
                return redirect(url_for("first"))
        elif request.method == 'POST':
            msg = 'Please fill all the blank columns !'
    except Exception as e:
        msg = str(e)
    cursor.close()
    return render_template('forgotpasswordresetsuccessful.html',msg=msg)


    

@app.route('/market_allcrypto')
def market_allcrypto():
    json_data = []
    # data = []
    cursor = db.cursor()
    msg = ''
    try:
        json_data=get_market_data(session['id'])
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # data = get_fav_crypto_list(session['id'])
    except Exception as e:
        msg = str(e)
    cursor.close()
    return render_template('market_allcrypto.html',jsondata=json_data,msg=msg)
    
@app.route('/mark_fav/<string:fav>')
def mark_fav(fav):
    cursor = db.cursor()
    cursor.execute('Select favourites from userinfo where email_id = %s',(session['id'],))
    favourite = cursor.fetchone()[0]
    favourites_list = favourite.split(",")
    if fav.strip() not in favourites_list:
        cursor.execute("UPDATE userinfo SET favourites = CONCAT(favourites, %s) WHERE email_id =%s",(","+fav,session['id'],))
        db.commit()
    print(get_fav_crypto_list(session['id']), "list after mark fav is ending")
    cursor.close()
    return redirect(url_for('market_allcrypto'))

@app.route('/mark_unfav/<string:fav>')
def mark_unfav(fav):
    cursor = db.cursor()
    cursor.execute('Select favourites from userinfo where email_id = %s',(session['id'],))
    favourites = (cursor.fetchone()[0]).split(',')
    if fav in favourites:
        favourites = [x for x in favourites if x != fav]
        favourites = ",".join(favourites)
        cursor.execute("UPDATE userinfo SET favourites = %s WHERE email_id =%s",(favourites,session['id'],))
        db.commit()
    print(get_fav_crypto_list(session['id']), "list after mark unfav is ending")
    cursor.close()
    return redirect(url_for('market_allcrypto'))

@app.route('/p2p_buy')
def p2p():
    # This is the code for p2p buy 
    list_ = []
    msg = ''
    cursor = db.cursor()
    try:
        list_ = get_p2p_buy_page_data()
        list_ = sorted(list_, key=lambda x: x['price'])
        print(list_)
    except Exception as e:
        msg = str(e)
    cursor.close()
    return render_template('p2p_buy.html',data=list_,msg=msg)
    
@app.route('/p2p_add_usdt/<float:balance>')  
def p2p_add_usdt(balance):
    cursor = db.cursor()
    # cursor.execute("SELECT JSON_EXTRACT(wallet, '$.USDT') FROM userinfo WHERE emailid=%s",(session['id'],))
    cursor.execute('SELECT wallet FROM userinfo WHERE email_id = %s', (session['id'],))
    wallet = cursor.fetchone()[0]
    wallet = json.loads(wallet)
    wallet['USDT']+=balance
    wallet = json.dumps(wallet)
    
    cursor.execute("UPDATE userinfo SET wallet = %s WHERE email_id= %s",(wallet,session['id'],))
    db.commit()
    cursor.close()
    return redirect(url_for('p2p_buy'))

@app.route('/p2p_sell')
def p2p_sell():
        # This is the code for p2p buy 
    list_ = []
    msg = ''
    cursor = db.cursor()
    try:
        list_ = get_p2p_sell_page_data()
        list_ = sorted(list_, key=lambda x: -x['price'])
        print(list_)
    except Exception as e:
        msg = str(e)
    cursor.close()
    return render_template('p2p_sell.html',data=list_,msg=msg)

@app.route('/p2p_deduct_usdt/<float:balance>')  
def p2p_deduct_usdt(balance):
    cursor = db.cursor()
    cursor.execute('SELECT wallet FROM userinfo WHERE email_id = %s', (session['id'],))
    wallet = cursor.fetchone()[0]
    wallet = json.loads(wallet)
    wallet['USDT']-=balance
    wallet = json.dumps(wallet)
    cursor.execute("UPDATE userinfo SET wallet = %s WHERE email_id= %s",(wallet,session['id'],))
    db.commit()
    cursor.close()
    return redirect(url_for('p2p_sell'))
    
@app.route('/change_password',methods = ['POST','GET'])
def change_password():
    msg = ''
    cursor = db.cursor()
    if request.method == 'POST' and 'password' in request.form and 'new_password' in request.form and 'confirm_new_password' in request.form:
        current_pass = request.form['password']
        newpass = request.form['new_password']
        newpass_confirm = request.form['confirm_new_password']
        print(session['id'],current_pass,newpass,newpass_confirm)
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            msg =  change_pass_help(session['id'],current_pass,newpass,newpass_confirm)
        except Exception as e:
            msg = str(e)
        print(msg)
    elif request.method == 'POST':
        msg = 'Please fill in all the blanks provided'
    cursor.close()
    return render_template('changepassword.html',msg=msg)
    
@app.route('/market_fav')
def market_fav():
    cursor = db.cursor()
    fav_details = []
    msg = ''
    try:
        fav_details = get_fav_page_data(session['id'])
    except Exception as e:
        msg = str(e)
    cursor.close()
    return render_template('market_fav.html',jsondata=fav_details,msg=msg)


@app.route('/user_profile')
def user_profile():
    cursor = db.cursor()
    data= {}
    msg = ''
    try:
        data = get_user_profile(session['id'])
        print(data['profile_pic'][-50:-35])
        cursor.close()
        return render_template('user_profile.html', data=data,msg=msg)
    except Exception as e:
        msg = str(e)
        print(msg)
        cursor.close()
        return render_template('user_profile.html', data=data,msg=msg)
    # data['profile_pic'] = 'data:image/png;base64,' + data['profile_pic'].decode('utf-8')
   
@app.route('/upload_pic',methods = ['GET','POST'])
def upload_pic():
    msg = ''
    cursor = db.cursor()
    if 'id' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        try:
            print(request.files)
            if 'photo' in request.files:
                photo = request.files['photo']
                if photo.filename != '' and is_allowed_file(photo.filename): # Check if the file has an allowed image extension
                    # Read the binary data from the file
                    image_data = photo.read()
                    encoded_data = base64.b64encode(image_data) # Encode the binary data as base64
                    cursor.execute('UPDATE userinfo SET profile_pic = %s WHERE email_id = %s', (encoded_data.decode('UTF-8') , session['id']))
                    db.commit()

                    msg = 'IMAGE UPDATED SUCCESSFULLY!'
                    # user_data['profile_pic'] = 'data:image/png;base64,' + base64.b64encode(user_data['profile_pic']).decode('utf-8')
                else:
                    msg="Only png , jpg and jpeg format is allowed"
                    # user_data['profile_pic_ext'] = os.path.splitext(photo.filename)[-1]
                    # image = 'data:image/png;base64,' + base64.b64encode(user_data['profile_pic']).decode('utf-8')
                    # user_data['profile_pic']= image
                    print(6)
            user_data= get_user_profile(session['id'])
            print(encoded_data[-50:-35],"here 2")
            user_data['profile_pic'] = encoded_data.decode("UTF-8")
            #return redirect(url_for('user_profile'))
            #return render_template('user_profile.html',data= user_data,msg=msg)
            print(user_data['profile_pic'][-50:-35])
            cursor.close()
            return jsonify({'msg':msg, 'profile_pic':user_data['profile_pic']})
        except Exception as e:
            print(e, "ERROR COMING HERE")
            msg = 'IMAGE CANNOT BE UPDATED!'
            # if user_data['profile_pic']!="":
                # user_data['profile_pic'] = 'data:image/png;base64,' + base64.b64encode(user_data['profile_pic']).decode('utf-8')   
            user_data= get_user_profile(session['id'])
            cursor.close()
            return render_template('user_profile.html',data=user_data,msg=msg)
    else:
        print(8)
        try:
            cursor.execute('SELECT profile_pic from userinfo where email_id=%s',(session['id']))
            image = cursor.fetchone()[0]
            image = base64.b64decode(image)
        except :
            msg = 'IMAGE CANNOT BE ACCESED AT THE MOMENT !'
        cursor.close()
        return render_template('user_profile.html',data = user_data,msg=msg)
        
        
@app.route('/order_history')
def order_history():
    cursor = db.cursor()
    history = []
    msg = ''
    try:
        history = get_order_history(session['id'])
    except Exception as e:
        msg = str(e)
    cursor.close()
    return render_template('order_history.html',history=history,msg=msg)
    
@app.route('/trade_page/<string:crypto>/<string:time_frame>')
def trade_page(crypto,time_frame):
    cursor = db.cursor()
    image = ''
    crypto_details = {}
    try:
        (image,crypto_details) = form_graph(crypto,time_frame)
        wallet_data = get_wallet_data(session['id'])
        crypto_details["crypto_size"] = wallet_data[crypto]
        crypto_details["USDT"] = wallet_data["USDT"]
        crypto_details["Current_crypto_value"] = crypto_details["last_price"]*crypto_details["crypto_size"]
    except Exception as e:
        msg = str(e)
    cursor.close()
    return render_template('btc_graph.html',image=image,data=crypto_details)

@app.route('/change_wallet/<string:order_type>/<string:crypto>/<float:usdt_qty>')
def change_wallet(order_type, crypto, usdt_qty):
    cursor = db.cursor()
    try:
        change_wallet(session['id'],order_type,crypto,usdt_qty)
    except Exception as e:
        msg = str(e)
    cursor.close()
    return redirect(url_for('trade_page'))


@app.route('/chat_buy/<string:seller_mailID>',methods = ['GET','POST'])
def chat_buy(seller_mailID):
    cursor = db.cursor()
    if request.method == 'POST' and 'messageInput' in request.form:
        message = request.form["messageInput"]
        try:
            update_chat_txt(session['id'],session['id'],seller_mailID,message)
            cursor.close()
            return redirect(url_for('chat_buy'))
        except Exception as e:
            msg = str(e)
            cursor.close()
            return render_template('chat_buy.html',msg=msg)
    elif request.method == "POST" and 'photo' in request.files:
        photo = request.files['photo']
        try:
            update_chat_image(session['id'],session['id'],seller_mailID,photo)
            cursor.close()
            return redirect(url_for('chat_buy'))
        except Exception as e:
            msg = str(e)
            cursor.close()
            return render_template('chat_buy.html',msg=msg)
    else:
        msg = ''
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT chat_messages FROM chat WHERE (email_id1 = %s AND email_id2 = %s) OR (email_id1 = %s AND email_id2 = %s)',(session['id'],seller_mailID,seller_mailID,session['id'],))
        t = cursor.fetchone()
        if t!=None:
            data = json.loads(t[0])
            if len(data[seller_mailID]) == 0 and len(data[session['id']]) == 0:
                msg = 'No messages'
            cursor.close()
            return render_template('chat_buy.html',data=data,msg=msg)
        else:
            msg="No Message"
            data=[]
            cursor.close()
            return render_template('chat_buy.html',data=data,msg=msg)
            

@app.route('/chat_sell/<string:buyer_mailID>',methods = ['GET','POST'])
def chat_sell(buyer_mailID):
    cursor = db.cursor()
    if request.method == 'POST' and 'messageInput' in request.form:
        message = request.form["messageInput"]
        try:
            update_chat_txt(session['id'],session['id'],buyer_mailID,message)
            cursor.close()
            return redirect(url_for('chat_sell'))
        except Exception as e:
            msg = str(e)
            cursor.close()
            return render_template('chat_sell.html',msg=msg)
        
    elif request.method == "POST" and 'photo' in request.files:
        photo = request.files['photo']
        try:
            update_chat_image(session['id'],session['id'],buyer_mailID,photo)
            cursor.close()
            return redirect(url_for('chat_sell'))
        except Exception as e:
            msg = str(e)
            cursor.close()
            return render_template('chat_sell.html',msg=msg)
    else:
        msg = ''
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT chat_messages FROM chat WHERE (email_id1 = %s AND email_id2 = %s) OR (email_id1 = %s AND email_id2 = %s)',(session['id'],buyer_mailID,buyer_mailID,session['id'],))
        t = cursor.fetchone()
        if t!=None:
            data = json.loads(t['chat_messages'])
            if len(data[buyer_mailID]) == 0 and len(data[session['id']]) == 0:
                msg = 'No messages'
            cursor.close()
            return render_template('chat_sell.html',data=data,msg=msg)
        else:
            data=[]
            cursor.close()
            return render_template('chat_sell.html',data=data,msg=msg)
            
    
# @app.route('/dropdown')
# def dropdown():
#     return render_template('dropdown.html')



if(__name__=="__main__"):
    app.run(debug=True)