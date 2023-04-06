from flask import Flask , render_template , request , redirect , url_for , session
# from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL 
import MySQLdb.cursors
import re 

app=Flask(__name__, static_folder='static')
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
app.secret_key='your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'swanDB'

sql=MySQL(app)

@app.route('/login')
def first():
	return render_template('login.html', msg = '')

@app.route('/login', methods =['GET', 'POST'])
def login():
	message = ''
	if request.method == 'GET' and 'email' in request.form and 'password' in request.form:
		email = request.form['email']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM userinfo WHERE email = % s AND password = % s', (email, password, ))
		account = cursor.fetchone()
		if account:
			session['loggedin'] = True
			session['id'] = account['user_id']
			session['username'] = account['username']
			message = 'Logged in successfully !'
			return redirect(url_for('index',userid=session['id']))
		else:
			message = 'Incorrect username / password !'
	return render_template('login.html', msg = message)


@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	# return render_template('pages-register.html', msg = msg)
	if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form and 'confirm-password' in request.form and 'phone-number' in request.form:
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
        confirm_password=request.form['confirm-password']
        phone_number = request.form['phone-number']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE email = % s', (email,))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif password!=confirm_password:
			msg = 'Password and confirm-Password must be same'
        
		else:
			cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)


@app.route('/')
def dashboard(userid):
    data={}
    data['username']=Vikash
    data['estimated_balance']=5,450
    data

    return render_template('dashboard.html',data=data)

@app.route('/market_allcrypto')
def market():
    return render_template('market_allcrypto.html')

@app.route('/p2p_buy')
def p2p():
    return render_template('p2p_buy.html')

@app.route('/p2p_sell')
def p2p_sell():
    return render_template('p2p_sell.html')

@app.route('/market_fav')
def market_fav():
    return render_template('market_fav.html')

@app.route('/user_profile')
def user_profile():
    return render_template('user_profile.html')

@app.route('/transaction')
def transaction():
    return render_template('transaction.html')

@app.route('/order_history')
def order_history():
    return render_template('order_history.html')

@app.route('/dropdown')
def dropdown():
    return render_template('dropdown.html')



if(__name__=="__main__"):
    app.run(debug=True)