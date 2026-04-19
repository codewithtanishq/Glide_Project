"""
services/map_service.py
-----------------------
LocationService — wraps the free OpenStreetMap Nominatim API for
geocoding (text -> lat/lng) and reverse-geocoding (lat/lng -> text),
plus a haversine helper to compute distance between two points.
"""
import math
import requests


class LocationService:
    def __init__(self, base_url: str, user_agent: str):
        self._base_url = base_url.rstrip("/")
        self._headers = {"User-Agent": user_agent}

    # ---------- geocoding ----------
    def geocode_destination(self, query: str):
        """Convert a place name into {lat, lng, display_name} or None."""
        if not query:
            return None
        try:
            resp = requests.get(
                f"{self._base_url}/search",
                params={"q": query, "format": "json", "limit": 1,
                        "addressdetails": 0, "countrycodes": "in"},
                headers=self._headers, timeout=6,
            )
            resp.raise_for_status()
            data = resp.json()
            if not data:
                return None
            top = data[0]
            return {
                "lat": float(top["lat"]),
                "lng": float(top["lon"]),
                "display_name": top["display_name"],
            }
        except requests.RequestException:
            return None

    def reverse_geocode(self, lat: float, lng: float):
        """Convert coordinates into a human-readable address."""
        try:
            resp = requests.get(
                f"{self._base_url}/reverse",
                params={"lat": lat, "lon": lng, "format": "json", "zoom": 16},
                headers=self._headers, timeout=6,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("display_name", f"{lat},{lng}")
        except requests.RequestException:
            return f"{lat},{lng}"

    # ---------- distance ----------
    @staticmethod
    def haversine_km(lat1, lng1, lat2, lng2) -> float:
        """Great-circle distance between two points in kilometres."""
        R = 6371.0  # Earth radius
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlmb = math.radians(lng2 - lng1)
        a = (math.sin(dphi / 2) ** 2
             + math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2) ** 2)
        return 2 * R * math.asin(math.sqrt(a))
