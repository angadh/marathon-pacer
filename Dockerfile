# Use an official Python runtime as a base image
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application files into the container
COPY . .

# Expose the port your Flask app runs on
EXPOSE 5001

# Command to run the Flask application
CMD ["python", "app.py"]