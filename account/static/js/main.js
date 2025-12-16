document.addEventListener("DOMContentLoaded", () => {
  const greetingEl = document.getElementById("greeting");

  if (!greetingEl) return;

  const hour = new Date().getHours();
  let greeting = "Good day";

  if (hour >= 5 && hour < 12) {
    greeting = "Good morning";
  } else if (hour >= 12 && hour < 17) {
    greeting = "Good afternoon";
  } else {
    greeting = "Good evening";
  }

  greetingEl.textContent = greeting;
});
