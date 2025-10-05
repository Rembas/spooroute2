document.addEventListener("DOMContentLoaded", function(){
  const el = document.getElementById("map");
  if(!el) return;

  const map = L.map('map', { scrollWheelZoom:false }).setView([50.06143, 19.93722], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom:19, attribution:'&copy; OpenStreetMap'
  }).addTo(map);

  const stops = [
    { id:"STOP_A", name:"Plac Wolnica", lat:50.06143, lon:19.93722 },
    { id:"STOP_B", name:"Old Town",     lat:50.06465, lon:19.94498 },
    { id:"STOP_C", name:"Kazimierz",    lat:50.05900, lon:19.94000 }
  ];

  const markers = {};
  const popupHtml = (s) => `
    <div style="min-width:160px">
      <strong>${s.name}</strong><br/>
      <a class="btn btn-sm btn-primary mt-2" href="/alternatives?from_stop=${s.id}">
        ${typeof t === 'function' ? t('show_alts') : 'Show alternatives'}
      </a>
    </div>`;

  stops.forEach(s=>{
    const m=L.marker([s.lat,s.lon]).addTo(map);
    m.bindPopup(popupHtml(s));
    m.__stop = s;       // per aggiornare al cambio lingua
    markers[s.id]=m;
  });

  // Se arrivo con #stop=STOP_X, centra/evidenzia
  if (location.hash.startsWith("#stop=")) {
    const id = decodeURIComponent(location.hash.split("=")[1] || "");
    const mk = markers[id];
    if (mk){
      map.setView(mk.getLatLng(), 15);
      mk.openPopup();
      const el = mk.getElement();
      if (el){ el.style.filter="drop-shadow(0 0 6px #06B6D4)"; setTimeout(()=>{ el.style.filter=""; }, 2000); }
    }
  }

  // Quando cambia lingua, rigenera i contenuti popup
  document.addEventListener('langchange', ()=>{
    Object.values(markers).forEach(mk=>{
      const p = mk.getPopup();
      if (p) p.setContent(popupHtml(mk.__stop));
    });
  });

  setTimeout(()=> map.invalidateSize(), 300);
});
