
from werkzeug.security import generate_password_hash

class UserService:
    def __init__(self, database_adapter):
        self.database_adapter = database_adapter

    def get_user_info(self, user_id):
        query = "SELECT * FROM User WHERE user_id = ?"
        parameters = (user_id,)
        result = self.database_adapter.fetch_all(query, parameters)
        return result[0] if result else None

    def update_user_info(self, user_id, new_data):
        
        
        query = "UPDATE User SET name = ?, address = ? WHERE user_id = ?"
        parameters = (new_data.get('name'), new_data.get('address'), user_id)
        self.database_adapter.execute_query(query, parameters)

    def create_user(self, username, password, role):
        password_hash = generate_password_hash(password)
        query = "INSERT INTO User (username, password_hash, role) VALUES (?, ?, ?)"
        parameters = (username, password_hash, role)
        self.database_adapter.execute_query(query, parameters)    