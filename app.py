"""
app.py
------
Main Flask application for Glide.

Wires together:
    - DatabaseManager (SQLite persistence)
    - LocationService (OpenStreetMap geocoding)
    - FareEngine (compare ride prices across providers)
    - Google OAuth login (Authlib + Flask-Login)

Run with:
    python app.py
"""
import json
import requests
from flask import (
    Flask, render_template, request, jsonify, redirect, url_for, session, flash,
)
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user,
)
from authlib.integrations.flask_client import OAuth

from config import Config
from models.database import DatabaseManager
from models.user import User
from services.map_service import LocationService
from services.fare_engine import FareEngine


# ----------------------------------------------------------------------
# Application factory pattern (kept simple for a college project)
# ----------------------------------------------------------------------
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Singletons used across requests
db = DatabaseManager(Config.DATABASE_PATH)
location_service = LocationService(Config.NOMINATIM_URL, Config.NOMINATIM_USER_AGENT)
fare_engine = FareEngine()

# ----------------------------------------------------------------------
# Flask-Login setup
# ----------------------------------------------------------------------
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    row = db.get_user(int(user_id))
    return User.from_db_row(row) if row else None


# ----------------------------------------------------------------------
# Google OAuth setup (Authlib)
# ----------------------------------------------------------------------
oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    server_metadata_url=Config.GOOGLE_DISCOVERY_URL,
    client_kwargs={"scope": "openid email profile"},
)


# ======================================================================
# PAGE ROUTES
# ======================================================================
@app.route("/")
def index():
    """Landing page with the search form."""
    return render_template("index.html", user=current_user)


@app.route("/dashboard")
def dashboard():
    """Results page. Reads pickup + destination from query string."""
    pickup = request.args.get("pickup", "").strip()
    destination = request.args.get("destination", "").strip()
    return render_template(
        "dashboard.html",
        user=current_user,
        pickup=pickup,
        destination=destination,
    )


@app.route("/history")
@login_required
def history():
    """Logged-in users see their past searches."""
    rows = db.get_history(int(current_user.id))
    return render_template("history.html", user=current_user, history=rows)


# ======================================================================
# AUTH ROUTES
# ======================================================================
@app.route("/login")
def login():
    if not Config.GOOGLE_CLIENT_ID:
        flash("Google login is not configured. Add GOOGLE_CLIENT_ID to .env",
              "warning")
        return redirect(url_for("index"))
    redirect_uri = url_for("auth_callback", _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route("/auth/callback")
def auth_callback():
    token = google.authorize_access_token()
    info = token.get("userinfo") or google.parse_id_token(token, nonce=None)
    user_id = db.save_user(
        google_id=info["sub"],
        name=info.get("name", "Glide User"),
        email=info.get("email", ""),
        picture=info.get("picture", ""),
    )
    user_row = db.get_user(user_id)
    user = User.from_db_row(user_row)
    login_user(user)
    flash(f"Welcome, {user.name}!", "success")
    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ======================================================================
# JSON API ROUTES (called by frontend JavaScript)
# ======================================================================
@app.route("/api/geocode")
def api_geocode():
    """Geocode a place name -> coordinates."""
    query = request.args.get("q", "")
    result = location_service.geocode_destination(query)
    if not result:
        return jsonify({"error": "Location not found"}), 404
    return jsonify(result)


@app.route("/api/reverse")
def api_reverse():
    """Reverse geocode lat/lng -> address (for 'detect my location')."""
    try:
        lat = float(request.args.get("lat"))
        lng = float(request.args.get("lng"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid coordinates"}), 400
    return jsonify({"display_name": location_service.reverse_geocode(lat, lng)})


@app.route("/api/compare", methods=["POST"])
def api_compare():
    """
    Body JSON:
        {
          "pickup":      "MG Road, Bengaluru",
          "destination": "Koramangala, Bengaluru",
          "pickup_lat":  12.97, "pickup_lng": 77.59,
          "dest_lat":    12.93, "dest_lng":   77.62
        }
    """
    payload = request.get_json(silent=True) or {}
    try:
        plat = float(payload["pickup_lat"])
        plng = float(payload["pickup_lng"])
        dlat = float(payload["dest_lat"])
        dlng = float(payload["dest_lng"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "pickup/dest coordinates required"}), 400

    pickup = payload.get("pickup", "Pickup")
    destination = payload.get("destination", "Destination")

    distance_km = round(
        location_service.haversine_km(plat, plng, dlat, dlng), 2
    )
    result = fare_engine.compare_prices(
        distance_km, plat, plng, dlat, dlng, pickup, destination,
    )
    result["distance_km"] = distance_km

    # Save to history if user is logged in
    if current_user.is_authenticated:
        current_user.save_history(
            db, pickup, destination, plat, plng, dlat, dlng, distance_km,
        )

    return jsonify(result)


# ======================================================================
# MAIN
# ======================================================================
if __name__ == "__main__":
    # debug=True auto-reloads on code changes — turn off for production.
    app.run(host="0.0.0.0", port=5000, debug=True)
