#!/usr/bin/env python3
"""
Simple script to update the Problem Statement ID for SIH monitoring
Usage: python update_problem_id.py <new_problem_id>
"""

import sys
import json
import os
from datetime import datetime

def update_problem_id(new_id, description=None):
    """Update the problem statement ID in the configuration"""
    config_file = 'problem_config.json'
    
    try:
        # Load existing config or create new one
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Update the configuration
        old_id = config.get('problem_statement_id', 'None')
        config['problem_statement_id'] = new_id
        config['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if description:
            config['description'] = description
        elif 'description' not in config:
            config['description'] = f"SIH 2025 Problem Statement ID {new_id} monitoring"
        
        if 'notes' not in config:
            config['notes'] = "Updated via update_problem_id.py script"
        
        # Save the updated configuration
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Successfully updated Problem Statement ID:")
        print(f"   Old ID: {old_id}")
        print(f"   New ID: {new_id}")
        print(f"   Config file: {config_file}")
        print(f"\n📝 Note: Restart the monitoring service to apply changes.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating problem ID: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python update_problem_id.py <new_problem_id> [description]")
        print("Example: python update_problem_id.py 25058 'New problem statement'")
        sys.exit(1)
    
    new_id = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Validate the ID (should be numeric)
    if not new_id.isdigit():
        print(f"❌ Error: Problem ID should be numeric, got: {new_id}")
        sys.exit(1)
    
    success = update_problem_id(new_id, description)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()