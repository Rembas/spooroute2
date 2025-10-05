document.addEventListener("DOMContentLoaded", function(){
  const el = document.getElementById("map");
  if(!el){ return; }

  // Kraków center
  const map = L.map('map', { scrollWheelZoom:false }).setView([50.06143, 19.93722], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, attribution: '&copy; OpenStreetMap'
  }).addTo(map);

  const stops = [
    { id: "STOP_A", name: "Plac Wolnica", lat: 50.06143, lon: 19.93722 },
    { id: "STOP_B", name: "Old Town",     lat: 50.06465, lon: 19.94498 },
    { id: "STOP_C", name: "Kazimierz",    lat: 50.05900, lon: 19.94000 }
  ];

  stops.forEach(s => {
    const m = L.marker([s.lat, s.lon]).addTo(map);
    m.bindPopup(
      `<div style="min-width:160px">
        <strong>${s.name}</strong><br/>
        <a class="btn btn-sm btn-primary mt-2" href="/alternatives?from_stop=${s.id}">
          Show alternatives
        </a>
      </div>`
    );
  });

  // Se la mappa nasce in un tab nascosto, forza il resize:
  setTimeout(()=> map.invalidateSize(), 300);
});
