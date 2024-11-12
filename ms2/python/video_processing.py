# video_processing.py
import subprocess
import os
from pymongo import MongoClient
#import movies from main.py
from flask import Flask, render_template, request, jsonify, url_for, flash, redirect, session, send_file
from flask_pymongo import PyMongo
app = Flask(__name__)
def process_video(file_path, output_dir, movie_id):
    #from main import db
    print("entered the function2------------------------------------------------------------------")
    filename = os.path.splitext(os.path.basename(file_path))[0]
    output_dir = "./media"

    print("filename: '"+str(filename)+"'")
    print("file path: "+file_path+"\noutput: "+output_dir)
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

    subprocess.run(ffmpeg_command, check=True)

    # MongoDB Update: Assuming the movie collection is already available
    
    db = PyMongo(app).db
    movies = db.movies
    movies.update_one({"id": movie_id}, {"$set": {"processed": "complete"}})
