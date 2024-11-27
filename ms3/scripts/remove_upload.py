import os

#gets rid of uploaded videos and other related things to reduce disk usage

# Directory containing the videos
padded = "../python/static/padded_upload/"
upload = "../python/static/upload/"
# Directory where thumbnails will be saved
thumbnail = "../python/static/thumbnails/"
media = "../python/media/"

for filename in os.listdir(padded):
    file_path = os.path.join(padded, filename)  # get the full path of the file
    print(file_path)
    if os.path.isfile(file_path):
        try:
            os.remove(file_path)  # Delete the file
            print(f"File {filename} has been deleted.")
        except Exception as e:
            print(f"Error deleting {filename}: {e}")

for filename in os.listdir(upload):
    file_path = os.path.join(upload, filename)  # get the full path of the file
    print(file_path)
    if os.path.isfile(file_path):
        try:
            os.remove(file_path)  # Delete the file
            print(f"File {filename} has been deleted.")
        except Exception as e:
            print(f"Error deleting {filename}: {e}")

for filename in os.listdir(thumbnail):
    if len(filename.split(".jpg")[0]) <= 5:
        file_path = os.path.join(thumbnail, filename)  # get the full path of the file
        
        os.remove(file_path)  # Delete the file

for filename in os.listdir(media):
    if len(filename.split("_")[0]) <= 5:
        file_path = os.path.join(media, filename)  # get the full path of the file
        
        os.remove(file_path)  # Delete the file
    elif len(filename.split(".mpd")[0]) <= 2:
        file_path = os.path.join(media, filename)  # get the full path of the file
        
        os.remove(file_path)  # Delete the file