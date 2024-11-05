# Use official Python image
FROM python:3.8

# Set working directory
WORKDIR /app

# COPY requirements.txt ./

# # Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --upgrade pip
RUN pip install flask flask-pymongo numpy pandas cython
RUN pip install git+https://github.com/NicolasHug/Surprise.git
# RUN pip install flask-session

EXPOSE 5000

# CMD ["python", "main.py"]

# pip install flask flask_pymongo
# python main.py