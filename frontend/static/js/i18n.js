// Minimal client-side i18n for EN/PL

(function(){
  const I18N = {
    en: {
      tagline: "Arrive calm, every time.",
      live: "Live status",
      map: "Map",
      report: "Report a problem",
      show_alts: "Show alternatives",
      install: "Install app"
    },
    pl: {
      tagline: "Jedź spokojnie.",
      live: "Status na żywo",
      map: "Mapa",
      report: "Zgłoś problem",
      show_alts: "Pokaż alternatywy",
      install: "Zainstaluj aplikację"
    }
  };

  // Espone funzioni globali leggere
  window.I18N = I18N;
  window.getLang = () => localStorage.getItem("lang") || "en";
  window.t = (key) => {
    const lang = window.getLang();
    return (I18N[lang] && I18N[lang][key]) || (I18N.en[key] || key);
  };

  window.applyI18n = () => {
    const lang = window.getLang();
    document.documentElement.lang = lang;
    // Applica i testi agli elementi con data-i18n
    document.querySelectorAll("[data-i18n]").forEach(el => {
      const k = el.getAttribute("data-i18n");
      const txt = (I18N[lang] && I18N[lang][k]) || null;
      if (txt) el.textContent = txt;
    });
    // Aggiorna label del bottone toggle
    const btn = document.getElementById("langToggle");
    if (btn) btn.textContent = (lang === "en" ? "PL" : "EN");
  };

  // Prima applicazione all’avvio
  document.addEventListener("DOMContentLoaded", window.applyI18n);
})();
