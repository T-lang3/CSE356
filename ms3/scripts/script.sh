#!/bin/bash

# Set the input directory containing the videos
input_dir="../python/static/padded_videos"  # Change this to your video folder path
output_dir="../python/media"  # Change this to your desired output folder path

# Create the output directory if it doesn't exist
mkdir -p "$output_dir"


# pad=width=1280:height=720:x=-1:y=-1:color=black # change the width and height for everything
# Iterate over all .mp4 files in the input directory
for video in "$input_dir"/*.mp4; do
    # Get the base filename without extension
    filename=$(basename "$video" .mp4)
    if [ ! -f "$output_dir/${filename}.mpd" ]; then
        ffmpeg -i "$video" \
        -map 0:v -b:v:0 512k -s:v:0 640x360 \
        -map 0:v -b:v:1 768k -s:v:1 960x540 \
        -map 0:v -b:v:2 1024k -s:v:2 1280x720 \
        -f dash -seg_duration 10 -use_template 1 -use_timeline 1 \
        -init_seg_name "${filename}_\$RepresentationID\$_init.m4s" \
        -media_seg_name "${filename}_\$Bandwidth\$_\$Number\$.m4s" \
        -adaptation_sets "id=0,streams=v" \
        "$output_dir/${filename}.mpd"
    else
        echo "File already exists, skipping processing. $output_dir/${filename}.mpd"
    fi
    # Construct the ffmpeg command
    # ffmpeg -i "$video" \
    #     -map 0:v -b:v:0 512k -s:v:0 640x360 \
    #     -map 0:v -b:v:1 768k -s:v:1 960x540 \
    #     -map 0:v -b:v:2 1024k -s:v:2 1280x720 \
    #     -f dash -seg_duration 10 -use_template 1 -use_timeline 1 \
    #     -init_seg_name "${filename}_\$RepresentationID\$_init.m4s" \
    #     -media_seg_name "${filename}_\$Bandwidth\$_\$Number\$.m4s" \
    #     -adaptation_sets "id=0,streams=v" \
    #     "$output_dir/${filename}.mpd"

done