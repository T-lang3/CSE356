import json
from flask import Flask, render_template, request, jsonify, url_for, flash, redirect, session, send_file
from flask_pymongo import PyMongo
import os, smtplib
from email.message import EmailMessage
from gorse import Gorse
from datetime import date 


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Warmup2"
app.secret_key = "secret"
gorse = Gorse('http://localhost:8088', '')  # replace with your Gorse URL
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
    'hello_world',
    'login',
    'tlogin',
    'logout',
    'get_session',  # Add your public endpoint names here
    # Add more public endpoints as needed
])

@app.before_request
def require_login():
    # Check if the requested endpoint is not in the public endpoints
    if request.endpoint not in public_endpoints and not is_authenticated():
        return ret_json(1, f"User not logged in. Go to /login")

def generate_verification_key():
    # characters = string.ascii_letters + string.digits  # Letters (both uppercase and lowercase) and digits
    # return ''.join(random.choice(characters) for _ in range(64))
    return "abc123"

video_files = "static/videos/m2.json"
with open(video_files, 'r') as file:
    data = json.load(file)
# video_ids = [id for id,description in data]

count10 = dict(list(data.items())[0:10])
@app.route("/", methods=['POST', 'GET'])
def hello_world():
    if 'username' in session:
        return render_template('index.html', videos=count10)
    else:
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
                return render_template('index.html', videos=count10)
            else:
                return ret_json(1, "Wrong username or password. Try a different one")
        else:
            return render_template('rootlogin.html')
    
    
@app.route("/media/<path:filename>")
def serve_media(filename):
    media_dir = "/root/CSE356/ms1/media/"
    filename = filename.lstrip("media/")
    return send_file(os.path.join(media_dir, filename), as_attachment=True)
    #return send_file(f"root/CSE356/ms1/media/{filename}", as_attachment=True)
    
@app.route("/media/output.mpd", methods=['POST', 'GET'])#Trying to get this to play the video instead of downloading it. Not working.
def output():
    # Define the directory where the media files are located
    # media_directory = '/usr/share/nginx/html/media'
    
    # Ensure the file exists in the media directory
    return send_file("p/output.mpd", as_attachment=True)

@app.route('/api/adduser', methods=['POST'])
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
        return add_user_body(name, password, email)

@app.route('/api/tempadduser', methods=['POST', 'GET'])
def temp_add_user():
    if request.method == 'POST':

        name = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # password = hashlib.sha256(password.encode()).hexdigest()

        return add_user_body(name, password, email)
    else:
        return render_template('adduser.html')
    
def add_user_body(name, password, email):
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
        verification_link = f"http://tim.cse356.compas.cs.stonybrook.edu/api/verify?email={email}&key={verification_key}"
        print(verification_link)
        # Send the verification email (Here you would integrate your mail server logic)
        send_verification_email(email, verification_link)
        return ret_json(0, "User added! Please verify with url that was sent to email. {verification_link}")
    except Exception as e:
        return ret_json(1, "An error occured adding user to database")

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
    
@app.route('/api/videos', methods=['POST'])
def videos():
    if request.method == 'POST':
        data = request.json
        count = data.get('count')  # Get 'username' from JSON
        video_files = "static/videos/m2.json"
        with open(video_files, 'r') as file:
            data = json.load(file)
        videos = dict(list(data.items())[0:count])
        print(videos)
        v = []
        for video in videos.items():
            print(video[0])
            temp = {
                "id": video[0].replace(".mp4", ""),
                "metadata": {
                    "description": video[1],
                    "title": video[0].split('-')[0]
                }
            }
            print(temp)
            v.append(temp)
        return json.dumps({"status": "OK", "videos": v})
    else:
        count = 10  # Get 'username' from JSON
        video_files = "static/videos/m2.json"
        with open(video_files, 'r') as file:
            data = json.load(file)
        videos = dict(list(data.items())[0:count])
        print(videos)
        v = []
        for video in videos.items():
            print(video[0])
            temp = {
                "id": video[0].replace(".mp4", ""),
                "metadata": {
                    "description": video[1],
                    "title": video[0].split('-')[0]
                }
            }
            print(temp)
            v.append(temp)
        return json.dumps({"status": "OK", "videos": v})
        

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


#2892038-uhd_3840_2160_30fps.mp4
#video_files = "static/videos/m2.json"
#with open(video_files, 'r') as file:
#    data = json.load(file)
@app.route("/play/<id>")
def serve_video(id):
    #print(data)
    return render_template('player.html', id=id)
    
@app.route('/api/manifest/<id>', methods=['GET'])
def get_manifest(id):
    # video_path = os.path.join("static/videos/", f"{os.path.splitext(id)[0]}.mp4")
    # # Send the thumbnail as a response
    # if os.path.exists(video_path):
    #     return render_template('player.html', video_path=id)
    # else:
    #     return ret_json(1, f"Current working directory:, {video_path})")
    return send_file(f"media/{id}.mpd", as_attachment=True)

def get_recommendations(user_id, count=5):
    # Get user's liked and disliked videos
    user_preferences = db.users.find_one({'user_id': user_id})
    liked_videos = user_preferences.get('liked', [])
    disliked_videos = user_preferences.get('disliked', [])
    
    # Perform collaborative filtering
    recommended_videos = gorse_client.recommend(user_id=user_id, count=count)

    # Filter out already watched videos
    recommended_videos = [
        video for video in recommended_videos 
        if video['id'] not in user_preferences['watched']
    ]
    
    # If no recommendations, fallback to random videos
    if not recommended_videos:
        all_videos = list(db.videos.find())
        recommended_videos = [video for video in all_videos 
                              if video['id'] not in user_preferences['watched']]
        
        # Randomly select videos already watched if necessary
        if not recommended_videos:
            recommended_videos = all_videos  # could limit to count if desired

    # Format the response
    response_videos = []
    for video in recommended_videos:
        response_videos.append({
            'id': video['id'],
            'description': video['description'],
            'title': video['title'],
            'watched': video['id'] in user_preferences['watched'],
            'liked': video['id'] in liked_videos,
            'likevalues': user_preferences.get('likevalues', {}).get(video['id'], 0)
        })

    return {'videos': response_videos[:count]}  # Return only the required count

# Example usage
# recommendations = get_recommendations(user_id='user123')
# print(recommendations)

gorse_url = "http://localhost:8080/api/user/like"  # Change this to your Gorse server URL

@app.route('/api/like', methods=['POST', 'GET'])
def like():
    res = 0   
    today = date.today().isoformat()
    id = value = user = res = 0
    if request.method == 'POST':
        data = request.json
        id = data.get('id')
        value = data.get('value')
        user = session['username']
        if value == True:
            value = 1
        elif value == False:
            value = -1
        else:
            value = 0
    else:
        id = request.args.get('id')
        value = request.args.get('value')
        user = request.args.get('user')
    data = {
        'user_id': user,
        'item_id': id,
        'value': 1  # 1 for like
    }
    res = gorse.insert_feedbacks([{ 'FeedbackType': 'like', 'UserId': f'{user}', 'ItemId': f'{id}', 'Value': value, "Timestamp": f"{today}"}])
    return json.dumps(res)

def insert_like(user_id, video_id):
    data = {
        'user_id': user_id,
        'item_id': video_id,
        'value': 1  # 1 for like
    }
    response = requests.post(gorse_url, json=data)
    if response.status_code == 200:
        print(f"Liked video {video_id} for user {user_id}.")
    else:
        print(f"Failed to like video {video_id}: {response.text}")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)