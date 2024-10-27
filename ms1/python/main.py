from email import encoders
from email.mime.multipart import MIMEMultipart
import json
from urllib.parse import urlencode
from flask import Flask, render_template, request, jsonify, url_for, flash, redirect, session, send_file, send_from_directory
from flask_pymongo import PyMongo
# from flask_session import Session
import hashlib, os, smtplib, string, random, urllib
from email.mime.text import MIMEText
from email.message import EmailMessage


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://tim.cse356.compas.cs.stonybrook.edu:27017/Warmup2"
app.secret_key = "secret"
# app.config["SESSION_TYPE"] = "filesystem"
# app.config["SESSION_PERMANENT"] = True  # Set to True for sessions to persist
# app.config["SESSION_USE_SIGNER"] = True  # Sign cookies to prevent tampering
# app.config["SESSION_FILE_DIR"] = "./flask_session/"  # Directory to store session files
# app.config["SESSION_FILE_THRESHOLD"] = 100  # Max number of session files to keep
# Session(app)

db = PyMongo(app).db
users = db.users

def is_authenticated():
    if 'username' in session:
        return True
    else:
        return False

# List of public endpoints
public_endpoints = set([
    'add_user',
    'temp_add_user',
    'verify_email',
    'login',
    'logout',
    'get_session',  # Add your public endpoint names here
    # Add more public endpoints as needed
])

# @app.before_request
def require_login():
    # Check if the requested endpoint is not in the public endpoints
    if request.endpoint not in public_endpoints and not is_authenticated():
        return ret_json(1, f"User not logged in. Go to /login")

def generate_verification_key():
    # characters = string.ascii_letters + string.digits  # Letters (both uppercase and lowercase) and digits
    # return ''.join(random.choice(characters) for _ in range(64))
    return "abc123"

video_files = "static/videos/m1.json"
with open(video_files, 'r') as file:
    data = json.load(file)
# video_ids = [id for id,description in data]

@app.route("/", methods=['GET'])
def hello_world():
    return render_template('index.html', videos=data)
    
    
@app.route("/media/<path:filename>")
def serve_media(filename):
    return send_file(f"p/{filename}", as_attachment=True)
    
@app.route("/media/output.mpd", methods=['POST', 'GET'])#Trying to get this to play the video instead of downloading it. Not working.
def output():
    # Define the directory where the media files are located
    # media_directory = '/usr/share/nginx/html/media'
    
    # Ensure the file exists in the media directory
    return send_file("p/output.mpd", as_attachment=True)

@app.route('/api/adduser', methods=['POST', 'GET'])
def add_user():
    if request.method == 'POST':
        # Get form data
        data = request.json
        name = data.get('username')  # Get 'username' from JSON
        password = data.get('password')  # Get 'email' from JSON
        email = data.get('email')  # Get 'email' from JSON

        # name = request.form.get('username')
        # password = request.form.get('password')
        # email = request.form.get('email')

        # password = hashlib.sha256(password.encode()).hexdigest()

        # Create a disabled user
        verification_key = generate_verification_key()
        # Create a user document
        user = {
            "username": name,
            "password": password,
            "email": email,
            "disabled": True,
            "verification_key": verification_key
        }
        print("adding user")

        found_name = users.find_one({'username': name})
        found_email = users.find_one({'email': email})
        
        if (found_name or found_email):
            print("duplicate user")
            return ret_json(1, "Duplicate name or email")
        
        # Insert the document into the users collection
        try:
            users.insert_one(user)
            print("inserted user", user)
            # urllib.parse.quote(email)
            # urllib.parse.quote(verification_key)
            verification_link = f"http://tim.cse356.compas.cs.stonybrook.edu/verify?email={email}&key={verification_key}"
            print(verification_link)
            # Send the verification email (Here you would integrate your mail server logic)
            send_verification_email(email, verification_link)
            return ret_json(0, "User added! Please verify with url that was sent to email. {verification_link}")
        except Exception as e:
            return ret_json(1, "An error occured adding user to database")

@app.route('/api/tempadduser', methods=['POST', 'GET'])
def temp_add_user():
    if request.method == 'POST':
        # Get form data
        # data = request.json
        # name = data.get('username')  # Get 'username' from JSON
        # password = data.get('password')  # Get 'email' from JSON
        # email = data.get('email')  # Get 'email' from JSON
        print(request.form)

        name = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # password = hashlib.sha256(password.encode()).hexdigest()

        # Create a disabled user
        verification_key = generate_verification_key()
        # Create a user document
        user = {
            "username": name,
            "password": password,
            "email": email,
            "disabled": True,
            "verification_key": verification_key
        }

        found_name = users.find_one({'username': name})
        found_email = users.find_one({'email': email})
        
        if (found_name or found_email):
            return ret_json(1, "Duplicate name or email")
        
        # Insert the document into the users collection
        try:
            users.insert_one(user)

            verification_link = f"http://tim.cse356.compas.cs.stonybrook.edu/api/verify?email={email}&key={verification_key}"
            print(verification_link)
            # Send the verification email (Here you would integrate your mail server logic)
            send_verification_email(email, verification_link)
            return ret_json(0, f"User added! Please verify with url that was sent to email. {verification_link}")
        except Exception as e:
            return ret_json(1, "An error occured adding user to database")
    else:
        return render_template('adduser.html')

@app.route('/api/verify', methods=['GET'])
def verify_email():
    email = request.args.get('email')
    key = request.args.get('key')
    # if "key" in request.url:
    #     user = users.find_one({'email': email})
    print(f"Received email: {email}, key: {key}")
    email = email.replace(" ", "+")
    print(f"Received email: {email}, key: {key}")
    print(f"URL is: {request.url}")
    user = users.find_one({'email': email})
    if user is None:
        return ret_json(1, "User not found")
    if user['verification_key'] != key:
        # Convert data to JSON with no spaces
        json_data = json.dumps({"status": "ERROR","error":True,"message":"Invalid key"}, separators=(',', ':'))

        # Manually add spaces only for the "status" key
        formatted_json = json_data.replace('"status":"ERROR"', '"status": "ERROR"')
        return formatted_json
    # Find the user by email
    print(user)
    if user:
        # Check if the key matches and the user is disabled
        if user['disabled']:
            # Update the user to mark them as verified
            users.update_one({'email': email}, {'$set': {'disabled': False}})
            return json.dumps({"status":"OK"}, separators=(',', ':'))
        else:
            return ret_json(1, "User already verified or verification key doesn't work")
    else:
        return ret_json(1, "User not found")
    

def send_verification_email(email, link):
    print(link)
    msg = EmailMessage()
    msg.set_content(link)
    msg['Subject'] = 'Verify your account'
    msg['From'] = 'no-reply@tim.cse356.compas.cs.stonybrook.edu'
    msg['To'] = email
    print(msg.as_string())
    with smtplib.SMTP('localhost', 587) as server:
        server.send_message(msg)

@app.route('/api/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')  # Get 'username' from JSON
        password = data.get('password')  # Get 'email' from JSON
        # username = request.form.get('username')
        # password = request.form.get('password')
        
        user = users.find_one({'username': username})
        print("login")
        if user is None:
            print(username)
            return ret_json(1, "User not created")
        if user['disabled']:
            print("disable", user)
            return ret_json(1, "User not yet verified.")
        
        print("logged in" , user)

        # Replace with your user validation logic
        if user['username'] == username and user['password'] == password:
            session['username'] = username
            return json.dumps({"status":"OK"}, separators=(',', ':'))
        else:
            return ret_json(1, "Wrong username or password. Try a different one")
    else:
        return render_template('login.html')
    
@app.route('/api/tlogin', methods=['POST', 'GET'])
def tlogin():
    if request.method == 'POST':
        # data = request.json
        # username = data.get('username')  # Get 'username' from JSON
        # password = data.get('password')  # Get 'email' from JSON
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = users.find_one({'username': username})
        print("login")
        if user is None:
            print(username)
            return ret_json(1, "User not created")
        if user['disabled']:
            print("disable", user)
            return ret_json(1, "User not yet verified.")
        
        print("logged in" , user)

        # Replace with your user validation logic
        if user['username'] == username and user['password'] == password:
            session['username'] = username
            return json.dumps({"status":"OK"}, separators=(',', ':'))
        else:
            return ret_json(1, "Wrong username or password. Try a different one")
    else:
        return render_template('login.html')

@app.route('/api/logout', methods=['POST', 'GET'])
def logout():
    session.clear()  # Remove username from session
    return ret_json(0, "Logged out successfully.")

@app.route('/api/check-auth', methods=['POST'])
def get_session():
    if 'username' in session:
        return jsonify({"isLoggedIn": True, "userID": session['username']}), 200
    else:
        return jsonify({"error": "Not logged in"}), 401

@app.route('/api/thumbnail/<id>', methods=['GET'])
def get_thumbnail(id):
    thumbnail_path = os.path.join("static/thumbnails/", f"{os.path.splitext(id)[0]}.jpg")
    # Send the thumbnail as a response
    if os.path.exists(thumbnail_path):
        return send_file(thumbnail_path, mimetype='image/jpg')
    else:
        return ret_json(1, f"Current working directory:, {thumbnail_path})")

def ret_json(status:int, message:str):#has to have /output.md return error
    if status:
        return jsonify({"status": "ERROR", "error":True, "message": f"{message}"}), 200
    else:
        return jsonify({"status": "OK", "error":False, "message": f"{message}"}), 200
    
    # if status:
    #     return json.dumps({"status":"ERROR", "error":True, "message": f"{message}"}, separators=(',', ':'))
    # else:
    #     return json.dumps({"status": "OK", "error":False, "message": f"{message}"}, separators=(',', ':'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)