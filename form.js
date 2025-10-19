// // form.js

// document.addEventListener("DOMContentLoaded", function () {
//   const steps = document.querySelectorAll(".form-step");
//   const nextBtns = document.querySelectorAll(".next-btn");
//   const prevBtns = document.querySelectorAll(".prev-btn");

//   let currentStep = 0;

//   function showStep(step) {
//     steps.forEach((s, i) => {
//       s.classList.toggle("active", i === step);
//     });
//   }

//   // Validate required fields before moving next
//   function validateStep(step) {
//     const inputs = steps[step].querySelectorAll("input, select, textarea");
//     for (let input of inputs) {
//       if (!input.checkValidity()) {
//         input.reportValidity(); // show browser validation message
//         return false;
//       }
//     }
//     return true;
//   }

//   // Next button logic
//   nextBtns.forEach(btn => {
//     btn.addEventListener("click", () => {
//       if (validateStep(currentStep)) {
//         if (currentStep < steps.length - 1) {
//           currentStep++;
//           showStep(currentStep);
//         }
//       }
//     });
//   });

//   // Previous button logic
//   prevBtns.forEach(btn => {
//     btn.addEventListener("click", () => {
//       if (currentStep > 0) {
//         currentStep--;
//         showStep(currentStep);
//       }
//     });
//   });

//   // Initialize form
//   showStep(currentStep);
// });

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("contactForm");
  const success = document.getElementById("formSuccess");

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const formData = new FormData(form);

    try {
      const response = await fetch("/api/submit-contact", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        // Hide form
        form.style.display = "none";

        // Show success container
        success.classList.remove("hidden");

        // Force reflow for Lordicon to render correctly
        success.offsetHeight; // hack to trigger reflow

        // Optional: animate opacity for smooth appearance
        success.style.opacity = 0;
        success.style.transition = "opacity 0.3s ease-in-out";
        requestAnimationFrame(() => {
          success.style.opacity = 1;
        });

        // Reset form fields
        form.reset();
      } else {
        // Try to extract JSON error if available
        let errorMsg = "Something went wrong. Please try again.";
        try {
          const data = await response.json();
          if (data.error) errorMsg = data.error;
        } catch (err) {
          // Not JSON or no body
        }
        alert(errorMsg);
      }
    } catch (error) {
      alert("Network error — please check your connection and try again.");
      console.error(error);
    }
  });
});





// Payment Method Logic
document.addEventListener("DOMContentLoaded", function () {
  const paymentSelect = document.getElementById("payment-method");

  if (paymentSelect) {
    paymentSelect.addEventListener("change", function () {
      const method = this.value;

      const sections = {
        "direct-deposit": document.getElementById("direct-deposit-section"),
        "paper-check": document.getElementById("paper-check-section"),
        "ffg-card": document.getElementById("ffg-card-section")
      };

      // Hide all first
      Object.values(sections).forEach(section => {
        if (section) section.style.display = "none";
      });

      // Show selected section
      if (sections[method]) {
        sections[method].style.display = "block";
      }
    });
  }
});



document.addEventListener("DOMContentLoaded", () => {
  const contactForm = document.querySelector("form[action='http://127.0.0.1:5000/api/submit-contact']");
  const successDiv = document.getElementById("formSuccess");

  contactForm.addEventListener("submit", function(e) {
    e.preventDefault(); // stop default form submit

    const formData = new FormData(contactForm);

    fetch(contactForm.action, {
      method: "POST",
      body: formData
    })
    .then(response => {
      if (response.ok) {
        contactForm.style.display = "none"; // hide form
        successDiv.classList.remove("hidden"); // show success
      } else {
        alert("Error submitting form. Try again.");
      }
    })
    .catch(err => {
      console.error("Fetch error:", err);
      alert("Server error. Try later.");
    });
  });
});


document.addEventListener("DOMContentLoaded", function () {
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
    btn.addEventListener("click", () => {
      if (validateStep(currentStep) && currentStep < steps.length - 1) {
        currentStep++;
        showStep(currentStep);
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

  showStep(currentStep); // show first step
});
