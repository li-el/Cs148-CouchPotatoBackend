
from pyrebase import pyrebase
config = {
  "apiKey": "AIzaSyCfagUCrWOtW1ulQ7IDwAStna25htiV950",
  "authDomain":  "cs148-couch-potato.firebaseapp.com",
  "databaseURL": "https://cs148-couch-potato.firebaseio.com",
  "storageBucket": "cs148-couch-potato.appspot.com",
}
firebase = pyrebase.initialize_app(config)
try:
    auth = firebase.auth()
    user = auth.create_user_with_email_and_password("li-el@ucsb.edu", "password")
    print("succ")
except Exception as e:
    print(e)
