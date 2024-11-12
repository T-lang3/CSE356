#!/bin/bash

# Ensure the correct number of arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <input_video_path> <output_directory>"
    exit 1
fi

# Input and output paths
file_path="$1"
output_dir="$2"
filename=$(basename "$file_path" .mp4)  # Assuming the input file is an MP4 file, change if needed

# Create output directory if it doesn't exist
#mkdir -p "$output_dir"

echo "Starting convert.sh"

#CSE356/ms2/python/media/videoplayback.mpd

# Run the ffmpeg command to transcode the video
ffmpeg -i "$file_path" \
    -map 0:v -b:v:0 254k -s:v:0 320x180 \
    -map 0:v -b:v:1 507k -s:v:1 320x180 \
    -map 0:v -b:v:2 759k -s:v:2 480x270 \
    -map 0:v -b:v:3 1013k -s:v:3 640x360 \
    -map 0:v -b:v:4 1254k -s:v:4 640x360 \
    -map 0:v -b:v:5 1883k -s:v:5 768x432 \
    -map 0:v -b:v:6 3134k -s:v:6 1024x576 \
    -map 0:v -b:v:7 4952k -s:v:7 1280x720 \
    -f dash -seg_duration 10 -use_template 1 -use_timeline 1 \
    -init_seg_name "${filename}_\$RepresentationID\$_init.m4s" \
    -media_seg_name "${filename}_\$Bandwidth\$_\$Number\$.m4s" \
    -adaptation_sets "id=0,streams=v" \
    "$output_dir/${filename}.mpd"

# Check if ffmpeg succeeded
if [ $? -eq 0 ]; then
    echo "Transcoding completed successfully!"
else
    echo "Transcoding failed!"
fi
