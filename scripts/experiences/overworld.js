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
