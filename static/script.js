/* ==========================================================
   Glide — frontend logic
   - Theme toggle
   - "Detect my location" via browser geolocation
   - Index search redirect (handled by <form>)
   - Dashboard: Leaflet map + /api/compare call
   ========================================================== */

// ---------- Theme toggle (persisted in localStorage) ----------
(function initTheme() {
  const saved = localStorage.getItem("glide-theme") || "light";
  document.documentElement.setAttribute("data-theme", saved);
  const btn = document.getElementById("themeToggle");
  if (btn) {
    btn.addEventListener("click", () => {
      const cur = document.documentElement.getAttribute("data-theme");
      const next = cur === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("glide-theme", next);
    });
  }
})();

// ---------- "Detect my location" button on index page ----------
(function initDetectBtn() {
  const btn = document.getElementById("detectBtn");
  const pickupInput = document.getElementById("pickupInput");
  if (!btn || !pickupInput) return;

  btn.addEventListener("click", async () => {
    if (!navigator.geolocation) { alert("Geolocation not supported"); return; }
    btn.disabled = true; btn.textContent = "…";
    navigator.geolocation.getCurrentPosition(async (pos) => {
      const { latitude, longitude } = pos.coords;
      try {
        const r = await fetch(`/api/reverse?lat=${latitude}&lng=${longitude}`);
        const j = await r.json();
        pickupInput.value = j.display_name || `${latitude},${longitude}`;
      } catch (e) {
        pickupInput.value = `${latitude},${longitude}`;
      }
      btn.disabled = false; btn.textContent = "📍";
    }, () => {
      alert("Could not detect your location.");
      btn.disabled = false; btn.textContent = "📍";
    });
  });
})();

// ---------- Dashboard: map + ride comparison ----------
(function initDashboard() {
  const mapEl = document.getElementById("map");
  if (!mapEl) return; // not on dashboard

  const map = L.map("map").setView([12.9716, 77.5946], 12); // Bengaluru default
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap",
    maxZoom: 19,
  }).addTo(map);

  let pickupMarker, destMarker, routeLine;

  async function geocode(query) {
    const r = await fetch(`/api/geocode?q=${encodeURIComponent(query)}`);
    if (!r.ok) return null;
    return await r.json();
  }

  function setMarker(existing, latlng, label, color) {
    if (existing) map.removeLayer(existing);
    return L.marker(latlng, { title: label })
      .addTo(map)
      .bindPopup(label);
  }

  function renderRides(data) {
    const list = document.getElementById("rideList");
    const surgeBanner = document.getElementById("surgeBanner");
    list.innerHTML = "";

    if (data.surge && data.surge > 1.15) {
      surgeBanner.textContent =
        `⚡ Surge active (×${data.surge}). Prices may be higher than usual.`;
      surgeBanner.classList.remove("d-none");
    } else {
      surgeBanner.classList.add("d-none");
    }

    data.rides.forEach((r) => {
      const card = document.createElement("a");
      card.href = r.booking_link;
      card.target = "_blank";
      card.rel = "noopener";
      card.className = "ride-card";
      card.style.borderLeftColor = r.color;
      card.innerHTML = `
        <div class="ride-meta">
          <span class="ride-provider">${r.provider}</span>
          <span class="ride-vehicle">${r.vehicle} • Trip ~${r.trip_minutes} min</span>
          <div class="mt-1">
            ${r.is_cheapest ? '<span class="badge badge-best me-1">Best Price</span>' : ""}
            ${r.is_fastest  ? '<span class="badge badge-fast">Fastest</span>' : ""}
          </div>
        </div>
        <div class="text-end">
          <div class="ride-price">₹${r.price}</div>
          <div class="ride-eta">ETA ${r.eta} min</div>
        </div>`;
      list.appendChild(card);
    });
  }

  async function runSearch() {
    const pickup = document.getElementById("pickupInput").value.trim();
    const destination = document.getElementById("destinationInput").value.trim();
    if (!pickup || !destination) { alert("Please enter both locations"); return; }

    document.getElementById("emptyState").classList.add("d-none");
    document.getElementById("loader").classList.remove("d-none");
    document.getElementById("rideList").innerHTML = "";

    const [p, d] = await Promise.all([geocode(pickup), geocode(destination)]);
    if (!p || !d) {
      document.getElementById("loader").classList.add("d-none");
      alert("Could not find one of the locations. Try a more specific name.");
      return;
    }

    pickupMarker = setMarker(pickupMarker, [p.lat, p.lng], "Pickup");
    destMarker   = setMarker(destMarker,   [d.lat, d.lng], "Destination");
    if (routeLine) map.removeLayer(routeLine);
    routeLine = L.polyline([[p.lat, p.lng], [d.lat, d.lng]],
                           { color: "#0d6efd", weight: 4, opacity: .7 }).addTo(map);
    map.fitBounds(routeLine.getBounds(), { padding: [40, 40] });

    const resp = await fetch("/api/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        pickup, destination,
        pickup_lat: p.lat, pickup_lng: p.lng,
        dest_lat: d.lat,  dest_lng: d.lng,
      }),
    });
    const data = await resp.json();

    document.getElementById("loader").classList.add("d-none");
    document.getElementById("distanceLabel").textContent =
      `Distance: ${data.distance_km} km • Surge ×${data.surge}`;
    renderRides(data);
  }

  document.getElementById("searchBtn").addEventListener("click", runSearch);

  // Auto-run if both fields were pre-filled from the index form.
  if (document.getElementById("pickupInput").value &&
      document.getElementById("destinationInput").value) {
    runSearch();
  }
})();
