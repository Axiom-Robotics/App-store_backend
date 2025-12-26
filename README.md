# Axiom OS App Store Backend

Cloud-based backend API for the Axiom OS App Store. Deployed on Railway, this service provides app metadata, user management, and installation endpoints for all Axiom-powered robots.

## 🚀 Live API

**Production:** `https://axiom-appstore.up.railway.app` (Update after deployment)

## 📋 API Endpoints

### Apps Management
- `GET /api/apps` - Retrieve all available apps
- `GET /api/apps/<app_id>` - Get specific app details
- `POST /api/apps` - Publish a new app
- `PUT /api/apps/<app_id>` - Update app metadata
- `DELETE /api/apps/<app_id>` - Remove an app

### User Management
- `GET /api/users` - Get all registered users
- `GET /api/users/<user_id>` - Get user profile
- `POST /api/users` - Register new user

### System
- `GET /health` - Health check endpoint

## 🏗️ Architecture

Robot/Desktop → Local Server → Railway API → JSON Storage
(localhost) (Cloud) (apps.json)


## 📂 Files

- **api_server.py** - Main Flask application
- **apps.json** - App store catalog
- **users.json** - User database
- **requirements.txt** - Python dependencies
- **Procfile** - Railway deployment config

## 🛠️ Local Development

Install dependencies

pip install -r requirements.txt
Run server

python api_server.py
Server starts at http://localhost:5000


## 🚢 Deployment

Automatically deployed to Railway from `main` branch.

## 🔗 Related Repositories

- [robot-apps](https://github.com/Axiom-Robotics/robot-apps) - Robot application code

## 📄 License

MIT License

