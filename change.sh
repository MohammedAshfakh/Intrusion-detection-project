#!/bin/bash

# Directory containing your files
ROOT_DIR="/root/intrusion-detection-project-ML"

# Set this to either "Home" or "Control Panel"
HOME_LABEL="Control Panel"

find "$ROOT_DIR" -type f \( -name "*.html" -o -name "*.php" -o -name "*.js" \) | while read -r file
do
    sed -i \
        -e "s|<a href=\"/\">Home</a>|<a href=\"/\">$HOME_LABEL</a>|g" \
        -e "s|<a href=\"/\">Control Panel</a>|<a href=\"/\">$HOME_LABEL</a>|g" \
        -e 's|<a href="/dashboard">Dashboard</a>|<a href="/dashboard">Security Dashboard</a>|g' \
        -e 's|<a href="/scan">Live Scan</a>|<a href="/scan">Threat Scanner</a>|g' \
        -e 's|<a href="/analytics">Analytics</a>|<a href="/analytics">Intelligence Hub</a>|g' \
        -e 's|<a href="/about">About</a>|<a href="/about">Documentation</a>|g' \
        "$file"
done

echo "Done."
