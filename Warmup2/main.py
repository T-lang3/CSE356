from flask import Flask, render_template, request, jsonify, url_for
from flask_pymongo import PyMongo
import hashlib, os, smtplib
from email.mime.text import MIMEText


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://tim.cse356.compas.cs.stonybrook.edu:27017/Warmup2"
db = PyMongo(app).db
users = db.users

def generate_verification_key():
    return hashlib.sha256(os.urandom(60)).hexdigest()

@app.route("/")
def hello_world():
    return "<p>Hello World!</>"

@app.route('/adduser', methods=['POST', 'GET'])
def add_user():
    if request.method == 'POST':
        # Get form data
        print(request.form)
        name = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Create a disabled user
        verification_key = generate_verification_key()
        # Create a user document
        user = {
            "username": name,
            "password": hashed_password,
            "email": email,
            "disabled": True,
            "verification_key": verification_key
        }

        # Insert the document into the users collection
        try:
            users.insert_one(user)

            verification_link = url_for('verify_email', email=email, key=verification_key, _external=True)
            print(verification_link)
            # Send the verification email (Here you would integrate your mail server logic)
            # send_verification_email(email, verification_link)
            return f"User added successfully! {verification_link}"
        except Exception as e:
            return f"An error occurred: {str(e)}"
    else:
        return render_template('index.html')

@app.route('/verify', methods=['GET'])
def verify_email():
    email = request.form.get('email')
    key = request.form.get('key')
    
    # Find the user by email
    user = users.find_one({'email': email})
    
    if user:
        # Check if the key matches and the user is disabled
        if user['verification_key'] == key and user['disabled']:
            # Update the user to mark them as verified
            users.update_one({'email': email}, {'$set': {'disabled': False}})
            return jsonify({"message": "Email verified successfully!"}), 200
        else:
            return jsonify({"error": "Invalid verification key or email already verified"}), 400
    else:
        return jsonify({"error": "User not found"}), 404
    

def send_verification_email(email, link):
    msg = MIMEText(f"Click the link to verify your account: {link}")
    msg['Subject'] = 'Verify your account'
    msg['From'] = 'no-reply@yourdomain.com'
    msg['To'] = email

    with smtplib.SMTP('localhost') as server:
        server.send_message(msg)

app.run(debug=True)