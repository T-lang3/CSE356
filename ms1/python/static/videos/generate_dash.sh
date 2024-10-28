#!/bin/bash

# Check if filename is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <input_filename>"
  exit 1
fi

# Input filename without extension
input_file="$1"
base_name=$(basename "$input_file" .mp4)
id=$(echo "$base_name" | cut -d'-' -f1)

# Output filename
output_dir="$HOME/docker-project/CSE356/ms1/python"
output_file="$output_dir/$base_name.mpd"

# ffmpeg command
ffmpeg -i "$input_file" \
  -map 0:v -b:v:0 254k -s:v:0 320x180 \
  -map 0:v -b:v:1 507k -s:v:1 320x180 \
  -map 0:v -b:v:2 759k -s:v:2 480x270 \
  -map 0:v -b:v:3 1013k -s:v:3 640x360 \
  -map 0:v -b:v:4 1254k -s:v:4 640x360 \
  -map 0:v -b:v:5 1883k -s:v:5 768x432 \
  -map 0:v -b:v:6 3134k -s:v:6 1024x576 \
  -map 0:v -b:v:7 4952k -s:v:7 1280x720 \
  -f dash -seg_duration 10 -use_template 1 -use_timeline 1 \
  -init_seg_name "media/$id_\$Bandwidth\$_init.m4s" \
  -media_seg_name "media/$id_\$Bandwidth\$_\$Number\$.m4s" \
  -adaptation_sets "id=0,streams=v" "$output_file"

echo "DASH manifest created at: $output_file"