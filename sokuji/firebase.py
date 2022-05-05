from typing import Optional
import os
import json
import firebase_admin
from firebase_admin import db, credentials

REFERENCE: Optional[db.Reference] = None


def connect_reference():
    global REFERENCE
    if not firebase_admin._apps:
        key = os.environ['FIREBASE_KEY']
        cred = credentials.Certificate(json.loads(key, strict=False))
        firebase_admin.initialize_app(cred, {'databaseURL': 'https://mksokuji-default-rtdb.firebaseio.com/'})
    REFERENCE = db.reference('user')
    return


def update(data: dict):
    if REFERENCE is None:
        connect_reference()
    try:
        REFERENCE.update(data)
    except:
        connect_reference()
        REFERENCE.update(data)
