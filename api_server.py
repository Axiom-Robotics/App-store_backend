from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime

# ============== FLASK APP SETUP ==============

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)  # Allow requests from any origin

# Data file paths
APPS_FILE = 'apps.json'
USERS_FILE = 'users.json'

# ============== HELPER FUNCTIONS ==============

def load_json(filename, default=None):
    """Load data from JSON file"""
    if default is None:
        default = {} if filename == USERS_FILE else []
    
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return default
    return default

def save_json(filename, data):
    """Save data to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return False

# ============== FRONTEND ROUTES ==============

@app.route('/')
def serve_frontend():
    """Serve main app store page"""
    return send_from_directory('static', 'index.html')

@app.route('/index_1.html')
def serve_alternate_frontend():
    """Serve alternate frontend"""
    return send_from_directory('static', 'index_1.html')

@app.route('/<path:path>')
def serve_static_files(path):
    """Serve static assets (CSS, JS, images, plugins)"""
    try:
        return send_from_directory('static', path)
    except Exception as e:
        return jsonify({"error": "File not found", "path": path}), 404

# ============== APPS API ==============

@app.route('/api/apps', methods=['GET'])
def get_apps():
    """Get all apps"""
    apps = load_json(APPS_FILE, [])
    return jsonify({
        "success": True,
        "apps": apps,
        "count": len(apps)
    })

@app.route('/api/apps/<app_id>', methods=['GET'])
def get_app(app_id):
    """Get single app by ID"""
    apps = load_json(APPS_FILE, [])
    app = next((a for a in apps if a.get('id') == app_id), None)
    
    if app:
        return jsonify({"success": True, "app": app})
    return jsonify({"success": False, "error": "App not found"}), 404

@app.route('/api/apps', methods=['POST'])
def add_app():
    """Add new app"""
    try:
        apps = load_json(APPS_FILE, [])
        new_app = request.get_json()
        new_app['created_at'] = datetime.now().isoformat()
        apps.append(new_app)
        save_json(APPS_FILE, apps)
        return jsonify({"success": True, "message": "App added", "app": new_app})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/apps/<app_id>', methods=['PUT'])
def update_app(app_id):
    """Update existing app"""
    try:
        apps = load_json(APPS_FILE, [])
        for i, app in enumerate(apps):
            if app.get('id') == app_id:
                apps[i] = {**app, **request.get_json()}
                apps[i]['updated_at'] = datetime.now().isoformat()
                save_json(APPS_FILE, apps)
                return jsonify({"success": True, "app": apps[i]})
        return jsonify({"success": False, "error": "App not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/apps/<app_id>', methods=['DELETE'])
def delete_app(app_id):
    """Delete app"""
    try:
        apps = load_json(APPS_FILE, [])
        apps = [a for a in apps if a.get('id') != app_id]
        save_json(APPS_FILE, apps)
        return jsonify({"success": True, "message": "App deleted"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============== USERS API ==============

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    users = load_json(USERS_FILE, {})
    return jsonify({"success": True, "users": users})

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get single user by ID"""
    users = load_json(USERS_FILE, {})
    user = users.get(user_id)
    
    if user:
        return jsonify({"success": True, "user": user})
    return jsonify({"success": False, "error": "User not found"}), 404

@app.route('/api/users', methods=['POST'])
def add_user():
    """Add or update user"""
    try:
        users = load_json(USERS_FILE, {})
        new_user = request.get_json()
        user_id = new_user.get('id') or new_user.get('email')
        
        if not user_id:
            return jsonify({"success": False, "error": "User ID or email required"}), 400
        
        new_user['created_at'] = datetime.now().isoformat()
        users[user_id] = new_user
        save_json(USERS_FILE, users)
        return jsonify({"success": True, "user": new_user})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============== USER DATA ENDPOINTS (COMPATIBILITY) ==============

@app.route('/user-data', methods=['POST', 'OPTIONS'])
def user_data():
    """Get user data by email (legacy endpoint)"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({"apps": [], "robots": []}), 200
        
        users = load_json(USERS_FILE, {})
        user = users.get(email, {"apps": [], "robots": []})
        
        return jsonify(user), 200
    except Exception as e:
        print(f"User data error: {e}")
        return jsonify({"apps": [], "robots": []}), 200

@app.route('/update-user', methods=['POST', 'OPTIONS'])
def update_user_data():
    """Update user data (legacy endpoint)"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({"status": "error", "message": "Email required"}), 400
        
        users = load_json(USERS_FILE, {})
        users[email] = {
            "apps": data.get('apps', []),
            "robots": data.get('robots', [])
        }
        save_json(USERS_FILE, users)
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"Update user error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/update-app-enabled', methods=['POST', 'OPTIONS'])
def update_app_enabled():
    """Update app enabled status"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        data = request.get_json()
        app_id = data.get('app_id')
        enabled = data.get('enabled')
        
        if app_id is None or enabled is None:
            return jsonify({"status": "error", "message": "Missing app_id or enabled"}), 400
        
        apps = load_json(APPS_FILE, [])
        for app in apps:
            if app.get('id') == app_id or app.get('name') == app_id:
                app['enabled'] = bool(enabled)
                save_json(APPS_FILE, apps)
                return jsonify({"status": "ok", "app": app}), 200
        
        return jsonify({"status": "error", "message": "App not found"}), 404
    except Exception as e:
        print(f"Update app enabled error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ============== AUTHENTICATION ==============

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    """User login"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        data = request.get_json()
        email = data.get('email') or data.get('username')
        password = data.get('password', '')
        
        if not email:
            return jsonify({"success": False, "error": "Email required"}), 400
        
        users = load_json(USERS_FILE, {})
        
        # Check if user exists
        if email in users:
            user = users[email]
            
            # Verify password if set
            if 'password' in user and user['password']:
                if user['password'] != password:
                    return jsonify({"success": False, "error": "Invalid password"}), 401
            
            return jsonify({
                "success": True,
                "message": "Login successful",
                "user": {
                    "email": email,
                    "apps": user.get('apps', []),
                    "robots": user.get('robots', [])
                }
            }), 200
        else:
            # Create new user
            users[email] = {
                "apps": [],
                "robots": [],
                "password": password if password else None,
                "created_at": datetime.now().isoformat()
            }
            save_json(USERS_FILE, users)
            
            return jsonify({
                "success": True,
                "message": "New user created",
                "user": {
                    "email": email,
                    "apps": [],
                    "robots": []
                }
            }), 200
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    """User registration"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        data = request.get_json()
        email = data.get('email') or data.get('username')
        password = data.get('password', '')
        
        if not email:
            return jsonify({"success": False, "error": "Email required"}), 400
        
        users = load_json(USERS_FILE, {})
        
        if email in users:
            return jsonify({"success": False, "error": "User already exists"}), 409
        
        users[email] = {
            "apps": [],
            "robots": [],
            "password": password if password else None,
            "created_at": datetime.now().isoformat()
        }
        save_json(USERS_FILE, users)
        
        return jsonify({
            "success": True,
            "message": "User registered successfully",
            "user": {
                "email": email,
                "apps": [],
                "robots": []
            }
        }), 200
    except Exception as e:
        print(f"Register error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ============== HEALTH CHECK ==============

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for monitoring"""
    try:
        apps = load_json(APPS_FILE, [])
        users = load_json(USERS_FILE, {})
        
        return jsonify({
            "status": "healthy",
            "apps_count": len(apps),
            "users_count": len(users),
            "version": "cloud-full",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

# ============== START SERVER ==============

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("=" * 70)
    print("🚀 Axiom OS App Store - Cloud Backend")
    print("=" * 70)
    print(f"📡 Port: {port}")
    print(f"📂 Apps file: {APPS_FILE}")
    print(f"👥 Users file: {USERS_FILE}")
    print(f"🌐 Static folder: {app.static_folder}")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=port, debug=False)

