import os
import json

def load_config():
    """Load configuration from environment variables or config file"""
    
    # Check if we're in production (Render sets this)
    is_production = os.getenv('RENDER') or os.getenv('PRODUCTION')
    
    if is_production:
        # Production: Load from environment variables
        config = {
            "email": {
                "enabled": os.getenv('EMAIL_ENABLED', 'true').lower() == 'true',
                "smtp_server": os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                "smtp_port": int(os.getenv('SMTP_PORT', '587')),
                "sender_email": os.getenv('SENDER_EMAIL'),
                "sender_password": os.getenv('SENDER_PASSWORD'),
                "recipient_email": os.getenv('RECIPIENT_EMAIL')
            },
            "whatsapp": {
                "enabled": os.getenv('WHATSAPP_ENABLED', 'true').lower() == 'true',
                "twilio_sid": os.getenv('TWILIO_SID'),
                "twilio_token": os.getenv('TWILIO_TOKEN'),
                "from_number": os.getenv('TWILIO_FROM_NUMBER'),
                "to_number": os.getenv('TWILIO_TO_NUMBER')
            }
        }
        
        # Validate required environment variables
        required_vars = []
        if config['email']['enabled']:
            required_vars.extend(['SENDER_EMAIL', 'SENDER_PASSWORD', 'RECIPIENT_EMAIL'])
        if config['whatsapp']['enabled']:
            required_vars.extend(['TWILIO_SID', 'TWILIO_TOKEN', 'TWILIO_FROM_NUMBER', 'TWILIO_TO_NUMBER'])
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return config
    
    else:
        # Development: Load from config.json
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError("config.json not found. Please create it or set environment variables.")

def load_problem_config():
    """Load problem configuration from environment or file"""
    
    # Check if problem ID is set via environment variable
    problem_id = os.getenv('PROBLEM_ID')
    
    if problem_id:
        return {
            "problem_statement_id": problem_id,
            "description": f"SIH 2025 Problem Statement ID {problem_id} (from environment)",
            "last_updated": "2025-09-18",
            "notes": "Configured via PROBLEM_ID environment variable"
        }
    
    else:
        # Load from file
        try:
            with open('problem_config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default fallback
            return {
                "problem_statement_id": "25057",
                "description": "SIH 2025 Problem Statement ID (default)",
                "last_updated": "2025-09-18",
                "notes": "Default configuration"
            }