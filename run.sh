#!/bin/bash
# Run script for Skill-aware Chat Runtime

# Check if we're in the right directory
if [ ! -f "skill_chat/cli.py" ]; then
    echo "Error: Please run this script from the claude-skill-chat directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found"
    echo "Please run: ./quickstart.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if API key is set
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "⚠ Warning: DEEPSEEK_API_KEY not set"
    echo ""
    echo "Please set your DeepSeek API key:"
    echo "  export DEEPSEEK_API_KEY='your-key-here'"
    echo ""
    echo "Or add it to your ~/.bashrc or ~/.zshrc:"
    echo "  echo 'export DEEPSEEK_API_KEY=\"your-key\"' >> ~/.zshrc"
    echo ""
    read -p "Enter your DeepSeek API key (or press Ctrl+C to cancel): " api_key
    if [ -n "$api_key" ]; then
        export DEEPSEEK_API_KEY="$api_key"
        echo "✓ API key set for this session"
    else
        echo "No API key provided. Exiting."
        exit 1
    fi
fi

# Run the chat
echo ""
echo "=== Starting Skill-aware Chat ==="
echo "API: DeepSeek"
echo "Skills: ./demo_skills"
echo ""
echo "Commands:"
echo "  - Type your message and press Enter"
echo "  - Type 'exit' or 'quit' to exit"
echo "  - Type 'reset' to clear conversation history"
echo ""

chat-with-skills --skills-dir ./demo_skills --show-routing "$@"
