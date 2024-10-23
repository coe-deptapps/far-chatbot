# Use the official Python image from the Docker Hub
#FROM python:3.9-slim
FROM image-registry.openshift-image-registry.svc:5000/openshift/python:3.9

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config

# Set the working directory in the container
WORKDIR /flaskapp

# Copy the current directory contents into the container at /app
COPY . /flaskapp

RUN cd /flaskapp && mkdir -p logs

# Install any necessary dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 9001 available to the world outside this container
EXPOSE 9001

# Define environment variable
ENV FLASK_APP=flaskapp.py

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=9001"]
