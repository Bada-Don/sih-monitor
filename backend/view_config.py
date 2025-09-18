#!/usr/bin/env python3
"""
Simple script to view the current SIH monitoring configuration
"""

import json
import os
from datetime import datetime

def view_config():
    """Display the current monitoring configuration"""
    print("🔍 SIH Monitoring Configuration")
    print("=" * 40)
    
    # Problem configuration
    problem_config_file = 'problem_config.json'
    if os.path.exists(problem_config_file):
        with open(problem_config_file, 'r') as f:
            problem_config = json.load(f)
        
        print(f"📋 Problem Statement Configuration:")
        print(f"   ID: {problem_config.get('problem_statement_id', 'Not set')}")
        print(f"   Description: {problem_config.get('description', 'Not set')}")
        print(f"   Last Updated: {problem_config.get('last_updated', 'Unknown')}")
        if problem_config.get('notes'):
            print(f"   Notes: {problem_config.get('notes')}")
    else:
        print("❌ Problem configuration file not found!")
    
    print()
    
    # Main configuration
    config_file = 'config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print(f"⚙️  Service Configuration:")
        print(f"   Email Notifications: {'✅ Enabled' if config.get('email', {}).get('enabled') else '❌ Disabled'}")
        print(f"   WhatsApp Notifications: {'✅ Enabled' if config.get('whatsapp', {}).get('enabled') else '❌ Disabled'}")
        
        if config.get('email', {}).get('enabled'):
            print(f"   Email Recipient: {config.get('email', {}).get('recipient_email', 'Not set')}")
        
        if config.get('whatsapp', {}).get('enabled'):
            print(f"   WhatsApp Number: {config.get('whatsapp', {}).get('to_number', 'Not set')}")
    else:
        print("❌ Main configuration file not found!")
    
    print()
    
    # Monitor state
    state_file = 'monitor_state.json'
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        print(f"📊 Current Monitor State:")
        print(f"   Last Count: {state.get('count', 'Unknown')}")
        print(f"   Last Refresh: {state.get('last_refresh', 'Unknown')}")
        print(f"   Monitoring ID: {state.get('target_id', state.get('problem_id', 'Unknown'))}")
        
        if state.get('error'):
            print(f"   ⚠️  Last Error: {state.get('error')}")
    else:
        print("📊 No monitor state found (first run)")
    
    print()
    print("💡 To update the problem ID, run:")
    print("   python update_problem_id.py <new_id>")

if __name__ == "__main__":
    view_config()