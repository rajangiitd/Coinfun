import mysql.connector
import time

try:
    db = mysql.connector.connect(host="localhost",
                                user="root",
                                password="Teamwork123",
                                database="Coinfun_database")
    
    while True:
        if(db.is_connected()):
            db.ping(reconnect=True)
            print("Sent a ping query to MySQL server at", time.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            db.reconnect(attempts=3, delay=5) 
        time.sleep(3600)

except mysql.connector.Error as error:
    print("Failed to connect to database: {}".format(error))
