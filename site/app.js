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
})();
