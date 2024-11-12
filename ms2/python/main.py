import json
from flask import Flask, render_template, request, jsonify, url_for, flash, redirect, session, send_file
from flask_pymongo import PyMongo
import os, smtplib
from email.message import EmailMessage
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import subprocess
from redis import Redis
from rq import Queue
from werkzeug.utils import secure_filename
from video_processing import process_video
import random


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Warmup2"
app.secret_key = "secret"
# app.config["SESSION_TYPE"] = "filesystem"
# app.config["SESSION_PERMANENT"] = True  # Set to True for sessions to persist
# app.config["SESSION_USE_SIGNER"] = True  # Sign cookies to prevent tampering
# app.config["SESSION_FILE_DIR"] = "./flask_session/"  # Directory to store session files
# app.config["SESSION_FILE_THRESHOLD"] = 100  # Max number of session files to keep
# Session(app)

db = PyMongo(app).db
users = db.users
feedbacks = db.feedbacks
movies = db.movies
counter = db.counter

#dummmy account
# db.users.insert_one({
#   'username': "sdf",
#   'password': "",
#   'email': "user@example.com",
#   'disabled': False
# })

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

#If a method is not in public_endpoints, then you must be logged in to use the api. Comment this out to use everything without logging in
@app.before_request
def require_login():
    # Check if the requested endpoint is not in the public endpoints
    if request.endpoint not in public_endpoints and not is_authenticated():
        return ret_json(1, f"User not logged in. Go to /login")

def generate_verification_key():
    # characters = string.ascii_letters + string.digits  # Letters (both uppercase and lowercase) and digits
    # return ''.join(random.choice(characters) for _ in range(64))
    return "abc123"

# video_files = "static/videos/m2.json"
# with open(video_files, 'r') as file:
#     data = json.load(file)
# # video_ids = [id for id,description in data]

# count10 = dict(list(data.items())[0:10])
# print(count10)
    
#sends the media. Used when player.html asks for a file
@app.route("/media/<path:filename>")
def serve_media(filename):
    print("hello")
    media_dir = "/root/CSE356/ms1/media/"
    filename = filename.lstrip("media/")
    return send_file(os.path.join(media_dir, filename), as_attachment=True)
    #return send_file(f"root/CSE356/ms1/media/{filename}", as_attachment=True)
    
#an old method. Not used right now
@app.route("/media/output.mpd", methods=['POST', 'GET'])
def output():
    # Define the directory where the media files are located
    # media_directory = '/usr/share/nginx/html/media'
    
    # Ensure the file exists in the media directory
    return send_file("p/output.mpd", as_attachment=True)

#Adds user using post method
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
        return add_user_body(name, password, email)

#adds user using a form which is given in adduser.html
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
    
#the main body that /adduser and /tempadduser uses. Generates a key and adds the user to mongodb. If there is already a user with the same name, it errors out.
#Then it send a email with the verification link.
def add_user_body(name, password, email):
    # Create a disabled user
    verification_key = generate_verification_key()
    # Create a user document
    user = {
        "username": name,
        "password": password,
        "email": email,
        "disabled": True,
        "verification_key": verification_key,
        "watched": [],
        "uploaded": []
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

#The result of clicking on the verification link. Checks mongo to see if there is a user with disabled = True and sets it to False.
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

#Login using Post.
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

#Login using Get, sending login.html and getting information from the form.
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
@app.route('/v', methods=['GET'])    
def get_next_id():
    # Increment the counter and return the new value
    count = counter.find_one_and_update(
        {"_id": "counter"},
        {"$inc": {"count": 1}},
        upsert=True,
        return_document=True       # Return the updated document
    )
    return count['count']

def get_count_from_request():
    count = 10  # default value
    if request.method == 'POST':
        data = request.json
        count = data.get('count', 10)  # Get 'count' from JSON or use 10 as default
    else:
        count = int(request.args.get('count', 10))  # Get 'count' from query string or use 10 as default
    return count

#sends a json of recommended videos. Gets all the feedback from the feedback collection which has {user_id, post_id, value}. Creates a sparse table and runs
#cosine_similarity to find similar users. Based on that, it finds videos that other users like.
#I still need to modify it so it recommends videos the user hasn't watched and then random videos.
#if there are recommended videos that haven't been watched, recommend those, then recommend videos that haven't been watched, then random videos
@app.route('/api/videos', methods=['POST', 'GET'])
def videos(count=10):
    count = get_count_from_request()
    recommendations = recommend_videos(count)
    return json.dumps({"videos": recommendations})

def recommend_videos(count=10):
    print("count", count)
    f = feedbacks.find()
    v = []#list of videos to recommend
    user = session['username']
    videos = list(movies.find({"processed":"complete"}))
    watched = users.find_one({"username": user}).get("watched", [])
    all_ids = list(movies.find({"processed":"complete"}, {'_id': 0, 'id': 1}))
    not_watched = list(set([doc['id'] for doc in all_ids]) - set(watched))
    print("videos that are not watched", not_watched)
    not_recommended = []#has to also be not watched
    if feedbacks.count_documents({}) != 0 and feedbacks.count_documents({"user_id": user}):#There is feedback to decide what to train and user has done recommendations before
        data = list(f)
        df = pd.DataFrame(data)

        # Optionally, you may want to ensure the columns are named properly
        df = df[['user_id', 'post_id', 'value']]  # Select relevant columns
        user_item_matrix = df.pivot_table(index='user_id', columns='post_id', values='value', fill_value=0)
        user_similarity = cosine_similarity(user_item_matrix)
        # Step 5: Convert similarity matrix to DataFrame for better readability

        user_similarity_df = pd.DataFrame(user_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)
        recommended_items = recommend_items(user, user_item_matrix, user_similarity_df, count)
        id_list = [id for id,_ in recommended_items]
        id_list_and_not_watched = list(set(id_list) & set(not_watched))
        not_watched_and_not_recommended = list(set(not_watched) - set(id_list))
        print("recommended videos", id_list)
        print("recommended videos not watched", id_list_and_not_watched)
        print("not recommended videos not watched", not_watched_and_not_recommended)
        not_recommended = list(movies.find({"processed":"complete", 'id': {'$in': not_watched_and_not_recommended}}))#list of videos that are not recommended and not watched
        recommended = list(movies.find({"processed":"complete", 'id': {'$in': id_list_and_not_watched}}))#list of videos that are are recommended and not watched
        print("length of recommendations:", len(recommended))
        for video in recommended:#video is post_id so I will need to first find the movie in movies collection to get the actual description
            temp = {
                "id": video.get("id"),
                "description": video.get("description"),
                "title": video.get("title"),
                "watched": False,
                "liked": False, #should be false because the user has not watched it before
                "likevalues": feedbacks.count_documents({"post_id": video.get("id"), "value": "1"})
            }
            # print(temp)
            v.append(temp)
    left = count - len(v)
    print("length of recommendations after adding recommended and not watched:", len(v))
    if left > 0:
        recommend_watched(v, user, not_recommended, left)
    left = count - len(v)
    print("length of recommendations after adding not watched and not recommended:", len(v))
    if left > 0 and len(videos):
        recommend_random(v, videos, left)
    print("length of recommendations after adding randoms:", len(v))
    return v

def recommend_watched(v, user, videos, left):#get watched, get all videos, get the difference between them and return random ones in those
    try:
        watched = users.find_one({"username": user}).get("watched", [])
    except:
        return ret_json(1, "User not found")
    videos = [video for video in videos if video["id"] not in watched]#get all documents whose ids are not in the watched list

    if len(videos) > left:#If there are more not watched videos than count, we have to randomly choose which ones to recommend
        videos = random.choices(videos, k = left)
    print("length of not watched and not recommended", len(videos))
    while videos:
        video = videos.pop(0)
        temp = {
            "id": video.get("id"),
            "description": video.get("description"),
            "title": video.get("title"),
            "watched": False,
            "liked": False, #should be false because the user has not watched it before
            "likevalues": feedbacks.count_documents({"post_id": video.get("id"), "value": "1"})
        }
        v.append(temp)
        
def recommend_random(v, videos, left):
    while left:
        video = random.choice(videos)
        temp = {
            "id": video.get("id"),
            "description": video.get("description"),
            "title": video.get("title"),
            "watched": False,
            "liked": False, #should be false because the user has not watched it before
            "likevalues": feedbacks.count_documents({"post_id": video.get("id"), "value": "1"})
        }
        v.append(temp)
        left-=1
    # if len(videos) > left:
    #     videos = random.choices(videos, k = left)
    # print("length of random videos", len(videos))
    # while videos:
    #     video = videos.pop(0)
    #     temp = {
    #         "id": video.get("id"),
    #         "description": video.get("description"),
    #         "title": video.get("title"),
    #         "watched": False,
    #         "liked": False, #should be false because the user has not watched it before
    #         "likevalues": feedbacks.count_documents({"post_id": video.get("id"), "value": "1"})
    #     }
    #     v.append(temp)

@app.route('/api/thumbnail/<id>', methods=['GET'])
def get_thumbnail(id):
    thumbnail_path = os.path.join("static/thumbnails/", f"{os.path.splitext(id)[0]}.jpg")
    # Send the thumbnail as a response
    if os.path.exists(thumbnail_path):
        return send_file(thumbnail_path, mimetype='image/jpg')
    else:
        return ret_json(1, f"Current working directory:, {thumbnail_path})")

#The basic json that returns when there's an error
def ret_json(status:int, message:str):#has to have /output.md return error
    if status:
        return jsonify({"status": "ERROR", "error":True, "message": f"{message}"}), 200
    else:
        return jsonify({"status": "OK", "error":False, "message": f"{message}"}), 200
    
    # if status:
    #     return json.dumps({"status":"ERROR", "error":True, "message": f"{message}"}, separators=(',', ':'))
    # else:
    #     return json.dumps({"status": "OK", "error":False, "message": f"{message}"}, separators=(',', ':'))

#serves the DASH player in player.html
@app.route("/play/<id>")
def serve_video(id):
    #print(data)
    return render_template('player.html', id=id, username = session['username'])
    
#serves the manifest which downloads
@app.route('/api/manifest/<id>', methods=['GET'])
def get_manifest(id):
    # video_path = os.path.join("static/videos/", f"{os.path.splitext(id)[0]}.mp4")
    # # Send the thumbnail as a response
    # if os.path.exists(video_path):
    #     return render_template('player.html', video_path=id)
    # else:
    #     return ret_json(1, f"Current working directory:, {video_path})")
    return send_file(f"media/{id}.mpd", as_attachment=True)

#adds to feedback collection. If it's the same value, it errors out. If there already was feedback, it changes it.
@app.route('/api/like', methods=['POST', 'GET'])
def like():
    id = value = 0
    user = session['username']
    if request.method == 'POST':
        data = request.json
        id = data.get('id')
        value = data.get('value')
        print(value)
        if data.get('user'):
            user = data.get('user')
        value = 1 if value == True else -1 if value == False else 0
    else:
        id = request.args.get('id')
        value = int(request.args.get('value'))
        print(value)
        if request.args.get('user'):
            user = request.args.get('user')
    print("id, value", id, value)

    current_feedback = feedbacks.find_one({"user_id": user, "post_id": id})
    
    print(type(value))
    if current_feedback and current_feedback['value'] == value:
        return ret_json(1, "Value is the same as before")   
    if current_feedback:
        feedbacks.update_one(
            {"user_id": user, "post_id": id},
            {"$set": {"value": value}}
        )
    else:
        feedbacks.insert_one({"user_id": user, "post_id": id, "value": value})
    like_count = feedbacks.count_documents({"post_id": id, "value": 1})
    return json.dumps({"status": "OK", "likes": like_count})

#The reccommendation system. It was described in /api/videos
def recommend_items(user_id, user_item_matrix, user_similarity_df, count = 10):
    # Step 7: Get similar users to the given user
    print(user_id)
    print(user_item_matrix)
    similar_users = user_similarity_df[user_id][user_similarity_df[user_id] > 0].sort_values(ascending=False)[1:].index
    # print(f"\nMost similar users to User {user_id}: {similar_users}, {user_similarity_df[user_id][user_similarity_df[user_id] > 0].sort_values(ascending=False)}")
    
    # Step 8: Aggregate ratings from similar users
    recommended_items = {}
    for similar_user in similar_users:
        for item, rating in user_item_matrix.loc[similar_user].items():
            # print(item, rating, user_item_matrix.loc[user_id][item] != 0)
            if rating > 0 and user_item_matrix.loc[user_id][item] == 0:  # Avoid already rated items
                if item not in recommended_items:
                    recommended_items[item] = rating
                    # print("added item", item)
                else:
                    recommended_items[item] += rating

    # Step 9: Sort recommended items and return the top N recommendations
    recommendations = sorted(recommended_items.items(), key=lambda x: x[1], reverse=True)[:count]
    return recommendations

#Made to add all the base videos into movies collection. Should only be run once
@app.route('/add_movies', methods=['GET'])
def add_movies_to_db():
    video_files = "static/videos/m2.json"
    videos = 0
    with open(video_files, 'r') as file:
        videos = json.load(file)
    # print(videos.items())
    for video in videos.items():
        print(video)
        movie = {
            "id": video[0].split(".")[0],
            "description": video[1],
            "title": video[0].replace(".mp4", ""),
            "processed": "complete"
        }
        try:
            movies.insert_one(movie)
        except Exception as e:
            return ret_json(1, "An error occured adding user to database")
    return ret_json(0, "Movie added")


redis = Redis(host='localhost', port=6379, db=0)  
q = Queue(connection=redis)

UPLOAD_FOLDER = '/python/static/upload'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/api/upload', methods=['POST'])
def upload_video():
    author = request.form.get('author')
    title = request.form.get('title')
    mp4_file = request.files.get('mp4File')

    if not author or not title or not mp4_file:
        return jsonify({"error": True, "message": "Missing fields", "status": "ERROR"}), 400

    #save movie to database
    movie_id = get_next_id()
    movie = {
            "id": movie_id,
            "description": title,
            "title": title,
            "author": author,
            "processed": "processing"
        }
    try:
        movies.insert_one(movie)
    except Exception as e:
        return jsonify({"error": True, "message": f"An error occurred adding movie to database: {str(e)}", "status": "ERROR"}), 500

    
    username = session['username']
    #user = users.find_one({"username": session['username']})
    user = db.users.find_one({"username": session['username']})

    print("user: "+str(username))
    print(user, session['username'])
    
    if user is None:
        return jsonify({"error": True, "message": "User not found", "status": "ERROR"}), 404

    uploaded = user.get("uploaded", [])
    uploaded.append({
        "id": movie_id,
        "title": title,
        "processed": "processing"
    })
    db.users.update_one({"username": session['username']}, {"$set": {"uploaded": uploaded}})
    

    file_path = os.path.join(UPLOAD_FOLDER, secure_filename(mp4_file.filename))
    try:
        mp4_file.save(file_path)
    except Exception as e:
        return jsonify({"error": True, "message": f"File save error: {str(e)}", "status": "ERROR"}), 500


    # Resize and process the video using ffmpeg
    output_dir = "../media"
    q.enqueue(process_video, file_path, output_dir, movie_id)
    '''
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.splitext(mp4_file.filename)[0]  # Get filename without extension

    ffmpeg_command = [
        "ffmpeg", "-i", file_path,
        "-map", "0:v", "-b:v:0", "254k", "-s:v:0", "320x180",
        "-map", "0:v", "-b:v:1", "507k", "-s:v:1", "320x180",
        "-map", "0:v", "-b:v:2", "759k", "-s:v:2", "480x270",
        "-map", "0:v", "-b:v:3", "1013k", "-s:v:3", "640x360",
        "-map", "0:v", "-b:v:4", "1254k", "-s:v:4", "640x360",
        "-map", "0:v", "-b:v:5", "1883k", "-s:v:5", "768x432",
        "-map", "0:v", "-b:v:6", "3134k", "-s:v:6", "1024x576",
        "-map", "0:v", "-b:v:7", "4952k", "-s:v:7", "1280x720",
        "-f", "dash", "-seg_duration", "10", "-use_template", "1", "-use_timeline", "1",
        "-init_seg_name", f"{output_dir}/{filename}_$RepresentationID$_init.m4s",
        "-media_seg_name", f"{output_dir}/{filename}_$Bandwidth$_$Number$.m4s",
        "-adaptation_sets", "id=0,streams=v",
        f"{output_dir}/{filename}.mpd"
    ]

    #run ffmpeg command
    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": True, "message": f"FFmpeg processing error: {str(e)}", "status": "ERROR"}), 500
    finally:
        # Remove the temporary file
        os.remove(file_path)'''

    return jsonify({"id": movie_id, "status": "processing"}), 202

    
            
@app.route('/upload', methods=['GET'])
def upload_page():
    return render_template('upload.html')

#Adds the video id to the user's watched field. If the user already watched, it doesn't change anything
@app.route('/api/view', methods=['POST', 'GET'])
def update_watched_videos():
    id = 0
    val = True
    if request.method == 'POST':
        data = request.json
        id = data.get('id')
    else:
        id = "854243-hd_1280_720_30fps"
    # Retrieve the user's current watched videos list
    user = db.users.find_one({"username": session['username']})
    watched = user.get("watched", [])
    
    # Add the video to the list if it's not already watched
    if id not in watched:
        watched.append(id)
        val = False
    
    # Update the user's watched list in the database
    db.users.update_one({"username": session['username']}, {"$set": {"watched": watched}})
    return json.dumps({"status": "OK", "viewed": val})


@app.route('/api/processing-status', methods=['GET'])
def processing_status():
    if 'username' not in session:
        return jsonify({"error": True, "message": "User not authenticated", "status": "ERROR"}), 401

    user = db.users.find_one({"username": session['username']})

    if not user:
        return jsonify({"error": True, "message": "User not found", "status": "ERROR"}), 404
    video_docs = user.get("uploaded", [])

    if not video_docs:
        return jsonify({"videos": [], "status": "OK"}), 200

    videos = []
    for video in video_docs:
        video_data = {
            "id": video["id"],
            "title": video["title"],
            "status": video["processed"]
        }
        videos.append(video_data)

    return jsonify({"videos": videos, "status": "OK"}), 200

#The base url. If logged in, goes to index.html, else it goes to rootlogin. If using POST, then it logs in with request.form information
@app.route("/", methods=['POST', 'GET'])
def hello_world():
    if 'username' in session:
        videos = recommend_videos()
        # video_dict = {video['id']: video['description'] for video in videos}
        # print(videos, len(videos))
        # print(video_dict, len(video_dict))
        return render_template('index.html', videos=videos)
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
                videos = recommend_videos()
                return render_template('index.html', videos=videos)
            else:
                return ret_json(1, "Wrong username or password. Try a different one")
        else:
            return render_template('rootlogin.html')


@app.route('/list_videos')
def list_videos():
    media_folder = os.path.join(os.path.dirname(__file__), 'media')

    video_files = [f for f in os.listdir(media_folder) if f.endswith('.mpd')]
    #print("Videofile1: "+str(video_files))
    return jsonify(video_files)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)