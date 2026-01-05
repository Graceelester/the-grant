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
    for (let input of inputs) {
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

    paymentSelect.addEventListener("change", function () {
      Object.values(sections).forEach(section => {
        if (section) section.style.display = "none";
      });

      if (sections[this.value]) {
        sections[this.value].style.display = "block";
      }
    });
  }

  /* =========================
     FORM SUBMISSION (FETCH)
  ========================== */
  const forms = document.querySelectorAll("form[data-ajax='true']");

  forms.forEach(form => {
    const successDiv = document.getElementById(form.dataset.success);

    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const submitBtn = form.querySelector("[type='submit']");
      if (submitBtn) submitBtn.disabled = true;

      try {
        const response = await fetch(form.action, {
          method: "POST",
          body: new FormData(form)
        });

        if (!response.ok) {
          throw new Error("Server returned error");
        }

        form.style.display = "none";
        if (successDiv) successDiv.classList.remove("hidden");

        form.reset();
        currentStep = 0;
        showStep(currentStep);

      } catch (err) {
        console.error("Form submit error:", err);
        alert("Submission failed. Please try again.");
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  });

});
