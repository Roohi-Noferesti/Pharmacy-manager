import sqlite3
from pathlib import Path
from flask import g
import uuid

class DatabaseAdapter:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_connection(self):
        if 'connection' not in g:
            g.connection = sqlite3.connect(self.db_path)
        return g.connection
    
    def execute_query(self, query, parameters=None):
        connection = self.get_connection()
        cursor = connection.cursor()
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        connection.commit()

    def fetch_all(self, query, parameters=None):
        connection = self.get_connection()
        cursor = connection.cursor()
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        return cursor.fetchall()

    def close_connection(self):
        connection = g.pop('connection', None)
        cursor = g.pop('cursor', None)
        if cursor:
            cursor.close()
        if connection:
            connection.close()


    def create_tables(self):
        sql_file_path = "database/pharmacy_db.sql"
        with open(sql_file_path, "r") as file:
            commands = file.read().split(';')

            for command in commands:
                if command.strip():  
                    
                    if "CREATE TABLE" in command:
                        table_name = command.split("(")[0].split()[-1]
                        if not self.table_exists(table_name):
                            self.execute_query(command)
                    else:
                        self.execute_query(command)

    def table_exists(self, table_name):
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
        result = self.fetch_all(query)
        return len(result) > 0


    
    def insert_drug(self, drug_data):
    
        query = """
            INSERT INTO Drug (drug_code, name, production_date, expiration_date, price, dosage, usage_instructions, drug_inventory, pharmacy_code, company_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        parameters = (
            drug_data['drug_code'],
            drug_data['name'],
            drug_data['production_date'],
            drug_data['expiration_date'],
            drug_data['price'],
            drug_data['dosage'],
            drug_data['usage_instructions'],
            drug_data['drug_inventory'],
            drug_data['pharmacy_code'],
            drug_data['company_code'],
        )

        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(query, parameters)
        connection.commit()

        return cursor.lastrowid
    
    # def insert_order(self, order_data):
    #     query = """
    #         INSERT INTO DrugOrder (order_code, patient_code, pharmacy_code, quantity)
    #         VALUES (?, ?, ?, ?);
    #     """
    #     parameters = (
    #         order_data['order_code'],
    #         order_data['patient_code'],
    #         order_data['pharmacy_code'],
    #         order_data['quantity'],
    #     )

    #     connection = self.get_connection()
    #     cursor = connection.cursor()
    #     cursor.execute(query, parameters)
    #     connection.commit()

    #     return cursor.lastrowid
    




    def insert_comment(self, comment_data):
        query = """
            INSERT INTO DrugComment (patient_code, drug_code, comment, rating)
            VALUES (?, ?, ?, ?);
        """
        
        # Convert UUID to string
        drug_code_str = str(comment_data['drug_code'])

        parameters = (
            comment_data['patient_id'],
            drug_code_str,  # Use the string representation of UUID
            comment_data['comment'],
            comment_data['rating'],
        )

        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(query, parameters)
        connection.commit()

        return cursor.lastrowid

    
    def authenticate_user(self, username, password):
        query = "SELECT user_id, role FROM User WHERE username = ? AND password = ?"
        parameters = (username, password)
        user_data = self.fetch_one(query, parameters)
        return user_data



    
    def get_user_by_id(self, user_id):
        query = "SELECT * FROM User WHERE user_id = ?"
        parameters = (user_id,)
        user_data = self.fetch_all(query, parameters)
        if user_data:
            return {
                'id': user_data[0][0],
                'role': user_data[0][1]
            }
        return None
    def signup_user(self, name, birthdate, address, age, sex, username, password, role):

        query = """
            INSERT INTO User (name, birthdate, address, age, sex, username, password, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        parameters = (name, birthdate, address, age, sex, username, password, role)

        try:
            connection = self.get_connection()  
            cursor = connection.cursor()      

            cursor.execute(query, parameters)
            user_id = cursor.lastrowid
            connection.commit()  

            return {'user_id': user_id, 'name': name, 'role': role}

        except Exception as e:
            
            print(f"Error during user signup: {e}")
            return None

        finally:
            
            cursor.close()
            
    def fetch_one(self, query, parameters=None):
        connection = self.get_connection()
        cursor = connection.cursor()
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        return cursor.fetchone()


    def fetch_all_available_drugs(self):
        query = "SELECT DISTINCT drug_code, name, price, comment, rating FROM Drug;"
        results = self.fetch_all(query)
        
        drug_list = [{'drug_code': result[0], 'name': result[1], 'price': result[2]} for result in results]

        return drug_list

            

            
    def fetch_all_pharmacy_codes(self):
        query = "SELECT pharmacy_code FROM Drug;"
        result = self.fetch_all(query)
        
        
        if result:
            
            return [row[0] for row in result]

        return []
    
    def fetch_drugs_with_comments(self):
        query = """
            SELECT DISTINCT d.drug_code, d.name, d.price, c.comment, c.rating
            FROM Drug d
            LEFT JOIN DrugComment c ON d.drug_code = c.drug_code;
        """

        connection = self.get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(query)
            results = cursor.fetchall()

            drugs_with_comments = {}

            # Convert the list of tuples to a dictionary with drug code as the key
            for result in results:
                drug_code = result[0]
                comment_data = {
                    'comment': result[3],
                    'rating': result[4],
                }

                if drug_code not in drugs_with_comments:
                    drugs_with_comments[drug_code] = {
                        'drug_code': drug_code,
                        'name': result[1],
                        'price': result[2],
                        'comments': [],
                    }

                drugs_with_comments[drug_code]['comments'].append(comment_data)

            # Convert the dictionary values to a list
            return list(drugs_with_comments.values())

        except Exception as e:
            print(f"Error fetching drugs with comments: {e}")
            return []
        finally:
            cursor.close()

    def fetch_single_drug_quantity(self,drug_code):
        query = "SELECT quantity FROM Drug WHERE drug_code = ?"
        parameters = (drug_code,)
        drug_data = DatabaseAdapter.fetch_all(query, parameters)
        if drug_data:
            return {
                'drug_code': drug_data[0][0],
                'quantity': drug_data[0][1]
            }
        return None    
    
    def generate_unique_order_code(self):
        
        return str(uuid.uuid4())
    
    def place_order(self, current_user, pharmacy_code, quantity):

        order_code = self.generate_unique_order_code()

        
        query = """
            INSERT INTO DrugOrder (order_code, patient_code, pharmacy_code , quantity)
            VALUES (?, ?, ?,?);
        """
        parameters = ( order_code, current_user, pharmacy_code, quantity)
   
        try:
            connection = self.get_connection()  
            cursor = connection.cursor()      

            cursor.execute(query, parameters)
            connection.commit()  


        except Exception as e:
            
            print(f"Error during placing order: {e}")
            return None

        finally:
            
            cursor.close()

    def fetch_user_orders(self, patient_code):
        query = """
            SELECT order_code, pharmacy_code, quantity
            FROM DrugOrder
            WHERE patient_code = ?;
        """
        parameters = (patient_code,)

        connection = self.get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(query, parameters)
            results = cursor.fetchall()

            orders = [{'order_code': result[0], 'pharmacy_code': result[1], 'quantity': result[2]} for result in results]
            return orders

        except Exception as e:
            print(f"Error fetching user orders: {e}")
            return []
        finally:
            cursor.close()

    def insert_drug_company(self, company_data):
        query = """
            INSERT INTO DrugCompany (registration_number , name, date_established, phone_number, address)
            VALUES (? ,?, ?, ?, ?)
        """
        parameters = (
            company_data['registration_number'],
            company_data['name'],
            company_data['date_established'],
            company_data['phone_number'],
            company_data['address'],
        )

        self.execute_query(query, parameters)

    def insert_drug_manufacturer(self, manufacturer_data):
        query = """
            INSERT INTO DrugManufacturer (manufacturer_number, registration_number)
            VALUES (?, ?)
        """
        parameters = (
            manufacturer_data['manufacturer_number'],
            manufacturer_data['registration_number'],
        )

        self.execute_query(query, parameters)

    def insert_pharmacy(self, pharmacy_data):
        query = """
            INSERT INTO Pharmacy (pharmacy_code ,name, established_date, phone_number, address, license)
            VALUES (?,?, ?, ?, ?, ?)
        """
        parameters = (
            pharmacy_data['pharmacy_code'],
            pharmacy_data['name'],
            pharmacy_data['established_date'],
            pharmacy_data['phone_number'],
            pharmacy_data['address'],
            pharmacy_data['license'],
        )
        self.execute_query(query, parameters)

    def place_mass_order(self, warehouse_clerk_id, pharmacy_code, drug_code, quantity):
        order_code = self.generate_unique_order_code()

        query = """
            INSERT INTO WarehouseOrder (order_code, warehouse_clerk_id, pharmacy_code, drug_code, quantity)
            VALUES (?, ?, ?, ?, ?);
        """
        parameters = (
            order_code,
            warehouse_clerk_id,
            pharmacy_code,
            drug_code,
            quantity,
        )

        try:
            connection = self.get_connection()
            cursor = connection.cursor()

            cursor.execute(query, parameters)
            connection.commit()

            return True

        except Exception as e:
            print(f"Error during placing mass order: {e}")
            return False

        finally:
            cursor.close()


    def fetch_all_manufacturers(self):
        query = "SELECT manufacturer_number FROM DrugManufacturer;"
        result = self.fetch_all(query)

        if result:
            return [row[0] for row in result]

        return []

    def fetch_all_pharmacy_codes(self):
        query = "SELECT pharmacy_code FROM Pharmacy;"
        result = self.fetch_all(query)

        if result:
            return [row[0] for row in result]

        return []