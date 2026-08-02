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

  /* ------------------------------------------------------------------ *
   * UNKNOWN SIGNAL — CRT receiver. Each product is a carrier on a band.
   * ------------------------------------------------------------------ */
  var SCRAMBLE = "▚▞█▓▒░#%&@*+=<>/\\|01";

  function unknownSignal() {
    var carriers = products.map(function (p, i) {
      return {
        code: "P" + String(i + 1).padStart(3, "0"),
        name: p.name.toUpperCase(),
        domain: p.lane,
        body: p.summary,
        href: p.href,
        f: 4 + (i * 92) / Math.max(1, products.length - 1),
        band: (14.4 + i * 0.062).toFixed(3) + " MHz"
      };
    });

    var freq = carriers[0].f, typeTimer = null, nameTimer = null, specTimer = null, ro = null;

    host.innerHTML = "";
    host.className = "xp xp-us";

    var scan = el("div", "position:absolute;inset:0;z-index:6;pointer-events:none;background:repeating-linear-gradient(180deg,rgba(255,255,255,.028) 0 1px,transparent 1px 3px);mix-blend-mode:screen");
    var vig = el("div", "position:absolute;inset:0;z-index:5;pointer-events:none;background:radial-gradient(120% 90% at 50% 45%,transparent 40%,rgba(0,0,0,.85) 100%)");
    scan.setAttribute("aria-hidden", "true");
    vig.setAttribute("aria-hidden", "true");

    var nav = el("nav", "display:flex;align-items:center;gap:clamp(12px,2.6vw,32px);padding:16px clamp(14px,3vw,34px);font:400 10.5px/1 ui-monospace,monospace;letter-spacing:.2em;text-transform:uppercase;border-bottom:1px solid #171310;position:relative;z-index:7");
    var catalogLink = null;
    [
      { label: "Catalog", href: "#archive" },
      { label: "Apps", href: "apps/" },
      { label: "Journal", href: "journal/" }
    ].forEach(function (item) {
      var t = item.label;
      var a = el("a", "color:#8a8377;text-decoration:none", t);
      a.href = item.href;
      if (t === "Catalog") catalogLink = a;
      a.onmouseenter = function () { a.style.color = "#ffb347"; };
      a.onmouseleave = function () { a.style.color = "#8a8377"; };
      nav.appendChild(a);
    });
    var rx = el("span", "margin-left:auto;color:#8f877b;letter-spacing:.14em", "RX · 0.7µV · unattended");
    nav.appendChild(rx);

    var main = el("main", "position:relative;z-index:7;display:grid;grid-template-columns:minmax(0,1fr);align-content:center;justify-items:center;gap:clamp(16px,3vh,30px);padding:clamp(16px,4vh,44px) clamp(16px,4vw,44px);min-height:0;overflow:auto");
    main.appendChild(el("div", "font:400 10.5px/1 ui-monospace,monospace;letter-spacing:.28em;text-transform:uppercase;color:#989186;text-align:center", "carrier detected · source unidentified · identifies itself only as"));

    var h1 = el("h1", "margin:0;text-align:center;font:700 clamp(30px,8.4vw,120px)/.95 ui-monospace,monospace;letter-spacing:-.03em;color:#f6f1e6;text-shadow:0 0 34px rgba(255,179,71,.22)");
    var nameSpan = el("span", null, "USEFUL SIGNALS");
    nameSpan.setAttribute("aria-hidden", "true");
    h1.setAttribute("aria-label", "Useful signals");
    h1.appendChild(nameSpan);
    main.appendChild(h1);

    var panel = el("div", "width:min(760px,100%);border:1px solid #201a15;background:linear-gradient(#08070600,#0b0907)");
    var head = el("div", "display:flex;align-items:center;gap:12px;padding:11px 14px;border-bottom:1px solid #201a15;font:400 10px/1 ui-monospace,monospace;letter-spacing:.16em;text-transform:uppercase;color:#a09889;flex-wrap:wrap");
    var lock = el("span", "color:#6b6257", "●");
    var status = el("span", null, "searching");
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    var freqLabel = el("span", "margin-left:auto", "");
    head.append(lock, status, freqLabel);

    var bodyWrap = el("div", "padding:16px 16px 18px;min-height:186px");
    var codeRow = el("div", "display:flex;gap:10px 22px;flex-wrap:wrap;font:400 10.5px/1 ui-monospace,monospace;letter-spacing:.14em;text-transform:uppercase;color:#ffb347;margin-bottom:12px");
    var cCode = el("span"), cName = el("span", "color:#cfc7b8"), cDom = el("span", "color:#a09889");
    codeRow.append(cCode, cName, cDom);
    var para = el("p", "margin:0 0 14px;font:400 14.5px/1.68 system-ui,sans-serif;color:#d6cfc2;max-width:66ch;min-height:3em");
    var caret = el("span", "display:inline-block;width:9px;height:16px;background:#ffb347;vertical-align:-3px;margin-left:3px;animation:sig-caret 1s steps(1) infinite");
    var actions = el("div", "display:flex;gap:8px;flex-wrap:wrap");
    var openRec = el("a", "border:1px solid #2a231c;padding:9px 12px;font:400 10px/1 ui-monospace,monospace;letter-spacing:.14em;text-transform:uppercase;color:#cfc7b8;text-decoration:none", "Open record");
    openRec.hidden = true;
    var arcBtn = el("a", "border:1px solid #2a231c;padding:9px 12px;font:400 10px/1 ui-monospace,monospace;letter-spacing:.14em;text-transform:uppercase;color:#cfc7b8;text-decoration:none;cursor:pointer", "Decoded archive");
    arcBtn.href = "#archive";
    actions.append(openRec, arcBtn);
    bodyWrap.append(codeRow, para, actions);
    panel.append(head, bodyWrap);
    main.appendChild(panel);

    var footer = el("footer", "position:relative;z-index:7;border-top:1px solid #171310;padding:12px clamp(14px,3vw,34px) 14px;display:grid;grid-template-columns:minmax(0,1fr);gap:10px");
    var canvas = el("canvas", "display:block;width:100%;height:clamp(56px,10vh,104px)");
    canvas.setAttribute("role", "img");
    canvas.setAttribute("aria-label", "Spectrum display. " + carriers.length + " carriers; every record is listed in the decoded archive.");
    var band = el("div", "position:relative;height:44px;border:1px solid #201a15;background:#050403;cursor:ew-resize;touch-action:none");
    band.setAttribute("role", "slider");
    band.tabIndex = 0;
    band.setAttribute("aria-label", "Tuning");
    band.setAttribute("aria-valuemin", "0");
    band.setAttribute("aria-valuemax", "100");
    band.appendChild(el("div", "position:absolute;inset:0;background:repeating-linear-gradient(90deg,#241d16 0 1px,transparent 1px 22px)"));
    var needle = el("div", "position:absolute;top:-6px;bottom:-6px;width:2px;background:#ffb347;box-shadow:0 0 12px rgba(255,179,71,.8);will-change:transform");
    band.appendChild(needle);
    band.appendChild(el("div", "position:absolute;left:8px;bottom:5px;font:400 9.5px/1 ui-monospace,monospace;letter-spacing:.16em;text-transform:uppercase;color:#8f877b", "drag to tune · ← → keys · " + carriers.length + " carriers in this band"));
    var ctrls = el("div", "display:flex;align-items:center;gap:8px;flex-wrap:wrap;font:400 10px/1 ui-monospace,monospace;letter-spacing:.14em;text-transform:uppercase");
    var bStyle = "appearance:none;border:1px solid #2a231c;background:#0a0806;color:#cfc7b8;padding:10px 12px;cursor:pointer;font:inherit;letter-spacing:inherit;text-transform:inherit";
    var prev = el("button", bStyle, "← Prev carrier"), next = el("button", bStyle, "Next carrier →");
    var hint = el("span", "margin-left:auto;color:#8f877b", "press A for archive");
    ctrls.append(prev, next, hint);
    footer.append(canvas, band, ctrls);

    host.append(scan, vig, nav, main, footer);

    /* archive overlay ------------------------------------------------- */
    var archive = el("div", "position:absolute;inset:0;z-index:9;background:rgba(4,3,2,.96);display:none;overflow:auto;padding:clamp(18px,5vh,60px) clamp(16px,5vw,60px)");
    archive.id = "archive";
    archive.tabIndex = -1;
    archive.setAttribute("role", "dialog");
    archive.setAttribute("aria-modal", "true");
    archive.setAttribute("aria-labelledby", "archive-title");
    archive.setAttribute("aria-hidden", "true");
    var arcInner = el("div", "max-width:1000px;margin:auto");
    var archiveHead = el("div", "display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:18px");
    var archiveTitle = el("h2", "margin:0;font:400 10px/1 ui-monospace,monospace;letter-spacing:.3em;text-transform:uppercase;color:#ffb347", "decoded archive · " + carriers.length + " records");
    archiveTitle.id = "archive-title";
    var archiveClose = el("button", null, "Close");
    archiveClose.className = "xp-dialog-close";
    archiveHead.append(archiveTitle, archiveClose);
    arcInner.appendChild(archiveHead);
    carriers.forEach(function (c) {
      var row = el("a", "display:grid;grid-template-columns:70px 200px 1fr;gap:18px;padding:14px 0;border-bottom:1px solid #201a15;text-decoration:none;align-items:baseline");
      row.className = "xp-list-row";
      row.href = c.href;
      row.append(
        el("span", "font:400 10px/1 ui-monospace,monospace;color:#ffb347;letter-spacing:.14em", c.code),
        el("span", "font:700 13px/1.3 ui-monospace,monospace;letter-spacing:.06em;color:#cfc7b8", c.name),
        el("span", "font:400 12px/1.6 system-ui,sans-serif;color:#8f877b", c.body)
      );
      arcInner.appendChild(row);
    });
    archive.appendChild(arcInner);
    host.appendChild(archive);

    function toggleArchive(on, trigger) {
      setHostDialog(archive, on, trigger || arcBtn);
      arcBtn.setAttribute("aria-expanded", String(on));
    }
    arcBtn.setAttribute("aria-controls", "archive");
    arcBtn.setAttribute("aria-expanded", "false");
    arcBtn.onclick = function (e) { e.preventDefault(); toggleArchive(archive.style.display !== "block"); };
    archiveClose.onclick = function () { toggleArchive(false); };
    archive.addEventListener("keydown", function (e) {
      trapDialogTab(archive, e);
      if (e.key === "Escape") { e.preventDefault(); toggleArchive(false); }
    });
    if (catalogLink) {
      catalogLink.onclick = function (e) { e.preventDefault(); toggleArchive(true, catalogLink); };
    }

    /* nearest carrier + lock ------------------------------------------ */
    function nearest() {
      var best = carriers[0], d = 1e9;
      carriers.forEach(function (c) {
        var dd = Math.abs(c.f - freq);
        if (dd < d) { d = dd; best = c; }
      });
      return { c: best, d: d };
    }

    var shownCode = null, shownStatus = null;
    function render() {
      var n = nearest(), locked = n.d < 2.2;
      var nextStatus = locked ? "carrier locked" : (n.d < 7 ? "signal near" : "searching");
      freqLabel.textContent = n.c.band;
      lock.style.color = locked ? "#ffb347" : "#6b6257";
      if (nextStatus !== shownStatus) {
        shownStatus = nextStatus;
        status.textContent = nextStatus;
      }
      band.setAttribute("aria-valuenow", String(Math.round(freq)));
      band.setAttribute("aria-valuetext", (locked ? "Locked: " + n.c.name : "Searching") + ", position " + Math.round(freq));
      needle.style.transform = "translateX(" + (freq / 100) * band.clientWidth + "px)";

      if (locked && n.c.code !== shownCode) {
        shownCode = n.c.code;
        cCode.textContent = n.c.code;
        cName.textContent = n.c.name;
        cDom.textContent = n.c.domain;
        openRec.href = n.c.href;
        openRec.hidden = false;
        typeOut(n.c.body);
      } else if (!locked && shownCode) {
        shownCode = null;
        clearInterval(typeTimer);
        cCode.textContent = ""; cName.textContent = ""; cDom.textContent = "";
        para.textContent = "";
        para.appendChild(caret);
        openRec.removeAttribute("href");
        openRec.hidden = true;
      }
    }

    function typeOut(text) {
      clearInterval(typeTimer);
      if (reduce) { para.textContent = text; para.appendChild(caret); return; }
      var i = 0;
      para.textContent = "";
      para.appendChild(caret);
      typeTimer = setInterval(function () {
        i += 2;
        para.textContent = text.slice(0, i);
        para.appendChild(caret);
        if (i >= text.length) clearInterval(typeTimer);
      }, 16);
    }

    function tune(v) {
      freq = Math.max(0, Math.min(100, v));
      render();
      if (reduce) drawSpec();
    }

    /* spectrum canvas -------------------------------------------------- */
    var noise = new Array(240).fill(0).map(function () { return Math.random(); });
    function sizeSpec() {
      var r = canvas.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.max(1, Math.floor(r.width * dpr));
      canvas.height = Math.max(1, Math.floor(r.height * dpr));
    }
    function drawSpec() {
      var ctx = canvas.getContext("2d");
      if (!ctx) return;
      var w = canvas.width, h = canvas.height;
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = "#050403";
      ctx.fillRect(0, 0, w, h);
      ctx.strokeStyle = "#1b1610";
      ctx.lineWidth = 1;
      for (var g = 0; g <= 10; g++) {
        var gx = (g / 10) * w;
        ctx.beginPath(); ctx.moveTo(gx, 0); ctx.lineTo(gx, h); ctx.stroke();
      }
      ctx.beginPath();
      for (var x = 0; x < w; x++) {
        var pct = (x / w) * 100;
        var amp = noise[(x + (reduce ? 0 : Date.now() / 40 | 0)) % noise.length] * 0.16;
        carriers.forEach(function (c) {
          var d = Math.abs(pct - c.f);
          amp += Math.exp(-(d * d) / 5) * 0.72;
        });
        var y = h - amp * h * 0.92;
        if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.strokeStyle = "#ffb347";
      ctx.lineWidth = Math.min(window.devicePixelRatio || 1, 2) * 1.1;
      ctx.stroke();
      var nx = (freq / 100) * w;
      ctx.strokeStyle = "rgba(255,179,71,.45)";
      ctx.beginPath(); ctx.moveTo(nx, 0); ctx.lineTo(nx, h); ctx.stroke();
    }

    /* interaction ------------------------------------------------------ */
    var dragging = false;
    function fromEvent(e) {
      var r = band.getBoundingClientRect();
      tune(((e.clientX - r.left) / r.width) * 100);
    }
    band.addEventListener("pointerdown", function (e) { dragging = true; band.setPointerCapture(e.pointerId); fromEvent(e); });
    band.addEventListener("pointermove", function (e) { if (dragging) fromEvent(e); });
    band.addEventListener("pointerup", function () { dragging = false; });
    band.addEventListener("pointercancel", function () { dragging = false; });
    band.addEventListener("lostpointercapture", function () { dragging = false; });
    band.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") { e.preventDefault(); e.stopPropagation(); tune(freq - 1.5); }
      if (e.key === "ArrowRight") { e.preventDefault(); e.stopPropagation(); tune(freq + 1.5); }
      if (e.key === "PageDown") { e.preventDefault(); e.stopPropagation(); tune(freq - 10); }
      if (e.key === "PageUp") { e.preventDefault(); e.stopPropagation(); tune(freq + 10); }
      if (e.key === "Home") { e.preventDefault(); e.stopPropagation(); tune(0); }
      if (e.key === "End") { e.preventDefault(); e.stopPropagation(); tune(100); }
    });
    function step(dir) {
      var sorted = carriers.slice().sort(function (a, b) { return a.f - b.f; });
      var i = sorted.findIndex(function (c) { return dir > 0 ? c.f > freq + 0.6 : c.f < freq - 0.6; });
      if (dir < 0) { for (var j = sorted.length - 1; j >= 0; j--) if (sorted[j].f < freq - 0.6) { i = j; break; } }
      if (i < 0) i = dir > 0 ? 0 : sorted.length - 1;
      tune(sorted[i].f);
    }
    prev.onclick = function () { step(-1); };
    next.onclick = function () { step(1); };

    var onKey = function (e) {
      if (isShortcutTarget(e)) return;
      if (e.key.toLowerCase() === "a") toggleArchive(archive.style.display !== "block");
      if (e.key === "Escape" && archive.style.display === "block") toggleArchive(false);
      if (e.key === "ArrowLeft" || e.key === "ArrowRight") { e.preventDefault(); tune(freq + (e.key === "ArrowLeft" ? -1.5 : 1.5)); }
    };
    window.addEventListener("keydown", onKey);

    /* scramble-decode headline ---------------------------------------- */
    if (!reduce) {
      var target = "USEFUL SIGNALS", stepN = 0;
      nameTimer = setInterval(function () {
        stepN++;
        var solved = Math.floor(stepN / 2), out = "";
        for (var i = 0; i < target.length; i++) {
          if (target[i] === " ") { out += " "; continue; }
          out += i < solved ? target[i] : SCRAMBLE[Math.floor(Math.random() * SCRAMBLE.length)];
        }
        nameSpan.textContent = out;
        if (solved > target.length) { clearInterval(nameTimer); nameSpan.textContent = target; }
      }, 55);
    }

    sizeSpec();
    drawSpec();
    if (window.ResizeObserver) {
      ro = new ResizeObserver(function () { sizeSpec(); drawSpec(); });
      ro.observe(canvas);
    }
    if (!reduce) {
      specTimer = setInterval(function () { if (!document.hidden) drawSpec(); }, 1000 / 24);
    }
    render();

    return {
      destroy: function () {
        if (archive.style.display === "block") setHostDialog(archive, false);
        clearInterval(typeTimer); clearInterval(nameTimer); clearInterval(specTimer);
        window.removeEventListener("keydown", onKey);
        if (ro) ro.disconnect();
        host.innerHTML = "";
        host.className = "xp";
      }
    };
  }

  /* ------------------------------------------------------------------ *
   * OVERWORLD — a signal maze; every project is a stationary receiver.
   * ------------------------------------------------------------------ */
  function overworld() {
    var W = 32, H = 20, TUNNEL_ROW = 10;

    /*
     * The terrain vocabulary survives from the earlier overworld, but every
     * solid tile is now rendered as circuitry. The extra blocks below turn
     * the field into an original connected maze with a side-to-side tunnel.
     */
    var grid = [];
    for (var y = 0; y < H; y++) grid.push(new Array(W).fill("."));
    for (var x = 0; x < W; x++) { grid[0][x] = "#"; grid[H - 1][x] = "#"; }
    for (var y2 = 0; y2 < H; y2++) { grid[y2][0] = "#"; grid[y2][W - 1] = "#"; }
    for (var wy = 2; wy <= 5; wy++) for (var wx = 2; wx <= 7; wx++) grid[wy][wx] = "~";
    [[11,6],[12,6],[13,6],[11,7],[24,15],[25,15],[26,15],[28,15],[29,15],[24,16],[24,17],[24,18],[29,16],[29,17],[29,18],[25,18],[26,18],[27,18],[28,18]]
      .forEach(function (c) { grid[c[1]][c[0]] = "#"; });
    [[9,2],[15,6],[19,6],[22,14],[25,14],[6,12],[8,18],[30,7],[12,18],[17,11],[21,2],[5,6],[30,13],[2,9]]
      .forEach(function (c) { grid[c[1]][c[0]] = "T"; });

    var MAZE_BLOCKS = [
      [10,2,4,2],[17,2,4,2],[24,2,6,2],
      [9,4,2,3],[14,4,4,2],[21,4,2,3],[26,4,3,2],
      [2,7,4,2],[8,8,4,2],[14,7,4,2],[20,8,4,2],[27,7,3,2],
      [4,11,3,3],[9,12,4,2],[15,12,3,3],[21,12,4,2],[27,11,3,3],
      [2,15,4,2],[8,15,4,2],[14,16,5,2],[21,15,4,2]
    ];
    MAZE_BLOCKS.forEach(function (r) {
      for (var by = r[1]; by < r[1] + r[3]; by++)
        for (var bx = r[0]; bx < r[0] + r[2]; bx++) grid[by][bx] = "#";
    });

    // The center lane is the wrap tunnel. Power signals and the bonus remain
    // ordinary walkable cells, so they never interrupt corridor mechanics.
    for (var tx = 0; tx < W; tx++) grid[TUNNEL_ROW][tx] = ".";
    grid[16][27] = "s";
    var SHARDS = [[7,4],[26,17],[3,15],[20,17],[29,3]];
    SHARDS.forEach(function (c) { grid[c[1]][c[0]] = "c"; });

    var spawn = { x: 16, y: TUNNEL_ROW };
    function keyFor(x, y) { return x + "," + y; }
    function solidCell(x, y) {
      if (x < 0 || y < 0 || x >= W || y >= H) return true;
      var tile = grid[y][x];
      return tile === "#" || tile === "~" || tile === "T";
    }

    // Reachability is calculated from the actual maze, including the tunnel.
    // Project targets can therefore only be placed in the player's component.
    function reachableFrom(start) {
      var queue = [[start.x, start.y]], head = 0, out = [], seen = {};
      seen[keyFor(start.x, start.y)] = true;
      while (head < queue.length) {
        var current = queue[head++], cx = current[0], cy = current[1];
        out.push(current);
        [[-1,0],[1,0],[0,-1],[0,1]].forEach(function (d) {
          var nx = cx + d[0], ny = cy + d[1];
          if (cy === TUNNEL_ROW && nx < 0) nx = W - 1;
          if (cy === TUNNEL_ROW && nx >= W) nx = 0;
          var k = keyFor(nx, ny);
          if (!solidCell(nx, ny) && !seen[k]) {
            seen[k] = true;
            queue.push([nx, ny]);
          }
        });
      }
      return { cells: out, seen: seen };
    }

    var component = reachableFrom(spawn);
    var PREFERRED_TARGETS = [
      [3,1],[15,1],[28,1],
      [8,4],[14,3],[24,4],[30,5],
      [2,6],[16,6],[26,6],
      [7,9],[18,9],[29,9],
      [2,14],[13,14],[26,14],[20,18]
    ];
    var targets = [], targetByCell = {}, usedTargetCells = {};
    products.forEach(function (product, i) {
      var preferred = PREFERRED_TARGETS[i];
      var cell = preferred && component.seen[keyFor(preferred[0], preferred[1])] &&
        !usedTargetCells[keyFor(preferred[0], preferred[1])] ? preferred : null;
      if (!cell) {
        cell = component.cells.find(function (candidate) {
          var k = keyFor(candidate[0], candidate[1]);
          return !usedTargetCells[k] && k !== keyFor(spawn.x, spawn.y) &&
            Math.abs(candidate[0] - spawn.x) + Math.abs(candidate[1] - spawn.y) > 3;
        });
      }
      if (!cell) return;
      var target = { x: cell[0], y: cell[1], p: product, n: i + 1 };
      targets.push(target);
      usedTargetCells[keyFor(target.x, target.y)] = true;
      targetByCell[keyFor(target.x, target.y)] = target;
    });

    var powerSignals = {}, pips = {}, signals = 0, signalTotal = 0;
    SHARDS.forEach(function (c) {
      var k = keyFor(c[0], c[1]);
      if (component.seen[k]) { powerSignals[k] = true; signalTotal++; }
    });
    var bonusKey = keyFor(27, 16), bonusAvailable = !!component.seen[bonusKey];
    if (bonusAvailable) signalTotal++;
    component.cells.forEach(function (cell) {
      var k = keyFor(cell[0], cell[1]);
      if (k !== keyFor(spawn.x, spawn.y) && !targetByCell[k] &&
          !powerSignals[k] && k !== bonusKey) {
        pips[k] = true;
        signalTotal++;
      }
    });

    host.innerHTML = "";
    host.className = "xp xp-ow";
    host.style.background = "#05070a";
    host.style.color = "#e9f2e4";
    host.style.fontFamily = "system-ui,'Helvetica Neue',Arial,sans-serif";
    host.style.gridTemplateRows = "auto auto 1fr auto";

    var nav = el("nav", "display:flex;align-items:center;gap:clamp(12px,2.4vw,30px);padding:14px clamp(14px,3vw,30px) 12px;font:400 10.5px/1 ui-monospace,monospace;letter-spacing:.18em;text-transform:uppercase;border-bottom:1px solid #12191f");
    var a1 = el("a", "color:#8fa094;text-decoration:none", "Catalog"); a1.href = "#";
    var a2 = el("a", "color:#8fa094;text-decoration:none", "Apps"); a2.href = "apps/";
    var a3 = el("a", "color:#8fa094;text-decoration:none", "Journal"); a3.href = "journal/";
    nav.append(a1, a2, a3, el("span", "margin-left:auto;color:#8d9a91;letter-spacing:.12em", "signal maze · " + targets.length + " targets"));

    var header = el("header", "display:flex;align-items:baseline;justify-content:center;padding:clamp(12px,2.4vh,22px) 16px clamp(8px,1.6vh,14px)");
    header.appendChild(el("h1", "margin:0;font:700 clamp(15px,3.2vw,34px)/1.25 ui-monospace,monospace;letter-spacing:.09em;color:#f2f7ee;text-shadow:0 4px 0 #1d2a1e,0 0 26px rgba(155,227,111,.16);text-align:center", "USEFUL SIGNALS // MAZE"));

    var wrap = el("main", "position:relative;min-height:0;overflow:hidden");
    var canvas = el("canvas", "display:block;width:100%;height:100%;image-rendering:pixelated;touch-action:none");
    canvas.setAttribute("role", "img");
    canvas.tabIndex = 0;
    canvas.setAttribute(
      "aria-label",
      "Interactive signal maze with " + targets.length + " stationary project targets. " +
      "Use arrow keys or W A S D to steer. Turns are buffered, the side tunnel wraps, " +
      "and touching a target opens its project. Every project is also available in the Catalog index."
    );

    var hud = el("div", "position:absolute;top:10px;left:12px;display:flex;flex-direction:column;gap:4px;font:700 10px/1.55 ui-monospace,monospace;color:#9fada3;pointer-events:none;text-shadow:0 2px 0 #05070a");
    var signalLabel = el("span", null, "SIGNALS 0/" + signalTotal);
    var targetLabel = el("span", null, "TARGETS " + targets.length);
    var eventLabel = el("span", "color:#9be36f", "");
    eventLabel.setAttribute("role", "status");
    eventLabel.setAttribute("aria-live", "polite");
    hud.append(signalLabel, targetLabel, eventLabel);

    var idxBtn = el("button", "position:absolute;top:10px;right:12px;appearance:none;border:2px solid #24312a;background:#0a1010;color:#cfe0c8;padding:8px 12px;font:700 10px/1 ui-monospace,monospace;letter-spacing:.16em;text-transform:uppercase;cursor:pointer", "Index (I)");
    idxBtn.setAttribute("aria-expanded", "false");

    var STOP = { name: "stop", x: 0, y: 0 };
    var DIRS = {
      left: { name: "left", x: -1, y: 0 },
      right: { name: "right", x: 1, y: 0 },
      up: { name: "up", x: 0, y: -1 },
      down: { name: "down", x: 0, y: 1 }
    };
    var direction = STOP, wanted = STOP, facing = DIRS.left;
    var pos = { x: spawn.x, y: spawn.y };
    var navigating = false, paused = false;

    function queueDirection(name) {
      if (DIRS[name]) wanted = DIRS[name];
    }

    var dpad = el("div");
    dpad.className = "ow-dpad";
    dpad.setAttribute("role", "group");
    dpad.setAttribute("aria-label", "Maze movement");
    [
      { dir: "up", label: "Turn up", text: "↑", cls: "up" },
      { dir: "left", label: "Turn left", text: "←", cls: "left" },
      { dir: "down", label: "Turn down", text: "↓", cls: "down" },
      { dir: "right", label: "Turn right", text: "→", cls: "right" }
    ].forEach(function (item) {
      var button = el("button", null, item.text);
      button.className = item.cls;
      button.setAttribute("aria-label", item.label);
      button.addEventListener("pointerdown", function (e) {
        e.preventDefault();
        queueDirection(item.dir);
        button.setPointerCapture(e.pointerId);
        canvas.focus();
      });
      button.addEventListener("click", function () { queueDirection(item.dir); });
      dpad.appendChild(button);
    });
    wrap.append(canvas, hud, idxBtn, dpad);

    var foot = el("footer", "border-top:1px solid #12191f;padding:10px clamp(14px,3vw,30px) 14px;font:400 10px/1.35 ui-monospace,monospace;letter-spacing:.14em;text-transform:uppercase;color:#8d9a91;display:flex;gap:16px;flex-wrap:wrap");
    foot.append(
      el("span", null, "arrows / WASD buffer the next turn"),
      el("span", null, "side tunnel wraps"),
      el("span", "margin-left:auto", "touch a project signal to open · I index")
    );

    host.append(nav, header, wrap, foot);

    /* accessible project index --------------------------------------- */
    var index = el("div", "position:absolute;inset:0;z-index:10;display:none;overflow:auto;background:rgba(5,7,10,.97);padding:clamp(18px,5vh,54px) clamp(16px,5vw,54px)");
    index.id = "overworld-index";
    index.tabIndex = -1;
    index.setAttribute("role", "dialog");
    index.setAttribute("aria-modal", "true");
    index.setAttribute("aria-labelledby", "overworld-index-title");
    index.setAttribute("aria-hidden", "true");
    host.appendChild(index);
    idxBtn.setAttribute("aria-controls", "overworld-index");

    var openDialog = null;
    function closeAll() {
      if (openDialog) setHostDialog(openDialog, false);
      openDialog = null;
      idxBtn.setAttribute("aria-expanded", "false");
    }
    function buildIndex() {
      index.innerHTML = "";
      var inner = el("div", "max-width:980px;margin:auto");
      var indexHead = el("div", "display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:18px");
      var indexTitle = el("h2", "margin:0;font:700 10px/1 ui-monospace,monospace;letter-spacing:.24em;text-transform:uppercase;color:#9be36f", "project index · " + targets.length + " signals");
      indexTitle.id = "overworld-index-title";
      var indexClose = el("button", null, "Close");
      indexClose.className = "xp-dialog-close";
      indexClose.onclick = closeAll;
      indexHead.append(indexTitle, indexClose);
      inner.appendChild(indexHead);
      targets.forEach(function (target) {
        var row = el("a", "display:grid;grid-template-columns:64px 190px 1fr;gap:18px;padding:13px 0;border-bottom:1px solid #12191f;text-decoration:none;align-items:baseline");
        row.className = "xp-list-row";
        row.href = target.p.href;
        row.append(
          el("span", "font:700 10px/1 ui-monospace,monospace;color:#9be36f;letter-spacing:.14em", "P" + String(target.n).padStart(3, "0")),
          el("span", "font:700 15px/1.2 system-ui,sans-serif;color:#e9f2e4", target.p.name),
          el("span", "font:400 13px/1.55 system-ui,sans-serif;color:#8fa094", target.p.summary)
        );
        inner.appendChild(row);
      });
      index.appendChild(inner);
    }
    buildIndex();
    function toggleIndex(trigger) {
      var on = index.style.display !== "block";
      closeAll();
      if (on) {
        openDialog = index;
        idxBtn.setAttribute("aria-expanded", "true");
        setHostDialog(index, true, trigger || idxBtn);
      }
    }
    idxBtn.onclick = function () { toggleIndex(idxBtn); };
    a1.onclick = function (e) { e.preventDefault(); toggleIndex(a1); };
    index.addEventListener("keydown", function (e) {
      trapDialogTab(index, e);
      if (e.key === "Escape") { e.preventDefault(); closeAll(); }
    });

    /* grid movement --------------------------------------------------- */
    var SPEED = 5.7, EPS = 0.0001;
    function canMoveFrom(cx, cy, dir) {
      if (!dir || (!dir.x && !dir.y)) return false;
      var nx = cx + dir.x, ny = cy + dir.y;
      if (cy === TUNNEL_ROW && dir.y === 0 && nx < 0) nx = W - 1;
      if (cy === TUNNEL_ROW && dir.y === 0 && nx >= W) nx = 0;
      return !solidCell(nx, ny);
    }
    function opposite(a, b) {
      return a && b && a.x === -b.x && a.y === -b.y &&
        (a.x !== 0 || a.y !== 0);
    }
    function navigateToTarget(target) {
      if (navigating) return;
      navigating = true;
      direction = STOP;
      eventLabel.textContent = "OPENING " + target.p.name.toUpperCase();
      canvas.setAttribute("aria-label", "Opening project: " + target.p.name);
      window.location.assign(target.p.href);
    }
    function handleCell(cx, cy) {
      var k = keyFor(cx, cy), target = targetByCell[k];
      if (target) { navigateToTarget(target); return; }
      if (pips[k]) {
        delete pips[k];
        signals++;
        signalLabel.textContent = "SIGNALS " + signals + "/" + signalTotal;
      }
      if (powerSignals[k]) {
        delete powerSignals[k];
        grid[cy][cx] = ".";
        signals++;
        signalLabel.textContent = "SIGNALS " + signals + "/" + signalTotal;
      }
      if (bonusAvailable && k === bonusKey) {
        bonusAvailable = false;
        grid[cy][cx] = ".";
        signals++;
        signalLabel.textContent = "SIGNALS " + signals + "/" + signalTotal;
        eventLabel.textContent = "BONUS CHANNEL FOUND";
      }
    }
    function processCenter() {
      var cx = Math.round(pos.x), cy = Math.round(pos.y);
      pos.x = cx; pos.y = cy;
      handleCell(cx, cy);
      if (navigating) return;
      if (canMoveFrom(cx, cy, wanted)) direction = wanted;
      if (!canMoveFrom(cx, cy, direction)) direction = STOP;
      if (direction !== STOP) facing = direction;
    }
    function wrapPosition() {
      if (Math.round(pos.y) !== TUNNEL_ROW) return;
      if (pos.x <= -1 + EPS) pos.x = W - 1;
      else if (pos.x >= W - EPS) pos.x = 0;
    }
    function advance(dt) {
      if (navigating || paused || index.style.display === "block") return false;
      var remaining = SPEED * Math.min(dt, 0.08), moved = false;
      if (opposite(wanted, direction)) {
        direction = wanted;
        facing = direction;
      }
      while (remaining > EPS && !navigating) {
        wrapPosition();
        var rx = Math.round(pos.x), ry = Math.round(pos.y);
        if (Math.abs(pos.x - rx) < EPS && Math.abs(pos.y - ry) < EPS) {
          processCenter();
          if (direction === STOP || navigating) break;
        }

        var targetCoordinate, distance;
        if (direction.x > 0) {
          targetCoordinate = Math.floor(pos.x + EPS) + 1;
          distance = targetCoordinate - pos.x;
        } else if (direction.x < 0) {
          targetCoordinate = Math.ceil(pos.x - EPS) - 1;
          distance = pos.x - targetCoordinate;
        } else if (direction.y > 0) {
          targetCoordinate = Math.floor(pos.y + EPS) + 1;
          distance = targetCoordinate - pos.y;
        } else {
          targetCoordinate = Math.ceil(pos.y - EPS) - 1;
          distance = pos.y - targetCoordinate;
        }

        var travel = Math.min(remaining, distance);
        pos.x += direction.x * travel;
        pos.y += direction.y * travel;
        remaining -= travel;
        moved = moved || travel > 0;
        if (Math.abs(travel - distance) < EPS) {
          wrapPosition();
          if (pos.x >= 0 && pos.x < W) processCenter();
        }
      }
      return moved;
    }

    /* canvas ---------------------------------------------------------- */
    var ts = 8, ox = 0, oy = 0, ro = null, raf = null;
    var last = performance.now(), dirty = true;
    var TARGET_COLORS = [
      "#ff7f6e","#73d2ff","#ffd166","#c79bff","#74e6ad",
      "#ff9bd2","#8ee3ef","#f2b56b","#9be36f"
    ];
    function size() {
      var r = wrap.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.max(1, Math.floor(r.width * dpr));
      canvas.height = Math.max(1, Math.floor(r.height * dpr));
      ts = Math.max(6, Math.floor(Math.min(canvas.width / W, canvas.height / H)));
      ox = Math.floor((canvas.width - ts * W) / 2);
      oy = Math.floor((canvas.height - ts * H) / 2);
      dirty = true;
    }
    function drawTarget(g, target, t) {
      var cx = ox + (target.x + 0.5) * ts, cy = oy + (target.y + 0.53) * ts;
      var r = Math.max(3, ts * 0.29), color = TARGET_COLORS[(target.n - 1) % TARGET_COLORS.length];
      var glow = reduce ? 0.12 : 0.1 + Math.abs(Math.sin(t / 700 + target.n)) * 0.12;
      g.fillStyle = "rgba(155,227,111," + glow.toFixed(2) + ")";
      g.beginPath(); g.arc(cx, cy, r * 1.45, 0, Math.PI * 2); g.fill();

      // Receiver antenna and soft robot body.
      g.strokeStyle = color; g.lineWidth = Math.max(1, ts * 0.07);
      g.beginPath(); g.moveTo(cx, cy - r * 0.9); g.lineTo(cx, cy - r * 1.35); g.stroke();
      g.fillStyle = "#e9f2e4";
      g.beginPath(); g.arc(cx, cy - r * 1.45, Math.max(1, r * 0.16), 0, Math.PI * 2); g.fill();
      g.fillStyle = color;
      g.beginPath(); g.arc(cx, cy - r * 0.25, r, Math.PI, 0); g.fill();
      g.fillRect(cx - r, cy - r * 0.25, r * 2, r * 1.02);
      g.beginPath();
      g.arc(cx - r * 0.55, cy + r * 0.72, r * 0.45, 0, Math.PI);
      g.arc(cx + r * 0.55, cy + r * 0.72, r * 0.45, 0, Math.PI);
      g.fill();

      g.fillStyle = "#f5fbf1";
      g.beginPath();
      g.arc(cx - r * 0.34, cy - r * 0.18, Math.max(1, r * 0.19), 0, Math.PI * 2);
      g.arc(cx + r * 0.34, cy - r * 0.18, Math.max(1, r * 0.19), 0, Math.PI * 2);
      g.fill();
      g.fillStyle = "#07100c";
      g.beginPath();
      g.arc(cx - r * 0.3, cy - r * 0.16, Math.max(1, r * 0.08), 0, Math.PI * 2);
      g.arc(cx + r * 0.3, cy - r * 0.16, Math.max(1, r * 0.08), 0, Math.PI * 2);
      g.fill();

      if (ts >= 12) {
        g.fillStyle = "#07100c";
        g.font = "700 " + Math.max(6, Math.floor(ts * 0.2)) + "px ui-monospace,monospace";
        g.textAlign = "center"; g.textBaseline = "middle";
        g.fillText(String(target.n).padStart(2, "0"), cx, cy + r * 0.38);
      }
    }
    function drawPlayerAt(g, tileX, tileY, t) {
      var cx = ox + (tileX + 0.5) * ts, cy = oy + (tileY + 0.5) * ts;
      var r = Math.max(3, ts * 0.34);
      var angle = facing === DIRS.right ? 0 :
        facing === DIRS.down ? Math.PI / 2 :
        facing === DIRS.left ? Math.PI : -Math.PI / 2;
      var activeMove = !paused && index.style.display !== "block" && direction !== STOP;
      var mouth = reduce || !activeMove ? 0.18 : 0.12 + Math.abs(Math.sin(t / 85)) * 0.34;

      g.fillStyle = "#05070a";
      g.beginPath(); g.arc(cx, cy, r * 1.18, 0, Math.PI * 2); g.fill();
      g.fillStyle = "#eaf66f";
      g.beginPath();
      g.moveTo(cx, cy);
      g.arc(cx, cy, r, angle + mouth, angle + Math.PI * 2 - mouth);
      g.closePath(); g.fill();

      var eyeAngle = angle - Math.PI / 2;
      g.fillStyle = "#07100c";
      g.beginPath();
      g.arc(
        cx + Math.cos(eyeAngle) * r * 0.42 + Math.cos(angle) * r * 0.12,
        cy + Math.sin(eyeAngle) * r * 0.42 + Math.sin(angle) * r * 0.12,
        Math.max(1, r * 0.11), 0, Math.PI * 2
      );
      g.fill();
    }
    function draw(t) {
      var g = canvas.getContext("2d");
      if (!g) return;
      g.fillStyle = "#05070a"; g.fillRect(0, 0, canvas.width, canvas.height);
      g.fillStyle = "#07100d"; g.fillRect(ox, oy, W * ts, H * ts);
      var u = Math.max(1, Math.floor(ts / 9));

      for (var gy = 0; gy < H; gy++) for (var gx = 0; gx < W; gx++) {
        var px = ox + gx * ts, py = oy + gy * ts, tile = grid[gy][gx], k = keyFor(gx, gy);
        if (solidCell(gx, gy)) {
          var wallColor = tile === "~" ? "#12394a" : tile === "T" ? "#184a32" : "#182a25";
          var wallEdge = tile === "~" ? "#1d6275" : tile === "T" ? "#28704a" : "#2b5948";
          g.fillStyle = wallColor;
          g.fillRect(px + u, py + u, ts - u * 2, ts - u * 2);
          g.fillStyle = wallEdge;
          g.fillRect(px + u, py + u, ts - u * 2, u);
          g.fillRect(px + u, py + u, u, ts - u * 2);
          if (tile === "T") {
            g.fillStyle = "#9be36f";
            g.fillRect(px + ts / 2 - u / 2, py + ts / 2 - u / 2, u, u);
          }
        } else if (pips[k]) {
          g.fillStyle = "#5c846f";
          g.beginPath(); g.arc(px + ts / 2, py + ts / 2, Math.max(1, ts * 0.06), 0, Math.PI * 2); g.fill();
        } else if (powerSignals[k]) {
          g.strokeStyle = "#9be36f"; g.lineWidth = Math.max(1, u);
          g.beginPath(); g.arc(px + ts / 2, py + ts / 2, Math.max(2, ts * 0.17), 0, Math.PI * 2); g.stroke();
          g.fillStyle = "#e9f2e4";
          g.beginPath(); g.arc(px + ts / 2, py + ts / 2, Math.max(1, ts * 0.07), 0, Math.PI * 2); g.fill();
        } else if (bonusAvailable && k === bonusKey) {
          g.fillStyle = "#ffd166";
          g.save();
          g.translate(px + ts / 2, py + ts / 2);
          g.rotate(Math.PI / 4);
          g.fillRect(-ts * 0.12, -ts * 0.12, ts * 0.24, ts * 0.24);
          g.restore();
        }
      }

      // Tunnel chevrons make the wrap mechanic visible without extra copy.
      g.fillStyle = "#365f4e";
      g.font = "700 " + Math.max(7, Math.floor(ts * 0.36)) + "px ui-monospace,monospace";
      g.textBaseline = "middle";
      g.textAlign = "left"; g.fillText("‹", ox + u, oy + (TUNNEL_ROW + 0.5) * ts);
      g.textAlign = "right"; g.fillText("›", ox + W * ts - u, oy + (TUNNEL_ROW + 0.5) * ts);

      targets.forEach(function (target) { drawTarget(g, target, t); });
      drawPlayerAt(g, pos.x, pos.y, t);
      if (pos.x < 0) drawPlayerAt(g, pos.x + W, pos.y, t);
      if (pos.x > W - 1) drawPlayerAt(g, pos.x - W, pos.y, t);
    }

    var KEY_TO_DIR = {
      arrowleft: "left", a: "left",
      arrowright: "right", d: "right",
      arrowup: "up", w: "up",
      arrowdown: "down", s: "down"
    };
    var onKd = function (e) {
      if (isShortcutTarget(e)) return;
      var k = e.key.toLowerCase();
      if (k === "i") { e.preventDefault(); toggleIndex(idxBtn); return; }
      if (e.key === "Escape") { closeAll(); return; }
      if (KEY_TO_DIR[k]) {
        e.preventDefault();
        queueDirection(KEY_TO_DIR[k]);
      }
    };
    var onBlur = function () { paused = true; dirty = true; };
    var onFocus = function () { paused = false; last = performance.now(); dirty = true; };
    // A project route can place this page in the back/forward cache while
    // `navigating` is true and the player is standing on that target cell.
    // Reloading on restore creates a fresh, playable round instead of
    // resuming the terminal navigation state.
    var onPageShow = function (e) {
      if (e.persisted) window.location.reload();
    };
    window.addEventListener("keydown", onKd);
    window.addEventListener("blur", onBlur);
    window.addEventListener("focus", onFocus);
    window.addEventListener("pageshow", onPageShow);

    function frame(now) {
      var moved = false;
      if (!document.hidden) moved = advance((now - last) / 1000);
      if (!reduce || moved || dirty) {
        draw(now);
        dirty = false;
      }
      last = now;
      raf = requestAnimationFrame(frame);
    }

    size();
    if (window.ResizeObserver) {
      ro = new ResizeObserver(function () { size(); draw(performance.now()); });
      ro.observe(wrap);
    }
    draw(0);
    raf = requestAnimationFrame(frame);

    return {
      destroy: function () {
        if (openDialog) closeAll();
        if (raf != null) cancelAnimationFrame(raf);
        window.removeEventListener("keydown", onKd);
        window.removeEventListener("blur", onBlur);
        window.removeEventListener("focus", onFocus);
        window.removeEventListener("pageshow", onPageShow);
        if (ro) ro.disconnect();
        host.innerHTML = ""; host.className = "xp";
        host.removeAttribute("style");
      }
    };
  }

  /* ------------------------------------------------------------------ *
   * CABINET — lacquer room, pointer-tracked spotlight, vitrine objects.
   * ------------------------------------------------------------------ */
  function cabinet() {
    host.innerHTML = "";
    host.className = "xp xp-cab";
    host.style.background = "#060605";
    host.style.color = "#ece5d8";
    host.style.fontFamily = 'Georgia,"Palatino Linotype",Palatino,serif';
    host.style.gridTemplateRows = "auto auto 1fr auto";

    var spot = el("div", "position:absolute;top:0;left:0;width:900px;height:900px;margin:-450px 0 0 -450px;pointer-events:none;z-index:1;background:radial-gradient(circle,rgba(255,240,214,.085),rgba(255,240,214,.035) 34%,transparent 68%);will-change:transform");
    spot.setAttribute("aria-hidden", "true");

    var nav = el("nav", "position:relative;z-index:4;display:flex;align-items:center;gap:clamp(12px,2.6vw,32px);padding:16px clamp(14px,3vw,38px);font:400 10.5px/1 ui-monospace,monospace;letter-spacing:.2em;text-transform:uppercase;border-bottom:1px solid #17150f");
    var n1 = el("a", "color:#8a8377;text-decoration:none", "Catalog"); n1.href = "#";
    var n2 = el("a", "color:#8a8377;text-decoration:none", "Apps"); n2.href = "apps/";
    var n3 = el("a", "color:#8a8377;text-decoration:none", "Journal"); n3.href = "journal/";
    nav.append(n1, n2, n3, el("span", "margin-left:auto;color:#8f8a80;letter-spacing:.14em", products.length + " holdings · open by appointment"));

    var header = el("header", "position:relative;z-index:4;text-align:center;padding:clamp(20px,5vh,46px) 20px clamp(10px,2vh,20px)");
    header.append(
      el("h1", "margin:0;font:400 clamp(30px,6.6vw,88px)/1 Georgia,serif;letter-spacing:.09em;text-transform:uppercase;color:#f3ecdf", "Useful Signals"),
      el("p", "margin:14px 0 0;font:400 10.5px/1 ui-monospace,monospace;letter-spacing:.28em;text-transform:uppercase;color:#8f8778", "Cabinet of strange objects · est. whenever")
    );

    var main = el("main", "position:relative;z-index:4;min-height:0;overflow:auto;display:flex;flex-direction:column;justify-content:center;gap:clamp(18px,4vh,44px);padding:clamp(20px,4vh,44px) clamp(14px,3vw,38px)");
    main.className = "xp-cab-main";
    var shelf = el("div", "display:flex;gap:clamp(10px,1.6vw,20px);overflow-x:auto;padding-bottom:14px;scroll-snap-type:x mandatory");
    shelf.className = "xp-cab-shelf";
    shelf.setAttribute("role", "group");
    shelf.setAttribute("aria-label", "Product holdings");
    var detail = el("div", "min-height:150px;border-top:1px solid #2b2620;padding-top:22px;display:grid;gap:10px;max-width:820px");
    detail.className = "xp-cab-detail";
    detail.setAttribute("aria-live", "polite");
    var dLabel = el("div", "font:400 10px/1 ui-monospace,monospace;letter-spacing:.3em;text-transform:uppercase;color:#c9a86a");
    var dName = el("h2", "margin:0;font:400 clamp(26px,3.4vw,44px)/1.05 Georgia,serif;letter-spacing:-.01em;color:#f3ecdf");
    var dBody = el("p", "margin:0;max-width:62ch;color:#8f8a80;font-size:17px;line-height:1.8");
    var dLink = el("a", "justify-self:start;margin-top:6px;border-bottom:1px solid #c9a86a;color:#c9a86a;text-decoration:none;font:400 10px/1.6 ui-monospace,monospace;letter-spacing:.24em;text-transform:uppercase", "Open record");
    detail.append(dLabel, dName, dBody, dLink);

    var cards = [];
    products.forEach(function (pr, i) {
      var c = el("button", "flex:0 0 auto;width:clamp(150px,17vw,210px);min-height:230px;scroll-snap-align:start;display:flex;flex-direction:column;justify-content:flex-end;gap:8px;padding:20px 18px;background:#121110;border:1px solid #2b2620;border-radius:3px;color:inherit;font:inherit;text-align:left;cursor:pointer;transition:border-color .3s,box-shadow .3s,transform .3s");
      c.setAttribute("aria-pressed", "false");
      c.append(
        el("span", "font:400 10px/1 ui-monospace,monospace;letter-spacing:.3em;color:#c9a86a", String(i + 1).padStart(2, "0")),
        el("span", "font:400 21px/1.15 Georgia,serif;color:#ece5d8", pr.name),
        el("span", "font:400 9px/1.5 ui-monospace,monospace;letter-spacing:.2em;text-transform:uppercase;color:#8f8a80", pr.lane)
      );
      c.onmouseenter = function () { c.style.borderColor = "#c9a86a"; c.style.transform = "translateY(-4px)"; };
      c.onmouseleave = function () { if (sel !== i) { c.style.borderColor = "#2b2620"; c.style.transform = "none"; } };
      c.onclick = function () { select(i); };
      c.onkeydown = function (e) {
        if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
        e.preventDefault();
        var nextIndex = Math.max(0, Math.min(products.length - 1, i + (e.key === "ArrowRight" ? 1 : -1)));
        select(nextIndex);
        cards[nextIndex].focus();
      };
      shelf.appendChild(c);
      cards.push(c);
    });

    var sel = -1;
    function select(i) {
      sel = i;
      cards.forEach(function (c, j) {
        c.style.borderColor = j === i ? "#c9a86a" : "#2b2620";
        c.style.boxShadow = j === i ? "0 0 0 1px rgba(201,168,106,.3),0 20px 50px rgba(0,0,0,.55)" : "none";
        c.style.transform = j === i ? "translateY(-4px)" : "none";
        c.setAttribute("aria-pressed", String(j === i));
      });
      var pr = products[i];
      dLabel.textContent = "Holding " + String(i + 1).padStart(2, "0") + " · " + pr.lane;
      dName.textContent = pr.name;
      dBody.textContent = pr.summary;
      dLink.href = pr.href;
      cards[i].scrollIntoView({ block: "nearest", inline: "center", behavior: reduce ? "auto" : "smooth" });
    }

    main.append(shelf, detail);
    var foot = el("footer", "position:relative;z-index:4;border-top:1px solid #17150f;padding:14px clamp(14px,3vw,38px);font:400 9px/1 ui-monospace,monospace;letter-spacing:.28em;text-transform:uppercase;color:#8f8a80;display:flex;gap:18px;flex-wrap:wrap");
    foot.append(el("span", null, "click an object"), el("span", null, "← → to browse"), el("span", "margin-left:auto", "priyanshchordia.com"));

    host.append(spot, nav, header, main, foot);
    select(0);
    n1.onclick = function (e) { e.preventDefault(); cards[sel].focus(); };

    var onMove = function (e) { spot.style.transform = "translate(" + e.clientX + "px," + e.clientY + "px)"; };
    var onKey = function (e) {
      if (isShortcutTarget(e)) return;
      if (e.key === "ArrowRight") { e.preventDefault(); select(Math.min(products.length - 1, sel + 1)); }
      if (e.key === "ArrowLeft") { e.preventDefault(); select(Math.max(0, sel - 1)); }
    };
    if (!reduce && !window.matchMedia("(pointer: coarse)").matches) host.addEventListener("pointermove", onMove);
    window.addEventListener("keydown", onKey);

    return {
      destroy: function () {
        host.removeEventListener("pointermove", onMove);
        window.removeEventListener("keydown", onKey);
        host.innerHTML = ""; host.className = "xp"; host.removeAttribute("style");
      }
    };
  }

  /* ------------------------------------------------------------------ *
   * PARALLEL UNIVERSES — a station; every product is its own reality.
   * ------------------------------------------------------------------ */
  function parallel() {
    // Each universe gets its own type, palette and layout — deliberately
    // sharing no design system with its neighbours.
    var UNIVERSES = [
      { bg:"#f4f1ea", fg:"#141414", acc:"#c0392b", font:'Georgia,"Palatino Linotype",serif', align:"center", scale:1.0, caps:false },
      { bg:"#04121a", fg:"#d7f5ff", acc:"#3fd0ff", font:'ui-monospace,Menlo,monospace', align:"left", scale:.82, caps:true },
      { bg:"#fff8e6", fg:"#2b1d05", acc:"#a84d00", font:'Impact,"Arial Black",sans-serif', align:"left", scale:1.25, caps:true },
      { bg:"#120018", fg:"#f6e6ff", acc:"#c06bff", font:'"Palatino Linotype",Palatino,serif', align:"center", scale:1.1, caps:false },
      { bg:"#0d0d0d", fg:"#f2f2f2", acc:"#d8ff58", font:'system-ui,"Helvetica Neue",sans-serif', align:"left", scale:1.0, caps:false },
      { bg:"#e8eef0", fg:"#0d2430", acc:"#046a6a", font:'"Courier New",Courier,monospace', align:"center", scale:.9, caps:true },
      { bg:"#1b0a0a", fg:"#ffe9e0", acc:"#ff5a3c", font:'Impact,"Arial Black",sans-serif', align:"center", scale:1.3, caps:true }
    ];
    function uni(i) { return UNIVERSES[i % UNIVERSES.length]; }

    var current = -1;
    host.innerHTML = "";
    host.className = "xp xp-par";
    host.style.gridTemplateRows = "1fr";
    host.style.background = "#040404";

    var stage = el("div", "position:relative;overflow:hidden");
    host.appendChild(stage);

    function renderHub(focusIndex) {
      current = -1;
      stage.innerHTML = "";
      var hub = el("div", "position:absolute;inset:0;background:#040404;color:#eceae6;font-family:system-ui,'Helvetica Neue',Arial,sans-serif;display:grid;grid-template-rows:auto 1fr;overflow:auto");
      var nav = el("nav", "display:flex;align-items:center;gap:clamp(12px,2.6vw,32px);padding:16px clamp(14px,3vw,38px);font:400 10.5px/1 ui-monospace,monospace;letter-spacing:.2em;text-transform:uppercase;border-bottom:1px solid #171717");
      var apps = el("a", "color:#8b8880;text-decoration:none", "Apps"); apps.href = "apps/";
      var j = el("a", "color:#8b8880;text-decoration:none", "Journal"); j.href = "journal/";
      nav.append(apps, j, el("span", "margin-left:auto;color:#8f8c85;letter-spacing:.14em", "transit hub · " + products.length + " realities · all reachable"));

      var body = el("main", "display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:clamp(22px,4vw,64px);align-content:center;padding:clamp(22px,5vh,60px) clamp(16px,4vw,44px)");
      body.className = "xp-par-hub-main";
      body.id = "xp-main";
      body.tabIndex = -1;
      var left = el("div");
      left.append(
        el("h1", "margin:0;font:700 clamp(38px,7vw,104px)/.9 system-ui,sans-serif;letter-spacing:-.05em;color:#f4f2ee", "Useful signals"),
        el("p", "margin:20px 0 0;max-width:40ch;font:400 15px/1.65 system-ui,sans-serif;color:#9a968f", "This page is only the station. Nothing here shares a design system with anything behind it — each product is its own universe, with its own type, colour and physics. You will always be able to get back."),
        el("p", "margin:16px 0 0;font:400 10.5px/1.7 ui-monospace,monospace;letter-spacing:.14em;text-transform:uppercase;color:#8f8c85", "keys 1–9 transit · esc returns")
      );
      var right = el("div", "display:grid;gap:2px");
      var rows = [];
      products.forEach(function (pr, i) {
        var u = uni(i);
        var row = el("button", "display:grid;grid-template-columns:34px 1fr auto;gap:14px;align-items:center;padding:14px 16px;background:#0b0b0b;border:0;border-left:3px solid " + u.acc + ";color:#eceae6;font:inherit;text-align:left;cursor:pointer");
        row.append(
          el("span", "font:400 10px/1 ui-monospace,monospace;color:" + u.acc, i < 9 ? String(i + 1) : "·"),
          el("span", "font:600 15px/1.2 system-ui,sans-serif", pr.name),
          el("span", "font:400 9px/1 ui-monospace,monospace;letter-spacing:.18em;text-transform:uppercase;color:#8f8c85", pr.lane)
        );
        row.onmouseenter = function () { row.style.background = "#141414"; };
        row.onmouseleave = function () { row.style.background = "#0b0b0b"; };
        row.onclick = function () { enter(i); };
        right.appendChild(row);
        rows.push(row);
      });
      body.append(left, right);
      hub.append(nav, body);
      stage.appendChild(hub);
      if (typeof focusIndex === "number" && rows[focusIndex]) rows[focusIndex].focus();
    }

    function enter(i) {
      current = i;
      var pr = products[i], u = uni(i);
      stage.innerHTML = "";
      var v = el("main", "position:absolute;inset:0;overflow:auto;background:" + u.bg + ";color:" + u.fg +
        ";font-family:" + u.font + ";display:grid;align-content:center;justify-items:" +
        (u.align === "center" ? "center" : "start") + ";text-align:" + u.align +
        ";gap:22px;padding:clamp(28px,7vh,80px) clamp(20px,6vw,90px)");
      if (!reduce) v.style.animation = "uni-in .34s ease";
      v.id = "xp-main";
      v.tabIndex = -1;
      var kicker = el("div", "font:400 10px/1 ui-monospace,monospace;letter-spacing:.3em;text-transform:uppercase;color:" + u.acc,
        "reality " + String(i + 1).padStart(2, "0") + " · " + pr.lane);
      var h = el("h1", "margin:0;max-width:18ch;font-size:clamp(" + (34 * u.scale).toFixed(0) + "px," + (7 * u.scale).toFixed(1) + "vw," + (108 * u.scale).toFixed(0) + "px);line-height:.94;letter-spacing:-.03em" + (u.caps ? ";text-transform:uppercase" : ""), pr.name);
      var body = el("p", "margin:0;max-width:56ch;font-size:18px;line-height:1.7;opacity:.82", pr.summary);
      var actions = el("div", "display:flex;gap:10px;flex-wrap:wrap;margin-top:8px");
      var go = el("a", "border:2px solid " + u.acc + ";color:" + u.acc + ";padding:11px 16px;text-decoration:none;font:400 10px/1 ui-monospace,monospace;letter-spacing:.2em;text-transform:uppercase", "Open record");
      go.href = pr.href;
      var back = el("button", "appearance:none;border:2px solid currentColor;background:transparent;color:inherit;padding:11px 16px;font:400 10px/1 ui-monospace,monospace;letter-spacing:.2em;text-transform:uppercase;cursor:pointer;opacity:.7", "← Station (Esc)");
      back.onclick = function () { renderHub(i); };
      actions.append(go, back);
      v.append(kicker, h, body, actions);
      stage.appendChild(v);
      h.tabIndex = -1;
      h.focus();
    }

    var onKey = function (e) {
      if (isShortcutTarget(e) && e.key !== "Escape") return;
      if (e.key === "Escape") { if (current >= 0) renderHub(current); return; }
      if (/^[1-9]$/.test(e.key)) {
        var i = parseInt(e.key, 10) - 1;
        if (i < products.length) { e.preventDefault(); enter(i); }
      }
    };
    window.addEventListener("keydown", onKey);
    renderHub();

    return {
      destroy: function () {
        window.removeEventListener("keydown", onKey);
        host.innerHTML = ""; host.className = "xp"; host.removeAttribute("style");
      }
    };
  }

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
