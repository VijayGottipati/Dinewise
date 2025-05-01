# =========================
# Imports and Configuration
# =========================
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import requests
import os
import json
import pyrebase
from dotenv import load_dotenv
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import firebase_admin
from firebase_admin import credentials, auth, db
import sys
import uuid
import jinja2

# =========================
# Flask App Initialization
# =========================
load_dotenv()
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

# =========================
# Firebase Admin SDK Initialization
# =========================
try:
    cred = credentials.Certificate('dinewise-1ade0-firebase-adminsdk-fbsvc-826e342dd1.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.getenv('FIREBASE_DATABASE_URL', 'https://your-project-id.firebaseio.com')
    })
    print("✅ Firebase Admin SDK initialized successfully")
except Exception as e:
    print(f"❌ Firebase Admin SDK Error: {str(e)}")

# =========================
# Pyrebase Client Initialization
# =========================
try:
    with open('firebase_config.json', 'r') as f:
        firebase_config = json.load(f)
    firebase = pyrebase.initialize_app(firebase_config)
    auth = firebase.auth()
    print("✅ Firebase client initialized successfully from config file")
except Exception as e:
    print(f"❌ Firebase client initialization error: {str(e)}")
    firebase = None
    auth = None

# =========================
# API Keys and Global Variables
# =========================
YELP_API_KEY = os.getenv('YELP_API_KEY')
YELP_ENDPOINT = 'https://api.yelp.com/v3/businesses'
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
HEADERS = {'Authorization': f'Bearer {YELP_API_KEY}'}

if not YELP_API_KEY:
    print("WARNING: YELP_API_KEY not found in environment variables!")

reviews = {}
wishlists = {}
users = {
    'test@example.com': {
        'id': '1',
        'name': 'Test User',
        'email': 'test@example.com',
        'password': generate_password_hash('password123')
    }
}

# =========================
# Login Required Decorator
# =========================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        try:
            user = session.get('user')
            id_token = user.get('idToken')
            if not id_token:
                print("❌ No idToken found in session user data.")
                session.clear()
                flash('Your session data is incomplete. Please log in again.', 'error')
                return redirect(url_for('login'))
            try:
                decoded_token = firebase_admin.auth.verify_id_token(id_token)
            except firebase_admin.auth.ExpiredIdTokenError:
                print("⏳ ID token expired. Attempting refresh...")
                try:
                    refresh_token = user.get('refreshToken')
                    if not refresh_token:
                        print("❌ No refreshToken found in session for refresh.")
                        raise Exception("Missing refresh token")
                    if not auth:
                        print("❌ Pyrebase auth object not available for token refresh.")
                        raise Exception("Pyrebase auth not initialized")
                    refreshed_user_info = auth.refresh(refresh_token)
                    print("✅ Token refreshed successfully.")
                    session['user'] = refreshed_user_info
                    firebase_admin.auth.verify_id_token(refreshed_user_info['idToken'])
                except Exception as refresh_err:
                    print(f"❌ Token refresh failed: {str(refresh_err)}")
                    session.clear()
                    flash('Your session has expired. Please log in again.', 'error')
                    return redirect(url_for('login'))
            except firebase_admin.auth.InvalidIdTokenError as invalid_token_err:
                print(f"❌ Invalid ID token: {str(invalid_token_err)}")
                session.clear()
                flash('Your session is invalid. Please log in again.', 'error')
                return redirect(url_for('login'))
        except Exception as e:
            print(f"❌ Error during session check/token verification: {str(e)}")
            session.clear()
            flash('An error occurred validating your session. Please log in again.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# =========================
# User Authentication: Login
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            if not auth:
                print("❌ Pyrebase auth object not initialized!")
                flash('Authentication service is not available. Please try again later.', 'error')
                return render_template('login.html')
            user = auth.sign_in_with_email_and_password(email, password)
            session.permanent = True
            session['user'] = user
            user_ref = db.reference(f'users/{user["localId"]}')
            user_data = user_ref.get()
            if user_data:
                session['name'] = user_data.get('name', 'User')
            else:
                print(f"⚠️ User data not found in DB for UID {user['localId']}. Creating entry.")
                user_ref.set({
                    'name': email.split('@')[0],
                    'email': email,
                    'wishlist': []
                })
                session['name'] = email.split('@')[0]
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        except requests.exceptions.HTTPError as http_err:
            error_message = 'UNKNOWN_ERROR'
            try:
                error_json = http_err.response.json()
                error_message = error_json.get('error', {}).get('message', 'UNKNOWN_ERROR')
                print(f"Firebase Login HTTP Error (JSON): {error_message}")
            except Exception as json_err:
                error_text = str(http_err)
                print(f"Firebase Login HTTP Error (Text): {error_text}. JSON parse failed: {json_err}")
                error_message = error_text
            if "INVALID_LOGIN_CREDENTIALS" in error_message or \
               "EMAIL_NOT_FOUND" in error_message or \
               "INVALID_PASSWORD" in error_message:
                flash('Invalid email or password. Please try again.', 'error')
            elif "USER_DISABLED" in error_message:
                flash('This account has been disabled.', 'error')
            else:
                flash(f'Login failed: {error_message}. Please try again later.', 'error')
            return render_template('login.html')
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error during login: {str(conn_err)}")
            flash('Unable to connect to authentication service. Please check your internet connection.', 'error')
            return render_template('login.html')
        except Exception as e:
            print(f"Unexpected Login error: {str(e)}")
            flash('An unexpected error occurred during login. Please try again.', 'error')
            return render_template('login.html')
    return render_template('login.html')

# =========================
# User Authentication: Register
# =========================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form.get('confirm_password', '')
        name = request.form['name']
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        try:
            print(f"Attempting to register user with email: {email}")
            auth = firebase.auth()
            try:
                user = auth.create_user_with_email_and_password(email, password)
                print(f"User created successfully with ID: {user.get('localId')}")
                user_ref = db.reference(f'users/{user["localId"]}')
                user_ref.set({
                    'name': name,
                    'email': email,
                    'wishlist': []
                })
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except requests.exceptions.ConnectionError as conn_err:
                print(f"Connection error: {str(conn_err)}")
                flash('Unable to connect to authentication service. Please check your internet connection.', 'error')
            except requests.exceptions.Timeout:
                print("Request timed out")
                flash('Connection to authentication service timed out. Please try again later.', 'error')
            except Exception as auth_err:
                error_message = str(auth_err)
                print(f"Authentication error: {error_message}")
                if "EMAIL_EXISTS" in error_message:
                    flash('Email already in use. Please use a different email or login.', 'error')
                elif "WEAK_PASSWORD" in error_message:
                    flash('Password is too weak. Please use at least 6 characters.', 'error')
                elif "INVALID_EMAIL" in error_message:
                    flash('Invalid email format. Please enter a valid email address.', 'error')
                else:
                    flash('Registration failed. Please try again later.', 'error')
        except Exception as e:
            print(f"Unexpected error during registration: {str(e)}")
            flash('An unexpected error occurred. Please try again later.', 'error')
    return render_template('register.html')

# =========================
# User Logout
# =========================
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# =========================
# Home Page and Restaurant Search
# =========================
@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
        location = request.form.get('location')
        term = request.form.get('term', '')
        price = request.form.get('price', '')
        cuisine = request.form.get('cuisine', '')
        if not location:
            flash('Please enter a location', 'error')
            return render_template('index.html', results=[])
        search_term = term
        if cuisine and not term:
            search_term = cuisine
        elif cuisine and term:
            search_term = f"{term} {cuisine}"
        headers = {'Authorization': f'Bearer {YELP_API_KEY}'}
        params = {
            'location': location,
            'term': search_term,
            'limit': 20,
        }
        if price:
            params['price'] = price
        try:
            response = requests.get('https://api.yelp.com/v3/businesses/search', headers=headers, params=params)
            response.raise_for_status()
            results = response.json().get('businesses', [])
            if results:
                print(f"DEBUG: First business ID: {results[0].get('id')}")
                print(f"DEBUG: First business URL: {results[0].get('url')}")
            if not results:
                flash('No restaurants found matching your criteria', 'info')
        except requests.exceptions.RequestException as e:
            print("Yelp API Error:", e)
            flash("Error searching for restaurants. Please try again.", "error")
        except Exception as e:
            print("Unexpected Error:", e)
            flash("An unexpected error occurred. Please try again.", "error")
    return render_template('index.html', results=results)

# =========================
# Nearby Restaurant Search
# =========================
@app.route('/nearby', methods=['GET', 'POST'])
def nearby():
    results = []
    if request.method == 'POST':
        address = request.form.get('address', '')
        city = request.form.get('city', '')
        state = request.form.get('state', '')
        zipcode = request.form.get('zipcode', '')
        country = request.form.get('country', 'USA')
        location_parts = []
        if address:
            location_parts.append(address)
        if city:
            location_parts.append(city)
        if state:
            location_parts.append(state)
        if zipcode:
            location_parts.append(zipcode)
        if country:
            location_parts.append(country)
        location = ", ".join(location_parts)
        if not city and not zipcode:
            flash('Please enter at least a city or zip code', 'error')
            return render_template('store_locator.html', results=[])
        headers = {'Authorization': f'Bearer {YELP_API_KEY}'}
        params = {
            'location': location,
            'term': 'restaurants',
            'limit': 20,
        }
        try:
            print(f"Searching for restaurants near: {location}")
            response = requests.get('https://api.yelp.com/v3/businesses/search', headers=headers, params=params)
            print(f"API Response status: {response.status_code}")
            if response.status_code != 200:
                print(f"API Error response: {response.text}")
            response.raise_for_status()
            results = response.json().get('businesses', [])
            if not results:
                flash('No restaurants found in your area', 'info')
        except requests.exceptions.RequestException as e:
            print("Yelp API Error:", e)
            flash("Error finding nearby restaurants. Please try again.", "error")
        except Exception as e:
            print("Unexpected Error:", e)
            flash("An unexpected error occurred. Please try again.", "error")
    return render_template('store_locator.html', results=results)

# =========================
# Restaurant Detail Page
# =========================
@app.route('/restaurant/<business_id>')
def restaurant_detail(business_id):
    headers = {'Authorization': f'Bearer {YELP_API_KEY}'}
    restaurant = None
    yelp_reviews = []
    user_reviews = []
    dinewise_rating = None
    weighted_average_rating = None
    total_combined_reviews = 0
    try:
        print(f"Fetching details for restaurant ID: {business_id}")
        response = requests.get(f'{YELP_ENDPOINT}/{business_id}', headers=headers)
        print(f"Restaurant API response status: {response.status_code}")
        if response.status_code == 200:
            restaurant = response.json()
        else:
            print(f"API Error response: {response.text}")
    except Exception as e:
        print(f"Error fetching restaurant details: {e}")
    if restaurant:
        try:
            reviews_response = requests.get(f'{YELP_ENDPOINT}/{business_id}/reviews', headers=headers)
            print(f"Reviews API response status: {reviews_response.status_code}")
            if reviews_response.status_code == 200:
                yelp_reviews = reviews_response.json().get('reviews', [])
            else:
                print(f"Reviews API Error response: {reviews_response.text}")
        except Exception as e:
            print(f"Error fetching Yelp reviews: {e}")
        try:
            reviews_ref = db.reference(f'reviews/{business_id}')
            user_reviews_data = reviews_ref.get() or {}
            user_reviews = [review for review_id, review in user_reviews_data.items()]
            user_reviews.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

            # --- Calculate Weighted Average Rating ---
            yelp_rating = None
            yelp_review_count = 0
            dinewise_review_count = len(user_reviews)
            total_score = 0.0
            total_reviews = 0

            # Get Yelp data if restaurant details were fetched
            if restaurant:
                try:
                    yelp_rating = float(restaurant.get('rating'))
                    yelp_review_count = int(restaurant.get('review_count', 0))
                    if yelp_rating is not None and yelp_review_count > 0:
                        total_score += yelp_rating * yelp_review_count
                        total_reviews += yelp_review_count
                except (ValueError, TypeError, AttributeError):
                    print(f"Warning: Could not parse Yelp rating/count for {business_id}")

            # Calculate Dinewise Rating and add its contribution to weighted average
            if user_reviews:
                total_dinewise_score = sum(float(review.get('rating', 0)) for review in user_reviews)
                if dinewise_review_count > 0:
                    dinewise_rating = round(total_dinewise_score / dinewise_review_count, 1)
                    total_score += total_dinewise_score
                    total_reviews += dinewise_review_count

            if total_reviews > 0:
                weighted_average_rating = round(total_score / total_reviews, 1)
            total_combined_reviews = total_reviews

            print(f"Found {len(user_reviews)} user reviews")
        except Exception as e:
            print(f"Error fetching user reviews: {e}")
    if not restaurant:
        restaurant = {
            'name': 'Restaurant information unavailable',
            'id': business_id,
            'image_url': None,
            'rating': None,
            'review_count': 0,
            'price': None,
            'is_closed': None,
            'location': {'display_address': ['Address unavailable']},
            'display_phone': None,
            'phone': None,
            'url': None,
            'coordinates': {'latitude': None, 'longitude': None},
            'categories': []
        }
        flash("Some restaurant information could not be loaded", "warning")
    is_potentially_new = session.get('user') is not None
    coordinates = restaurant.get('coordinates') if restaurant else None
    latitude = coordinates.get('latitude') if coordinates else None
    longitude = coordinates.get('longitude') if coordinates else None
    show_promo_banner = is_potentially_new
    return render_template('restaurant_detail.html',
                         restaurant=restaurant,
                         yelp_reviews=yelp_reviews,
                         user_reviews=user_reviews,
                         dinewise_rating=dinewise_rating,
                         weighted_average_rating=weighted_average_rating,
                         total_combined_reviews=total_combined_reviews,
                         show_new_user_promo=show_promo_banner,
                         gmaps_api_key=GOOGLE_MAPS_API_KEY,
                         latitude=latitude,
                         longitude=longitude)

# =========================
# Simple Restaurant Detail (for fallback/testing)
# =========================
@app.route('/simple-restaurant/<business_id>')
def simple_restaurant_detail(business_id):
    headers = {'Authorization': f'Bearer {YELP_API_KEY}'}
    try:
        response = requests.get(f'{YELP_ENDPOINT}/{business_id}', headers=headers)
        response.raise_for_status()
        restaurant = response.json()
        yelp_reviews = []
        user_reviews = []
    except Exception as e:
        print(f"Error: {e}")
        flash("Error loading restaurant details", "error")
        return redirect(url_for('index'))
    return render_template('restaurant_detail.html',
                         restaurant=restaurant,
                         yelp_reviews=yelp_reviews,
                         user_reviews=user_reviews)

# =========================
# Add Review to Restaurant
# =========================
@app.route('/add_review/<business_id>', methods=['POST'])
def add_review(business_id):
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    if not rating or not comment:
        flash("Please provide both a rating and a comment.", "error")
        return redirect(url_for('restaurant_detail', business_id=business_id))
    try:
        rating = float(rating)
        if not 1 <= rating <= 5:
            flash("Rating must be between 1 and 5", "error")
            return redirect(url_for('restaurant_detail', business_id=business_id))
        review_id = str(uuid.uuid4())
        review_data = {
            'user_id': session['user']['localId'],
            'user_name': session.get('name', 'Anonymous User'),
            'user_email': session['user'].get('email', 'No email'),
            'business_id': business_id,
            'rating': rating,
            'comment': comment,
            'timestamp': datetime.now().isoformat()
        }
        reviews_ref = db.reference(f'reviews/{business_id}/{review_id}')
        reviews_ref.set(review_data)
        flash("Review added successfully!", "success")
    except ValueError:
        flash("Invalid rating value", "error")
    except Exception as e:
        print("Error adding review:", e)
        flash("Error adding review. Please try again.", "error")
    return redirect(url_for('restaurant_detail', business_id=business_id))

# =========================
# Wishlist Page
# =========================
@app.route('/wishlist')
@login_required
def wishlist():
    user_id = session['user']['localId']
    user_ref = db.reference(f'users/{user_id}/wishlist')
    wishlist_items = user_ref.get() or []
    restaurants = []
    for business_id in wishlist_items:
        try:
            response = requests.get(f'https://api.yelp.com/v3/businesses/{business_id}',
                                   headers={'Authorization': f'Bearer {YELP_API_KEY}'})
            if response.status_code == 200:
                restaurants.append(response.json())
            else:
                print(f"Error fetching restaurant {business_id}: Status {response.status_code}, Response: {response.text}")
        except Exception as e:
            print(f"Error fetching restaurant {business_id}: {str(e)}")
            continue
    return render_template('wishlist.html', restaurants=restaurants)

# =========================
# Add to Wishlist
# =========================
@app.route('/add_to_wishlist/<business_id>')
@login_required
def add_to_wishlist(business_id):
    if 'user' not in session:
        flash('Please log in to add to wishlist.', 'error')
        return redirect(url_for('login'))
    user_ref = db.reference(f'users/{session["user"]["localId"]}/wishlist')
    current_wishlist = user_ref.get() or []
    if business_id not in current_wishlist:
        current_wishlist.append(business_id)
        user_ref.set(current_wishlist)
        flash('Restaurant added to wishlist!', 'success')
    else:
        flash('Restaurant is already in your wishlist.', 'info')
    return redirect(request.referrer or url_for('index'))

# =========================
# Remove from Wishlist
# =========================
@app.route('/remove_from_wishlist/<business_id>')
@login_required
def remove_from_wishlist(business_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    user_ref = db.reference(f'users/{session["user"]["localId"]}/wishlist')
    current_wishlist = user_ref.get() or []
    if business_id in current_wishlist:
        current_wishlist.remove(business_id)
        user_ref.set(current_wishlist)
        flash('Restaurant removed from wishlist.', 'success')
    return redirect(url_for('wishlist'))

# =========================
# Yelp Autocomplete API Endpoint
# =========================
@app.route('/api/autocomplete')
def autocomplete():
    term = request.args.get('term', '')
    location = request.args.get('location', '')
    if not term or not location:
        return jsonify([])
    headers = {'Authorization': f'Bearer {YELP_API_KEY}'}
    params = {
        'text': term,
        'latitude': location.split(',')[0] if ',' in location else None,
        'longitude': location.split(',')[1] if ',' in location else None,
        'limit': 5
    }
    try:
        response = requests.get('https://api.yelp.com/v3/autocomplete', headers=headers, params=params)
        response.raise_for_status()
        return jsonify(response.json().get('terms', []))
    except Exception as e:
        print("Autocomplete Error:", e)
        return jsonify([])

# =========================
# Debug: Yelp API Test Endpoint
# =========================
@app.route('/debug/api-test')
def debug_api_test():
    if not app.debug:
        return "Debug routes only available in debug mode", 403
    results = {
        'api_key_set': bool(YELP_API_KEY),
        'api_key_length': len(YELP_API_KEY) if YELP_API_KEY else 0,
        'endpoint': YELP_ENDPOINT,
    }
    try:
        search_params = {
            'term': 'coffee',
            'location': 'San Francisco',
            'limit': 1
        }
        search_response = requests.get(f'{YELP_ENDPOINT}/search',
                                      headers=HEADERS,
                                      params=search_params)
        results['search_status'] = search_response.status_code
        results['search_response'] = search_response.json() if search_response.status_code == 200 else search_response.text
        if search_response.status_code == 200 and search_response.json().get('businesses'):
            business_id = search_response.json()['businesses'][0]['id']
            results['test_business_id'] = business_id
            business_response = requests.get(f'{YELP_ENDPOINT}/{business_id}', headers=HEADERS)
            results['business_status'] = business_response.status_code
            results['business_response'] = business_response.json() if business_response.status_code == 200 else business_response.text
    except Exception as e:
        results['error'] = str(e)
    return jsonify(results)

# =========================
# Debug: Firebase Auth Test Endpoint
# =========================
@app.route('/debug/auth-test', methods=['GET'])
def debug_auth_test():
    if not app.debug:
        return "Debug routes only available in debug mode", 403
    results = {
        'firebase_config': {k: '***' if k in ['apiKey', 'appId'] else v for k, v in firebase_config.items()},
        'auth_initialized': auth is not None,
        'admin_initialized': firebase_admin._apps is not None and len(firebase_admin._apps) > 0
    }
    test_email = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
    test_password = "Test123456!"
    try:
        user = auth.create_user_with_email_and_password(test_email, test_password)
        results['user_creation'] = 'success'
        results['user_id'] = user.get('localId')
        login = auth.sign_in_with_email_and_password(test_email, test_password)
        results['login'] = 'success'
        try:
            user_ref = db.reference(f'users/{user["localId"]}')
            user_ref.set({
                'name': 'Test User',
                'email': test_email,
                'test': True
            })
            results['database_write'] = 'success'
            user_data = user_ref.get()
            results['database_read'] = 'success'
            results['user_data'] = user_data
            user_ref.delete()
            results['database_delete'] = 'success'
        except Exception as db_error:
            results['database_error'] = str(db_error)
    except Exception as auth_error:
        results['auth_error'] = str(auth_error)
    return jsonify(results)

# =========================
# Debug: Firebase Config Check Endpoint
# =========================
@app.route('/debug/firebase-config')
def debug_firebase_config():
    if not app.debug:
        return "Debug routes only available in debug mode", 403
    required_keys = ['apiKey', 'authDomain', 'databaseURL', 'projectId', 'storageBucket', 'messagingSenderId', 'appId']
    missing_keys = [key for key in required_keys if not firebase_config.get(key)]
    cred_file_exists = os.path.exists("dinner-7744a-firebase-adminsdk-fbsvc-4214593bae.json")
    try:
        firebase_config = {
            "apiKey": os.getenv('FIREBASE_API_KEY'),
            "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
            "databaseURL": os.getenv('FIREBASE_DATABASE_URL'),
            "projectId": os.getenv('FIREBASE_PROJECT_ID'),
            "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
            "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
            "appId": os.getenv('FIREBASE_APP_ID')
        }
        if not all(firebase_config.values()):
            raise ValueError("One or more Firebase configuration environment variables are missing.")
        firebase = pyrebase.initialize_app(firebase_config)
        auth = firebase.auth()
        print("✅ Firebase client initialized successfully from environment variables")
    except Exception as e:
        print(f"❌ Firebase client (Pyrebase) initialization error: {str(e)}")
        firebase = None
        auth = None
    masked_config = {k: ('***' if k in ['apiKey', 'appId'] else v) for k, v in firebase_config.items()}
    masked_env_vars = {k: ('***' if v and 'API_KEY' in k or 'APP_ID' in k else v) for k, v in os.environ.items()}
    return jsonify({
        'firebase_config': masked_config,
        'missing_config_keys': missing_keys,
        'credential_file_exists': cred_file_exists,
        'environment_variables': masked_env_vars,
        'firebase_initialized': auth is not None,
        'firebase_admin_initialized': firebase_admin._apps is not None and len(firebase_admin._apps) > 0
    })

# =========================
# Debug: Test Yelp API Endpoint
# =========================
@app.route('/test-yelp-api/<business_id>')
def test_yelp_api(business_id):
    if not app.debug:
        return "This route is only available in debug mode", 403
    results = {
        'api_key_set': bool(YELP_API_KEY),
        'api_key_length': len(YELP_API_KEY) if YELP_API_KEY else 0,
        'endpoint': YELP_ENDPOINT,
    }
    headers = {'Authorization': f'Bearer {YELP_API_KEY}'}
    try:
        business_response = requests.get(f'{YELP_ENDPOINT}/{business_id}', headers=headers)
        results['business_status'] = business_response.status_code
        if business_response.status_code == 200:
            results['business_data'] = {
                'name': business_response.json().get('name'),
                'rating': business_response.json().get('rating'),
                'review_count': business_response.json().get('review_count')
            }
        else:
            results['business_error'] = business_response.text
        reviews_response = requests.get(f'{YELP_ENDPOINT}/{business_id}/reviews', headers=headers)
        results['reviews_status'] = reviews_response.status_code
        if reviews_response.status_code == 200:
            results['reviews_count'] = len(reviews_response.json().get('reviews', []))
        else:
            results['reviews_error'] = reviews_response.text
    except Exception as e:
        results['error'] = str(e)
    return jsonify(results)

# =========================
# Debug: Firebase Admin Check Endpoint
# =========================
@app.route('/check-firebase')
def check_firebase():
    if not app.debug:
        return "This route is only available in debug mode", 403
    results = {
        'firebase_admin_imported': 'firebase_admin' in sys.modules,
        'db_imported': 'db' in dir(),
    }
    if 'firebase_admin' in sys.modules:
        results['firebase_admin_apps'] = len(firebase_admin._apps)
        try:
            test_ref = db.reference('test')
            test_ref.set({'timestamp': datetime.now().isoformat()})
            test_data = test_ref.get()
            results['firebase_write_read'] = 'success'
            results['test_data'] = test_data
            test_ref.delete()
        except Exception as e:
            results['firebase_error'] = str(e)
    return jsonify(results)

# =========================
# Debug: Template Render Test Endpoint
# =========================
@app.route('/debug/template-test')
def debug_template_test():
    if not app.debug:
        return "Debug routes only available in debug mode", 403
    test_restaurant = {
        'id': 'test-id',
        'name': 'Test Restaurant',
        'image_url': None,
        'rating': 4.5,
        'review_count': 100,
        'price': '$$',
        'location': {'display_address': ['123 Test St', 'Test City, TS 12345']},
        'display_phone': '(555) 555-5555',
        'categories': [{'title': 'Test Cuisine'}]
    }
    try:
        rendered = render_template('restaurant_detail.html',
                                  restaurant=test_restaurant,
                                  yelp_reviews=[],
                                  user_reviews=[])
        return "Template rendered successfully!"
    except Exception as e:
        return f"Template error: {str(e)}", 500

# =========================
# Error Handlers
# =========================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500, message="Server error"), 500

@app.errorhandler(jinja2.exceptions.TemplateSyntaxError)
def template_syntax_error(e):
    return render_template('error.html',
                          error_code=500,
                          message=f"Template syntax error: {str(e)}"), 500

# =========================
# Main Entrypoint
# =========================
if __name__ == '__main__':
    app.run(debug=True, port=5002)