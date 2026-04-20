# 🚖 Glide — Sahi Ride. Sahi Price. Bas Glide.

A college project that compares ride prices from **Uber, Ola, Rapido, and BluSmart**
in a single search, using **Python (Flask) + OOP**, OpenStreetMap, and Google login.

---

## ✨ Features

- Single search box → compare prices, ETAs, and trip times across 4 providers.
- 🟢 **Best Price** badge on the cheapest ride.
- ⚡ **Fastest** badge on the quickest pickup.
- 📍 "Detect my location" via browser geolocation.
- 🗺️ Interactive map (Leaflet + free OpenStreetMap tiles, no Google Maps key).
- 🔐 Sign in with Google (OAuth).
- 🕘 Search history saved per user.
- ⚡ Smart mock surge engine (rush-hour aware).
- 🌗 Light / dark theme toggle.
- 1-click deep links to each provider's booking page with pickup/drop pre-filled.
- 📱 Mobile responsive (Bootstrap 5).

---

## 🧱 Tech Stack

| Layer        | Choice                                  |
| ------------ | --------------------------------------- |
| Backend      | Python 3.10+, Flask 3                   |
| Auth         | Authlib + Flask-Login (Google OAuth)    |
| Database     | SQLite (built-in)                       |
| Frontend     | HTML, CSS, JS, Bootstrap 5              |
| Maps         | Leaflet.js + OpenStreetMap + Nominatim  |

---

## 🧠 OOP Concepts Used

| Concept         | Where to find it                                                          |
| --------------- | ------------------------------------------------------------------------- |
| **Class/Object**| `User`, `DatabaseManager`, `LocationService`, `FareEngine`, `RideProvider`|
| **Inheritance** | `UberRide`, `OlaRide`, `RapidoRide`, `BluSmartRide` ← `RideProvider`      |
| **Polymorphism**| `FareEngine.compare_prices()` calls `get_price()`/`get_eta()` uniformly   |
| **Encapsulation**| Private attrs (`_distance_km`, `_surge`, `_base_url`) + public methods   |
| **Abstraction** | `RideProvider(ABC)` with abstract `get_booking_link()`                    |
| **Composition** | `FareEngine` holds a list of `RideProvider` classes                       |

---

## 📁 Folder Structure

```
glide_project/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .env.example
├── models/
│   ├── __init__.py
│   ├── database.py      # DatabaseManager (SQLite)
│   ├── user.py          # User class (Flask-Login)
│   └── provider.py      # RideProvider + 4 subclasses
├── services/
│   ├── __init__.py
│   ├── map_service.py   # LocationService (OpenStreetMap)
│   └── fare_engine.py   # FareEngine (surge + comparison)
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   └── history.html
├── static/
│   ├── style.css
│   └── script.js
└── database/
    └── glide.db        # auto-created on first run
```

---

## ⚙️ Installation

> Requires **Python 3.10+** installed on your machine.

```bash
# 1. Clone or unzip the project
cd glide_project

# 2. Create a virtual environment (recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy the env template and fill in your Google OAuth keys
cp .env.example .env       # (Windows: copy .env.example .env)
#    -> Open .env and paste your GOOGLE_CLIENT_ID & GOOGLE_CLIENT_SECRET

# 5. Run!
python app.py
```

Then open <http://127.0.0.1:5000> in your browser. 🚀

---

## 🔐 Setting up Google Login

1. Go to <https://console.cloud.google.com/apis/credentials>.
2. Create an **OAuth 2.0 Client ID** (Application type: *Web application*).
3. Add this **Authorized redirect URI**:
   ```
   http://127.0.0.1:5000/auth/callback
   ```
4. Copy the Client ID and Client Secret into your `.env` file.

You can still use the app **without** Google login — search and price comparison
work for guests; only history requires sign-in.

---

## 🚧 Future Improvements

- Real provider APIs (where partnerships allow) instead of smart mock pricing.
- AI surge predictor trained on historical data.
- Promo code auto-apply and target price alerts (push notifications).
- PWA / mobile app build with React Native.
- Multi-modal routing (e.g., "Bike to Metro, then walk").

---

## 📜 License

Made for educational use as a college project. Feel free to fork and learn from it.
