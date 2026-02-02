#!/bin/bash

# AI Cover Letter Generator Setup Script
# --------------------------------------

set -e # Exit immediately if a command exits with a non-zero status.

echo "🚀 Starting AI Cover Letter Generator Setup..."

# Phase 1: System Level
echo ""
echo "📦 Phase 1: Checking System Dependencies..."

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found."
    read -p "Do you want to install Homebrew now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🍺 Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        echo "❌ Homebrew is required to proceed. Exiting."
        exit 1
    fi
else
    echo "✅ Homebrew is found."
fi

# Check for Python3 using Homebrew
if ! brew list python3 &> /dev/null; then
    echo "🐍 Python3 not found in Homebrew. Installing..."
    brew install python3
else
    echo "✅ Python3 is installed."
fi

# Phase 2: Project Level
echo ""
echo "🛠️ Phase 2: Setting up Project Environment..."

# Check requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found! Please check your project folder."
    exit 1
fi

# Create Virtual Environment
echo "🌱 Creating virtual environment..."
python3 -m venv venv

# Activate and Install
echo "🔌 Activating virtual environment and installing libraries..."
source venv/bin/activate

echo "⬇️ Installing core components: Streamlit, OpenAI, PyPDF2, python-docx, fpdf2..."
if pip install -r requirements.txt; then
    echo "✅ Dependencies installed successfully."
else
    echo "❌ Failed to install dependencies. Please check the error log above."
    exit 1
fi

# Phase 3: Launch Setup
echo ""
echo "🚀 Phase 3: Finalizing..."

# Create run.sh
echo "#!/bin/bash" > run.sh
echo "source venv/bin/activate" >> run.sh
echo "streamlit run app.py" >> run.sh
chmod +x run.sh

echo "✅ Created 'run.sh' for easy launching."

echo ""
echo "🎉 Environment Ready! Type './run.sh' to start the App."
