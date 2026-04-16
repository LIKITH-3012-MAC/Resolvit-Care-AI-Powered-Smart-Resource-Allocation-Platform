import os
import asyncio
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from backend.config import settings
from backend.database import init_db, close_db, ensure_schema

# Import Blueprints (to be converted)
# from backend.routes.auth import auth_bp
# from backend.routes.reports import reports_bp
# from backend.routes.ai_chat import ai_bp

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static',
            static_url_path='/static')

CORS(app)
load_dotenv()

# Database lifecycle management
@app.before_request
async def startup():
    # Note: Flask 2.3+ supports async before_request
    # However, for a persistent pool, we check if it exists
    from backend import database
    if database.pool is None:
        await init_db()
        await ensure_schema()

@app.teardown_appcontext
async def shutdown(exception=None):
    await close_db()

# --- Frontend Routes ---

@app.route('/')
async def index():
    return render_template('index.html')

@app.route('/dashboard')
async def dashboard():
    return render_template('dashboard.html')

@app.route('/report')
async def report_page():
    return render_template('report.html')

@app.route('/login')
async def login_page():
    return render_template('login.html')

@app.route('/signup')
async def signup_page():
    return render_template('signup.html')

@app.route('/map')
async def map_page():
    return render_template('map.html')

@app.route('/analytics')
async def analytics_page():
    return render_template('analytics.html')

@app.route('/forgot-password')
async def forgot_password_page():
    return render_template('forgot-password.html')

@app.route('/reset-password')
async def reset_password_page():
    return render_template('reset-password.html')

@app.route('/callback')
async def callback_page():
    return render_template('callback.html')

# --- API Routes ---

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "RESOLVIT Unified Platform", 
        "version": "3.0.0 (Flask)"
    })

# Error Handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify(error="Internal Server Error", detail=str(e)), 500

if __name__ == '__main__':
    # For local development
    app.run(host='0.0.0.0', port=settings.BACKEND_PORT, debug=settings.DEBUG)
