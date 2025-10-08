#!/bin/bash

# WBS Dashboard Startup Script
# This script starts the dashboard server and opens it in your browser

# Configuration - Task file name (can be overridden)
TASK_FILE="new_tasks.yaml"

echo "🕷️ Trip.com Crawler - WBS Dashboard"
echo "=================================="
echo "📋 Using task file: $TASK_FILE"
echo ""

# Show usage if help is requested
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "Usage: $0 [task_file.yaml]"
    echo ""
    echo "Examples:"
    echo "  $0                    # Use default tasks.yaml"
    echo "  $0 new_tasks.yaml    # Use new_tasks.yaml"
    echo "  TASK_FILE=my.yaml $0 # Use environment variable"
    echo ""
    echo "The script will start the dashboard server and open it in your browser."
    exit 0
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check if virtual environment exists, create if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if PyYAML is available, install if needed
if ! python3 -c "import yaml" &> /dev/null; then
    echo "📦 Installing PyYAML..."
    python3 -m pip install PyYAML
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install PyYAML"
        exit 1
    fi
    echo "✅ PyYAML installed successfully"
fi

# Check if the specified task file exists
if [ ! -f "$TASK_FILE" ]; then
    echo "❌ $TASK_FILE not found in current directory."
    echo "Please make sure the task file exists or specify a different one."
    echo "Usage: $0 [task_file.yaml]"
    echo "   or: TASK_FILE=my_tasks.yaml $0"
    exit 1
fi

# Make server.py executable
chmod +x server.py

echo "🚀 Starting dashboard server..."
echo "📁 Current directory: $(pwd)"
echo ""

# Start the server in background (using virtual environment)
export TASK_FILE="$TASK_FILE"
source venv/bin/activate && python3 server.py &
SERVER_PID=$!

# Wait a moment for server to start
sleep 2

# Check if server started successfully
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Server started successfully (PID: $SERVER_PID)"
    echo ""
    echo "🌐 Dashboard URLs:"
    echo "   Main Dashboard: http://localhost:8000/dashboard.html"
    echo "   Tasks YAML:     http://localhost:8000/$TASK_FILE"
    echo "   API Endpoints:  http://localhost:8000/api/"
    echo ""
    
    # Try to open in browser (macOS)
    if command -v open &> /dev/null; then
        echo "🔗 Opening dashboard in your default browser..."
        open "http://localhost:8000/dashboard.html"
    # Try to open in browser (Linux)
    elif command -v xdg-open &> /dev/null; then
        echo "🔗 Opening dashboard in your default browser..."
        xdg-open "http://localhost:8000/dashboard.html"
    # Try to open in browser (Windows/WSL)
    elif command -v cmd.exe &> /dev/null; then
        echo "🔗 Opening dashboard in your default browser..."
        cmd.exe /c start "http://localhost:8000/dashboard.html"
    else
        echo "💡 Please open http://localhost:8000/dashboard.html in your browser"
    fi
    
    echo ""
    echo "📝 Usage Instructions:"
    echo "   • View project progress and task status"
    echo "   • Assign tasks to team members"
    echo "   • Track time and update task progress"
    echo "   • Monitor risks and sprint progress"
    echo "   • Export project reports"
    echo ""
    echo "🛑 To stop the server, press Ctrl+C or run: kill $SERVER_PID"
    echo ""
    
    # Wait for server process
    wait $SERVER_PID
else
    echo "❌ Failed to start server"
    exit 1
fi
