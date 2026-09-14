(() => {
  const postJson = async (url, body) => {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    let data = {};
    try {
      data = await response.json();
    } catch {
      data = {};
    }
    return { response, data };
  };

  document.querySelectorAll("form[data-waitlist]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const status = form.querySelector(".waitlist-status");
      const email = form.elements.email;
      const consent = form.elements.consent;
      const app = form.dataset.appName || "this app";
      const appSlug = (form.dataset.appSlug || app).toLowerCase();
      const endpoint = form.dataset.intakeEndpoint;

      if (!email.value.trim()) {
        status.textContent = "Enter the email address where invitations should go.";
      } else if (!email.validity.valid) {
        status.textContent = "That does not look like an email address. Check for a missing @ or domain.";
      } else if (!consent.checked) {
        status.textContent = `Please tick the consent box so we can email you about ${app}.`;
      } else if (!endpoint) {
        status.textContent =
          "The signup form is unavailable right now. Use the email link below and you will be added by hand.";
      } else {
        status.textContent = "Submitting your request…";
        try {
          const { response, data } = await postJson(endpoint, {
            app_slug: appSlug,
            email: email.value.trim(),
            first_name: form.elements.first_name?.value?.trim() || null,
            device_note: form.elements.device?.value?.trim() || null,
            source_page: window.location.href,
            consent: true,
          });
          if (response.ok && data.ok) {
            if (data.status === "duplicate") {
              status.textContent =
                "We already have this request on file for that email address. No duplicate was created.";
            } else {
              status.textContent = "Thank you — your interest was recorded. We will follow up by email when appropriate.";
            }
          } else if (response.status >= 500 || response.status === 0) {
            status.textContent =
              "The signup service is unavailable right now. Use the email link below and you will be added by hand.";
          } else {
            status.textContent =
              data.error ||
              "We could not record that request. Check the details and try again, or use the email link below.";
          }
        } catch {
          status.textContent =
            "Could not reach the signup service. Use the email link below and you will be added by hand.";
        }
      }
      status.focus();
    });
  });
})();
