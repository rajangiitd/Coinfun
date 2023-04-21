import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Teamwork123",
    database="Coinfun_database"
)
cursor = db.cursor()

def get_transaction_history_data(email_id): # returns a list of dictionaries containing transaction history data of P2P trades
    try:
        # query the P2PTradeHistoryData table for transactions involving the given email_id
        query = "SELECT * FROM P2PTradeHistoryData WHERE buyer_email_id = %s OR seller_email_id = %s"
        cursor.execute(query, (email_id, email_id))
        result = cursor.fetchall()
        
        # check if the result is empty and raise an exception if so
        if not result:
            raise Exception("No Transaction History Available")
        # convert the result to a list of dictionaries
        keys = ['order_id', 'buyer_email_id', 'seller_email_id', 'transaction_usdt', 'price', 'time_stamp']
        transaction_history = []
        for row in result:
            transaction_dict = dict(zip(keys, row))
            transaction_history.append(transaction_dict)
        return transaction_history
    except Exception as e:
        raise e