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
