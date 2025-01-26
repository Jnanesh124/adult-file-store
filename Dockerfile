FROM python:3.8-slim-buster

# Install dependencies for FFmpeg (curl, tar, and ffmpeg)
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Download and install FFmpeg from the heroku buildpack (if needed for a specific version)
RUN curl -L https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest/releases/download/v4.4/ffmpeg-linux-x64.tar.xz -o ffmpeg.tar.xz \
    && tar -xf ffmpeg.tar.xz \
    && mv ffmpeg-*/bin/* /usr/local/bin/ \
    && rm -rf ffmpeg.tar.xz ffmpeg-*

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
