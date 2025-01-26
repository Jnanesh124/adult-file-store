FROM python:3.8-slim-buster

# Install dependencies for FFmpeg (curl, ffmpeg, and other tools)
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set up the work directory
WORKDIR /app

# Install requirements from requirements.txt
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy your application code
COPY . .

# Expose the desired port
EXPOSE 8585

# Command to run the application
CMD ["python3", "main.py"]
