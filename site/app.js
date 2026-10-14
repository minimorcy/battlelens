// Selector de idioma (en/es). Los textos están en atributos data-en / data-es de cada elemento.
(function () {
  "use strict";
  var KEY = "battlelens-lang";
  var html = document.documentElement;

  function stored() {
    try { return window.localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function remember(lang) {
    try { window.localStorage.setItem(KEY, lang); } catch (e) { /* almacenamiento no disponible */ }
  }
  function initial() {
    var saved = stored();
    if (saved === "en" || saved === "es") return saved;
    var nav = (navigator.languages && navigator.languages[0]) || navigator.language || "en";
    return nav.toLowerCase().indexOf("es") === 0 ? "es" : "en";
  }

  function apply(lang) {
    html.lang = lang;
    document.querySelectorAll("[data-" + lang + "]").forEach(function (el) {
      el.innerHTML = el.getAttribute("data-" + lang);
    });
    document.querySelectorAll("[data-" + lang + "-alt]").forEach(function (el) {
      el.setAttribute("alt", el.getAttribute("data-" + lang + "-alt"));
    });
    document.querySelectorAll("[data-" + lang + "-content]").forEach(function (el) {
      el.setAttribute("content", el.getAttribute("data-" + lang + "-content"));
    });
    document.querySelectorAll("[data-" + lang + "-aria-label]").forEach(function (el) {
      el.setAttribute("aria-label", el.getAttribute("data-" + lang + "-aria-label"));
    });
    // Eventos de Umami (si está activo): el idioma de la página como propiedad
    document.querySelectorAll("[data-umami-event]").forEach(function (el) {
      el.setAttribute("data-umami-event-lang", lang);
    });
  }

  // Aviso de analítica solo si el contenedor ha insertado el script de Umami
  var note = document.getElementById("analytics-note");
  if (note && document.querySelector("script[data-website-id]")) {
    note.hidden = false;
  }

  var current = initial();
  apply(current);
  var toggle = document.getElementById("lang-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      current = current === "es" ? "en" : "es";
      apply(current);
      remember(current);
    });
  }

  // Ficha competitiva recortada: el botón la despliega entera
  var expand = document.getElementById("pro-expand");
  if (expand) {
    expand.addEventListener("click", function () {
      document.getElementById("pro-shot").classList.add("open");
    });
  }

  // Aparición al hacer scroll. Lo que ya está a la vista se muestra sin animar
  // (antes de activar la clase .js) para que no parpadee al cargar.
  var items = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    items.forEach(function (el) {
      if (el.getBoundingClientRect().top < window.innerHeight) el.classList.add("in");
      else observer.observe(el);
    });
  } else {
    items.forEach(function (el) { el.classList.add("in"); });
  }
  html.classList.add("js");
})();
