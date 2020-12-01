# myapp.py
''' 
    This file is based off of this tutorial: https://stackabuse.com/deploying-a-flask-application-to-heroku/ 
    Author: Chandra Krintz, 
    License: UCSB BSD -- see LICENSE file in this repository
'''

import os, json
from flask import Flask, request, jsonify, make_response, session
from pyrebase import pyrebase
#use this if linking to a reaact app on the same server
#app = Flask(__name__, static_folder='./build', static_url_path='/')
app = Flask(__name__)
DEBUG=True

config = {
  "apiKey": "AIzaSyCfagUCrWOtW1ulQ7IDwAStna25htiV950",
  "authDomain":  "cs148-couch-potato.firebaseapp.com",
  "databaseURL": "https://cs148-couch-potato.firebaseio.com",
  "storageBucket": "cs148-couch-potato.appspot.com",
}
firebase = pyrebase.initialize_app(config)
### CORS section
@app.after_request
def after_request_func(response):
    if DEBUG:
        print("in after_request")
    origin = request.headers.get('Origin')
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Headers', 'x-csrf-token')
        response.headers.add('Access-Control-Allow-Methods',
                            'GET, POST, OPTIONS, PUT, PATCH, DELETE')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)

    return response
### end CORS section

'''
Note that flask automatically redirects routes without a final slash (/) to one with a final slash (e.g. /getmsg redirects to /getmsg/). Curl does not handle redirects but instead prints the updated url. The browser handles redirects (i.e. takes them). You should always code your routes with both a start/end slash.
'''
@app.route('/api/getmsg/', methods=['GET'])
def respond():
    # Retrieve the msg from url parameter of GET request 
    # and return MESSAGE response (or error or success)
    msg = request.args.get("msg", None)

    if DEBUG:
        print("GET respond() msg: {}".format(msg))

    response = {}
    if not msg: #invalid/missing message
        response["MESSAGE"] = "no msg key found, please send a msg."
        status = 400
    else: #valid message
        response["MESSAGE"] = f"Welcome {msg}!"
        status = 200
        database = firebase.database()
        data = {"name": "Mortimer 'Morty' Smith"}
        database.push(data)

    # Return the response in json format with status code
    return jsonify(response), status

@app.route('/api/login/', methods=['POST'])
def login():
    response = {}
    #only accept json content type
    if request.headers['content-type'] != 'application/json':
        return jsonify({"MESSAGE": "invalid content-type"}),400
    else:
        try:
            data = json.loads(request.data)
        except ValueError:
            return jsonify({"MESSAGE": "JSON load error"}),405
    email = data['email']
    password = data['password']
    if email and password:
        try:
            auth = firebase.auth()
            user = auth.sign_in_with_email_and_password(email, password)
            response['USER'] = user['localId']
            response["MESSAGE"]= "Login Succesful"
            status = 200
        except Exception as e:
            status = 400
            try:
                response["MESSAGE"] = str(json.loads(e.args[1])['error']['message'])
            except:
                response["MESSAGE"] = "There was an error signing in" 
    else:
        status = 400
        response["MESSAGE"]= "Incorrect Username or Password"
    return jsonify(response), status



@app.route('/api/saveroom/', methods=['POST'])
def saveRoom():
    try:
        response = {}
        #only accept json content type
        if request.headers['content-type'] != 'application/json':
            return jsonify({"MESSAGE": "invalid content-type"}),400
        else:
            try:
                data = json.loads(request.data)
            except ValueError:
                return jsonify({"MESSAGE": "JSON load error"}),405
        room = data['room']
        user = data['user']
        key = data['roomkey']
        if room:
            try:
                db = firebase.database()
                db.child(user).child(key).set(room)
                #db.push(room)
                response["MESSAGE"]= "Room Successfully saved"
                status = 200
            except Exception as e:
                status = 400
                try:
                    response["MESSAGE"] = str(json.loads(e.args[1])['error']['message'])
                except:
                    response["MESSAGE"] = str(e)
        else:
            status = 400
            response["MESSAGE"]= "Invalid Room Object"
    except Exception as e:
        status = 400
        response["MESSAGE"] = "There was an error somewhere"
        return jsonify(response), status
    return jsonify(response), status

@app.route('/api/roomname/', methods=['POST'])
def roomName():
    try:
        response = {}
        #only accept json content type
        if request.headers['content-type'] != 'application/json':
            return jsonify({"MESSAGE": "invalid content-type"}),400
        else:
            try:
                data = json.loads(request.data)
            except ValueError:
                return jsonify({"MESSAGE": "JSON load error"}),405
        user = data['user']
        key = data['roomkeys']
        if key and user:
            try:
                db = firebase.database()
                for name in key:
                    response["NAME"].append(db.child(user).child(name)["name"])
                #db.push(room)
                response["MESSAGE"]= "Room Successfully saved"
                status = 200
            except Exception as e:
                status = 400
                try:
                    response["MESSAGE"] = str(json.loads(e.args[1])['error']['message'])
                except:
                    response["MESSAGE"] = str(e)
        else:
            status = 400
            response["MESSAGE"]= "Invalid User or Room"
    except Exception as e:
        status = 400
        response["MESSAGE"] = "There was an error somewhere"
        return jsonify(response), status
    return jsonify(response), status


@app.route('/api/listrooms/', methods=['POST'])
def listRooms():
    try:
        response = {}
        #only accept json content type
        if request.headers['content-type'] != 'application/json':
            return jsonify({"MESSAGE": "invalid content-type"}),400
        else:
            try:
                data = json.loads(request.data)
            except ValueError:
                return jsonify({"MESSAGE": "JSON load error"}),405
        user = data['user']
        if user:
            try:
                db = firebase.database()
                lists = db.child(user).get()
                response["LIST"] = []
                response["NAME"] = []
                for room in lists.each():
                    response["LIST"].append(room.key())
                    response["NAME"].append(room.val())
                response["MESSAGE"]= "List of Room Keys returned"
                status = 200
            except Exception as e:
                status = 400
                try:
                    response["MESSAGE"] = str(json.loads(e.args[1])['error']['message'])
                except:
                    response["MESSAGE"] = str(e)
        else:
            status = 400
            response["MESSAGE"]= "Invalid User Id"
    except Exception as e:
        status = 400
        response["MESSAGE"] = "There was an error somewhere"
        return jsonify(response), status
    return jsonify(response), status



@app.route('/api/passRoom/', methods=['POST'])
def passRoom():

    response = {}
    #only accept json content type
    if request.headers['content-type'] != 'application/json':
        return jsonify({"MESSAGE": "invalid content-type"}),400
    else:
        try:
            data = json.loads(request.data)
        except ValueError:
            return jsonify({"MESSAGE": "JSON load error"}),405
    room = data['room']
    user = data['user']
    if room:
        try:
            db = firebase.database()
            response["ROOMKEY"] = db.child(user).push(room)["name"]
            #db.push(room)
            response["MESSAGE"]= "Room Successfully saved"
            status = 200
        except Exception as e:
            status = 400
            try:
                response["MESSAGE"] = str(json.loads(e.args[1])['error']['message'])
            except:
                response["MESSAGE"] = str(e)
    else:
        status = 400
        response["MESSAGE"]= "Enter both email and password"
    return jsonify(response), status

@app.route('/api/signup/', methods=['POST'])
def signup():
    
    response = {}
    #only accept json content type
    if request.headers['content-type'] != 'application/json':
        return jsonify({"MESSAGE": "invalid content-type"}),400
    else:
        try:
            data = json.loads(request.data)
        except ValueError:
            return jsonify({"MESSAGE": "JSON load error"}),405
    email = data['email']
    password = data['password']
    if email and password:
        try:
            auth = firebase.auth()
            user = auth.create_user_with_email_and_password(email, password)
            db = firebase.database()
            db.child(user['localId']).set("room")
            response["MESSAGE"]= "Account Created email {} password {}".format(email,password)
            response['USER'] = user['localId']
            status = 200
        except Exception as e:
            status = 400
            try:
                response["MESSAGE"] = str(json.loads(e.args[1])['error']['message'])
            except:
                response["MESSAGE"] = str(e)
    else:
        status = 400
        response["MESSAGE"]= "Enter both email and password"
    return jsonify(response), status



@app.route('/api/keys/', methods=['POST']) 
def postit(): 
    '''
    Implement a POST api for key management.
    Note that flask handles request.method == OPTIONS for us automatically -- and calls after_request_func (above)after each request to satisfy CORS
    '''
    response = {}
    #only accept json content type
    if request.headers['content-type'] != 'application/json':
        return jsonify({"MESSAGE": "invalid content-type"}),400
    else:
        try:
            data = json.loads(request.data)
        except ValueError:
            return jsonify({"MESSAGE": "JSON load error"}),405
    acc = data['acckey']
    sec = data['seckey']
    if DEBUG:
        print("POST: acc={}, sec={}".format(acc,sec))
    if acc:
        response["MESSAGE"]= "Welcome! the POST args are {} and {}".format(acc,sec)
        status = 200
        database = firebase.database()
        data = {"name": "Mortimer 'Morty' Smith"}
        database.push(data)
    else:
        response["MESSAGE"]= "No acckey or seckey keys found, please resend."
        status = 400

    return jsonify(response), status

# Set the base route to be the react index.html
@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>",200

    #use this instead if linking to a raact app on the same server
    #make sure and update the app = Flask(...) line above for the same
    #return app.send_static_file('index.html') 

def main():
    '''The threaded option for concurrent accesses, 0.0.0.0 host says listen to all network interfaces (leaving this off changes this to local (same host) only access, port is the port listened on -- this must be open in your firewall or mapped out if within a Docker container. In Heroku, the heroku runtime sets this value via the PORT environment variable (you are not allowed to hard code it) so set it from this variable and give a default value (8118) for when we execute locally.  Python will tell us if the port is in use.  Start by using a value > 8000 as these are likely to be available.
    '''
    localport = int(os.getenv("PORT", 8118))
    app.run(threaded=True, host='0.0.0.0', port=localport)

if __name__ == '__main__':
    main()
