from flask import Flask, render_template, redirect, request
from adapters.ui_adapter import UIAdapter
from core_logic.services.order_service import OrderService
from core_logic.services.inventory_service import InventoryService
from core_logic.services.user_service import UserService
from adapters.database_adapter import DatabaseAdapter
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import redirect,url_for,flash
from flask_login import current_user
import uuid
from adapters.database_adapter import DatabaseAdapter

app = Flask(__name__, template_folder='templates')
app.secret_key = 'secret_key'  # Change this to a secure key
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize adapters
ui_adapter = UIAdapter()
database_adapter = DatabaseAdapter("database/pharmacy_db.sqlite")  # Adjust the path accordingly
order_service = OrderService(database_adapter)

# Initialize services
order_service = OrderService(database_adapter)
inventory_service = InventoryService(database_adapter)
user_service = UserService(database_adapter)

# Pass adapters to services
order_service.database_adapter = database_adapter
inventory_service.database_adapter = database_adapter
user_service.database_adapter = database_adapter

class User:
    def __init__(self, user_id, role):
        self.id = user_id
        self.role = role

    def is_authenticated(self):
        return True  # You can add more logic here if needed

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    # Load user from your database
    user_data = database_adapter.get_user_by_id(user_id)
    if user_data:
        return User(user_data['id'], user_data['role'])
    return None

# Function to create database tables
def create_tables():
    with app.app_context():
        database_adapter.create_tables()

# Run the function to create tables when the application starts
create_tables()

def get_user_dashboard_url(role):
    if role == 'patient':
        return '/patient_dashboard'
    elif role == 'pharmacy_clerk':
        return '/pharmacy_clerk_dashboard'
    elif role == 'warehouse_clerk':
        return '/warehouse_clerk_dashboard'
    else:
        return '/'

# Define a simple route for the home page
@app.route('/')
def home():
    return render_template('login.html')

# Define a route for the admin page
@app.route('/admin')
def admin_page():
    return render_template('admin_page.html')



# Define a route for adding new drugs
@app.route('/add_drug', methods=['POST'])
def add_drug():
    # Retrieve form data
    drug_name = request.form.get('drug_name')
    production_date = datetime.strptime(request.form.get('production_date'), '%Y-%m-%d').date()
    expiration_date = datetime.strptime(request.form.get('expiration_date'), '%Y-%m-%d').date()
    price = float(request.form.get('price'))
    dosage = request.form.get('dosage')
    usage_instructions = request.form.get('usage_instructions')
    drug_inventory = int(request.form.get('drug_inventory'))
    pharmacy_code = int(request.form.get('pharmacy_code')) if request.form.get('pharmacy_code') else None
    company_code = int(request.form.get('company_code'))
    drug_code = str(uuid.uuid4())


    # Perform database insertion for the new drug
    drug_data = {
        'drug_code': drug_code,
        'name': drug_name,
        'production_date': production_date,
        'expiration_date': expiration_date,
        'price': price,
        'dosage': dosage,
        'usage_instructions': usage_instructions,
        'drug_inventory': drug_inventory,
        'pharmacy_code': pharmacy_code,
        'company_code': company_code,
    }

    database_adapter.insert_drug(drug_data)

    print("Drug Data:", drug_data)

    # Redirect to the admin page or another appropriate page
    return redirect('/pharmacy_clerk_dashboard')






# Define routes for placing an order and checking inventory
@app.route('/place_order')
def place_order():
    # Implement logic for placing an order
    return render_template('order.html')

@app.route('/check_inventory')
def check_inventory():
    # Implement logic for checking inventory
    return render_template('inventory.html')


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password match in the database
        user_data = database_adapter.authenticate_user(username, password)

        if user_data:
            user_id, role = user_data
            user = User(user_id, role)
            login_user(user)

            # Redirect to the appropriate dashboard based on the user's role
            if user.role == 0:  # Patient
                return redirect(url_for('patient_dashboard'))
            elif user.role == 1:  # Warehouse Clerk
                return redirect(url_for('warehouse_clerk_dashboard'))
            elif user.role == 2:  # Pharmacy Clerk
                return redirect(url_for('pharmacy_clerk_dashboard'))

        flash('Invalid username or password', 'error')

    return render_template('login.html')


# Define a route for the pharmacy clerk dashboard
@app.route('/pharmacy_clerk_dashboard')
@login_required
def pharmacy_clerk_dashboard():
    return render_template('pharmacy_clerk_dashboard.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('name')
        birthdate = request.form.get('birthdate')
        address = request.form.get('address')
        age = request.form.get('age')
        sex = request.form.get('sex')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        # Perform database insertion for the new user
        user_data = database_adapter.signup_user(name, birthdate, address, age, sex, username, password, role)

        if user_data:
            # Redirect to the login page or another appropriate page
            return redirect('/login')

    return render_template('signup.html')


@app.route('/order_drug/<uuid:drug_code>', methods=['POST'])
@login_required
def order_drug(drug_code):
    drug_code_from_form = request.form.get('my_drug_code')
    pharmacy_code = request.form.get('pharmacy_code')  # Access pharmacy_code from form data
    quantity = int(request.form.get('quantity', 1))

    success = database_adapter.place_order(current_user.id, pharmacy_code, quantity)

    # if success:
    #     flash('Drug ordered successfully!', 'success')
    # else:
    #     flash('Failed to order the drug. Not enough stock or an error occurred.', 'error')

    return redirect(url_for('patient_dashboard'))




@app.route('/patient_dashboard')
@login_required
def patient_dashboard():
    # Fetch available drugs with comments
    available_drugs = database_adapter.fetch_drugs_with_comments()

    # Fetch pharmacy codes
    current_orders = database_adapter.fetch_user_orders(current_user.id)
    
    pharmacy_codes = database_adapter.fetch_all_pharmacy_codes()
    return render_template('patient_dashboard.html', available_drugs=available_drugs, pharmacy_codes=pharmacy_codes, current_orders=current_orders)


@app.route('/comment_and_rate/<uuid:drug_code>', methods=['POST'])
@login_required
def comment_and_rate(drug_code):
    patient_id = current_user.id
    comment = request.form.get('comment')
    rating = int(request.form.get('rating'))
    comment_data = {
        'patient_id': patient_id,
        'drug_code': drug_code,
        'comment': comment,
        'rating': rating,
    }

    # Create an instance of DatabaseAdapter
    db_adapter = DatabaseAdapter("database/pharmacy_db.sqlite")

    # Call the instance method insert_comment
    success = db_adapter.insert_comment(comment_data)

    if success:
        flash('Comment and rating submitted successfully!', 'success')
    else:
        flash('Failed to submit comment and rating. Please try again.', 'error')

    # Redirect to the patient_dashboard page after submitting the comment and rating
    return redirect(url_for('patient_dashboard'))


@app.route('/warehouse_clerk_dashboard')
@login_required
def warehouse_clerk_dashboard():
    # Fetch pharmacy codes and manufacturers
    pharmacy_codes = database_adapter.fetch_all_pharmacy_codes()
    manufacturer_numbers = database_adapter.fetch_all_manufacturers()
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxx",pharmacy_codes , manufacturer_numbers)
    return render_template('warehouse_clerk_dashboard.html', pharmacy_codes=pharmacy_codes, manufacturer_numbers=manufacturer_numbers)

@app.route('/add_drug_company', methods=['POST'])
@login_required
def add_drug_company():
    # Retrieve form data
    registration_number = request.form.get('registration_number')
    company_name = request.form.get('company_name')
    establishment_date = datetime.strptime(request.form.get('establishment_date'), '%Y-%m-%d').date()
    phone_number = request.form.get('phone_number')
    address = request.form.get('address')

    # Perform database insertion for the new drug company
    company_data = {
        'registration_number':registration_number,
        'name': company_name,
        'date_established': establishment_date,
        'phone_number': phone_number,
        'address': address,
    }

    database_adapter.insert_drug_company(company_data)

    # Redirect to the warehouse clerk dashboard or another appropriate page
    return redirect('/warehouse_clerk_dashboard')

@app.route('/add_drug_manufacturer', methods=['POST'])
@login_required
def add_drug_manufacturer():
    # Retrieve form data
    manufacturer_number = int(request.form.get('manufacturer_number'))
    registration_number = int(request.form.get('registration_number'))

    # Perform database insertion for the new drug manufacturer
    manufacturer_data = {
        'manufacturer_number': manufacturer_number,
        'registration_number': registration_number,
    }

    database_adapter.insert_drug_manufacturer(manufacturer_data)

    # Redirect to the warehouse clerk dashboard or another appropriate page
    return redirect('/warehouse_clerk_dashboard')

@app.route('/add_pharmacy', methods=['POST'])
@login_required
def add_pharmacy():
    # Retrieve form data
    pharmacy_code = request.form.get('pharmacy_code')
    pharmacy_name = request.form.get('pharmacy_name')
    establishment_date = datetime.strptime(request.form.get('establishment_date'), '%Y-%m-%d').date()
    phone_number = request.form.get('phone_number')
    address = request.form.get('address')
    license = int(request.form.get('license'))

    # Perform database insertion for the new pharmacy
    pharmacy_data = {
        'pharmacy_code' : pharmacy_code,
        'name': pharmacy_name,
        'established_date': establishment_date,
        'phone_number': phone_number,
        'address': address,
        'license': license,
    }
    database_adapter.insert_pharmacy(pharmacy_data)

    # Redirect to the warehouse clerk dashboard or another appropriate page
    return redirect('/warehouse_clerk_dashboard')

@app.route('/place_mass_order', methods=['POST'])
@login_required
def place_mass_order():
    # Retrieve form data
    drug_code = request.form.get('drug_code')
    pharmacy_code = int(request.form.get('pharmacy_code'))
    quantity = int(request.form.get('quantity'))

    # Perform database insertion for the mass order
    success = database_adapter.place_mass_order(current_user.id, pharmacy_code, drug_code, quantity)

    # Redirect to the warehouse clerk dashboard or another appropriate page
    return redirect('/warehouse_clerk_dashboard')


if __name__ == "__main__":
    app.run(debug=True)
    
