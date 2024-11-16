#!/bin/bash

# Update system packages
echo "Updating package list..."
sudo apt update -y && sudo apt upgrade -y

# Install Docker
if ! [ -x "$(command -v docker)" ]; then
    echo "Installing Docker..."
    sudo apt install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    echo "Docker installed successfully."
else
    echo "Docker is already installed."
fi

# Install Docker Compose
if ! [ -x "$(command -v docker-compose)" ]; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose installed successfully."
else
    echo "Docker Compose is already installed."
fi

# Install Python3
if ! [ -x "$(command -v python3)" ]; then
    echo "Installing Python3..."
    sudo apt install -y python3 python3-pip
    echo "Python3 installed successfully."
else
    echo "Python3 is already installed."
fi

# Install ngrok
if ! [ -x "$(command -v ngrok)" ]; then
    echo "Installing ngrok..."
    wget -qO ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-linux-amd64.zip
    unzip ngrok.zip
    sudo mv ngrok /usr/local/bin/
    rm ngrok.zip
    echo "ngrok installed successfully."
else
    echo "ngrok is already installed."
fi

# Final confirmation
echo "Installation completed."
echo "Docker version: $(docker --version || echo 'Not installed')"
echo "Docker Compose version: $(docker-compose --version || echo 'Not installed')"
echo "Python version: $(python3 --version || echo 'Not installed')"
echo "ngrok version: $(ngrok version || echo 'Not installed')"
