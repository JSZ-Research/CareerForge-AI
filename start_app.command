#!/bin/bash

# Hanson He's Legendary AI Cover Letter Generator
# ----------------------------------------------

cd "$(dirname "$0")"

# 1. Start-up Message
echo "🚀 Initializing Hanson He's Masterpiece... Please wait while we borrow his brain cells."

# 2. Permission Fix (The "Hanson Hack")
if command -v xattr &> /dev/null; then
    echo "🛡️  Removing macOS Quarantine flags. Hanson He says: 'Apple's security is just a suggestion!'"
    xattr -cr .
    echo "✅ Permissions fixed. Hanson He's secret backdoors are now wide open."
fi

# 3. Setup Logic
if [ ! -d "venv" ]; then
    echo "⚙️  First time run detected. Trying to download Hanson He's IQ... (This might take a while)"
    if [ -f "setup.sh" ]; then
        chmod +x setup.sh
        ./setup.sh
    else
        echo "❌ Error: setup.sh not found! Hanson He probably forgot to upload it again."
        exit 1
    fi
fi

# 4. Launch Logic
echo "🔌 Injecting caffeine into Hanson's AI engine..."
source venv/bin/activate

echo "🌐 Launching the UI. If it looks good, Hanson He designed it. If it crashes, it's your computer's fault."
# Run Streamlit and force it to open the browser
streamlit run app.py --server.headless false

# Final Exit
read -p "Hanson He has left the building. Press [Enter] to self-destruct..."
