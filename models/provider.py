"""
models/provider.py
------------------
Ride provider classes.

OOP concepts demonstrated:
- INHERITANCE: UberRide, OlaRide, RapidoRide, BluSmartRide all inherit
  from the abstract base class RideProvider.
- POLYMORPHISM: Each subclass overrides get_price(), get_eta(),
  get_booking_link() — the FareEngine treats them all the same way.
- ENCAPSULATION: pricing rules (base fare, per-km rate, surge factor)
  are kept inside each provider.
"""
from abc import ABC, abstractmethod
from urllib.parse import quote_plus
import random


class RideProvider(ABC):
    """Abstract base class for every ride provider."""

    # Subclasses MUST set these
    name: str = "Provider"
    vehicle: str = "Cab"
    color: str = "#000000"           # used for the card border in UI
    base_fare: float = 30.0
    per_km: float = 12.0
    per_min: float = 1.5
    avg_speed_kmph: float = 25.0     # used to estimate trip duration

    def __init__(self, distance_km: float, surge: float = 1.0):
        self._distance_km = distance_km
        self._surge = surge

    # ---------- shared (concrete) methods ----------
    def get_eta(self) -> int:
        """Driver arrival time in minutes — small random spread per provider."""
        # A bike usually arrives faster than a sedan, so use class default
        # plus a small random variation so each request feels live.
        random.seed(f"{self.name}-{self._distance_km}-eta")
        return max(1, self._eta_baseline() + random.randint(-1, 2))

    def get_trip_minutes(self) -> int:
        """Approximate total trip time in minutes."""
        return max(1, int((self._distance_km / self.avg_speed_kmph) * 60))

    def get_price(self) -> int:
        """Price = (base + dist*rate + time*rate) * surge — rounded to ₹."""
        time_min = self.get_trip_minutes()
        raw = (
            self.base_fare
            + self._distance_km * self.per_km
            + time_min * self.per_min
        ) * self._surge
        return int(round(raw))

    def to_dict(self, pickup_lat, pickup_lng, dest_lat, dest_lng,
                pickup_label, dest_label) -> dict:
        """Serialise this ride option for the frontend."""
        return {
            "provider": self.name,
            "vehicle": self.vehicle,
            "color": self.color,
            "price": self.get_price(),
            "eta": self.get_eta(),
            "trip_minutes": self.get_trip_minutes(),
            "booking_link": self.get_booking_link(
                pickup_lat, pickup_lng, dest_lat, dest_lng,
                pickup_label, dest_label,
            ),
        }

    # ---------- methods subclasses customise ----------
    def _eta_baseline(self) -> int:
        return 4

    @abstractmethod
    def get_booking_link(self, pickup_lat, pickup_lng,
                         dest_lat, dest_lng,
                         pickup_label, dest_label) -> str:
        """Return a deep link / website URL with pickup & drop pre-filled."""
        ...


# ----------------------------------------------------------------------
# Concrete providers
# ----------------------------------------------------------------------
class UberRide(RideProvider):
    name = "Uber"
    vehicle = "Mini"
    color = "#000000"
    base_fare = 50
    per_km = 14
    per_min = 1.5
    avg_speed_kmph = 24

    def _eta_baseline(self):
        return 5

    def get_booking_link(self, pickup_lat, pickup_lng,
                         dest_lat, dest_lng, pickup_label, dest_label):
        # Uber universal deep link (works on web + mobile).
        return (
            "https://m.uber.com/ul/?action=setPickup"
            f"&pickup[latitude]={pickup_lat}"
            f"&pickup[longitude]={pickup_lng}"
            f"&pickup[nickname]={quote_plus(pickup_label)}"
            f"&dropoff[latitude]={dest_lat}"
            f"&dropoff[longitude]={dest_lng}"
            f"&dropoff[nickname]={quote_plus(dest_label)}"
        )


class OlaRide(RideProvider):
    name = "Ola"
    vehicle = "Auto"
    color = "#0F8A3C"
    base_fare = 35
    per_km = 11
    per_min = 1.2
    avg_speed_kmph = 22

    def _eta_baseline(self):
        return 4

    def get_booking_link(self, pickup_lat, pickup_lng,
                         dest_lat, dest_lng, pickup_label, dest_label):
        # Ola does not expose a public deep-link spec, so we fall back to
        # their booking page with coordinates appended as query params.
        return (
            "https://book.olacabs.com/?"
            f"pickup_lat={pickup_lat}&pickup_lng={pickup_lng}"
            f"&drop_lat={dest_lat}&drop_lng={dest_lng}"
            f"&pickup_name={quote_plus(pickup_label)}"
            f"&drop_name={quote_plus(dest_label)}"
        )


class RapidoRide(RideProvider):
    name = "Rapido"
    vehicle = "Bike"
    color = "#FFD400"
    base_fare = 20
    per_km = 7
    per_min = 0.8
    avg_speed_kmph = 28      # bikes weave through traffic faster

    def _eta_baseline(self):
        return 2

    def get_booking_link(self, pickup_lat, pickup_lng,
                         dest_lat, dest_lng, pickup_label, dest_label):
        # Rapido web booking page — supports lat/lng query params.
        return (
            "https://rapido.bike/?"
            f"pickup_lat={pickup_lat}&pickup_lng={pickup_lng}"
            f"&drop_lat={dest_lat}&drop_lng={dest_lng}"
        )


class BluSmartRide(RideProvider):
    name = "BluSmart"
    vehicle = "EV Cab"
    color = "#0057FF"
    base_fare = 60
    per_km = 13
    per_min = 1.4
    avg_speed_kmph = 25

    def _eta_baseline(self):
        return 6

    def get_booking_link(self, pickup_lat, pickup_lng,
                         dest_lat, dest_lng, pickup_label, dest_label):
        return (
            "https://blu-smart.com/?"
            f"pickup_lat={pickup_lat}&pickup_lng={pickup_lng}"
            f"&drop_lat={dest_lat}&drop_lng={dest_lng}"
        )
