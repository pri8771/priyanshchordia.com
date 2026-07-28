/* Interactive design experiences, ported from the Claude Design concepts.
 *
 * Each experience takes over the homepage as a fixed full-viewport piece when
 * its theme is active, and tears down cleanly when the theme changes. The
 * semantic catalogue in the document is the no-JS fallback and stays intact
 * underneath — nothing here is required to read the site.
 *
 * The originals are React/DCLogic; these are vanilla ports driven by the real
 * product registry instead of placeholder records.
 */
(function () {
  "use strict";

  var products = window.__PRODUCTS || [];
  if (!products.length) return;

  var root = document.documentElement;
  var host = document.getElementById("xp");
  if (!host) return;

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var active = null; // { destroy: fn }

  function el(tag, style, text) {
    var n = document.createElement(tag);
    if (style) n.setAttribute("style", style);
    if (text != null) n.textContent = text;
    return n;
  }

