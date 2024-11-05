#Copies over videos that weren't padded. I made this because I accidentally skipped over videos that were already 16:9 in s.sh before changing it.
import os
import shutil

# Paths to your folders
source_folder = "../python/static/videos"
destination_folder = "../python/static/padded_videos"

# List all video files in the source folder
source_videos = os.listdir(source_folder)

# Loop through each video file in the source folder
for video in source_videos:
    # Create the full path for both source and destination files
    source_path = os.path.join(source_folder, video)
    destination_path = os.path.join(destination_folder, video)

    # Check if the video file already exists in the destination folder
    if not os.path.exists(destination_path):
        # If not, copy the video from source to destination
        shutil.copy2(source_path, destination_path)
        print(f"Copied {video} to {destination_folder}")
    else:
        print(f"Skipped {video}, already exists in {destination_folder}")