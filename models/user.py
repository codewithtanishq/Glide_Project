"""
models/user.py
--------------
User class — represents a logged-in user and exposes simple helpers.

OOP concepts demonstrated:
- Encapsulation: user data is wrapped in an object with methods.
- Integration with Flask-Login: we inherit from UserMixin so Flask-Login
  knows how to handle login sessions for our objects.
"""
from flask_login import UserMixin


class User(UserMixin):
    """A simple user object stored in the session after Google login."""

    def __init__(self, id_, name, email, picture):
        self.id = str(id_)        # Flask-Login expects a string id
        self.name = name
        self.email = email
        self.picture = picture

    # --- Class-level helpers ---
    @staticmethod
    def from_db_row(row: dict) -> "User":
        """Build a User object from a database row (a dict)."""
        return User(
            id_=row["id"],
            name=row["name"],
            email=row["email"],
            picture=row.get("picture", ""),
        )

    def save_history(self, db, pickup, destination,
                     pickup_lat, pickup_lng, dest_lat, dest_lng, distance_km):
        """Convenience method so route code can call user.save_history(...)."""
        db.save_search(
            int(self.id), pickup, destination,
            pickup_lat, pickup_lng, dest_lat, dest_lng, distance_km,
        )
