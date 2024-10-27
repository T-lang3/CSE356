This is done using Dockers.

The nginx serves the websites, which FLASK is used to create the routes such as /adduser. FLASK takes index.html to create the webpage which uses main.js as some internal logic.

In order to bring this online, first download docker, then do "docker compose up -d" or "docker-compose up -d" to bring up the containers.
Then you should be able to go to http://tim.cse356.compas.cs.stonybrook.edu/

do pip install ffmpeg to use processing.py to create thumbnails and chunks for all the videos.