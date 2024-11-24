import os
import subprocess
import json

# Directory containing the videos
video_directory = "../python/static/videos/"
# Directory where thumbnails will be saved
output_directory = "../python/static/thumbnails/"
i = 1
# Ensure the output directory exists
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

def extract_thumbnail(video_path, thumbnail_path):
    """
    Extracts the first frame from a video using FFmpeg.
    """
    command = [
        'ffmpeg', '-i', video_path,   # Input file
        '-vf', 'select=eq(n\\,0),scale=320:180',    # Select the first frame
        '-q:v', '3',                  # Quality setting (lower number = higher quality)
        thumbnail_path                # Output image file
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

# Process all MP4 videos in the directory
for filename in os.listdir(video_directory):
    if filename.endswith(".mp4"):
        video_path = os.path.join(video_directory, filename)
        thumbnail_name = os.path.splitext(filename)[0] + ".jpg"
        thumbnail_path = os.path.join(output_directory, thumbnail_name)

        print(f"Processing {video_path} -> {thumbnail_path}")
        extract_thumbnail(video_path, thumbnail_path)

print("Thumbnails generated for all videos.")

def get_new_ids_json():
    #converts video ids to sequential id and stores it in new_ids.json
    video_files = "../python/static/videos/m2.json"
    with open(video_files, 'r') as file:
        data = json.load(file)
    # print(data)
    video_ids = [id.split(".")[0] for id, description in data.items()]
    # video_ids = sorted(video_ids)
    new_ids = {}
    print(video_ids)
    for i in range(len(video_ids)):
        new_ids[i+1] = video_ids[i]#reverse this to convert back and forth the filenames
    with open("../python/static/videos/new_ids.json", 'w') as file:
        json.dump(new_ids, file)

def convert_video_ids_to_sequence():
    get_new_ids_json()
    #actual converts video names to sequential id
    source_folder = "../python/static/thumbnails"
    # destination_folder = "../python/static/padded_videos"
    new_ids_file = "../python/static/videos/new_ids.json"
    with open(new_ids_file, 'r') as file:
        new_ids = json.load(file)
    # List all video files in the source folder
    source_videos = os.listdir(source_folder)
    # print(new_ids)
    for video in source_videos:
        # Get the ID part from the filename by splitting at the first '-'
        file_id = video.split('.')[0]
        
        # Check if this ID exists in the dictionary
        if file_id in new_ids:
            # Generate the new filename by replacing the ID with the corresponding number
            new_filename = video.replace(file_id, str(new_ids[file_id]), 1)
            
            # Construct full old and new file paths
            old_filepath = os.path.join(source_folder, video)
            new_filepath = os.path.join(source_folder, new_filename)
            
            # Rename the file
            os.rename(old_filepath, new_filepath)
            print(f'Renamed: {file_id} -> {new_filename}')
# convert_video_ids_to_sequence()
# print("done with everything")