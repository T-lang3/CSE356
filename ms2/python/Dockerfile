# Use official Python image
FROM python:latest

# Set working directory
WORKDIR /app

# COPY requirements.txt ./

# # Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --upgrade pip
#commented the 2 pip out jack
RUN pip install flask flask-pymongo 
RUN pip install numpy pandas 
RUN pip install redis rq
# RUN apt-get install -y ffmpeg


RUN pip install ffmpeg-python
RUN pip install cython scikit-learn
# RUN pip install git+https://github.com/NicolasHug/Surprise.git
# RUN pip install PyGorse

EXPOSE 5000

# CMD ["python", "main.py"]

# pip install flask flask_pymongo
# python main.py