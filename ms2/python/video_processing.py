# video_processing.py
import subprocess
import os
from pymongo import MongoClient

def process_video(file_path, output_dir, movie_id):
    filename = os.path.splitext(os.path.basename(file_path))[0]

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
    client = MongoClient()
    db = client.your_database_name  # replace with actual db name
    movies = db.movies
    movies.update_one({"id": movie_id}, {"$set": {"processed": "complete"}})
