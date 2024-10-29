#!/bin/bash

# Set the input directory containing the videos
input_dir="../videos"  # Change this to your video folder path
# output_dir="../media"  # Change this to your desired output folder path

# Create the output directory if it doesn't exist
# mkdir -p "$output_dir"


# pad=width=1280:height=720:x=-1:y=-1:color=black # change the width and height for everything
# Iterate over all .mp4 files in the input directory
for video in "$input_dir"/*.mp4; do
    # Get the base filename without extension
    filename=$(basename "$video" .mp4)
    
    # Construct the ffmpeg command
    # ffmpeg -i "$video" \
    #     -vf "pad=ih*16/9:ih:-1:-1:black" -c:a copy "${filename}.mp4"
    ffmpeg -i "$video" \
        -vf "scale=w=iw*min(1280/iw\,720/ih):h=ih*min(1280/iw\,720/ih),pad=1280:720:(1280-iw*min(1280/iw\,720/ih))/2:(720-ih*min(1280/iw\,720/ih))/2" \
        -c:a copy \
        "${filename}.mp4" -y
done