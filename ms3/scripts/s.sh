#!/bin/bash

# Set the input directory containing the videos
input_dir="../python/static/videos"  # Change this to your video folder path
output_dir="../python/static/padded_videos"  # Change this to your desired output folder path

# Create the output directory if it doesn't exist
# mkdir -p "$output_dir"


# pad=width=1280:height=720:x=-1:y=-1:color=black # change the width and height for everything
# Iterate over all .mp4 files in the input directory
for video in "$input_dir"/*.mp4; do
    # Get the base filename without extension
    filename=$(basename "$video" .mp4)
    aspect_ratio=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$video" | awk -F'x' '{ ratio = $1 / $2; if (ratio == (16 / 9)) {print "16:9"} else {print "other"}}')

    
    # Construct the ffmpeg command
    # ffmpeg -i "$video" \
    #     -vf "pad=ih*16/9:ih:-1:-1:black" -c:a copy "${filename}.mp4"
    if [ "$aspect_ratio" = "other" ]; then
    ffmpeg -i "$video" \
        -vf "scale=w=iw*min(1280/iw\,720/ih):h=ih*min(1280/iw\,720/ih),pad=1280:720:(1280-iw*min(1280/iw\,720/ih))/2:(720-ih*min(1280/iw\,720/ih))/2" \
        -c:a copy \
        "$output_dir/${filename}.mp4" -y
    else
        ffmpeg -i "$video" \
        -c:a copy \
        "$output_dir/${filename}.mp4" -y
    fi
done