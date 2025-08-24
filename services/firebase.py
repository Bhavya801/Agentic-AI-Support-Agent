import firebase_admin
from firebase_admin import credentials, firestore
import os

class FirebaseService:
    def __init__(self):
        """
        Initializes the Firebase app using service account credentials from a file.
        """
        try:
            # Check if an app is already initialized to avoid re-initialization
            if not firebase_admin._apps:
                firebase_config_path = os.getenv("FIREBASE_CONFIG_PATH")
                if not firebase_config_path or not os.path.exists(firebase_config_path):
                    raise FileNotFoundError(f"Firebase config file not found at: {firebase_config_path}")
                
                cred = credentials.Certificate(firebase_config_path)
                firebase_admin.initialize_app(cred)
            
            print("Firebase app initialized successfully.")
            self.db = firestore.client()
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            self.db = None

    def add_ticket(self, ticket_data):
        """
        Adds a new support ticket document to the 'support_tickets' collection.
        """
        if not self.db:
            print("Database not connected. Cannot add ticket.")
            return

        try:
            doc_ref = self.db.collection("support_tickets").add(ticket_data)
            print(f"Logged to Firestore with ID: {doc_ref[1].id}")
        except Exception as e:
            print(f"Error logging to Firestore: {e}")

