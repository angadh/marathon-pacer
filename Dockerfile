# Use the official Python 3.11 base image
FROM python:3.11-slim-bookworm

# Install Python 3 and its development headers, and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip nginx gcc g++ make && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy your application code into the container
COPY . /app

# Install any Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose ports
EXPOSE 5001

CMD ["gunicorn", "--config", "gunicorn_configs.py", "-b", "0.0.0.0:5001", "app:app"]