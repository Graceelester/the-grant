document.addEventListener("DOMContentLoaded", function () {
  const steps = document.querySelectorAll(".form-step");
  const nextBtns = document.querySelectorAll(".next-btn");
  const prevBtns = document.querySelectorAll(".prev-btn");
  const form = document.getElementById("grant-form");

  let currentStep = 0;

  // Show a specific step
  function showStep(step) {
    steps.forEach((s, i) => {
      s.classList.toggle("active", i === step);
    });
  }

  // Validate required fields before next step
  function validateStep(step) {
    const inputs = steps[step].querySelectorAll("input, select, textarea");
    for (let input of inputs) {
      if (!input.checkValidity()) {
        input.reportValidity();
        return false;
      }
    }
    return true;
  }

  // Next / Prev navigation
  nextBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      if (validateStep(currentStep)) {
        if (currentStep < steps.length - 1) {
          currentStep++;
          showStep(currentStep);
        }
      }
    });
  });

  prevBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      if (currentStep > 0) {
        currentStep--;
        showStep(currentStep);
      }
    });
  });

  // Initialize first step
  showStep(currentStep);

  // Payment Method Logic
  const paymentSelect = document.getElementById("payment-method");
  if (paymentSelect) {
    paymentSelect.addEventListener("change", function () {
      const method = this.value;
      const sections = {
        "direct-deposit": document.getElementById("direct-deposit-section"),
        "paper-check": document.getElementById("paper-check-section"),
        "ffg-card": document.getElementById("ffg-card-section")
      };

      Object.values(sections).forEach(sec => sec.style.display = "none");
      if (sections[method]) sections[method].style.display = "block";
    });
  }

  // Spinner & Redirect on submit
  form.addEventListener("submit", function () {
    const overlay = document.createElement("div");
    overlay.style.position = "fixed";
    overlay.style.top = 0;
    overlay.style.left = 0;
    overlay.style.width = "100%";
    overlay.style.height = "100%";
    overlay.style.background = "rgba(0,0,0,0.6)";
    overlay.style.display = "flex";
    overlay.style.flexDirection = "column";
    overlay.style.justifyContent = "center";
    overlay.style.alignItems = "center";
    overlay.style.zIndex = "9999";

    overlay.innerHTML = `
      <div style="display: flex; flex-direction: column; align-items: center; color: #fff; font-size: 1.2em;">
        <div class="spinner" style="
          border: 6px solid #f3f3f3;
          border-top: 6px solid #28a745;
          border-radius: 50%;
          width: 50px;
          height: 50px;
          animation: spin 1s linear infinite;
          margin-bottom: 15px;">
        </div>
        Submitting your application...
      </div>
    `;

    document.body.appendChild(overlay);
  });
});
