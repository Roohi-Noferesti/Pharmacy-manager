

import uuid
import sqlite3
from adapters.database_adapter import DatabaseAdapter

class OrderService:
    def __init__(self, database_adapter):
        self.database_adapter = database_adapter


    def track_order(self, order_id):
        
        
        return f"Tracking information for Order {order_id}"

    def check_inventory(self, drug_code):
        
        query = "SELECT drug_inventory FROM Drug WHERE drug_code = ?"
        parameters = (drug_code,)
        result = DatabaseAdapter.fetch_one(query, parameters)
        return result[0] if result else None


    def initialize_order_code_table():
        
        connection = sqlite3.connect('database\pharmacy_db.sqlite.db')  
        cursor = connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS OrderCode (
                next_order_code INTEGER
            )
        ''')

        connection.commit()
        connection.close()
