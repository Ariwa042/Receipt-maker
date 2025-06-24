#!/bin/bash
# Install Playwright system dependencies
echo "Installing Playwright dependencies..."
apt-get update
apt-get install -y libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 \
    libxi-dev libxtst-dev libnss3 libcups2 libxss1 libxrandr2 \
    libgconf-2-4 libasound2 libatk1.0-0 libgtk-3-0 libgbm-dev

# Install Playwright browser
python -m playwright install chromium

echo "Playwright setup complete"
exit 0
