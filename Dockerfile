# Use the official Python image as the base image
FROM python:3.9

# Set the working directory within the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN apt-get update && apt-get install -y sqlite3
RUN pip3 install --no-cache-dir gunicorn && \
    pip3 install --no-cache-dir -r requirements.txt

# Copy the app source code into the container
COPY . .

# Create the database
RUN mkdir -p db
RUN sqlite3 ./db/db.sqlite < ./app/schema.sql

# Expose the port that Gunicorn will listen on
EXPOSE 4242
CMD ["gunicorn", "--bind", "0.0.0.0:4242", "app.server:app"]
