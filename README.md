# SIH Submission Monitor

A web application to monitor submission counts for SIH problems. The application automatically refreshes data every hour and allows manual refreshes with a single click.

## Project Structure

- **Backend**: Flask API that scrapes the SIH website and provides endpoints for the frontend
- **Frontend**: React application with a clean UI to display submission counts

## Deployment Instructions

### Backend Deployment (Render)

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: sih-monitor-backend
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && gunicorn app:app`
   - **Environment Variables**: Add any necessary environment variables (SMTP credentials, etc.)

### Frontend Deployment (Vercel)

1. Create a new project on Vercel
2. Connect your GitHub repository
3. Configure the project:
   - **Framework Preset**: Create React App
   - **Root Directory**: frontend
   - **Environment Variables**: Set `REACT_APP_API_URL` to your Render backend URL

## Local Development

### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Features

- Automatic hourly refresh of submission count
- Manual refresh with a single click
- Clean, responsive UI
- Email and WhatsApp notifications when count changes (configurable)