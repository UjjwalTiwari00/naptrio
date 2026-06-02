/* ============================================================
   Naptrio – page chrome (slideshow, rails, cart, subscribe)
   Pure vanilla JS. Cart backed by server sessions via AJAX.
   ============================================================ */
(() => {
  "use strict";

  /* ---------- CSRF ---------- */
  function getCookie(name) {
    const m = document.cookie.match(new RegExp("(^|; )" + name + "=([^;]*)"));
    return m ? decodeURIComponent(m[2]) : "";
  }

  /* ---------- Cart badge ---------- */
  function setCartBadge(count) {
    const el = document.getElementById("cartCount");
    if (!el) return;
    el.textContent = count;
    if (count > 0) {
      el.classList.remove("hidden");
      el.classList.add("flex");
    } else {
      el.classList.add("hidden");
      el.classList.remove("flex");
    }
  }

  /* ---------- Toast ---------- */
  function toast(msg) {
    const t = document.getElementById("toast");
    if (!t) return;
    t.textContent = msg;
    t.classList.add("show");
    clearTimeout(toast._t);
    toast._t = setTimeout(() => t.classList.remove("show"), 2200);
  }

  /* ---------- Hero slideshow ---------- */
  const slides = document.querySelectorAll(".slide");
  const dots   = document.querySelectorAll("[data-dot]");
  let current  = 0;

  function goToSlide(i) {
    if (!slides.length) return;
    current = (i + slides.length) % slides.length;
    slides.forEach((el, idx) => (el.style.opacity = idx === current ? 1 : 0));
    dots.forEach((el, idx) => {
      el.className = "transition-all rounded-full " +
        (idx === current ? "w-8 h-2 bg-[#4a9eff]" : "w-2 h-2 bg-white/50 hover:bg-white/80");
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    if (window.lucide) window.lucide.createIcons();

    /* slideshow */
    if (slides.length > 1) setInterval(() => goToSlide(current + 1), 4500);
    document.querySelectorAll("[data-dot]").forEach((b) =>
      b.addEventListener("click", () => goToSlide(parseInt(b.dataset.dot, 10)))
    );

    /* product rails */
    document.querySelectorAll(".rail-prev, .rail-next").forEach((btn) => {
      btn.addEventListener("click", () => {
        const rail = document.getElementById("rail-" + btn.dataset.rail);
        if (!rail) return;
        const delta = btn.classList.contains("rail-next") ? 1 : -1;
        rail.scrollBy({ left: delta * 340, behavior: "smooth" });
      });
    });

    /* mobile menu */
    const menuBtn = document.getElementById("mobileMenuBtn");
    const mobile  = document.getElementById("mobileMenu");
    if (menuBtn && mobile) menuBtn.addEventListener("click", () => mobile.classList.toggle("hidden"));

    /* delegated: add-to-cart (AJAX → server session) */
    document.addEventListener("click", async (e) => {
      const btn = e.target.closest("[data-add]");
      if (!btn) return;

      const productId = btn.dataset.add;
      const name      = btn.dataset.name || "Item";

      // Find the cart-add URL embedded in the page or fall back to a convention
      const url = document.querySelector("meta[name='cart-add-url']")?.content || "/cart/add/";

      const fd = new FormData();
      fd.append("product_id", productId);
      fd.append("qty", "1");

      try {
        const res  = await fetch(url, {
          method:  "POST",
          body:    fd,
          headers: { "X-CSRFToken": getCookie("csrftoken") },
        });
        const json = await res.json();
        if (json.ok) {
          setCartBadge(json.count);
          toast(`${json.name || name} added to cart!`);
        } else {
          toast("Could not add to cart. Please try again.");
        }
      } catch {
        toast("Could not reach the server. Please try again.");
      }
    });

    /* newsletter subscribe (AJAX) */
    const form = document.getElementById("subscribeForm");
    if (form) {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const data = new FormData(form);
        try {
          const res  = await fetch(form.action, {
            method:  "POST",
            body:    data,
            headers: { "X-CSRFToken": getCookie("csrftoken") },
          });
          const json = await res.json();
          toast(json.message || (json.ok ? "Subscribed!" : "Something went wrong"));
          if (json.ok) form.reset();
        } catch {
          toast("Couldn't reach the server. Please try again.");
        }
      });
    }

    /* scroll-reveal */
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) en.target.classList.add("in"); });
    }, { threshold: 0.12 });
    document.querySelectorAll(".fade-in").forEach((el) => io.observe(el));
  });
})();
