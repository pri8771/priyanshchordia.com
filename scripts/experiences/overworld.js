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
