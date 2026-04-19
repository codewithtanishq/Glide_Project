"""
services/fare_engine.py
-----------------------
FareEngine — orchestrates all RideProvider subclasses.

OOP concepts demonstrated:
- POLYMORPHISM: the engine loops over a list of RideProvider objects
  and calls the same methods on each one without caring about its type.
- COMPOSITION: the engine holds a list of provider classes.
"""
from datetime import datetime
import random

from models.provider import (
    RideProvider, UberRide, OlaRide, RapidoRide, BluSmartRide,
)


class FareEngine:
    """Compares prices and ETAs across all configured providers."""

    # Default providers — easy to add new ones later.
    DEFAULT_PROVIDERS = [UberRide, OlaRide, RapidoRide, BluSmartRide]

    def __init__(self, providers=None):
        self._provider_classes = providers or self.DEFAULT_PROVIDERS

    # ---------- surge logic ----------
    def apply_surge(self) -> float:
        """
        Smart mock surge multiplier.

        Real apps look at demand vs supply. Here we approximate that with
        time of day: morning + evening rush hours -> 1.3x to 1.7x,
        late night -> 1.2x, otherwise 1.0x to 1.1x. A small random factor
        is added so each refresh feels alive.
        """
        hour = datetime.now().hour
        if hour in (8, 9, 18, 19, 20):
            return round(random.uniform(1.3, 1.7), 2)
        if hour in (22, 23, 0, 1, 2):
            return round(random.uniform(1.15, 1.35), 2)
        return round(random.uniform(1.0, 1.1), 2)

    # ---------- main comparison ----------
    def compare_prices(self, distance_km, pickup_lat, pickup_lng,
                       dest_lat, dest_lng, pickup_label, dest_label):
        """
        Returns a list of dicts ready to send to the frontend:
        [{provider, vehicle, color, price, eta, trip_minutes, booking_link,
          is_cheapest, is_fastest}, ...]
        """
        surge = self.apply_surge()

        rides = []
        for cls in self._provider_classes:
            ride: RideProvider = cls(distance_km=distance_km, surge=surge)
            rides.append(ride.to_dict(
                pickup_lat, pickup_lng, dest_lat, dest_lng,
                pickup_label, dest_label,
            ))

        # Sort by price (cheapest first) for the UI
        rides.sort(key=lambda r: r["price"])

        # Tag the cheapest and fastest rides
        cheapest = self.find_cheapest(rides)
        fastest = self.find_fastest(rides)
        for r in rides:
            r["is_cheapest"] = (r is cheapest)
            r["is_fastest"] = (r is fastest)

        return {"surge": surge, "rides": rides}

    # ---------- helpers ----------
    @staticmethod
    def find_cheapest(rides):
        return min(rides, key=lambda r: r["price"]) if rides else None

    @staticmethod
    def find_fastest(rides):
        return min(rides, key=lambda r: r["eta"]) if rides else None
