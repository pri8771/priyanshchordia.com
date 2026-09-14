(() => {
  "use strict";

  const form = document.querySelector("#fit-form");
  const panel = document.querySelector("#fit-result");
  const packet = document.querySelector("#fit-packet");
  if (!form || !panel) return;

  const EVENT_KEY = "bidetfit:fit_checker:aggregate:v1";
  const RULES = {
    bolt_spacing: { incompatible_below_in: 5.5, incompatible_above_in: 7.5 },
    rear_clearance: { manufacturer_minimum_in: 1.5, common_screen_in: 1.75 },
    french_curve: {
      manufacturer: "Bio Bidet",
      url: "https://biobidet.com/pages/compatibility",
      retrieved_at: "2026-09-14",
      guidance: "Bio Bidet seats and attachments do not fit well on deep French-curve one-piece toilets because limited space near the mounting bolts.",
    },
    source_freshness: "2026-09-14",
  };

  const LABELS = {
    toilet_type: {
      "two-piece": "Two-piece",
      "one-piece": "One-piece",
      "wall-hung": "Wall-hung",
      unsure: "Not sure",
    },
    bowl_shape: {
      round: "Round",
      elongated: "Elongated",
      unusual: "Square / unusual",
      unsure: "Not sure",
    },
    french_curve: { no: "Flat rear deck", yes: "Rises or slopes (French curve)", unsure: "Not sure" },
    skirted: {
      no: "Exposed plumbing",
      yes: "Concealed / skirted",
      unsure: "Not sure",
    },
    outlet: { yes: "Outlet nearby", no: "No suitable outlet", unsure: "Outlet unknown" },
    product_type: {
      electric: "Electric replacement seat",
      attachment: "Non-electric attachment",
      handheld: "Handheld sprayer",
      unsure: "Not sure yet",
    },
  };

  const selected = (name) => form.querySelector(`input[name="${name}"]:checked`)?.value || "";
  const numeric = (name) => {
    const raw = form.elements[name]?.value?.trim();
    if (!raw) return null;
    const value = Number(raw);
    return Number.isFinite(value) ? value : null;
  };
  const labelFor = (group, value) => (value && LABELS[group]?.[value]) || value || "—";

  const add = (items, severity, title, body) => items.push({ severity, title, body });

  function recordEvent(eventType, aggregate) {
    try {
      const payload = {
        event_id: crypto.randomUUID(),
        schema_version: 1,
        project_id: "bidetfit",
        event_type: eventType,
        source_ref: "fit_checker",
        observed_at_utc: new Date().toISOString(),
        aggregate,
      };
      const prior = JSON.parse(sessionStorage.getItem(EVENT_KEY) || "{}");
      prior[eventType] = (prior[eventType] || 0) + 1;
      prior.last_event = payload;
      sessionStorage.setItem(EVENT_KEY, JSON.stringify(prior));
    } catch {
      /* sessionStorage unavailable — skip silently */
    }
  }

  function missingChecklist(input) {
    const checklist = [];
    if (input.rearClearance === null) checklist.push("Measure rear clearance (A) from bolt centerline to tank or rising porcelain.");
    if (input.boltSpacing === null) checklist.push("Measure bolt spacing (B) between seat mounting holes.");
    if (input.bowlLength === null) checklist.push("Measure bowl length (C) from bolt centerline to front outside edge.");
    if (input.frenchCurve === "unsure") checklist.push("Confirm rear geometry with a side photo — flat deck or French curve.");
    if (input.skirted === "unsure") checklist.push("Check whether the fill-valve hose and shutoff are exposed or concealed.");
    if (input.outlet === "unsure" && input.productType === "electric") {
      checklist.push("Confirm outlet location, GFCI protection, and cord reach for an electric seat.");
    }
    if (input.bowlShape === "unsure" || input.bowlShape === "unusual") {
      checklist.push("Identify bowl shape or exact toilet model number before choosing a seat size.");
    }
    if (!checklist.length) checklist.push("Compare the exact toilet and bidet installation drawings; retain the return policy.");
    return checklist;
  }

  function analyzeInput(input) {
    const items = [];
    const missing = [];
    if (!input.toiletType) missing.push("toilet construction");
    if (!input.bowlShape) missing.push("bowl shape");
    if (!input.frenchCurve) missing.push("rear geometry");
    if (!input.skirted) missing.push("plumbing access");
    if (!input.outlet) missing.push("outlet status");
    if (!input.productType) missing.push("bidet category");

    if (missing.length) {
      return {
        level: "incomplete",
        badge: "Incomplete",
        heading: "Add the missing basics",
        intro: `This checker needs: ${missing.join(", ")}.`,
        items: [],
        missing,
        missingBasicCount: missing.length,
      };
    }

    if (input.toiletType === "wall-hung") {
      add(items, "high", "Wall-hung toilet", "Conventional under-seat valves and top-mounted seat hardware may not have accessible plumbing or compatible fixing points. Verify the exact toilet and bidet installation drawings.");
    } else if (input.toiletType === "one-piece") {
      add(items, "caution", "One-piece geometry", "One-piece toilets can work, but the rear curve and flat mounting area matter more than the one-piece label itself.");
    }

    if (input.frenchCurve === "yes") {
      const fc = RULES.french_curve;
      add(
        items,
        "high",
        "French-curve conflict (manufacturer guidance)",
        `${fc.guidance} ${fc.manufacturer} recommends contacting them with the exact toilet make and model for one-piece French-curve cases. Source checked ${fc.retrieved_at}.`,
      );
      if (input.rearClearance !== null && input.rearClearance < 2) {
        add(items, "high", "Limited space at mounting bolts", `${input.rearClearance.toFixed(2)} in rear clearance with a French curve is a high-risk combination for seat housings and attachment bodies.`);
      }
    } else if (input.frenchCurve === "unsure") {
      add(items, "caution", "Rear shape not confirmed", "Take a side photo and check whether the bowl stays flat behind the bolt holes or rises into a curve.");
    }

    if (input.skirted === "yes") {
      add(items, "caution", "Concealed plumbing", "The seat may fit while the supplied T-adapter does not. Confirm where the fill-valve connection and shutoff are accessible, and whether the manufacturer offers an alternate adapter.");
    } else if (input.skirted === "unsure") {
      add(items, "caution", "Plumbing access unknown", "Look for an exposed hose running from the wall shutoff to the underside of the toilet tank. Hidden connections need product-specific planning.");
    }

    if (input.productType === "electric") {
      if (input.outlet === "no") {
        add(items, "high", "No nearby receptacle", "An electric bidet seat needs a code-compliant power source. Do not treat an extension cord as a permanent bathroom solution.");
      } else if (input.outlet === "unsure") {
        add(items, "caution", "Power location unknown", "Confirm the product cord length, outlet location, GFCI requirements, and local electrical rules before buying.");
      }
      if (input.boltSpacing !== null && (input.boltSpacing < RULES.bolt_spacing.incompatible_below_in || input.boltSpacing > RULES.bolt_spacing.incompatible_above_in)) {
        add(items, "high", "Bolt spacing outside Bio Bidet compatibility range", `Your ${input.boltSpacing.toFixed(2)} in measurement is outside the ${RULES.bolt_spacing.incompatible_below_in}–${RULES.bolt_spacing.incompatible_above_in} in range Bio Bidet lists as likely incompatible. Individual products can differ; verify the exact mounting plate.`);
      } else if (input.boltSpacing !== null) {
        add(items, "ok", "Bolt spacing within Bio Bidet broad range", `Your ${input.boltSpacing.toFixed(2)} in spacing clears the manufacturer screen, but the exact product mounting plate still controls.`);
      }
    } else if (input.productType === "attachment") {
      if (input.boltSpacing !== null && (input.boltSpacing < RULES.bolt_spacing.incompatible_below_in || input.boltSpacing > RULES.bolt_spacing.incompatible_above_in)) {
        add(items, "high", "Bolt spacing outside Bio Bidet compatibility range", `Your ${input.boltSpacing.toFixed(2)} in measurement is outside the ${RULES.bolt_spacing.incompatible_below_in}–${RULES.bolt_spacing.incompatible_above_in} in range Bio Bidet lists as likely incompatible.`);
      } else if (input.boltSpacing !== null) {
        add(items, "ok", "Attachment bolt spacing within Bio Bidet range", `Your ${input.boltSpacing.toFixed(2)} in spacing falls within the manufacturer broad range; verify the exact sliding brackets.`);
      }
    } else if (input.productType === "handheld") {
      add(items, "ok", "Seat shape matters less for a handheld sprayer", "The main questions become accessible plumbing, mounting location, hose reach, local code, and safe shutoff habits.");
    }

    const rearMin = RULES.rear_clearance.manufacturer_minimum_in;
    const rearScreen = RULES.rear_clearance.common_screen_in;
    if (input.rearClearance === null) {
      add(items, "caution", "Rear clearance not measured", "Measure from the centerline of the seat bolt holes to the nearest tank or rising porcelain.");
    } else if (input.rearClearance < rearMin) {
      add(items, "high", "Below Bio Bidet minimum rear clearance", `${input.rearClearance.toFixed(2)} in is below the ${rearMin} in minimum Bio Bidet cites for bolt-hole-to-tank clearance.`);
    } else if (input.rearClearance < rearScreen) {
      add(items, "caution", "Product-specific rear clearance", `${input.rearClearance.toFixed(2)} in meets Bio Bidet's ${rearMin} in minimum but many electronic seats call for ${rearScreen} in or more.`);
    } else {
      add(items, "ok", "Rear clearance clears a common screen", `${input.rearClearance.toFixed(2)} in is at or above a common ${rearScreen} in screening value. Confirm the exact product drawing.`);
    }

    if (input.bowlLength === null) {
      add(items, "caution", "Bowl length not measured", "Measure from the bolt-hole centerline to the front outside edge; labels such as compact elongated can be misleading.");
    } else if (input.bowlLength < 16) {
      add(items, "high", "Unusually short bowl measurement", `${input.bowlLength.toFixed(2)} in is below common round-bowl guidance. Expect overhang or incompatibility unless the exact product says otherwise.`);
    } else if (input.bowlLength <= 17.5) {
      if (input.bowlShape === "elongated") add(items, "caution", "Shape and measurement disagree", "This measurement is in a common round-bowl band, while elongated was selected. Re-measure from the bolt centerline.");
      else add(items, "ok", "Measurement is consistent with many round bowls", `${input.bowlLength.toFixed(2)} in falls within a commonly cited 16–17.5 in round-bowl range (Bio Bidet cites ~16.5 in).`);
    } else if (input.bowlLength <= 18.5) {
      add(items, "caution", "Compact or borderline length", `${input.bowlLength.toFixed(2)} in sits between common round and elongated rules. Product brands use different cutoffs, so compare the exact dimensional drawing.`);
    } else {
      if (input.bowlShape === "round") add(items, "caution", "Shape and measurement disagree", "This measurement is consistent with many elongated bowls, while round was selected. Re-measure before choosing a seat size.");
      else add(items, "ok", "Measurement is consistent with many elongated bowls", `${input.bowlLength.toFixed(2)} in clears a common elongated screening value (Bio Bidet cites ~18.5 in).`);
    }

    const high = items.filter((item) => item.severity === "high").length;
    const caution = items.filter((item) => item.severity === "caution").length;
    let level = "likely";
    let badge = "Likely category fit";
    let heading = "No obvious universal blocker found";
    let intro = "Your measurements clear the broad screening rules entered here. This is not a guarantee for a specific model.";
    if (high > 0) {
      level = "high-risk";
      badge = "High fit risk";
      heading = "Resolve these blockers before buying";
      intro = "At least one answer conflicts with a common fit requirement or cited manufacturer guidance. Look for a product-specific exception or a different bidet category.";
    } else if (caution >= 2) {
      level = "caution";
      badge = "Needs verification";
      heading = "The category may work, but details matter";
      intro = "No single hard blocker was found, but several measurements or installation details need exact-model confirmation.";
    }

    return { level, badge, heading, intro, items, missing: [], high, caution, missingBasicCount: 0 };
  }

  function renderResult(result) {
    panel.className = `result-panel ${result.level === "incomplete" ? "caution" : result.level}`;
    if (result.level === "incomplete") {
      panel.innerHTML = `<span class="result-badge">${result.badge}</span><h2>${result.heading}</h2><p>${result.intro}</p><p class="result-meta">Measurements can be left blank, but every blank reduces confidence.</p>`;
      if (packet) packet.hidden = true;
      return;
    }
    panel.innerHTML = `
      <span class="result-badge">${result.badge}</span>
      <h2>${result.heading}</h2>
      <p>${result.intro}</p>
      <ul class="result-list">${result.items.map((item) => `<li><strong>${item.title}:</strong> ${item.body}</li>`).join("")}</ul>
      <p class="result-meta">Category screening only — not an exact compatibility guarantee. Manufacturer source freshness: ${RULES.source_freshness}. Compare every result with the exact product installation drawing and return policy before purchase. No affiliate links are active in this beta.</p>
      <div class="button-row packet-actions"><button class="button secondary" type="button" id="print-packet">Save / print measurement packet</button></div>
    `;
    panel.querySelector("#print-packet")?.addEventListener("click", () => {
      renderPacket(lastInput, result);
      recordEvent("fit_checker.completed", { ...lastAggregate, packet_printed: true });
      window.print();
    });
    if (packet) packet.hidden = false;
  }

  let lastInput = null;
  let lastAggregate = null;

  function renderPacket(input, result) {
    if (!packet) return;
    const checklist = missingChecklist(input);
    packet.innerHTML = `
      <header class="packet-header">
        <p class="packet-brand">BidetFit measurement packet</p>
        <p class="packet-date">Generated ${new Date().toLocaleString()} — save or print for store visits and support questions.</p>
      </header>
      <section>
        <h2>Your inputs</h2>
        <table class="packet-table">
          <tbody>
            <tr><th>Toilet type</th><td>${labelFor("toilet_type", input.toiletType)}</td></tr>
            <tr><th>Bowl shape</th><td>${labelFor("bowl_shape", input.bowlShape)}</td></tr>
            <tr><th>Rear clearance (A)</th><td>${input.rearClearance === null ? "Not measured" : `${input.rearClearance.toFixed(2)} in`}</td></tr>
            <tr><th>Bolt spacing (B)</th><td>${input.boltSpacing === null ? "Not measured" : `${input.boltSpacing.toFixed(2)} in`}</td></tr>
            <tr><th>Bowl length (C)</th><td>${input.bowlLength === null ? "Not measured" : `${input.bowlLength.toFixed(2)} in`}</td></tr>
            <tr><th>Rear geometry</th><td>${labelFor("french_curve", input.frenchCurve)}</td></tr>
            <tr><th>Plumbing access</th><td>${labelFor("skirted", input.skirted)}</td></tr>
            <tr><th>Outlet</th><td>${labelFor("outlet", input.outlet)}</td></tr>
            <tr><th>Bidet category</th><td>${labelFor("product_type", input.productType)}</td></tr>
          </tbody>
        </table>
      </section>
      <section>
        <h2>Screening result</h2>
        <p><strong>${result.badge}</strong> — ${result.heading}</p>
        <ul>${result.items.map((item) => `<li><strong>${item.title}:</strong> ${item.body}</li>`).join("")}</ul>
      </section>
      <section>
        <h2>Still unknown or to verify</h2>
        <ul>${checklist.map((line) => `<li>${line}</li>`).join("")}</ul>
      </section>
      <footer class="packet-footer">
        <p>This packet is a conservative category screen, not proof that a specific model fits. Exact toilet model numbers, product installation drawings, and return policies control the purchase decision.</p>
        <p>Questions or corrections: bidetfit@unsubscriber.me</p>
      </footer>
    `;
  }

  function readInput() {
    return {
      toiletType: selected("toilet_type"),
      bowlShape: selected("bowl_shape"),
      frenchCurve: selected("french_curve"),
      skirted: selected("skirted"),
      outlet: selected("outlet"),
      productType: selected("product_type"),
      boltSpacing: numeric("bolt_spacing"),
      rearClearance: numeric("rear_clearance"),
      bowlLength: numeric("bowl_length"),
    };
  }

  function analyze(event) {
    event.preventDefault();
    recordEvent("fit_checker.started", { source_ref: "fit_checker" });
    const input = readInput();
    lastInput = input;
    const result = analyzeInput(input);
    renderResult(result);

    lastAggregate = {
      outcome_level: result.level,
      high_count: result.high || 0,
      caution_count: result.caution || 0,
      missing_basic_count: result.missingBasicCount,
      product_type: input.productType || null,
      has_french_curve_flag: input.frenchCurve === "yes",
      has_skirted_flag: input.skirted === "yes",
      packet_printed: false,
    };
    const eventType = result.level === "high-risk" || result.level === "incomplete" ? "fit_checker.unresolved" : "fit_checker.completed";
    recordEvent(eventType, lastAggregate);
    renderPacket(input, result);
    panel.focus();
  }

  form.addEventListener("submit", analyze);
  form.addEventListener("reset", () => {
    window.setTimeout(() => {
      panel.className = "result-panel empty";
      panel.innerHTML = "<span class=\"result-badge\">Waiting for measurements</span><h2>Your fit report appears here</h2><p>Complete the form. Unknown is a valid answer; the checker will tell you what to verify.</p>";
      if (packet) {
        packet.hidden = true;
        packet.innerHTML = "";
      }
    }, 0);
  });

  recordEvent("fit_checker.started", { source_ref: "fit_checker_page_load" });
})();
