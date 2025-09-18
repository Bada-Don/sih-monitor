import os
import json
from sih_monitor import SIHSubmissionMonitor

def create_config_from_env():
    """Create config from environment variables for GitHub Actions"""
    config = {
        "email": {
            "enabled": True,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "harshitashwani@gmail.com",
            "sender_password": os.getenv('EMAIL_PASSWORD'),
            "recipient_email": "ashuharshit@gmail.com"
        },
        "whatsapp": {
            "enabled": bool(os.getenv('TWILIO_SID')),
            "twilio_sid": os.getenv('TWILIO_SID'),
            "twilio_token": os.getenv('TWILIO_TOKEN'),
            "from_number": "whatsapp:+14155238886",
            "to_number": "whatsapp:+917695513958"
        }
    }
    
    # Create problem config
    problem_config = {
        "problem_statement_id": os.getenv('PROBLEM_ID', '25057'),
        "description": "SIH 2025 Problem Statement ID to monitor",
        "last_updated": "2025-09-18",
        "notes": "Configured via environment variable PROBLEM_ID"
    }
    
    # Save configs temporarily
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    with open('problem_config.json', 'w') as f:
        json.dump(problem_config, f, indent=2)

def main():
    # Create config from environment
    create_config_from_env()
    
    # Run single check
    monitor = SIHSubmissionMonitor()
    monitor.load_state()
    monitor.check_submissions()

if __name__ == "__main__":
    main()