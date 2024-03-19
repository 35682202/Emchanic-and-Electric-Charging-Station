from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.sql import text
from datetime import datetime
import requests


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.secret_key = 'PassWord@123'
db = SQLAlchemy(app)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    service_type = db.Column(db.String(100))
    service_date = db.Column(db.String(100))
    special_request = db.Column(db.String(200))
    place = db.Column(db.String(200))
    role = db.Column(db.Boolean, default=False)

    def __init__(self, name, email, service_type, service_date, special_request):
        self.name = name
        self.email = email
        self.service_type = service_type
        self.service_date = service_date
        self.special_request = special_request


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    agree_to_terms = db.Column(db.Boolean)

    def __init__(self, first_name, middle_name, last_name, email, password,  agree_to_terms):
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.agree_to_terms = agree_to_terms

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_lat = db.Column(db.Float, nullable=False)
    location_log = db.Column(db.Float, nullable=False)
    service_need = db.Column(db.String(100))
    car_type = db.Column(db.String(100))
    car_model = db.Column(db.String(100))
    req_time = db.Column(db.DateTime, default=datetime.utcnow)
    attended_time = db.Column(db.DateTime, default=datetime.utcnow)
    held_status = db.Column(db.Boolean, default=False)
    car_service = db.Column(db.String(100))

class Mechanic(UserMixin, db.Model):
    __tablename__ = 'mechanic'  # Add this line

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    address = db.Column(db.String(100))
    license_number = db.Column(db.String(50))
    city = db.Column(db.String(50))
    experience = db.Column(db.Integer)
    booked_by = db.Column(db.String(100), nullable=True)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    is_booked = db.Column(db.Boolean, default=False)
    location_lat = db.Column(db.Float, nullable=False)
    location_log = db.Column(db.Float, nullable=False)

    def check_password(self, password):
        return self.password == password

    def is_active(self):
        return True  # You may customize this based on your requirements

class ChargingStation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    alternative_contact = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    license_number = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float(100))
    longitude = db.Column(db.Float(100))
    zip_code = db.Column(db.String(10))
    agree_terms = db.Column(db.Boolean, nullable=False)

    def __init__(self, station_name, phone_number, alternative_contact, address, license_number,latitude, longitude,  zip_code, agree_terms):
        self.station_name = station_name
        self.phone_number = phone_number
        self.alternative_contact = alternative_contact
        self.address = address
        self.license_number = license_number
        self.latitude =latitude
        self.longitude = longitude
        self.zip_code = zip_code
        self.agree_terms = agree_terms



login_manager = LoginManager(app)
login_manager.login_view = 'login'

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/service')
def service():
	return render_template('service.html')

@app.route('/booking')
def booking():
	return render_template('booking.html')

@app.route('/contact')
def contact():
	return render_template('contact.html')

@app.route('/filter')
def filter():
	return render_template('filter.html')

@app.route('/user_log')
def user_log():
	return render_template('userlog.html')

@app.route('/user_reg')
def user_reg():
	return render_template('user_reg.html')

@app.route('/client_log')
def client_log():
	return render_template('client_log.html')

@app.route('/client')
def client():
	return render_template('client.html')

@app.route('/charging')
def charging():
	return render_template('charging.html')








@app.route('/register_mechanic', methods=['POST'])
def register_mechanic():
    if request.method == 'POST':
        try:
            first_name = request.form['first_name']
            middle_name = request.form['middle_name']
            last_name = request.form['last_name']
            email = request.form['email']
            password = request.form['password']
            address = request.form['address']
            license_number = request.form['license_number']
            city = request.form['city']
            experience = request.form['experience']
            latitude = float(request.form['latitude'])
            longitude = float(request.form['longitude'])

            existing_mechanic = Mechanic.query.filter_by(email=email).first()

            if existing_mechanic:
                flash('Email already exists. Please use a different email.', 'error')
                return redirect(url_for('user_reg'))

            mechanic = Mechanic(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                email=email,
                password=password,
                address=address,
                license_number=license_number,
                city=city,
                experience=experience,
                location_lat=latitude,
                location_log=longitude
            )

            flash('Registration successful', 'success')
            db.session.add(mechanic)
            db.session.commit()

            return redirect(url_for('mec_login'))

        except Exception as e:
            import traceback
            traceback.print_exc()
            flash('Registration failed. Please try again.', 'error')
            return redirect(url_for('user_reg'))


@login_manager.user_loader
def load_user(user_id):
    return Mechanic.query.get(int(user_id))

@app.route('/mec_login', methods=['GET', 'POST'])
def mec_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        mechanic = Mechanic.query.filter_by(email=email).first()

        if mechanic and mechanic.check_password(password):
            login_user(mechanic)
            flash('Login successful!', 'success')
            return redirect(url_for('mechanic_dashboard'))

        flash('Login failed. Check your email and password.', 'error')

    return render_template('userlog.html')

@app.route('/mechanic_dashboard')
@login_required
def mechanic_dashboard():
    mechanic = current_user
    stations = ChargingStation.query.filter_by(license_number=mechanic.license_number).all()
    return render_template('mechanic_dashboard.html', mechanic=mechanic, stations=stations)


# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/new_client', methods=['POST'])
def register():
    first_name = request.form['first_name']
    middle_name = request.form['middle_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']  # Plain text password

    # Hash the password using generate_password_hash
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    agree_to_terms = request.form.get('agree_to_terms')

    # Convert agree_to_terms to a boolean (True/False)
    agree_to_terms = agree_to_terms == 'on'

    client = Client(
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        email=email,
        password=hashed_password,  # Store the hashed password in the database
        
        agree_to_terms=agree_to_terms
    )

    db.session.add(client)
    db.session.commit()

    return redirect(url_for('client_log'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    client = Client.query.filter_by(email=email).first()

    if client:
        if check_password_hash(client.password, password):
            # Successful login
            session['user_id'] = client.id
            session['user_email'] = client.email
            session['user_first_name'] = client.first_name
            session['user_last_name'] = client.last_name

            # Redirect to the client dashboard
            return redirect(url_for('client_dash'))
        else:
            return render_template('client_log.html', error="Incorrect password")
    else:
        return render_template('client_log.html', error="Client not found")

@app.route('/client_dash')
def client_dash():
    if 'user_id' in session:
        user = {
            'user_id': session['user_id'],
            'user_email': session['user_email'],
            'user_first_name': session['user_first_name'],
            'user_last_name': session['user_last_name']
        }
        return render_template('client_dash.html', user=user)
    else:
        return redirect(url_for('login'))





@app.route('/trial')
def trial():
	return render_template('trial.html')


@app.route('/search_charging_station', methods=['POST'])
def search_charging_station():
    try:
        latitude = float(request.form.get('latitude'))
        longitude = float(request.form.get('longitude'))
    except ValueError:
        # Handle invalid input (non-numeric values)
        return render_template('error.html', message='Invalid coordinates provided')

    # Replace the following with your TomTom Maps API key
    api_key = '88U6EIt0pfb9wuMoSo0vC0BszxpaGb7f'

    # Constructing the TomTom Maps API URL for search
    api_url = f'https://api.tomtom.com/search/2/search/{latitude},{longitude}.json?limit=1&key={api_key}'

    # Making a request to the TomTom Maps API
    response = requests.get(api_url)

    if response.status_code == 200:
        additional_data = response.json()
    else:
        # Handle API error
        return render_template('error.html', message='Error fetching additional data from TomTom Maps API')

    return render_template('map.html', latitude=latitude, longitude=longitude, additional_data=additional_data)


@app.route('/search_mec', methods=['POST'])
def search_mec():
    try:
        latitude = float(request.form.get('latitude'))
        longitude = float(request.form.get('longitude'))
        service_need = request.form.get('service_need')
        car_type = request.form.get('car_type')
        car_model = request.form.get('car_model')
        car_service = request.form.get('car_service')

        # Create a new ServiceRequest instance and add it to the database
        new_request = ServiceRequest(
            location_lat=latitude,
            location_lon=longitude,
            service_need=service_need,
            car_type=car_type,
            car_model=car_model,
            car_service=car_service
        )

        db.session.add(new_request)
        db.session.commit()

    except ValueError:
        # Handle invalid input (non-numeric values)
        return render_template('error.html', message='Invalid coordinates provided')

    # Rest of your existing code goes here

    return render_template('map.html', latitude=latitude, longitude=longitude, additional_data=additional_data)

@app.route('/add_station', methods=['GET', 'POST'])
def add_station():
    if request.method == 'POST':
        # Get data from the form
        station_name = request.form['station_name']
        phone_number = request.form['phone_number']
        alternative_contact = request.form['alternative_contact']
        address = request.form['address']
        license_number = request.form['license_number']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        zip_code = request.form['zip_code']
        agree_terms = request.form.get('agree_terms') == 'on'

        # Replace the following with your TomTom Maps API key
        api_key = '88U6EIt0pfb9wuMoSo0vC0BszxpaGb7f'

        # Constructing the TomTom Maps API URL for search
        api_url = f'https://api.tomtom.com/search/2/search/{latitude},{longitude}.json?limit=1&key={api_key}'

        # Making a request to the TomTom Maps API
        response = requests.get(api_url)
        
        # Create a new ChargingStation object
        new_station = ChargingStation(
            station_name=station_name,
            phone_number=phone_number,
            alternative_contact=alternative_contact,
            address=address,
            license_number=license_number,
            latitude=latitude,
            longitude=longitude,
            zip_code=zip_code,
            agree_terms=agree_terms
        )

        # Add the new station to the database session
        db.session.add(new_station)

        # Commit changes to the database
        db.session.commit()

        # Redirect to a success page or another appropriate route
        return "ChargingStation successfully added"

    # Render the HTML form for adding a station
    return redirect(url_for('mechanic_dashboard'))



@app.route('/get_coordinates', methods=['GET'])
def get_coordinates():
    address = request.args.get('address')  # Assuming you pass the address as a query parameter
    api_key = '88U6EIt0pfb9wuMoSo0vC0BszxpaGb7f'
    
    # Constructing the TomTom Maps API URL for geocoding
    api_url = f'https://api.tomtom.com/search/2/geocode/{address}.json?key={api_key}'

    # Making a request to the TomTom Maps API
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        latitude = data['results'][0]['position']['lat']
        longitude = data['results'][0]['position']['lon']
        return jsonify({'latitude': latitude, 'longitude': longitude})
    else:
        return jsonify({'error': 'Failed to fetch coordinates'})



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
