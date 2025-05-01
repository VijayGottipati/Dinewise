# DineWise: Restaurant Discovery & Review Platform

DineWise is a Flask-based web application that helps users discover restaurants, view details and reviews, and manage wishlists. It integrates with the Yelp API for restaurant data and Google Maps for location features. User authentication and data storage are handled via Firebase.

---

## Features

- User registration and login with Firebase authentication
- Restaurant search by location, cuisine, and price (Yelp API)
- Restaurant search by current location
- Restaurant detail pages with Yelp and user reviews
- Add, view, and remove restaurants from wishlists
- Submit and display user reviews and ratings  
- Google Maps integration for restaurant locations
- Admin/debug endpoints for API and Firebase checks

---

## Project Structure

```
.
├── templates/              # Jinja2 HTML templates
├── static/                 # Static files (CSS, JS, images)
├── .env                    # Environment variables (excluded from git)
├── .gitignore
├── app.py                  # Main Flask application
├── dinewise-1ade0-firebase-adminsdk-fbsvc-826e342dd1.json  # Firebase Admin SDK credentials (excluded from git)
├── firebase_config.json    # Pyrebase client config (excluded from git)
├── firebase_config.py      # Firebase configuration and initialization
├── init_db.py              # Script to initialize Firebase database structure
├── README.md               # Info on Project
└── requirements.txt        # Python dependencies

```

---

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone 
   cd 
   ```

2. **Create and activate a virtual environment:**
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Create a `.env` file in the project root with the following keys:
     ```
     FLASK_SECRET_KEY=your_secret_key
     YELP_API_KEY=your_yelp_api_key
     GOOGLE_MAPS_API_KEY=your_google_maps_api_key
     FIREBASE_API_KEY=...
     FIREBASE_AUTH_DOMAIN=...
     FIREBASE_DATABASE_URL=...
     FIREBASE_PROJECT_ID=...
     FIREBASE_STORAGE_BUCKET=...
     FIREBASE_MESSAGING_SENDER_ID=...
     FIREBASE_APP_ID=...
     FIREBASE_CREDENTIALS_PATH=dinewise-1ade0-firebase-adminsdk-fbsvc-826e342dd1.json
     ```

5. **Add Firebase config files:**
   - Place `firebase_config.json` and `dinewise-1ade0-firebase-adminsdk-fbsvc-826e342dd1.json` in the project root. These files contain sensitive keys and are excluded from git for security.

6. **Initialize the Firebase database (optional):**
   ```
   python init_db.py
   ```

7. **Run the Flask app:**
   ```
   python app.py
   ```
   The app will start on `http://localhost:5001`.

---

## Usage

- Register a new account or log in.
- Search for restaurants by location, cuisine, or price.
- View restaurant details, including Yelp and user reviews.
- Add restaurants to your wishlist or remove them.
- Submit your own reviews for restaurants which is stored and displayed.
- Click on directions to view the location of the restaurant in GOogle map.

---

## Notes

- **Security:** Never commit your `.env`, `firebase_config.json`, or Firebase Admin SDK credentials to version control.
- **Debug Routes:** Some `/debug/*` and `/check-firebase` routes are only accessible in debug mode.
- **Dependencies:** See `requirements.txt` for all required Python packages.

---

## Contributors
1. Manish Kumbham
2. Nirbhaya Reddy G
3. Theodore Hua
4. Vijay Gotipati