#!/bin/bash
# Quick start script for Skill-aware Chat Runtime

echo "=== Skill-aware Chat Runtime - Quick Start ==="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.10 or higher required. Found: Python $python_version"
    exit 1
fi

echo "✓ Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    if python3 -m venv venv; then
        echo "✓ Virtual environment created successfully"
    else
        echo "✗ Failed to create virtual environment"
        echo ""
        echo "Please try manually:"
        echo "  python3 -m venv venv"
        echo ""
        echo "If that fails, you may need to install python3-venv:"
        echo "  sudo apt-get install python3-venv  # Debian/Ubuntu"
        echo "  sudo yum install python3-venv      # RHEL/CentOS"
        exit 1
    fi
else
    echo "✓ Virtual environment already exists"
fi

# Verify venv/bin/activate exists
if [ ! -f "venv/bin/activate" ]; then
    echo "✗ Error: venv/bin/activate not found"
    echo ""
    echo "Virtual environment may be corrupted. Try:"
    echo "  rm -rf venv"
    echo "  python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

if [ -z "$VIRTUAL_ENV" ]; then
    echo "✗ Failed to activate virtual environment"
    exit 1
fi

echo "✓ Virtual environment activated: $VIRTUAL_ENV"
echo ""

# Check if API key is set
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "⚠ Warning: DEEPSEEK_API_KEY not set"
    echo "Please set your DeepSeek API key:"
    echo "  export DEEPSEEK_API_KEY='your-deepseek-key-here'"
    echo ""
    echo "Get your API key from: https://platform.deepseek.com/"
    echo ""
    echo "Or copy .env.example to .env and fill in your key"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Set DeepSeek API configuration
export OPENAI_API_KEY="${DEEPSEEK_API_KEY}"
export OPENAI_BASE_URL="https://api.deepseek.com/v1"

# Install dependencies
echo ""
echo "Installing dependencies..."
if pip install -q -r requirements.txt; then
    echo "✓ Dependencies installed"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

# Install package
echo "Installing skill-chat..."
if pip install -q -e .; then
    echo "✓ skill-chat installed"
else
    echo "✗ Failed to install skill-chat"
    exit 1
fi

echo ""
echo "✓ Installation complete!"
echo ""
echo "=== Demo Skills Available ==="
ls -1 demo_skills/ 2>/dev/null || echo "(demo_skills directory not found)"
echo ""
echo "=== Run the chat ==="
echo "Virtual environment is already active. Simply run:"
echo ""
echo "  chat-with-skills --skills-dir ./demo_skills --show-routing"
echo ""
echo "Or with explicit model names:"
echo "  chat-with-skills --skills-dir ./demo_skills --show-routing --chat-model deepseek-chat --router-model deepseek-chat"
echo ""
echo "To deactivate virtual environment later: deactivate"
echo ""
