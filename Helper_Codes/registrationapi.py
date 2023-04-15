from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_USER'] = 'your_username'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'Coinfun_database'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

class RegistrationAPI:
    
    def __init__(self):
        pass
    
    @app.route('/register', methods=['POST'])
    def register(self):
        email_id = request.json['email_id']
        username = request.json['username']
        password = request.json['password']
        wallet = request.json['wallet']
        favourites = request.json.get('favourites', '')
        profile_pic = request.json.get('profile_pic', '')
        kyc = request.json.get('kyc', False)

        cur = mysql.connection.cursor()

        # Check if email_id is already registered
        cur.execute("SELECT * FROM userinfo WHERE email_id=%s", (email_id,))
        row = cur.fetchone()
        if row:
            return jsonify({'error': 'Email already registered'})

        # Insert user data into userinfo table
        cur.execute("INSERT INTO userinfo (email_id, username, password, wallet, favourites, profile_pic, kyc) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (email_id, username, password, wallet, favourites, profile_pic, kyc))

        mysql.connection.commit()
        cur.close()

        return jsonify({'success': 'Registration successful'})

