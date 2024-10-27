import os
import subprocess

# Directory containing the videos
video_directory = "../videos/"
# Directory where thumbnails will be saved
output_directory = "../thumbnails/"

# Ensure the output directory exists

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