#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Install Playwright system dependencies
echo "Installing Playwright dependencies..."
apt-get update
apt-get install -y libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 \
    libxi-dev libxtst-dev libnss3 libcups2 libxss1 libxrandr2 \
    libgconf-2-4 libasound2 libatk1.0-0 libgtk-3-0 libgbm-dev \
    libnss3-dev libdrm-dev libxshmfence-dev fonts-noto-color-emoji \
    fonts-liberation fonts-freefont-ttf

# Create browser installation directory with proper permissions
echo "Setting up browser installation directory..."
mkdir -p /opt/render/.playwright
chmod -R 777 /opt/render/.playwright

# Install Playwright browser with specific path for Render.com
echo "Installing Playwright browsers..."
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/.playwright
python -m playwright install --with-deps chromium

# Set permissions on the installed browser
echo "Setting permissions for browser executables..."
chmod -R 755 /opt/render/.playwright

echo "Playwright setup complete for production environment"
exit 0
