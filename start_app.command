#!/bin/bash

# AI Cover Letter Generator - One-Click Launcher
# ----------------------------------------------

# 1. Set Working Directory
# Navigate to the folder where this script lives, so it works from anywhere.
cd "$(dirname "$0")"

echo "🚀 Launching AI Cover Letter Generator..."

# 2. The "Magic" Permission Fix
# Recursively remove macOS 'Quarantine' flags from all files in this folder to stop permission pop-ups.
if command -v xattr &> /dev/null; then
    echo "🛡️  Fixing macOS permissions (removing Quarantine flags)..."
    xattr -cr .
    echo "✅ Permissions fixed."
fi

# 3. Auto-Install Logic
# Check if venv exists. If not, run setup.sh.
if [ ! -d "venv" ]; then
    echo "⚙️  First time run detected. Running setup..."
    if [ -f "setup.sh" ]; then
        chmod +x setup.sh
        ./setup.sh
    else
        echo "❌ Error: setup.sh not found!"
        exit 1
    fi
fi

# 4. Launch Logic
echo "🔌 Activating environment..."
source venv/bin/activate

echo "🌐 Starting Streamlit App..."
# Run Streamlit and force it to open the browser
streamlit run app.py --server.headless false

# Keep window open if streamlit crashes immediately
read -p "Press [Enter] to close..."
