import os
import json
import time
import sys

# Set UTF-8 encoding for Windows
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import threading

# Import the SIH monitor class
from sih_monitor import SIHSubmissionMonitor

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the monitor
monitor = SIHSubmissionMonitor()
last_refresh_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# State to store the current count
current_state = {
    "count": None,
    "last_refresh": last_refresh_time,
    "problem_id": monitor.target_id
}

# Lock for thread safety
state_lock = threading.Lock()

def update_submission_count():
    """Update the submission count and save to state"""
    global current_state, last_refresh_time
    
    try:
        # Fetch the page and parse the count
        html_content = monitor.fetch_page_content()
        count = monitor.parse_submission_count(html_content)
        
        # Update the state with thread safety
        with state_lock:
            previous_count = current_state.get("count")
            current_state["count"] = count
            current_state["problem_id"] = monitor.target_id  # Ensure problem_id is always current
            current_state["last_refresh"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Clear any previous error
            if "error" in current_state:
                del current_state["error"]
            
            # Save state to file for persistence
            with open('monitor_state.json', 'w') as f:
                json.dump(current_state, f)
            
            # If count changed and we have a previous count, send notifications
            if previous_count is not None and count != previous_count:
                try:
                    monitor.send_email_notification(count, previous_count)
                except Exception as email_err:
                    monitor.logger.error(f"Email notification error: {email_err}")
                
                try:
                    monitor.send_whatsapp_notification(count, previous_count)
                except Exception as whatsapp_err:
                    monitor.logger.error(f"WhatsApp notification error: {whatsapp_err}")
                
        return True
    except Exception as e:
        error_msg = str(e)
        monitor.logger.error(f"Error updating count: {error_msg}")
        
        # Handle different types of errors
        with state_lock:
            current_state["problem_id"] = monitor.target_id  # Ensure problem_id is always current
            current_state["last_refresh"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_state["error"] = error_msg
            
            # Only set count to 0 if it's not a 403 error (keep previous count for 403)
            if "403" not in error_msg and "Forbidden" not in error_msg:
                current_state["count"] = 0
            # For 403 errors, keep the previous count and add a warning
            elif "403" in error_msg or "Forbidden" in error_msg:
                current_state["error"] = "Website is blocking requests (403 Forbidden). This is likely due to anti-bot measures."
                current_state["status"] = "blocked"
            
            # Save state to file for persistence
            with open('monitor_state.json', 'w') as f:
                json.dump(current_state, f)
        return False

# Try to load previous state if it exists
try:
    if os.path.exists('monitor_state.json'):
        with open('monitor_state.json', 'r') as f:
            loaded_state = json.load(f)
            # Update current_state with loaded data
            current_state.update(loaded_state)
            # Ensure problem_id is set correctly from monitor
            current_state["problem_id"] = monitor.target_id
except Exception as e:
    monitor.logger.error(f"Error loading previous state: {e}")

# Ensure problem_id is always set correctly
current_state["problem_id"] = monitor.target_id

# Initialize scheduler for hourly updates
scheduler = BackgroundScheduler()
scheduler.add_job(update_submission_count, 'interval', hours=1)
scheduler.start()

# API Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "problem_id": monitor.target_id
    })

@app.route('/api/count', methods=['GET'])
def get_count():
    """Get the current submission count"""
    return jsonify(current_state)

@app.route('/api/refresh', methods=['POST'])
def refresh_count():
    """Manually refresh the submission count"""
    success = update_submission_count()
    return jsonify({
        "success": success,
        "data": current_state if success else None,
        "message": "Count refreshed successfully" if success else "Failed to refresh count"
    })

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get the current configuration (excluding sensitive data)"""
    # Create a copy of the config without sensitive information
    safe_config = {
        "target_problem_id": monitor.target_id,
        "email_enabled": monitor.config.get("email", {}).get("enabled", False),
        "whatsapp_enabled": monitor.config.get("whatsapp", {}).get("enabled", False)
    }
    return jsonify(safe_config)

@app.route('/api/problem-config', methods=['GET'])
def get_problem_config():
    """Get the current problem statement configuration"""
    return jsonify(monitor.problem_config)

@app.route('/api/problem-config', methods=['POST'])
def update_problem_config():
    """Update the problem statement configuration"""
    try:
        data = request.get_json()
        
        if not data or 'problem_statement_id' not in data:
            return jsonify({
                "success": False,
                "message": "problem_statement_id is required"
            }), 400
        
        # Update the problem config
        monitor.problem_config['problem_statement_id'] = data['problem_statement_id']
        monitor.problem_config['last_updated'] = datetime.now().strftime("%Y-%m-%d")
        
        if 'description' in data:
            monitor.problem_config['description'] = data['description']
        if 'notes' in data:
            monitor.problem_config['notes'] = data['notes']
        
        # Save to file
        with open('problem_config.json', 'w') as f:
            json.dump(monitor.problem_config, f, indent=2)
        
        # Update the monitor's target_id
        monitor.target_id = data['problem_statement_id']
        
        # Reset the state since we're monitoring a new problem
        with state_lock:
            current_state["count"] = None
            current_state["problem_id"] = monitor.target_id
            current_state["last_refresh"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if "error" in current_state:
                del current_state["error"]
        
        return jsonify({
            "success": True,
            "message": "Problem configuration updated successfully",
            "data": monitor.problem_config
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error updating problem configuration: {str(e)}"
        }), 500

@app.route('/api/debug', methods=['GET'])
def debug_info():
    """Debug endpoint to help troubleshoot issues"""
    try:
        import requests
        debug_info = {
            "timestamp": datetime.now().isoformat(),
            "target_url": monitor.url,
            "target_id": monitor.target_id,
            "current_state": current_state.copy(),
            "environment": {
                "python_version": sys.version,
                "requests_version": requests.__version__,
                "has_proxy": bool(os.environ.get('HTTP_PROXY') or os.environ.get('HTTPS_PROXY'))
            }
        }
        
        # Test basic connectivity
        try:
            session = monitor.get_session_with_headers()
            response = session.head(monitor.url, timeout=10)
            debug_info["connectivity_test"] = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "success": True
            }
        except Exception as e:
            debug_info["connectivity_test"] = {
                "error": str(e),
                "success": False
            }
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# Serve static files from frontend build directory
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path and os.path.exists(os.path.join('../frontend/build', path)):
        return send_from_directory('../frontend/build', path)
    else:
        return send_from_directory('../frontend/build', 'index.html')

if __name__ == '__main__':
    # Initial update on startup
    update_submission_count()
    # Render provides PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)