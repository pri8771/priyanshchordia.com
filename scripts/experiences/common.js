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
  var pageSkip = document.querySelector("body > .skip");
  var pageMain = document.getElementById("main");
  if (!host) return;

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var active = null; // { destroy: fn }

  function el(tag, style, text) {
    var n = document.createElement(tag);
    if (style) n.setAttribute("style", style);
    if (text != null) n.textContent = text;
    return n;
  }

  function isShortcutTarget(e) {
    if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.altKey) return true;
    var target = e.target;
    return !!(target && target.closest &&
      target.closest("a,button,input,select,textarea,[contenteditable=true],[role=dialog]"));
  }

  function dialogFocusables(dialog) {
    return [].slice.call(dialog.querySelectorAll(
      'a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])'
    )).filter(function (node) { return node.offsetParent !== null; });
  }

  function setHostDialog(dialog, on, trigger) {
    var design = document.getElementById("themer2");
    if (on) {
      dialog.__returnFocus = trigger || document.activeElement;
      [].slice.call(host.children).forEach(function (child) {
        if (child !== dialog) child.inert = true;
      });
      if (design) {
        design.disabled = true;
        design.inert = true;
        design.hidden = true;
      }
      if (pageSkip) {
        pageSkip.inert = true;
        pageSkip.hidden = true;
      }
      dialog.style.display = dialog.getAttribute("data-open-display") || "block";
      dialog.setAttribute("aria-hidden", "false");
      var focusables = dialogFocusables(dialog);
      (focusables[0] || dialog).focus();
    } else {
      dialog.style.display = "none";
      dialog.setAttribute("aria-hidden", "true");
      [].slice.call(host.children).forEach(function (child) { child.inert = false; });
      if (design) {
        design.disabled = false;
        design.inert = false;
        design.hidden = false;
      }
      if (pageSkip) {
        pageSkip.inert = false;
        pageSkip.hidden = false;
      }
      var returnFocus = dialog.__returnFocus;
      if (returnFocus && returnFocus.isConnected) returnFocus.focus();
      dialog.__returnFocus = null;
    }
  }

  function trapDialogTab(dialog, e) {
    if (e.key !== "Tab") return;
    var focusables = dialogFocusables(dialog);
    if (!focusables.length) { e.preventDefault(); dialog.focus(); return; }
    var first = focusables[0], last = focusables[focusables.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault(); last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault(); first.focus();
    }
  }

  function installExperienceSkip() {
    var main = host.querySelector("main");
    if (!main) return;
    main.id = "xp-main";
    if (!main.hasAttribute("tabindex")) main.tabIndex = -1;
    if (pageMain) pageMain.hidden = true;
    if (!pageSkip) return;
    pageSkip.textContent = "Skip to experience";
    pageSkip.href = "#xp-main";
    pageSkip.classList.add("xp-skip");
    pageSkip.onclick = function () {
      var currentMain = host.querySelector("main");
      if (currentMain) currentMain.focus();
    };
  }

  function restorePageSkip() {
    if (pageMain) pageMain.hidden = false;
    if (!pageSkip) return;
    pageSkip.hidden = false;
    pageSkip.inert = false;
    pageSkip.textContent = "Skip to content";
    pageSkip.href = "#main";
    pageSkip.classList.remove("xp-skip");
    pageSkip.onclick = null;
  }
