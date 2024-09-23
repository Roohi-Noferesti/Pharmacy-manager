from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, user_id, username, password_hash, role):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        return f"User {self.username} (ID: {self.user_id}, Role: {self.role})"
