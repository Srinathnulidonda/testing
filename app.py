from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change to a strong secret key

# Get the directory path of the current script
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'users.db')
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Create the database directory if it doesn't exist
database_dir = os.path.join(basedir, 'database')
if not os.path.exists(database_dir):
    os.makedirs(database_dir)

# Create the database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the email already exists
        if User.query.filter_by(email=email).first():
            flash('Email address already exists. Please use a different email.')
            return redirect(url_for('register'))

        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different username.')
            return redirect(url_for('register'))

        # Create a new user
        new_user = User(
            email=email,
            username=username,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))

        session['user_id'] = user.id
        session['username'] = user.username  # Store the username in the session
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    username = session.get('username')  # Retrieve the username from the session
    return render_template('dashboard.html', username=username)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)  # Clear the username from the session
    return redirect(url_for('index'))

# Sample destination data with image references
destinations = {
    "paris": {
        "name": "Paris, France",
        "tourist_spots": ["Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral", "Montmartre", "Seine River Cruises"],
        "local_attractions": ["Champs-Élysées", "Arc de Triomphe", "Disneyland Paris", "Palace of Versailles"],
        "climate": "Mild and moderately wet. Best travel times are spring (April-June) and fall (September-October) when temperatures are pleasant and tourist crowds are smaller.",
        "best_travel_times": "April to June, September to October"
    },
    "tokyo": {
        "name": "Tokyo, Japan",
        "tourist_spots": ["Tokyo Tower", "Senso-ji Temple", "Meiji Shrine", "Shibuya Crossing", "Ueno Park"],
        "local_attractions": ["Akihabara", "Ginza District", "Tsukiji Market", "Odaiba", "Tokyo Disneyland and DisneySea"],
        "climate": "Humid subtropical with four distinct seasons. Spring (March-May) and autumn (September-November) offer the most comfortable weather.",
        "best_travel_times": "March to May, September to November"
    },
    "new_york": {
        "name": "New York City, USA",
        "tourist_spots": ["Statue of Liberty", "Central Park", "Times Square", "Empire State Building", "Brooklyn Bridge"],
        "local_attractions": ["Broadway", "Museum of Modern Art (MoMA)", "Fifth Avenue", "High Line", "One World Observatory"],
        "climate": "Humid subtropical. Winters are cold, summers are hot and humid. Best times are spring (April-June) and fall (September-November).",
        "best_travel_times": "April to June, September to November"
    },
    "rome": {
        "name": "Rome, Italy",
        "tourist_spots": ["Colosseum", "Vatican Museums", "St. Peter's Basilica", "Trevi Fountain", "Roman Forum"],
        "local_attractions": ["Pantheon", "Piazza Navona", "Spanish Steps", "Villa Borghese"],
        "climate": "Mediterranean climate with hot, dry summers and mild, wet winters. Spring (April-June) and fall (September-October) are ideal for travel.",
        "best_travel_times": "April to June, September to October"
    },
    "sydney": {
        "name": "Sydney, Australia",
        "tourist_spots": ["Sydney Opera House", "Sydney Harbour Bridge", "Bondi Beach", "Taronga Zoo", "Darling Harbour"],
        "local_attractions": ["Royal Botanic Garden", "The Rocks", "Blue Mountains", "Manly Beach"],
        "climate": "Temperate with warm summers and mild winters. Best times are spring (September-November) and autumn (March-May).",
        "best_travel_times": "September to November, March to May"
    }
}

@app.route('/search')
def search():
    query = request.args.get('query', '').lower()
    search_results = {k: v for k, v in destinations.items() if query in v['name'].lower()}
    return render_template('search_results.html', destinations=search_results)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/accommodation_finder')
def accommodation_finder():
    # Example data, replace with actual data fetching logic
    accommodations = [
        {
            'name': 'Hotel A',
            'description': 'A nice place to stay',
            'price': '$100 per night',
            'latitude': -34.397,
            'longitude': 150.644,
            'image': 'hotel_a.jpg'
        },
        {
            'name': 'Hostel B',
            'description': 'Budget-friendly accommodation',
            'price': '$50 per night',
            'latitude': -34.397,
            'longitude': 150.644,
            'image': 'hostel_b.jpg'
        }
    ]
    return render_template('accommodations_finder.html', accommodation_finder=accommodation_finder)

@app.route('/destination/<destination_id>')
def destination(destination_id):
    destination_data = destinations.get(destination_id)
    if destination_data:
        return render_template('destination_detail.html', destination=destination_data, destination_id=destination_id)
    else:
        return "Destination not found", 404

if __name__ == '__main__':
    app.run(debug=True)
