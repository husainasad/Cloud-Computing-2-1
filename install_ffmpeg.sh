#!/bin/bash

# Download ffmpeg and its md5 checksum
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz.md5

# Verify md5 checksum
md5sum -c ffmpeg-release-amd64-static.tar.xz.md5

# Extract ffmpeg archive
tar xvf ffmpeg-release-amd64-static.tar.xz

# Create directory for ffmpeg binaries
mkdir -p ffmpeg/bin

# Copy ffmpeg binary to the bin directory
cp ffmpeg-*/ffmpeg ffmpeg/bin/

# Zip the ffmpeg directory
cd ffmpeg
zip -r ../ffmpeg.zip .
cd ..