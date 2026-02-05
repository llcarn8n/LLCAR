#!/bin/bash
# Installation script for LLCAR Video Processing Pipeline

set -e

echo "=============================================="
echo "LLCAR Video Processing Pipeline - Installation"
echo "=============================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python 3.8 or higher is required (found $PYTHON_VERSION)"
    exit 1
fi

echo "✓ Python $PYTHON_VERSION detected"

# Check for FFmpeg
echo ""
echo "Checking for FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "Warning: FFmpeg is not installed"
    echo "Please install FFmpeg:"
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org/download.html"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ FFmpeg detected"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
echo "This may take several minutes..."

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "Error: requirements.txt not found"
    exit 1
fi

# Download NLTK data
echo ""
echo "Downloading NLTK data..."
python3 -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)"
echo "✓ NLTK data downloaded"

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p output models input
echo "✓ Directories created"

# Setup environment file
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "IMPORTANT: Edit .env file and add your HuggingFace token"
    echo "Get your token from: https://huggingface.co/settings/tokens"
else
    echo "✓ .env file already exists"
fi

# Test installation
echo ""
echo "Testing installation..."
if python3 test_pipeline.py; then
    echo ""
    echo "=============================================="
    echo "Installation completed successfully!"
    echo "=============================================="
    echo ""
    echo "Next steps:"
    echo "1. Edit .env and add your HuggingFace token (HF_TOKEN)"
    echo "2. Activate the virtual environment: source venv/bin/activate"
    echo "3. Run the pipeline: python main.py --help"
    echo ""
    echo "Example usage:"
    echo "  python main.py --video input/video.mp4 --language en"
    echo ""
else
    echo ""
    echo "Warning: Some tests failed, but installation may still work"
    echo "Check error messages above"
fi
