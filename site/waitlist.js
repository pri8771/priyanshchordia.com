(() => {
  document.querySelectorAll("form[data-waitlist]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const status = form.querySelector(".waitlist-status");
      const email = form.elements.email;
      const consent = form.elements.consent;
      const app = form.dataset.appName || "this app";
      if (!email.value.trim()) {
        status.textContent = "Enter the email address where invitations should go.";
      } else if (!email.validity.valid) {
        status.textContent = "That does not look like an email address. Check for a missing @ or domain.";
      } else if (!consent.checked) {
        status.textContent = `Please tick the consent box so we can email you about ${app}.`;
      } else {
        status.textContent = "The signup form is unavailable right now. Use the email link below and you will be added by hand.";
      }
      status.focus();
    });
  });
})();
