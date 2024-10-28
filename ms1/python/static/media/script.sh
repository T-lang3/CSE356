#!/bin/bash

# Set the input directory containing the videos
input_dir="../videos"  # Change this to your video folder path
# output_dir="../media"  # Change this to your desired output folder path

# Create the output directory if it doesn't exist
# mkdir -p "$output_dir"

# Iterate over all .mp4 files in the input directory
for video in "$input_dir"/*.mp4; do
    # Get the base filename without extension
    filename=$(basename "$video" .mp4)
    
    # Construct the ffmpeg command
    ffmpeg -i "$video" \
        -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=black,scale=iw:ih:force_original_aspect_ratio=decrease,pad=ceil(iw*16/9/2)*2:ceil(ih*16/9/2)*2:(ow-iw)/2:(oh-ih)/2" -map 0:v -b:v:0 254k -s:v:0 320x180 \
        -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=black,scale=iw:ih:force_original_aspect_ratio=decrease,pad=ceil(iw*16/9/2)*2:ceil(ih*16/9/2)*2:(ow-iw)/2:(oh-ih)/2" -map 0:v -b:v:1 507k -s:v:1 320x180 \
        -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=black,scale=iw:ih:force_original_aspect_ratio=decrease,pad=ceil(iw*16/9/2)*2:ceil(ih*16/9/2)*2:(ow-iw)/2:(oh-ih)/2" -map 0:v -b:v:2 759k -s:v:2 480x270 \
        -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=black,scale=iw:ih:force_original_aspect_ratio=decrease,pad=ceil(iw*16/9/2)*2:ceil(ih*16/9/2)*2:(ow-iw)/2:(oh-ih)/2" -map 0:v -b:v:3 1013k -s:v:3 640x360 \
        -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=black,scale=iw:ih:force_original_aspect_ratio=decrease,pad=ceil(iw*16/9/2)*2:ceil(ih*16/9/2)*2:(ow-iw)/2:(oh-ih)/2" -map 0:v -b:v:4 1254k -s:v:4 640x360 \
        -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=black,scale=iw:ih:force_original_aspect_ratio=decrease,pad=ceil(iw*16/9/2)*2:ceil(ih*16/9/2)*2:(ow-iw)/2:(oh-ih)/2" -map 0:v -b:v:5 1883k -s:v:5 768x432 \
        -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=black,scale=iw:ih:force_original_aspect_ratio=decrease,pad=ceil(iw*16/9/2)*2:ceil(ih*16/9/2)*2:(ow-iw)/2:(oh-ih)/2" -map 0:v -b:v:6 3134k -s:v:6 1024x576 \
        -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=black,scale=iw:ih:force_original_aspect_ratio=decrease,pad=ceil(iw*16/9/2)*2:ceil(ih*16/9/2)*2:(ow-iw)/2:(oh-ih)/2" -map 0:v -b:v:7 4952k -s:v:7 1280x720 \
        -f dash -seg_duration 10 -use_template 1 -use_timeline 1 \
        -init_seg_name "${filename}_\$RepresentationID\$_init.m4s" \
        -media_seg_name "${filename}_\$Bandwidth\$_\$Number\$.m4s" \
        -adaptation_sets "id=0,streams=v" \
        "${filename}.mpd"

done