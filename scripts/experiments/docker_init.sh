#!/bin/bash

# Install Docker
if rpm -q docker; then
  echo "docker already installed, skipping..."
else
  echo "Installing docker..."
  sudo yum install docker -y
fi

# Add group membership for the default ec2-user 
# so you can run all docker commands without using the sudo command
sudo usermod -a -G docker ec2-user

# Run subsequent commands in the current shell without using newgrp
(
  # Enable docker service at AMI boot time and start docker service
  sudo systemctl enable --now docker.service
  sudo systemctl start docker.service
  service docker status
)

# Check if the Docker image exists locally
if [[ "$(docker images -q <your_image> 2> /dev/null)" == "" ]]; then
  echo "Docker image not found locally. Pulling from Docker Hub..."
  docker pull <your_image>
else
  echo "Docker image found locally. Running the image..."
  docker run -it <your_image>
fi