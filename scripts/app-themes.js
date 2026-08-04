(function () {
  "use strict";

  var root = document.querySelector("[data-app-landing]");
  var picker = root && root.querySelector("[data-app-theme-picker]");
  var description = root && root.querySelector("[data-app-theme-description]");
  if (!root || !picker || !description) return;

  var app = root.getAttribute("data-app") || "app";
  var storageKey = "pc-app-theme-" + app;
  var allowed = Array.prototype.map.call(picker.options, function (option) {
    return option.value;
  });

  function isAllowed(value) {
    return allowed.indexOf(value) >= 0;
  }

  function apply(value, remember, updateUrl) {
    if (!isAllowed(value)) value = allowed[0];
    root.setAttribute("data-app-theme", value);
    picker.value = value;
    var selected = picker.options[picker.selectedIndex];
    description.textContent = selected.getAttribute("data-principle") || "";
    root.querySelectorAll("[data-app-scene]").forEach(function (scene) {
      scene.hidden = scene.getAttribute("data-app-scene") !== value;
    });
    if (remember) {
      try { localStorage.setItem(storageKey, value); } catch (error) {}
    }
    if (updateUrl && window.history && window.URL) {
      var url = new URL(window.location.href);
      url.searchParams.set("design", value);
      window.history.replaceState(null, "", url.pathname + url.search + url.hash);
    }
  }

  var initial = "";
  try { initial = new URL(window.location.href).searchParams.get("design") || ""; } catch (error) {}
  if (!isAllowed(initial)) {
    try { initial = localStorage.getItem(storageKey) || ""; } catch (error) {}
  }
  apply(isAllowed(initial) ? initial : allowed[0], false, false);

  picker.addEventListener("change", function () {
    apply(picker.value, true, true);
  });
})();
