#!/bin/bash

# Exit on errors or unset variables, and propagate errors in pipelines
set -euo pipefail

echo "Starting NVIDIA Container Toolkit and Driver installation..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required dependencies
echo "Checking prerequisites..."

# Check if Docker is installed
if ! command_exists docker; then
    echo "Docker is not installed. Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo systemctl enable docker
    sudo systemctl start docker
    echo "Docker installed successfully."
else
    echo "Docker is already installed."
fi

# Install ALSA utilities (optional)
if ! command_exists alsamixer; then
    echo "Installing ALSA utilities..."
    sudo apt-get install -y alsa-utils
else
    echo "ALSA utilities are already installed."
fi

# Install NVIDIA Container Toolkit
echo "Installing NVIDIA Container Toolkit..."
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
    sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list > /dev/null

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
echo "NVIDIA Container Toolkit installed successfully."

# Configure Docker to use NVIDIA runtime
echo "Configuring Docker to use NVIDIA Container Runtime..."
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
echo "Docker configured successfully."

# Install NVIDIA drivers
echo "Installing recommended NVIDIA drivers..."
sudo ubuntu-drivers autoinstall
echo "NVIDIA drivers installed successfully."

echo "Installation and configuration complete. Run sudo reboot to apply changes."
