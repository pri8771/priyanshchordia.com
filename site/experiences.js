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
    ["Catalog", "Journal"].forEach(function (t, i) {
      var a = el("a", "color:#8a8377;text-decoration:none", t);
      a.href = i ? "journal/" : "#xp";
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
    var arcInner = el("div", "max-width:1000px;margin:auto");
    arcInner.appendChild(el("div", "font:400 10px/1 ui-monospace,monospace;letter-spacing:.3em;text-transform:uppercase;color:#ffb347;margin-bottom:18px", "decoded archive · " + carriers.length + " records · press escape"));
    carriers.forEach(function (c) {
      var row = el("a", "display:grid;grid-template-columns:70px 200px 1fr;gap:18px;padding:14px 0;border-bottom:1px solid #201a15;text-decoration:none;align-items:baseline");
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

    function toggleArchive(on) {
      archive.style.display = on ? "block" : "none";
    }
    arcBtn.onclick = function (e) { e.preventDefault(); toggleArchive(archive.style.display !== "block"); };

    /* nearest carrier + lock ------------------------------------------ */
    function nearest() {
      var best = carriers[0], d = 1e9;
      carriers.forEach(function (c) {
        var dd = Math.abs(c.f - freq);
        if (dd < d) { d = dd; best = c; }
      });
      return { c: best, d: d };
    }

    var shownCode = null;
    function render() {
      var n = nearest(), locked = n.d < 2.2;
      freqLabel.textContent = n.c.band;
      lock.style.color = locked ? "#ffb347" : "#6b6257";
      status.textContent = locked ? "carrier locked" : (n.d < 7 ? "signal near" : "searching");
      band.setAttribute("aria-valuenow", String(Math.round(freq)));
      band.setAttribute("aria-valuetext", locked ? "Locked: " + n.c.name : "Searching");
      needle.style.transform = "translateX(" + (freq / 100) * band.clientWidth + "px)";

      if (locked && n.c.code !== shownCode) {
        shownCode = n.c.code;
        cCode.textContent = n.c.code;
        cName.textContent = n.c.name;
        cDom.textContent = n.c.domain;
        openRec.href = n.c.href;
        typeOut(n.c.body);
      } else if (!locked && shownCode) {
        shownCode = null;
        clearInterval(typeTimer);
        cCode.textContent = ""; cName.textContent = ""; cDom.textContent = "";
        para.textContent = "";
        para.appendChild(caret);
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

    function tune(v) { freq = Math.max(0, Math.min(100, v)); render(); }

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
    band.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") { e.preventDefault(); tune(freq - 1.5); }
      if (e.key === "ArrowRight") { e.preventDefault(); tune(freq + 1.5); }
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
      if (e.metaKey || e.ctrlKey || /^(INPUT|SELECT|TEXTAREA)$/.test(e.target.tagName)) return;
      if (e.key.toLowerCase() === "a") toggleArchive(archive.style.display !== "block");
      if (e.key === "Escape") toggleArchive(false);
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
    if (window.ResizeObserver) { ro = new ResizeObserver(sizeSpec); ro.observe(canvas); }
    specTimer = setInterval(drawSpec, 1000 / (reduce ? 4 : 24));
    render();

    return {
      destroy: function () {
        clearInterval(typeTimer); clearInterval(nameTimer); clearInterval(specTimer);
        window.removeEventListener("keydown", onKey);
        if (ro) ro.disconnect();
        host.innerHTML = "";
        host.className = "xp";
      }
    };
  }


  /* ------------------------------------------------------------------ *
   * OVERWORLD — walkable pixel map; every product is a portal tile.
   * ------------------------------------------------------------------ */
  function overworld() {
    var W = 32, H = 20;

    // Base terrain, transcribed from the original map.
    var grid = [];
    for (var y = 0; y < H; y++) grid.push(new Array(W).fill("."));
    for (var x = 0; x < W; x++) { grid[0][x] = "#"; grid[H - 1][x] = "#"; }
    for (var y2 = 0; y2 < H; y2++) { grid[y2][0] = "#"; grid[y2][W - 1] = "#"; }
    for (var wy = 2; wy <= 5; wy++) for (var wx = 2; wx <= 7; wx++) grid[wy][wx] = "~";
    [[11,6],[12,6],[13,6],[11,7],[24,15],[25,15],[26,15],[28,15],[29,15],[24,16],[24,17],[24,18],[29,16],[29,17],[29,18],[25,18],[26,18],[27,18],[28,18]]
      .forEach(function (c) { grid[c[1]][c[0]] = "#"; });
    [[9,2],[15,6],[19,6],[27,14],[25,14],[6,12],[8,18],[30,7],[12,18],[17,11],[21,2],[5,6],[30,13],[2,9]]
      .forEach(function (c) { grid[c[1]][c[0]] = "T"; });
    grid[16][27] = "s";
    var SHARDS = [[7,4],[26,17],[3,15],[20,17],[29,3]];
    SHARDS.forEach(function (c) { grid[c[1]][c[0]] = "c"; });

    // Scatter one portal per product over free ground, deterministically.
    var portals = [], slots = [];
    for (var sy = 2; sy < H - 2; sy++)
      for (var sx = 2; sx < W - 2; sx++)
        if (grid[sy][sx] === "." && Math.abs(sx - 16) + Math.abs(sy - 10) > 3) slots.push([sx, sy]);
    var stride = Math.max(1, Math.floor(slots.length / products.length));
    products.forEach(function (pr, i) {
      var s = slots[(i * stride + (i * 7) % stride) % slots.length];
      if (!s || grid[s[1]][s[0]] !== ".") {
        s = slots.find(function (q) { return grid[q[1]][q[0]] === "."; });
      }
      if (!s) return;
      grid[s[1]][s[0]] = "P";
      portals.push({ x: s[0], y: s[1], p: pr, n: i + 1 });
    });
    function portalAt(x, y) {
      for (var i = 0; i < portals.length; i++) if (portals[i].x === x && portals[i].y === y) return portals[i];
      return null;
    }

    host.innerHTML = "";
    host.className = "xp xp-ow";
    host.style.background = "#05070a";
    host.style.color = "#e9f2e4";
    host.style.fontFamily = "system-ui,'Helvetica Neue',Arial,sans-serif";
    host.style.gridTemplateRows = "auto auto 1fr auto";

    var nav = el("nav", "display:flex;align-items:center;gap:clamp(12px,2.4vw,30px);padding:14px clamp(14px,3vw,30px) 12px;font:400 10.5px/1 ui-monospace,monospace;letter-spacing:.18em;text-transform:uppercase;border-bottom:1px solid #12191f");
    var a1 = el("a", "color:#8fa094;text-decoration:none", "Catalog"); a1.href = "#";
    var a2 = el("a", "color:#8fa094;text-decoration:none", "Journal"); a2.href = "journal/";
    nav.append(a1, a2, el("span", "margin-left:auto;color:#8d9a91;letter-spacing:.12em", "overworld · " + products.length + " portals"));

    var header = el("header", "display:flex;align-items:baseline;justify-content:center;padding:clamp(14px,3vh,26px) 16px clamp(10px,2vh,18px)");
    header.appendChild(el("h1", "margin:0;font:700 clamp(15px,3.2vw,34px)/1.25 ui-monospace,monospace;letter-spacing:.06em;color:#f2f7ee;text-shadow:0 4px 0 #1d2a1e,0 0 26px rgba(155,227,111,.16);text-align:center", "USEFUL SIGNALS"));

    var wrap = el("div", "position:relative;min-height:0;overflow:hidden");
    var canvas = el("canvas", "display:block;width:100%;height:100%;image-rendering:pixelated;touch-action:none");
    canvas.setAttribute("role", "img");
    canvas.setAttribute("aria-label", "Pixel overworld map with " + products.length + " project portals. Every project is also listed in the index panel.");
    var hud = el("div", "position:absolute;top:10px;left:12px;display:flex;flex-direction:column;gap:6px;font:700 10px/1.6 ui-monospace,monospace;color:#9fada3;pointer-events:none;text-shadow:0 2px 0 #05070a");
    var shardLabel = el("span", null, "SHARDS 0/" + SHARDS.length);
    var secretLabel = el("span", null, "");
    hud.append(shardLabel, secretLabel);
    var idxBtn = el("button", "position:absolute;top:10px;right:12px;appearance:none;border:2px solid #24312a;background:#0a1010;color:#cfe0c8;padding:8px 12px;font:700 10px/1 ui-monospace,monospace;letter-spacing:.16em;text-transform:uppercase;cursor:pointer", "Index (I)");
    wrap.append(canvas, hud, idxBtn);

    var foot = el("footer", "border-top:1px solid #12191f;padding:10px clamp(14px,3vw,30px) 14px;font:400 10px/1 ui-monospace,monospace;letter-spacing:.16em;text-transform:uppercase;color:#8d9a91;display:flex;gap:16px;flex-wrap:wrap");
    foot.append(el("span", null, "WASD / arrows to walk"), el("span", null, "walk onto a portal to open it"), el("span", "margin-left:auto", "I index · Esc close"));

    host.append(nav, header, wrap, foot);

    /* modal + index -------------------------------------------------- */
    var modal = el("div", "position:absolute;inset:0;z-index:9;display:none;align-items:center;justify-content:center;background:rgba(5,7,10,.82);padding:24px");
    var card = el("div", "width:min(560px,100%);border:2px solid #24312a;background:#0a1010;padding:26px");
    modal.appendChild(card);
    var index = el("div", "position:absolute;inset:0;z-index:10;display:none;overflow:auto;background:rgba(5,7,10,.96);padding:clamp(18px,5vh,54px) clamp(16px,5vw,54px)");
    wrap.append(modal, index);

    var open = null;
    function closeAll() { open = null; modal.style.display = "none"; index.style.display = "none"; }
    function openPortal(pt) {
      open = pt;
      card.innerHTML = "";
      card.append(
        el("div", "font:700 10px/1 ui-monospace,monospace;letter-spacing:.2em;text-transform:uppercase;color:#9be36f;margin-bottom:12px",
           "P" + String(pt.n).padStart(3, "0") + " · " + pt.p.lane),
        el("h2", "margin:0 0 12px;font:700 28px/1.05 system-ui,sans-serif;letter-spacing:-.03em;color:#e9f2e4", pt.p.name),
        el("p", "margin:0 0 20px;color:#8fa094;font-size:14px;line-height:1.65", pt.p.summary)
      );
      var go = el("a", "display:inline-block;border:2px solid #24312a;padding:10px 14px;font:700 10px/1 ui-monospace,monospace;letter-spacing:.16em;text-transform:uppercase;color:#9be36f;text-decoration:none", "Open record");
      go.href = pt.p.href;
      var close = el("button", "appearance:none;margin-left:8px;border:2px solid #24312a;background:transparent;color:#8fa094;padding:10px 14px;font:700 10px/1 ui-monospace,monospace;letter-spacing:.16em;text-transform:uppercase;cursor:pointer", "Close (Esc)");
      close.onclick = closeAll;
      card.append(go, close);
      modal.style.display = "flex";
    }
    function buildIndex() {
      index.innerHTML = "";
      var inner = el("div", "max-width:980px;margin:auto");
      inner.appendChild(el("div", "font:700 10px/1 ui-monospace,monospace;letter-spacing:.24em;text-transform:uppercase;color:#9be36f;margin-bottom:18px", "index · " + products.length + " records · press I or Esc"));
      portals.forEach(function (pt) {
        var row = el("a", "display:grid;grid-template-columns:64px 190px 1fr;gap:18px;padding:13px 0;border-bottom:1px solid #12191f;text-decoration:none;align-items:baseline");
        row.href = pt.p.href;
        row.append(
          el("span", "font:700 10px/1 ui-monospace,monospace;color:#9be36f;letter-spacing:.14em", "P" + String(pt.n).padStart(3, "0")),
          el("span", "font:700 15px/1.2 system-ui,sans-serif;color:#e9f2e4", pt.p.name),
          el("span", "font:400 13px/1.55 system-ui,sans-serif;color:#8fa094", pt.p.summary)
        );
        inner.appendChild(row);
      });
      index.appendChild(inner);
    }
    buildIndex();
    idxBtn.onclick = function () {
      var on = index.style.display !== "block";
      closeAll(); index.style.display = on ? "block" : "none";
    };

    /* loop ------------------------------------------------------------ */
    var keys = {}, pos = { x: 16.5, y: 10.5 }, taken = {}, cool = null, shards = 0, secret = false;
    var ts = 8, ox = 0, oy = 0, ro = null, timer = null, last = performance.now();

    function solid(x, y) {
      var gx = Math.floor(x), gy = Math.floor(y);
      if (gx < 0 || gy < 0 || gx >= W || gy >= H) return true;
      var v = grid[gy][gx];
      return v === "#" || v === "~" || v === "T";
    }
    function size() {
      var r = wrap.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.max(1, Math.floor(r.width * dpr));
      canvas.height = Math.max(1, Math.floor(r.height * dpr));
      ts = Math.max(6, Math.floor(Math.min(canvas.width / W, canvas.height / H)));
      ox = Math.floor((canvas.width - ts * W) / 2);
      oy = Math.floor((canvas.height - ts * H) / 2);
    }
    function step(dt) {
      if (open || index.style.display === "block") return;
      dt = Math.min(dt, 0.05);
      var sp = 5.4 * dt, dx = 0, dy = 0;
      if (keys.arrowleft || keys.a) dx -= 1;
      if (keys.arrowright || keys.d) dx += 1;
      if (keys.arrowup || keys.w) dy -= 1;
      if (keys.arrowdown || keys.s) dy += 1;
      if (dx && dy) { dx *= 0.707; dy *= 0.707; }
      var r = 0.32;
      if (dx) {
        var nx = pos.x + dx * sp;
        if (!solid(nx + Math.sign(dx) * r, pos.y - r) && !solid(nx + Math.sign(dx) * r, pos.y + r)) pos.x = nx;
      }
      if (dy) {
        var ny = pos.y + dy * sp;
        if (!solid(pos.x - r, ny + Math.sign(dy) * r) && !solid(pos.x + r, ny + Math.sign(dy) * r)) pos.y = ny;
      }
      var gx = Math.floor(pos.x), gy = Math.floor(pos.y), v = grid[gy] && grid[gy][gx], here = gx + "," + gy;
      if (v === "c" && !taken[here]) {
        taken[here] = true; grid[gy][gx] = "."; shards++;
        shardLabel.textContent = "SHARDS " + shards + "/" + SHARDS.length;
      }
      if (cool && cool !== here) cool = null;
      if (!cool && v && v !== "." && v !== "c") {
        if (v === "P") { cool = here; openPortal(portalAt(gx, gy)); }
        else if (v === "s") {
          cool = here; secret = true;
          secretLabel.textContent = "SECRET FOUND";
          card.innerHTML = "";
          card.append(
            el("div", "font:700 10px/1 ui-monospace,monospace;letter-spacing:.2em;text-transform:uppercase;color:#9be36f;margin-bottom:12px", "unlisted"),
            el("h2", "margin:0 0 12px;font:700 28px/1.05 system-ui,sans-serif;color:#e9f2e4", "The room"),
            el("p", "margin:0 0 20px;color:#8fa094;font-size:14px;line-height:1.65", "You walked through a wall that looked solid. Whatever is being built here does not have a name yet.")
          );
          var cb = el("button", "appearance:none;border:2px solid #24312a;background:transparent;color:#8fa094;padding:10px 14px;font:700 10px/1 ui-monospace,monospace;letter-spacing:.16em;text-transform:uppercase;cursor:pointer", "Close (Esc)");
          cb.onclick = closeAll; card.appendChild(cb);
          modal.style.display = "flex";
        }
      }
    }
    function draw(t) {
      var g = canvas.getContext("2d");
      if (!g) return;
      g.fillStyle = "#05070a"; g.fillRect(0, 0, canvas.width, canvas.height);
      var u = Math.max(1, Math.floor(ts / 8));
      for (var y = 0; y < H; y++) for (var x = 0; x < W; x++) {
        var px = ox + x * ts, py = oy + y * ts, tile = grid[y][x];
        g.fillStyle = ((x * 7 + y * 13) % 5 === 0) ? "#0c1116" : "#0a0e12";
        g.fillRect(px, py, ts, ts);
        if (tile === "#") {
          g.fillStyle = "#1a2229"; g.fillRect(px, py, ts, ts);
          g.fillStyle = "#26313a"; g.fillRect(px, py, ts, u);
          g.fillStyle = "#0e1418"; g.fillRect(px, py + ts - u, ts, u);
        } else if (tile === "~") {
          g.fillStyle = "#0d2230"; g.fillRect(px, py, ts, ts);
          g.fillStyle = "#14384a";
          var ph = reduce ? 0 : Math.sin(t / 420 + x * 0.7 + y * 0.5) * u;
          g.fillRect(px, py + ts / 2 + ph, ts, u);
        } else if (tile === "T") {
          g.fillStyle = "#123021"; g.fillRect(px + u, py + u, ts - u * 2, ts - u * 2);
          g.fillStyle = "#1c4a31"; g.fillRect(px + u * 2, py + u, ts - u * 4, ts - u * 3);
        } else if (tile === "c") {
          var bob = reduce ? 0 : Math.sin(t / 260 + x) * u;
          g.fillStyle = "#9be36f";
          g.fillRect(px + ts / 2 - u, py + ts / 2 - u + bob, u * 2, u * 2);
        } else if (tile === "P") {
          var pulse = reduce ? 0.6 : 0.45 + Math.abs(Math.sin(t / 520 + x)) * 0.4;
          g.fillStyle = "rgba(155,227,111," + pulse.toFixed(2) + ")";
          g.fillRect(px + u, py + u, ts - u * 2, ts - u * 2);
          g.fillStyle = "#05070a";
          g.fillRect(px + u * 2, py + u * 2, ts - u * 4, ts - u * 4);
          g.fillStyle = "#9be36f";
          g.fillRect(px + ts / 2 - u / 2, py + ts / 2 - u / 2, u, u);
        } else if (tile === "s") {
          g.fillStyle = "#0a0e12"; g.fillRect(px, py, ts, ts);
        }
      }
      // player
      var ppx = ox + pos.x * ts, ppy = oy + pos.y * ts, ps = Math.max(3, Math.floor(ts * 0.52));
      g.fillStyle = "#05070a"; g.fillRect(ppx - ps / 2 - u, ppy - ps / 2 - u, ps + u * 2, ps + u * 2);
      g.fillStyle = "#e9f2e4"; g.fillRect(ppx - ps / 2, ppy - ps / 2, ps, ps);
      g.fillStyle = "#9be36f"; g.fillRect(ppx - ps / 2, ppy - ps / 2, ps, Math.max(1, Math.floor(ps / 4)));
    }

    var onKd = function (e) {
      if (e.metaKey || e.ctrlKey || /^(INPUT|SELECT|TEXTAREA)$/.test(e.target.tagName)) return;
      var k = e.key.toLowerCase();
      if (k === "i") { e.preventDefault(); idxBtn.onclick(); return; }
      if (e.key === "Escape") { closeAll(); return; }
      if (["arrowup","arrowdown","arrowleft","arrowright","w","a","s","d"].indexOf(k) >= 0) { e.preventDefault(); keys[k] = true; }
    };
    var onKu = function (e) { keys[e.key.toLowerCase()] = false; };
    window.addEventListener("keydown", onKd);
    window.addEventListener("keyup", onKu);

    size();
    if (window.ResizeObserver) { ro = new ResizeObserver(size); ro.observe(wrap); }
    draw(0);
    timer = setInterval(function () {
      var now = performance.now();
      try { step((now - last) / 1000); last = now; draw(now); } catch (err) { clearInterval(timer); }
    }, 1000 / 40);

    return {
      destroy: function () {
        clearInterval(timer);
        window.removeEventListener("keydown", onKd);
        window.removeEventListener("keyup", onKu);
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
    var n2 = el("a", "color:#8a8377;text-decoration:none", "Journal"); n2.href = "journal/";
    nav.append(n1, n2, el("span", "margin-left:auto;color:#8f8a80;letter-spacing:.14em", products.length + " holdings · open by appointment"));

    var header = el("header", "position:relative;z-index:4;text-align:center;padding:clamp(20px,5vh,46px) 20px clamp(10px,2vh,20px)");
    header.append(
      el("h1", "margin:0;font:400 clamp(30px,6.6vw,88px)/1 Georgia,serif;letter-spacing:.09em;text-transform:uppercase;color:#f3ecdf", "Useful Signals"),
      el("p", "margin:14px 0 0;font:400 10.5px/1 ui-monospace,monospace;letter-spacing:.28em;text-transform:uppercase;color:#8f8778", "Cabinet of strange objects · est. whenever")
    );

    var main = el("main", "position:relative;z-index:4;min-height:0;overflow:auto;display:flex;flex-direction:column;justify-content:center;gap:clamp(18px,4vh,44px);padding:clamp(20px,4vh,44px) clamp(14px,3vw,38px)");
    var shelf = el("div", "display:flex;gap:clamp(10px,1.6vw,20px);overflow-x:auto;padding-bottom:14px;scroll-snap-type:x mandatory");
    var detail = el("div", "min-height:150px;border-top:1px solid #2b2620;padding-top:22px;display:grid;gap:10px;max-width:820px");
    var dLabel = el("div", "font:400 10px/1 ui-monospace,monospace;letter-spacing:.3em;text-transform:uppercase;color:#c9a86a");
    var dName = el("h2", "margin:0;font:400 clamp(26px,3.4vw,44px)/1.05 Georgia,serif;letter-spacing:-.01em;color:#f3ecdf");
    var dBody = el("p", "margin:0;max-width:62ch;color:#8f8a80;font-size:17px;line-height:1.8");
    var dLink = el("a", "justify-self:start;margin-top:6px;border-bottom:1px solid #c9a86a;color:#c9a86a;text-decoration:none;font:400 10px/1.6 ui-monospace,monospace;letter-spacing:.24em;text-transform:uppercase", "Open record");
    detail.append(dLabel, dName, dBody, dLink);

    var cards = [];
    products.forEach(function (pr, i) {
      var c = el("button", "flex:0 0 auto;width:clamp(150px,17vw,210px);min-height:230px;scroll-snap-align:start;display:flex;flex-direction:column;justify-content:flex-end;gap:8px;padding:20px 18px;background:#121110;border:1px solid #2b2620;border-radius:3px;color:inherit;font:inherit;text-align:left;cursor:pointer;transition:border-color .3s,box-shadow .3s,transform .3s");
      c.append(
        el("span", "font:400 10px/1 ui-monospace,monospace;letter-spacing:.3em;color:#c9a86a", String(i + 1).padStart(2, "0")),
        el("span", "font:400 21px/1.15 Georgia,serif;color:#ece5d8", pr.name),
        el("span", "font:400 9px/1.5 ui-monospace,monospace;letter-spacing:.2em;text-transform:uppercase;color:#8f8a80", pr.lane)
      );
      c.onmouseenter = function () { c.style.borderColor = "#c9a86a"; c.style.transform = "translateY(-4px)"; };
      c.onmouseleave = function () { if (sel !== i) { c.style.borderColor = "#2b2620"; c.style.transform = "none"; } };
      c.onclick = function () { select(i); };
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

    var onMove = function (e) { spot.style.transform = "translate(" + e.clientX + "px," + e.clientY + "px)"; };
    var onKey = function (e) {
      if (e.metaKey || e.ctrlKey || /^(INPUT|SELECT|TEXTAREA)$/.test(e.target.tagName)) return;
      if (e.key === "ArrowRight") { e.preventDefault(); select(Math.min(products.length - 1, sel + 1)); }
      if (e.key === "ArrowLeft") { e.preventDefault(); select(Math.max(0, sel - 1)); }
    };
    host.addEventListener("pointermove", onMove);
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
      { bg:"#fff8e6", fg:"#2b1d05", acc:"#e0731a", font:'Impact,"Arial Black",sans-serif', align:"left", scale:1.25, caps:true },
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

    function renderHub() {
      current = -1;
      stage.innerHTML = "";
      var hub = el("div", "position:absolute;inset:0;background:#040404;color:#eceae6;font-family:system-ui,'Helvetica Neue',Arial,sans-serif;display:grid;grid-template-rows:auto 1fr;overflow:auto");
      var nav = el("nav", "display:flex;align-items:center;gap:clamp(12px,2.6vw,32px);padding:16px clamp(14px,3vw,38px);font:400 10.5px/1 ui-monospace,monospace;letter-spacing:.2em;text-transform:uppercase;border-bottom:1px solid #171717");
      var j = el("a", "color:#8b8880;text-decoration:none", "Journal"); j.href = "journal/";
      nav.append(j, el("span", "margin-left:auto;color:#8f8c85;letter-spacing:.14em", "transit hub · " + products.length + " realities · all reachable"));

      var body = el("main", "display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:clamp(22px,4vw,64px);align-content:center;padding:clamp(22px,5vh,60px) clamp(16px,4vw,44px)");
      var left = el("div");
      left.append(
        el("h1", "margin:0;font:700 clamp(38px,7vw,104px)/.9 system-ui,sans-serif;letter-spacing:-.05em;color:#f4f2ee", "Useful signals"),
        el("p", "margin:20px 0 0;max-width:40ch;font:400 15px/1.65 system-ui,sans-serif;color:#9a968f", "This page is only the station. Nothing here shares a design system with anything behind it — each product is its own universe, with its own type, colour and physics. You will always be able to get back."),
        el("p", "margin:16px 0 0;font:400 10.5px/1.7 ui-monospace,monospace;letter-spacing:.14em;text-transform:uppercase;color:#8f8c85", "keys 1–9 transit · esc returns")
      );
      var right = el("div", "display:grid;gap:2px");
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
      });
      body.append(left, right);
      hub.append(nav, body);
      stage.appendChild(hub);
    }

    function enter(i) {
      current = i;
      var pr = products[i], u = uni(i);
      stage.innerHTML = "";
      var v = el("div", "position:absolute;inset:0;overflow:auto;background:" + u.bg + ";color:" + u.fg +
        ";font-family:" + u.font + ";display:grid;align-content:center;justify-items:" +
        (u.align === "center" ? "center" : "start") + ";text-align:" + u.align +
        ";gap:22px;padding:clamp(28px,7vh,80px) clamp(20px,6vw,90px)");
      if (!reduce) v.style.animation = "uni-in .34s ease";
      var kicker = el("div", "font:400 10px/1 ui-monospace,monospace;letter-spacing:.3em;text-transform:uppercase;color:" + u.acc,
        "reality " + String(i + 1).padStart(2, "0") + " · " + pr.lane);
      var h = el("h1", "margin:0;max-width:18ch;font-size:clamp(" + (34 * u.scale).toFixed(0) + "px," + (7 * u.scale).toFixed(1) + "vw," + (108 * u.scale).toFixed(0) + "px);line-height:.94;letter-spacing:-.03em" + (u.caps ? ";text-transform:uppercase" : ""), pr.name);
      var body = el("p", "margin:0;max-width:56ch;font-size:18px;line-height:1.7;opacity:.82", pr.summary);
      var actions = el("div", "display:flex;gap:10px;flex-wrap:wrap;margin-top:8px");
      var go = el("a", "border:2px solid " + u.acc + ";color:" + u.acc + ";padding:11px 16px;text-decoration:none;font:400 10px/1 ui-monospace,monospace;letter-spacing:.2em;text-transform:uppercase", "Open record");
      go.href = pr.href;
      var back = el("button", "appearance:none;border:2px solid currentColor;background:transparent;color:inherit;padding:11px 16px;font:400 10px/1 ui-monospace,monospace;letter-spacing:.2em;text-transform:uppercase;cursor:pointer;opacity:.7", "← Station (Esc)");
      back.onclick = renderHub;
      actions.append(go, back);
      v.append(kicker, h, body, actions);
      stage.appendChild(v);
    }

    var onKey = function (e) {
      if (e.metaKey || e.ctrlKey || /^(INPUT|SELECT|TEXTAREA)$/.test(e.target.tagName)) return;
      if (e.key === "Escape") { if (current >= 0) renderHub(); return; }
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
    if (active) { active.destroy(); active = null; }
    root.classList.toggle("has-xp", !!REGISTRY[theme]);
    if (REGISTRY[theme]) active = REGISTRY[theme]();
  }

  new MutationObserver(sync).observe(root, { attributes: true, attributeFilter: ["data-theme"] });
  sync();
})();
