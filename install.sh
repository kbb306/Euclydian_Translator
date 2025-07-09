#!/bin/bash

echo "Updating package lists..."
sudo apt update

echo "Installing system dependencies..."
sudo apt install -y \
    python3-venv \
    python3-pip \
    libglib2.0-dev \
    libcairo2-dev \
    gir1.2-pango-1.0 \
    gir1.2-gtk-3.0 \
    libgirepository1.0-dev \
    python3-gi \
    python3-gi-cairo


