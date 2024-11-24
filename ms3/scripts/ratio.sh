#finds the ratio of every video

input_dir="../python/static/videos"
for video in $input_dir/*.mp4; do
    echo "Processing $video"
    resolution=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$video")
    width=$(echo $resolution | cut -d',' -f1)
    height=$(echo $resolution | cut -d',' -f2)
    aspect_ratio=$(bc -l <<< "$width/$height")
    echo "Resolution: ${width}x${height}, Aspect Ratio: $aspect_ratio"
done