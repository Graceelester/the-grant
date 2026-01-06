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
     FORM SUBMISSION WITH FILE SIZE CHECK
  ========================== */
  const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB per file

  const forms = document.querySelectorAll("form");
  forms.forEach(form => {
    form.addEventListener("submit", (event) => {
      // Validate current step
      if (steps.length > 0 && !validateStep(currentStep)) {
        event.preventDefault();
        return;
      }

      // Step 5: check file sizes
      const fileInputs = steps[currentStep].querySelectorAll("input[type='file']");
      for (const input of fileInputs) {
        for (const file of input.files) {
          if (file.size > MAX_FILE_SIZE) {
            alert(`File "${file.name}" exceeds the 5 MB limit.`);
            event.preventDefault();
            return;
          }
        }
      }
      // If valid, browser handles normal form submission and redirect
    });
  });

});
