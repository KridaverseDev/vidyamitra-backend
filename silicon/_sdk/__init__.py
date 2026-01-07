import json

import firebase_admin
from django.conf import settings
from firebase_admin import auth, credentials

# load firebase credentials

with open(settings.FIREBASE_CRED_PATH, "r") as read_file:
    cred = credentials.Certificate(json.load(read_file))
default_app = firebase_admin.initialize_app(cred)
