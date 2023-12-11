import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account.
cred = credentials.Certificate('firestore-key.json')

app = firebase_admin.initialize_app(cred)

db = firestore.client()

def delete_event(event_id: str):
	db.collection("Events").document(event_id).delete()