  /* ------------------------------------------------------------------ */
  var REGISTRY = {
    "unknown-signal": unknownSignal,
    "overworld": overworld,
    "cabinet": cabinet,
    "parallel": parallel
  };

  function sync() {
    var theme = root.getAttribute("data-theme");
    if (active) { active.destroy(); active = null; }
    root.classList.toggle("has-xp", !!REGISTRY[theme]);
    if (REGISTRY[theme]) active = REGISTRY[theme]();
  }

  new MutationObserver(sync).observe(root, { attributes: true, attributeFilter: ["data-theme"] });
  sync();
})();
