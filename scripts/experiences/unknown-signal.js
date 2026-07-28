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
