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
