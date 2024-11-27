This is done using Dockers.

The nginx serves the websites, which FLASK is used to create the routes such as /adduser. FLASK takes index.html to create the webpage which uses main.js as some internal logic.

In order to bring this online, first download docker, then do "docker compose up -d" or "docker-compose up -d" to bring up the containers.
Then you should be able to go to http://tim.cse356.compas.cs.stonybrook.edu/

do pip install ffmpeg to use processing.py to create thumbnails and chunks for all the videos.

s.sh creates the padded videos at 16:9 ratio. If a video is already 16:9, it just copies it over to padded_videos directory.
copy.py copies the videos over as well. I made this because I accidentally made s.sh just skip over 16:9 videos originally.
script.sh chunks the padded_videos
ratio.sh prints out the width:height and aspect ratio of all the videos in /videos. I wanted to see all the different ratios.

to handle multiple request use this command
gunicorn -w 16 -t 2 -b 0.0.0.0:5000 main:app