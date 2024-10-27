from flask import Flask, render_template, request, jsonify, url_for, flash, redirect, session
from flask_pymongo import PyMongo
# from flask_session import Session
import hashlib, os, smtplib
from email.mime.text import MIMEText


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://tsit.cse356.compas.cs.stonybrook.edu:27017/Warmup2"
mongo = PyMongo(app)
db = mongo.db
users = db.users

app.secret_key = "secret"
# app.config["SESSION_TYPE"] = "mongodb"
# app.config["SESSION_MONGODB"] = mongo
# app.config["SESSION_PERMANENT"] = True  # Set to True for sessions to persist
# app.config["SESSION_USE_SIGNER"] = True  # Sign cookies to prevent tampering
# Session(app)


def generate_verification_key():
    return hashlib.sha256(os.urandom(60)).hexdigest()

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route('/adduser', methods=['POST', 'GET'])
def add_user():
    if request.method == 'POST':
        # Get form data
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

        # flash("hello")
        # Insert the document into the users collection
        try:
            users.insert_one(user)

            verification_link = url_for('verify_email', email=email, key=verification_key, _external=True)
            verification_link = f"http://tim.cse356.compas.cs.stonybrook.edu/verify?email={email}&key={verification_key}"
            print(verification_link)
            # Send the verification email (Here you would integrate your mail server logic)
            send_verification_email(email, verification_link)
            return f"User added successfully! {verification_link}"
        except Exception as e:
            return f"An error occurred: {str(e)}"
    else:
        return render_template('index.html')

@app.route('/verify', methods=['GET'])
def verify_email():
    email = request.args.get('email')
    key = request.args.get('key')
    
    # Find the user by email
    user = users.find_one({'email': email})
    
    if user:
        # Check if the key matches and the user is disabled
        if user['verification_key'] == key and user['disabled']:
            # Update the user to mark them as verified
            users.update_one({'email': email}, {'$set': {'disabled': False}})
            return jsonify({"message": "Email verified successfully!"}), 200
        else:
            return jsonify({"error": f"Invalid verification key or email already verified. {user['verification_key']}"}), 400
    else:
        return jsonify({"error": "User not found"}), 404
    

def send_verification_email(email, link):
    msg = MIMEText(f"Click the link to verify your account: {link}")
    msg['Subject'] = 'Verify your account'
    msg['From'] = 'no-reply@tim.cse356.compas.cs.stonybrook.edu'
    msg['To'] = email

    with smtplib.SMTP('postfix', 25) as server:
        server.send_message(msg)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')
        
        user = users.find_one({'username': username})

        # Replace with your user validation logic
        if user['username'] == username and user['password'] == password:
            session['username'] = username
            return jsonify({"message": "Logged in successfully"}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    else:
        return "<p>Hello World!</>"

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)  # Remove username from session
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/session', methods=['GET'])
def get_session():
    if 'username' in session:
        return jsonify({"username": session['username']}), 200
    else:
        return jsonify({"error": "Not logged in"}), 401


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)