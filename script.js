document.addEventListener("DOMContentLoaded", function () {
  var swiper = new Swiper(".testimonialSwiper", {
      slidesPerView: 4, // Default for large screens
      spaceBetween: 20,
      loop: true,
      autoplay: {
          delay: 3000,
          disableOnInteraction: false,
      },
      navigation: {
          nextEl: ".swiper-button-next",
          prevEl: ".swiper-button-prev",
      },
      breakpoints: {
          1024: { slidesPerView: 3 },
          768: { slidesPerView: 2 }, 
      },
      on: {
          init: function () {
              this.update(); 
          },
          resize: function () {
              this.update(); 
          },
      },
  });
});

// Newsletter success popup
const form = document.getElementById("newsletter-form");
const successMessage = document.getElementById("success-message");

form.addEventListener("submit", function (e) {
  e.preventDefault();
  successMessage.style.display = "block";
  setTimeout(() => {
    successMessage.style.display = "none";
  }, 4000); // hide after 4 seconds
  form.reset();
});


// Simple count-up when stats enter view
(function(){
  const nums = document.querySelectorAll('.kpi-number');
  if(!nums.length) return;

  const speed = 800; // ms
  const easeOut = t => 1 - Math.pow(1 - t, 3);

  const animate = el => {
    const target = +el.dataset.target || 0;
    const start = 0;
    const startTime = performance.now();

    function frame(now){
      const p = Math.min(1, (now - startTime)/speed);
      const val = Math.round(start + (target - start) * easeOut(p));
      el.textContent = val.toLocaleString();
      if(p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  };

  const io = new IntersectionObserver(entries=>{
    entries.forEach(entry=>{
      if(entry.isIntersecting){
        animate(entry.target);
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.4 });

  nums.forEach(n => io.observe(n));
})();


