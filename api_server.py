from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime

# Create Flask app (this is our web server)
app = Flask(__name__)

# CORS allows your local laptop to talk to this server
CORS(app)

# File names where data is stored
APPS_FILE = 'apps.json'
USERS_FILE = 'users.json'

# ============== HELPER FUNCTIONS ==============

def load_json(filename, default=[]):
    """
    Load data from JSON file
    Why: We need to read the apps/users data to send back to clients
    """
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return default  # Return empty list if file doesn't exist

def save_json(filename, data):
    """
    Save data to JSON file
    Why: When someone adds/updates an app, we need to save it permanently
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

# ============== APP STORE API ENDPOINTS ==============

@app.route('/api/apps', methods=['GET'])
def get_apps():
    """
    GET /api/apps - Returns all apps in the store
    Why: When your app store UI opens, it calls this to show all available apps
    Example response: {"success": true, "apps": [...], "count": 5}
    """
    apps = load_json(APPS_FILE, [])
    return jsonify({
        "success": True, 
        "apps": apps, 
        "count": len(apps)
    })

@app.route('/api/apps/<app_id>', methods=['GET'])
def get_app(app_id):
    """
    GET /api/apps/12345 - Returns one specific app
    Why: When user clicks on an app, get detailed info about that app only
    """
    apps = load_json(APPS_FILE, [])
    # Find the app with matching ID
    app = next((a for a in apps if a.get('id') == app_id), None)
    
    if app:
        return jsonify({"success": True, "app": app})
    else:
        return jsonify({"success": False, "error": "App not found"}), 404

@app.route('/api/apps', methods=['POST'])
def add_app():
    """
    POST /api/apps - Add a new app to the store
    Why: When a developer publishes a new app, this saves it
    """
    apps = load_json(APPS_FILE, [])
    new_app = request.json  # Get the app data sent by client
    new_app['created_at'] = datetime.now().isoformat()  # Add timestamp
    apps.append(new_app)
    save_json(APPS_FILE, apps)
    return jsonify({"success": True, "message": "App added", "app": new_app})

@app.route('/api/apps/<app_id>', methods=['PUT'])
def update_app(app_id):
    """
    PUT /api/apps/12345 - Update an existing app
    Why: When developer updates their app description/version, this saves changes
    """
    apps = load_json(APPS_FILE, [])
    for i, app in enumerate(apps):
        if app.get('id') == app_id:
            # Merge old data with new data
            apps[i] = {**app, **request.json}
            apps[i]['updated_at'] = datetime.now().isoformat()
            save_json(APPS_FILE, apps)
            return jsonify({"success": True, "app": apps[i]})
    
    return jsonify({"success": False, "error": "App not found"}), 404

@app.route('/api/apps/<app_id>', methods=['DELETE'])
def delete_app(app_id):
    """
    DELETE /api/apps/12345 - Remove an app from store
    Why: If an app is deprecated or removed, this deletes it
    """
    apps = load_json(APPS_FILE, [])
    apps = [a for a in apps if a.get('id') != app_id]  # Keep all except this one
    save_json(APPS_FILE, apps)
    return jsonify({"success": True, "message": "App deleted"})

# ============== USER MANAGEMENT ==============

@app.route('/api/users', methods=['GET'])
def get_users():
    """
    GET /api/users - Returns all users
    Why: For displaying user list or checking user permissions
    """
    users = load_json(USERS_FILE, [])
    return jsonify({"success": True, "users": users})

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """
    GET /api/users/user123 - Get specific user info
    Why: For user profile pages or authentication
    """
    users = load_json(USERS_FILE, [])
    user = next((u for u in users if u.get('id') == user_id), None)
    
    if user:
        return jsonify({"success": True, "user": user})
    return jsonify({"success": False, "error": "User not found"}), 404

@app.route('/api/users', methods=['POST'])
def add_user():
    """
    POST /api/users - Register a new user
    Why: When someone creates an account
    """
    users = load_json(USERS_FILE, [])
    new_user = request.json
    new_user['created_at'] = datetime.now().isoformat()
    users.append(new_user)
    save_json(USERS_FILE, users)
    return jsonify({"success": True, "user": new_user})

# ============== HEALTH CHECK ==============

@app.route('/health', methods=['GET'])
def health():
    """
    GET /health - Check if server is running properly
    Why: Railway uses this to monitor if your app is alive
    """
    apps_count = len(load_json(APPS_FILE, []))
    users_count = len(load_json(USERS_FILE, []))
    return jsonify({
        "status": "healthy",
        "apps_count": apps_count,
        "users_count": users_count
    })

# ============== START SERVER ==============

if __name__ == '__main__':
    # Railway sets PORT environment variable automatically
    port = int(os.environ.get('PORT', 5000))
    # Run server accessible from internet (0.0.0.0)
    app.run(host='0.0.0.0', port=port, debug=False)

