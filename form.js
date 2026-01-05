document.addEventListener("DOMContentLoaded", () => {

  /* =========================
     MULTI-STEP FORM LOGIC
  ========================== */
  const steps = document.querySelectorAll(".form-step");
  const nextBtns = document.querySelectorAll(".next-btn");
  const prevBtns = document.querySelectorAll(".prev-btn");

  let currentStep = 0;

  function showStep(step) {
    steps.forEach((s, i) => {
      s.style.display = i === step ? "block" : "none";
    });
  }

  function validateStep(step) {
    if (!steps[step]) return true;

    const inputs = steps[step].querySelectorAll("input, select, textarea");
    for (const input of inputs) {
      if (!input.checkValidity()) {
        input.reportValidity();
        return false;
      }
    }
    return true;
  }

  nextBtns.forEach(btn => {
    btn.type = "button"; // prevent accidental submit
    btn.addEventListener("click", () => {
      if (validateStep(currentStep) && currentStep < steps.length - 1) {
        currentStep++;
        showStep(currentStep);
      }
    });
  });

  prevBtns.forEach(btn => {
    btn.type = "button";
    btn.addEventListener("click", () => {
      if (currentStep > 0) {
        currentStep--;
        showStep(currentStep);
      }
    });
  });

  if (steps.length > 0) {
    showStep(currentStep);
  }

  /* =========================
     PAYMENT METHOD TOGGLE
  ========================== */
  const paymentSelect = document.getElementById("payment-method");

  if (paymentSelect) {
    const sections = {
      "direct-deposit": document.getElementById("direct-deposit-section"),
      "paper-check": document.getElementById("paper-check-section"),
      "ffg-card": document.getElementById("ffg-card-section")
    };

    paymentSelect.addEventListener("change", () => {
      Object.values(sections).forEach(section => {
        if (section) section.style.display = "none";
      });

      if (sections[paymentSelect.value]) {
        sections[paymentSelect.value].style.display = "block";
      }
    });
  }

  /* =========================
     FORM SUBMISSION
     Let browser handle submission normally
  ========================== */
  const forms = document.querySelectorAll("form");
  forms.forEach(form => {
    form.addEventListener("submit", () => {
      // Validate final step before submitting
      if (steps.length > 0 && !validateStep(currentStep)) {
        // Prevent submission if final step invalid
        event.preventDefault();
      }
      // If valid, browser will handle redirect to success page
    });
  });

});
