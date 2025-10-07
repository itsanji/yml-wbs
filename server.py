#!/usr/bin/env python3
"""
Simple HTTP server for the WBS Dashboard
Serves the dashboard.html and tasks.json files with CORS enabled
"""

import http.server
import socketserver
import json
import os
from urllib.parse import urlparse, parse_qs
import datetime

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS for all requests
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # API endpoints
        if parsed_path.path == '/api/tasks':
            self.serve_tasks_api()
        elif parsed_path.path == '/api/stats':
            self.serve_stats_api()
        elif parsed_path.path == '/api/team':
            self.serve_team_api()
        else:
            # Serve static files
            super().do_GET()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/tasks/assign':
            self.handle_task_assignment()
        elif parsed_path.path == '/api/tasks/update':
            self.handle_task_update()
        else:
            self.send_error(404, "API endpoint not found")

    def serve_tasks_api(self):
        """Serve tasks data as JSON API"""
        try:
            with open('tasks.json', 'r') as f:
                data = json.load(f)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        except FileNotFoundError:
            self.send_error(404, "tasks.json not found")
        except json.JSONDecodeError:
            self.send_error(500, "Invalid JSON in tasks.json")

    def serve_stats_api(self):
        """Serve project statistics"""
        try:
            with open('tasks.json', 'r') as f:
                data = json.load(f)
            
            # Calculate stats
            tasks = data.get('tasks', [])
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t['status'] == 'complete'])
            in_progress_tasks = len([t for t in tasks if t['status'] == 'partial'])
            not_started_tasks = len([t for t in tasks if t['status'] == 'not_started'])
            
            total_planned_hours = sum(t['planned_hours'] for t in tasks)
            total_actual_hours = sum(t['actual_hours'] for t in tasks)
            completion_percentage = (total_actual_hours / total_planned_hours * 100) if total_planned_hours > 0 else 0
            
            stats = {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'not_started_tasks': not_started_tasks,
                'completion_percentage': round(completion_percentage, 1),
                'total_planned_hours': total_planned_hours,
                'total_actual_hours': total_actual_hours,
                'hours_remaining': total_planned_hours - total_actual_hours
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode())
        except Exception as e:
            self.send_error(500, f"Error calculating stats: {str(e)}")

    def serve_team_api(self):
        """Serve team data with current assignments"""
        try:
            with open('tasks.json', 'r') as f:
                data = json.load(f)
            
            team = data.get('team', [])
            tasks = data.get('tasks', [])
            
            # Add current assignments to team members
            for member in team:
                member_tasks = [t for t in tasks if t['assignee'] == member['name'] and t['status'] != 'complete']
                member['active_tasks'] = len(member_tasks)
                member['active_task_names'] = [t['name'] for t in member_tasks[:3]]  # Show first 3
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(team).encode())
        except Exception as e:
            self.send_error(500, f"Error getting team data: {str(e)}")

    def handle_task_assignment(self):
        """Handle task assignment requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            task_id = request_data.get('task_id')
            assignee = request_data.get('assignee')
            
            if not task_id or not assignee:
                self.send_error(400, "Missing task_id or assignee")
                return
            
            # Load current data
            with open('tasks.json', 'r') as f:
                data = json.load(f)
            
            # Find and update task
            task_found = False
            for task in data['tasks']:
                if task['id'] == task_id:
                    task['assignee'] = assignee
                    task_found = True
                    break
            
            if not task_found:
                self.send_error(404, "Task not found")
                return
            
            # Save updated data
            with open('tasks.json', 'w') as f:
                json.dump(data, f, indent=2)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'message': f'Task {task_id} assigned to {assignee}'}).encode())
            
        except Exception as e:
            self.send_error(500, f"Error assigning task: {str(e)}")

    def handle_task_update(self):
        """Handle task status/progress updates"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            task_id = request_data.get('task_id')
            updates = request_data.get('updates', {})
            
            if not task_id:
                self.send_error(400, "Missing task_id")
                return
            
            # Load current data
            with open('tasks.json', 'r') as f:
                data = json.load(f)
            
            # Find and update task
            task_found = False
            for task in data['tasks']:
                if task['id'] == task_id:
                    # Update allowed fields
                    allowed_fields = ['status', 'actual_hours', 'assignee', 'notes']
                    for field in allowed_fields:
                        if field in updates:
                            task[field] = updates[field]
                    
                    # Recalculate hours_remaining
                    task['hours_remaining'] = max(0, task['planned_hours'] - task['actual_hours'])
                    
                    task_found = True
                    break
            
            if not task_found:
                self.send_error(404, "Task not found")
                return
            
            # Save updated data
            with open('tasks.json', 'w') as f:
                json.dump(data, f, indent=2)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'message': f'Task {task_id} updated'}).encode())
            
        except Exception as e:
            self.send_error(500, f"Error updating task: {str(e)}")

    def log_message(self, format, *args):
        """Override to add timestamp to logs"""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def main():
    PORT = 8000
    
    # Change to the directory containing the files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"🚀 Starting WBS Dashboard Server...")
    print(f"📁 Serving files from: {script_dir}")
    print(f"🌐 Dashboard URL: http://localhost:{PORT}/dashboard.html")
    print(f"📊 API Base URL: http://localhost:{PORT}/api/")
    print(f"📋 Tasks JSON: http://localhost:{PORT}/tasks.json")
    print(f"\n💡 Available API endpoints:")
    print(f"   GET  /api/tasks  - Get all tasks")
    print(f"   GET  /api/stats  - Get project statistics")
    print(f"   GET  /api/team   - Get team data with assignments")
    print(f"   POST /api/tasks/assign - Assign task to team member")
    print(f"   POST /api/tasks/update - Update task status/progress")
    print(f"\n🛑 Press Ctrl+C to stop the server\n")
    
    try:
        with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {PORT} is already in use. Try a different port or stop the existing server.")
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
