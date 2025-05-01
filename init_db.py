from firebase_config import db

def initialize_database():
    # Create root nodes if they don't exist
    collections = ['users', 'reviews', 'wishlists']
    
    for collection in collections:
        # Just try to create a dummy entry to ensure the node exists
        try:
            ref = db.reference(collection)
            ref.child('init').set({'initialized': True})
            ref.child('init').delete()  # Remove the dummy entry
        except Exception as e:
            print(f"Error initializing {collection}: {e}")

    # Create indexes for reviews (in Realtime Database, this is just a convention)
    try:
        db.reference('reviews/indexes').set({
            'business_id_index': True
        })
    except Exception as e:
        print(f"Error creating indexes: {e}")

    print("Database initialization complete!")

if __name__ == "__main__":
    initialize_database() 

