"""
ElectIQ — Flask application factory.

Initialises extensions (CORS, compression, caching, CSRF, rate limiting),
registers blueprints, applies security headers, and registers error handlers.
"""

import os
import logging
from flask import Flask, render_template
from dotenv import load_dotenv
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_compress import Compress
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key_change_in_production")

# ── Extensions ────────────────────────────────────────────────────────────────
CORS(app, resources={r"/api/*": {"origins": "*"}})
Compress(app)
csrf = CSRFProtect(app)

cache = Cache(
    app,
    config={
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": 3600,  # 1 hour
    },
)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# ── App config ────────────────────────────────────────────────────────────────
app.config["GA_MEASUREMENT_ID"] = os.environ.get("GA_MEASUREMENT_ID", "")
app.config["GOOGLE_MAPS_API_KEY"] = os.environ.get("GOOGLE_MAPS_KEY", "")
app.config["FIREBASE_DB_URL"] = os.environ.get("FIREBASE_DB_URL", "")

firebase_url: str = os.environ.get("FIREBASE_DB_URL", "")
if firebase_url:
    logger.info("Firebase Realtime DB configured: %s", firebase_url)
    app.config["FIREBASE_ENABLED"] = True
else:
    logger.warning(
        "FIREBASE_DB_URL not set — checklist will use session storage fallback."
    )
    app.config["FIREBASE_ENABLED"] = False

# ── Blueprints ────────────────────────────────────────────────────────────────
from routes.main import main_bp  # noqa: E402
from routes.ai import ai_bp  # noqa: E402
from routes.maps import maps_bp  # noqa: E402
from routes.quiz import quiz_bp  # noqa: E402
from checklist_firebase import checklist_bp  # noqa: E402

app.register_blueprint(main_bp)
app.register_blueprint(ai_bp, url_prefix="/api")
app.register_blueprint(maps_bp, url_prefix="/api")
app.register_blueprint(quiz_bp, url_prefix="/api")
app.register_blueprint(checklist_bp, url_prefix="/api")

# Exempt API blueprints from CSRF — they use JSON / fetch, not HTML forms.
for bp in (checklist_bp, ai_bp, maps_bp, quiz_bp, main_bp):
    csrf.exempt(bp)


# ── Security headers ──────────────────────────────────────────────────────────
@app.after_request
def add_security_headers(response):
    """Attach security headers to every HTTP response."""
    response.headers["Content-Security-Policy"] = (
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
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    if os.environ.get("FLASK_ENV") == "production":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
    return response


# ── Error handlers ────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found_error(error):
    """Render a custom 404 page."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    """Render a generic 500 error page."""
    logger.error("Internal server error: %s", error)
    return (
        render_template(
            "base.html",
            error_message="500 Internal Server Error. Please try again later.",
            error_code=500,
        ),
        500,
    )


if __name__ == "__main__":
    debug: bool = os.environ.get("FLASK_ENV") == "development"
    app.run(debug=debug, port=5000)