"""
config.py
---------
Central configuration for the Glide app.
Reads sensitive values from environment variables (.env file)
so we never hardcode secrets in the source code.
"""
import os
from dotenv import load_dotenv

load_dotenv()  # load variables from a .env file if present


class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")

    # SQLite database file path
    DATABASE_PATH = os.path.join(
        os.path.dirname(__file__), "database", "glide.db"
    )

    # Google OAuth credentials (create them at https://console.cloud.google.com/)
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )

    # Free OpenStreetMap Nominatim endpoint (no key required).
    # Be polite: include a unique User-Agent and don't spam requests.
    NOMINATIM_URL = "https://nominatim.openstreetmap.org"
    NOMINATIM_USER_AGENT = "Glide-College-Project/1.0 (contact@example.com)"
