  /* ------------------------------------------------------------------ */
  var REGISTRY = {
    "unknown-signal": unknownSignal,
    "overworld": overworld,
    "cabinet": cabinet,
    "parallel": parallel
  };

  function sync() {
    var theme = root.getAttribute("data-theme");
    if (active) {
      var previous = active;
      active = null;
      try {
        previous.destroy();
      } catch (destroyError) {
        console.error("Experience teardown failed; continuing with a clean host.", destroyError);
      }
    }
    host.innerHTML = "";
    host.className = "xp";
    host.removeAttribute("style");
    restorePageSkip();
    root.classList.remove("has-xp");
    if (!REGISTRY[theme]) return;
    var next = null;
    try {
      next = REGISTRY[theme]();
      active = next;
      installExperienceSkip();
      root.classList.add("has-xp");
    } catch (err) {
      if (next && typeof next.destroy === "function") {
        try { next.destroy(); } catch (cleanupError) {
          console.error("Failed to clean up an unavailable experience.", cleanupError);
        }
      }
      active = null;
      host.innerHTML = "";
      host.className = "xp";
      host.removeAttribute("style");
      restorePageSkip();
      console.error("Experience unavailable; showing the accessible catalogue.", err);
    }
  }

  new MutationObserver(sync).observe(root, { attributes: true, attributeFilter: ["data-theme"] });
  sync();
})();
