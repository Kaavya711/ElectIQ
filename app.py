import os
from flask import Flask, render_template
from dotenv import load_dotenv
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_compress import Compress
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key_change_in_production')

# Extensions
CORS(app, resources={r"/api/*": {"origins": "*"}})
Compress(app)
csrf = CSRFProtect(app)

cache = Cache(app, config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 3600  # 1 hour
})

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Config
app.config['GA_MEASUREMENT_ID'] = os.environ.get('GA_MEASUREMENT_ID', '')
app.config['GOOGLE_MAPS_API_KEY'] = os.environ.get('GOOGLE_MAPS_KEY', '')
app.config['FIREBASE_DB_URL'] = os.environ.get('FIREBASE_DB_URL', '')

firebase_url = os.environ.get('FIREBASE_DB_URL', '')
if firebase_url:
    print(f"Firebase Realtime DB configured: {firebase_url}")
    app.config['FIREBASE_ENABLED'] = True
else:
    print("Warning: FIREBASE_DB_URL not set. Checklist will use session storage fallback.")
    app.config['FIREBASE_ENABLED'] = False

# Blueprints
from routes.main import main_bp
from routes.ai import ai_bp
from routes.maps import maps_bp
from routes.quiz import quiz_bp

app.register_blueprint(main_bp)
app.register_blueprint(ai_bp, url_prefix='/api')
app.register_blueprint(maps_bp, url_prefix='/api')
app.register_blueprint(quiz_bp, url_prefix='/api')

# Register checklist blueprint (Firebase-backed)
from checklist_firebase import checklist_bp
app.register_blueprint(checklist_bp, url_prefix='/api')

# Exempt blueprints from CSRF (API routes use fetch/JSON, not forms)
csrf.exempt(checklist_bp)
csrf.exempt(ai_bp)
csrf.exempt(maps_bp)
csrf.exempt(quiz_bp)
csrf.exempt(main_bp)


@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
        "maps.googleapis.com www.googletagmanager.com "
        "translate.google.com translate.googleapis.com; "
        "style-src 'self' 'unsafe-inline' fonts.googleapis.com translate.googleapis.com; "
        "font-src fonts.gstatic.com; "
        "img-src 'self' data: maps.gstatic.com *.googleapis.com "
        "translate.google.com translate.googleapis.com www.gstatic.com; "
        "connect-src 'self' *.googleapis.com *.firebaseio.com"
    )
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    if os.environ.get('FLASK_ENV') == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html',
                           error_message="500 Internal Server Error. Please try again later.",
                           error_code=500), 500


if __name__ == '__main__':
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, port=5000)