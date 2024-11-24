# video_processing.py
import subprocess
import os
from pymongo import MongoClient
from flask import session

def process_video(file_path, output_dir, pad_dir, movie_id, movies, users, username):
    print("entered the function0------------------------------------------------------------------")
    filename = os.path.splitext(os.path.basename(file_path))[0]
    pad_path = os.path.join(pad_dir, str(movie_id)+".mp4")
    #output_dir = "./media"

    print("filename: '"+str(filename)+"'")                  #'videoplayback'
    print("file path: "+file_path+"\noutput: "+output_dir)  # './static/upload/videoplayback.mp4'
    print("pad path: "+pad_path)  # './static/upload/videoplayback.mp4'
    print("stored path: "+f"{output_dir}/{filename}")       #'
    pad_command = [
        "ffmpeg", "-i", file_path,
        "-vf", "scale=w=iw*min(1280/iw\,720/ih):h=ih*min(1280/iw\,720/ih),pad=1280:720:(1280-iw*min(1280/iw\,720/ih))/2:(720-ih*min(1280/iw\,720/ih))/2",
        "-c:a", "copy",
        f"{pad_dir}/{movie_id}.mp4", "-y"
    ]
    ffmpeg_command = [
        "ffmpeg", "-i", pad_path,
        "-map", "0:v", "-b:v:0", "512k", "-s:v:0", "640x360",
        "-map", "0:v", "-b:v:1", "768k", "-s:v:1", "960x540",
        "-map", "0:v", "-b:v:2", "1024k", "-s:v:2", "1280x720",
        "-f", "dash", "-seg_duration", "10", "-use_template", "1", "-use_timeline", "1",
        "-init_seg_name", f"{movie_id}_$RepresentationID$_init.m4s",
        "-media_seg_name", f"{movie_id}_$RepresentationID$_$Bandwidth$_$Number$.m4s",
        "-adaptation_sets", "id=0,streams=v",
        f"{output_dir}/{movie_id}.mpd", "-y"
    ]
    thumbnail_path= "./static/thumbnails/"+str(movie_id)+".jpg"
    print(file_path)
    thumbnail_command = [
        'ffmpeg', '-i', file_path,   # Input file
        '-vf', 'select=eq(n\\,0),scale=320:180',    # Select the first frame
        '-q:v', '3', "-y",                  # Quality setting (lower number = higher quality)
        thumbnail_path                # Output image file
    ]

    process = subprocess.run(pad_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("finished pad")
    process = subprocess.run(thumbnail_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("finished thumbnail")
    process = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("finished chunks")

    print(f"FFmpeg finished successfully for {movie_id}")
    
    movies.update_one({"id": movie_id}, {"$set": {"processed": "complete"}})
    user = users.find_one({"username": username})
    uploaded = user.get("uploaded", [])
    for movie in uploaded:
        print(movie['id'], movie_id, movie['id'] == movie_id)
        if movie['id'] == movie_id:
            # Update the field you want to change
            movie['processed'] = 'complete'
    users.update_one({"username": username}, {"$set": {"uploaded": uploaded}})
    

# if __name__ == "__main__":
#     # Example arguments
#     file_path = "./static/upload/videoplayback.mp4"
#     output_dir = "./media"
#     movie_id = 1  # Replace with an actual movie ID

#     process_video(file_path, output_dir, movie_id)