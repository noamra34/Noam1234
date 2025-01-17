# Use an official Python runtime as a parent image
FROM python:3.10-slim
# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install dependencies
# COPY requirements.txt requirements.txt


# Copy the rest of the application code into the container
COPY . .
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt
RUN pip install pymongo
# Expose the port the app runs on
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the Flask application
CMD ["python", "-m", "flask", "run"]