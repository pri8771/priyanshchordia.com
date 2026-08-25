(() => {
  "use strict";

  const form = document.querySelector("#fit-form");
  const panel = document.querySelector("#fit-result");
  if (!form || !panel) return;

  const selected = (name) => form.querySelector(`input[name="${name}"]:checked`)?.value || "";
  const numeric = (name) => {
    const raw = form.elements[name]?.value?.trim();
    if (!raw) return null;
    const value = Number(raw);
    return Number.isFinite(value) ? value : null;
  };

  const add = (items, severity, title, body) => items.push({ severity, title, body });

  function analyze(event) {
    event.preventDefault();
    const toiletType = selected("toilet_type");
    const bowlShape = selected("bowl_shape");
    const frenchCurve = selected("french_curve");
    const skirted = selected("skirted");
    const outlet = selected("outlet");
    const productType = selected("product_type");
    const boltSpacing = numeric("bolt_spacing");
    const rearClearance = numeric("rear_clearance");
    const bowlLength = numeric("bowl_length");

    const missing = [];
    if (!toiletType) missing.push("toilet construction");
    if (!bowlShape) missing.push("bowl shape");
    if (!frenchCurve) missing.push("rear geometry");
    if (!skirted) missing.push("plumbing access");
    if (!outlet) missing.push("outlet status");
    if (!productType) missing.push("bidet category");

    if (missing.length) {
      panel.className = "result-panel caution";
      panel.innerHTML = `<span class="result-badge">Incomplete</span><h2>Add the missing basics</h2><p>This checker needs: ${missing.join(", ")}.</p><p class="result-meta">Measurements can be left blank, but every blank reduces confidence.</p>`;
      panel.focus();
      return;
    }

    const items = [];

    if (toiletType === "wall-hung") {
      add(items, "high", "Wall-hung toilet", "Conventional under-seat valves and top-mounted seat hardware may not have accessible plumbing or compatible fixing points. Verify the exact toilet and bidet installation drawings.");
    } else if (toiletType === "one-piece") {
      add(items, "caution", "One-piece geometry", "One-piece toilets can work, but the rear curve and flat mounting area matter more than the one-piece label itself.");
    }

    if (frenchCurve === "yes") {
      add(items, "high", "French-curve conflict", "A sloped or rising rear deck often blocks the body of a bidet seat or attachment. Do not assume a universal attachment will fit.");
    } else if (frenchCurve === "unsure") {
      add(items, "caution", "Rear shape not confirmed", "Take a side photo and check whether the bowl stays flat behind the bolt holes or rises into a curve.");
    }

    if (skirted === "yes") {
      add(items, "caution", "Concealed plumbing", "The seat may fit while the supplied T-adapter does not. Confirm where the fill-valve connection and shutoff are accessible, and whether the manufacturer offers an alternate adapter.");
    } else if (skirted === "unsure") {
      add(items, "caution", "Plumbing access unknown", "Look for an exposed hose running from the wall shutoff to the underside of the toilet tank. Hidden connections need product-specific planning.");
    }

    if (productType === "electric") {
      if (outlet === "no") {
        add(items, "high", "No nearby receptacle", "An electric bidet seat needs a code-compliant power source. Do not treat an extension cord as a permanent bathroom solution.");
      } else if (outlet === "unsure") {
        add(items, "caution", "Power location unknown", "Confirm the product cord length, outlet location, GFCI requirements, and local electrical rules before buying.");
      }
      if (boltSpacing !== null && (boltSpacing < 5.5 || boltSpacing > 7.5)) {
        add(items, "high", "Bolt spacing outside a common seat range", `Your ${boltSpacing.toFixed(2)} in measurement is outside the 5.5–7.5 in range used by a broad electronic-seat fit guide. Individual products can be narrower.`);
      } else if (boltSpacing !== null) {
        add(items, "ok", "Bolt spacing is within a common broad range", `Your ${boltSpacing.toFixed(2)} in spacing clears the first screen, but the exact product mounting plate still controls.`);
      }
    } else if (productType === "attachment") {
      if (boltSpacing !== null && (boltSpacing < 5 || boltSpacing > 7.5)) {
        add(items, "high", "Bolt spacing outside a common attachment range", `Your ${boltSpacing.toFixed(2)} in measurement is outside the 5–7.5 in range in a broad attachment guide.`);
      } else if (boltSpacing !== null) {
        add(items, "ok", "Attachment bolt spacing looks plausible", `Your ${boltSpacing.toFixed(2)} in spacing falls within a common broad attachment range; verify the exact sliding brackets.`);
      }
    } else if (productType === "handheld") {
      add(items, "ok", "Seat shape matters less for a handheld sprayer", "The main questions become accessible plumbing, mounting location, hose reach, local code, and safe shutoff habits.");
    }

    if (rearClearance === null) {
      add(items, "caution", "Rear clearance not measured", "Measure from the centerline of the seat bolt holes to the nearest tank or rising porcelain.");
    } else if (rearClearance < 1.5) {
      add(items, "high", "Very limited rear clearance", `${rearClearance.toFixed(2)} in is below the 1.5 in minimum cited by broad fit guides for some seats and attachments.`);
    } else if (rearClearance < 1.75) {
      add(items, "caution", "Product-specific rear clearance", `${rearClearance.toFixed(2)} in may work for products requiring 1.5 in, but many electronic seats call for 1.75 in or more.`);
    } else {
      add(items, "ok", "Rear clearance clears a common screen", `${rearClearance.toFixed(2)} in is at or above a common 1.75 in screening value. Confirm the exact product drawing.`);
    }

    if (bowlLength === null) {
      add(items, "caution", "Bowl length not measured", "Measure from the bolt-hole centerline to the front outside edge; labels such as compact elongated can be misleading.");
    } else if (bowlLength < 16) {
      add(items, "high", "Unusually short bowl measurement", `${bowlLength.toFixed(2)} in is below common round-bowl guidance. Expect overhang or incompatibility unless the exact product says otherwise.`);
    } else if (bowlLength <= 17.5) {
      if (bowlShape === "elongated") add(items, "caution", "Shape and measurement disagree", "This measurement is in a common round-bowl band, while elongated was selected. Re-measure from the bolt centerline.");
      else add(items, "ok", "Measurement is consistent with many round bowls", `${bowlLength.toFixed(2)} in falls within a commonly cited 16–17.5 in round-bowl range.`);
    } else if (bowlLength <= 18.5) {
      add(items, "caution", "Compact or borderline length", `${bowlLength.toFixed(2)} in sits between common round and elongated rules. Product brands use different cutoffs, so compare the exact dimensional drawing.`);
    } else {
      if (bowlShape === "round") add(items, "caution", "Shape and measurement disagree", "This measurement is consistent with many elongated bowls, while round was selected. Re-measure before choosing a seat size.");
      else add(items, "ok", "Measurement is consistent with many elongated bowls", `${bowlLength.toFixed(2)} in clears a common elongated screening value.`);
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
      intro = "At least one answer conflicts with a common fit requirement. Look for a product-specific exception or a different bidet category.";
    } else if (caution >= 2) {
      level = "caution";
      badge = "Needs verification";
      heading = "The category may work, but details matter";
      intro = "No single hard blocker was found, but several measurements or installation details need exact-model confirmation.";
    }

    panel.className = `result-panel ${level}`;
    panel.innerHTML = `
      <span class="result-badge">${badge}</span>
      <h2>${heading}</h2>
      <p>${intro}</p>
      <ul class="result-list">${items.map((item) => `<li><strong>${item.title}:</strong> ${item.body}</li>`).join("")}</ul>
      <p class="result-meta">Screening only. Compare every result with the exact product installation drawing and return policy before purchase. No affiliate links are active in this beta.</p>
    `;
    panel.focus();
  }

  form.addEventListener("submit", analyze);
  form.addEventListener("reset", () => {
    window.setTimeout(() => {
      panel.className = "result-panel empty";
      panel.innerHTML = "<span class=\"result-badge\">Waiting for measurements</span><h2>Your fit report appears here</h2><p>Complete the form. Unknown is a valid answer; the checker will tell you what to verify.</p>";
    }, 0);
  });
})();
