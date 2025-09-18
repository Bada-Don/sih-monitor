# SIH Monitor Configuration Guide

This guide explains how to easily configure and manage the Problem Statement ID for SIH monitoring.

## Configuration Files

### 1. `problem_config.json` - Problem Statement Configuration
This dedicated file contains only the Problem Statement ID and related metadata:

```json
{
  "problem_statement_id": "25057",
  "description": "SIH 2025 Problem Statement ID to monitor",
  "last_updated": "2025-09-18",
  "notes": "Change this ID to monitor a different problem statement"
}
```

### 2. `config.json` - Service Configuration
Contains email and WhatsApp notification settings (sensitive credentials).

## Easy Configuration Management

### View Current Configuration
```bash
python view_config.py
```

### Update Problem Statement ID
```bash
# Update just the ID
python update_problem_id.py 25058

# Update ID with description
python update_problem_id.py 25058 "New problem statement description"
```

### Manual Configuration
Edit `problem_config.json` directly:
1. Change the `problem_statement_id` value
2. Update `last_updated` to current date
3. Restart the monitoring service

## API Endpoints

### Get Problem Configuration
```bash
GET /api/problem-config
```

### Update Problem Configuration
```bash
POST /api/problem-config
Content-Type: application/json

{
  "problem_statement_id": "25058",
  "description": "Updated description",
  "notes": "Updated via API"
}
```

## Important Notes

1. **Restart Required**: After changing the problem ID, restart the monitoring service to apply changes
2. **Validation**: Problem IDs should be numeric strings
3. **State Reset**: Changing the problem ID resets the monitoring state (count history)
4. **Backup**: The system automatically backs up the previous configuration

## Troubleshooting

- If `problem_config.json` doesn't exist, it will be created automatically with default values
- Check `view_config.py` output to verify current settings
- Monitor logs in `sih_monitor.log` for any configuration issues