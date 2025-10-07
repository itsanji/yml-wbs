#!/bin/bash

# WBS Dashboard Startup Script
# This script starts the dashboard server and opens it in your browser

echo "🕷️ Trip.com Crawler - WBS Dashboard"
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check if tasks.json exists
if [ ! -f "tasks.json" ]; then
    echo "❌ tasks.json not found in current directory."
    echo "Please make sure you're running this script from the wbs folder."
    exit 1
fi

# Make server.py executable
chmod +x server.py

echo "🚀 Starting dashboard server..."
echo "📁 Current directory: $(pwd)"
echo ""

# Start the server in background
python3 server.py &
SERVER_PID=$!

# Wait a moment for server to start
sleep 2

# Check if server started successfully
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Server started successfully (PID: $SERVER_PID)"
    echo ""
    echo "🌐 Dashboard URLs:"
    echo "   Main Dashboard: http://localhost:8000/dashboard.html"
    echo "   Tasks JSON:     http://localhost:8000/tasks.json"
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
