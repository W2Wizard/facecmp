# Use the official Python image as the base image
FROM python:3.11.4

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y libglib2.0-0 libsm6 libxext6 libxrender-dev

# Install Python dependencies
#COPY requirements.txt /app/
RUN pip3 install flask face-recognition

# Copy the application code into the container
COPY ./app /app/

# Expose the port that the Flask app will run on
EXPOSE 5000

# Command to run the application
CMD ["python", "main.py"]
