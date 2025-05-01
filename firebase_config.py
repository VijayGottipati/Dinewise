import os
import pyrebase
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Firebase configuration
firebase_config = {
    "apiKey": os.getenv('FIREBASE_API_KEY'),
    "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
    "projectId": os.getenv('FIREBASE_PROJECT_ID'),
    "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
    "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
    "appId": os.getenv('FIREBASE_APP_ID'),
    "databaseURL": os.getenv('FIREBASE_DATABASE_URL')
}

# Initialize Firebase Admin SDK
cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', "dinewise-1ade0-firebase-adminsdk-fbsvc-826e342dd1.json")
try:
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
        })
    else:
        print(f"WARNING: Firebase credentials file not found at {cred_path}")
except ValueError:
    # App already initialized
    pass
except Exception as e:
    print(f"Firebase Admin SDK initialization error: {e}")

# Initialize Pyrebase for authentication
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# Export the database reference
db = firebase_admin.db

