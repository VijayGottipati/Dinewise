# DineWise: Restaurant Discovery & Review Platform

DineWise is a Flask-based web application that helps users discover restaurants, view details and reviews, and manage wishlists. It integrates with the Yelp API for restaurant data and Google Maps for location features. User authentication and data storage are handled via Firebase.

## Demo Video
Video Link - https://drive.google.com/file/d/1A1PCicaIyDGobH43OVXhhr8vMG_zRtbV/view?usp=sharing

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
   git clone https://github.com/VijayGottipati/Dinewise.git
   cd Dinewise
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
     FLASK_APP=app.py
     FLASK_ENV=development
     YELP_API_KEY=your_yelp_api_key
     GOOGLE_MAPS_API_KEY=your_google_maps_api_key
     FIREBASE_API_KEY=your_firebase_api_key
     FIREBASE_AUTH_DOMAIN=your_firebase_auth_domain
     FIREBASE_DATABASE_URL=your_firebase_database_url
     FIREBASE_PROJECT_ID=your_firebase_project_id
     FIREBASE_STORAGE_BUCKET=your_firebase_storage_bucket
     FIREBASE_MESSAGING_SENDER_ID=your_firebase_messaging_sender_id
     FIREBASE_APP_ID=your_firebase_app_id
     FIREBASE_CREDENTIALS_PATH=dinewise-1ade0-firebase-adminsdk-fbsvc-826e342dd1.json
     ```

5. **Add Firebase config files:**

   The app requires two Firebase configuration files in the project root:

   - `firebase_config.json` – Pyrebase client configuration for authentication and database access.
   - `dinewise-1ade0-firebase-adminsdk-fbsvc-826e342dd1.json` – Firebase Admin SDK service account credentials for server-side access.

   **These files are sensitive and are NOT included in the repository. You must generate and add them yourself.**

   ### How to Obtain the JSON Files

   - **firebase_config.json**
     - Go to the [Firebase Console](https://console.firebase.google.com/) and select your project.
     - Click the gear icon next to **Project Overview** and choose **Project settings**.
     - In the **General** tab, scroll to the **Your apps** section.
     - Select your registered web app, or register a new one if needed.
     - Under **SDK setup and configuration**, choose the **Config** option.
     - Copy the configuration snippet (it looks like a JavaScript object).
     - Paste it into a text editor, format it as JSON (with double quotes), and save it as `firebase_config.json` in your project root.

   - **dinewise-1ade0-firebase-adminsdk-fbsvc-826e342dd1.json**
     - In the Firebase Console, go to **Project settings** > **Service Accounts**.
     - Click **Generate new private key** and confirm.
     - This will download a JSON file (named like `dinewise-1ade0-firebase-adminsdk-xxxx.json`).
     - Move or rename this file to `dinewise-1ade0-firebase-adminsdk-fbsvc-826e342dd1.json` if needed, and place it in your project root.

   > **Note:** If you are a collaborator, request these files from the project owner or be added to the Firebase project to generate your own.

6. **Initialize the Firebase database (optional):**
   ```
   python init_db.py
   ```

7. **Run the Flask app:**
   ```
   python app.py
   ```
   The app will start on `http://localhost:5002`.

---

## Usage

- Register a new account or log in.
- Search for restaurants by location, cuisine, or price.
- Search for restaurants near your current location.
- View restaurant details, including Yelp and user reviews.
- Add restaurants to your wishlist or remove them.
- Submit your own reviews for restaurants, which are stored and displayed.
- Click on directions to view the location of the restaurant in Google Maps.

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

---

## Citations:
```
[1] https://firebase.google.com/docs/studio/get-started-template
[2] https://firebase.google.com/docs/firestore/best-practices
[3] https://firebase.google.com/docs/samples
[4] https://docs.readme.com/main/docs/python-flask-api-metrics
[5] https://firebase.google.com/docs/projects/dev-workflows/general-best-practices
[6] https://developers.google.com/maps/documentation/places/web-service/web-services-best-practices
[7] https://stackoverflow.com/questions/72093172/how-to-display-a-google-map-in-flask-django
[8] https://stackoverflow.com/questions/41149079/working-with-yelp-api-and-or-google-places-api
```
