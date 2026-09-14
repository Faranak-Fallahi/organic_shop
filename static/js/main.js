// ================================================
// عطاری آویشن — main.js
// helper های سراسری: toast, confirm, سبد، اسلایدر
// ================================================

(function () {
  "use strict";

  /* ---------------- Toast ---------------- */
  function showToast(message, type) {
    type = type || "success";
    var container = document.querySelector(".toast-container-organic");
    if (!container) {
      container = document.createElement("div");
      container.className = "toast-container-organic";
      document.body.appendChild(container);
    }

    var iconMap = {
      success: '<i class="bi bi-check-lg"></i>',
      danger: '<i class="bi bi-exclamation-triangle"></i>',
      info: '<i class="bi bi-info-circle"></i>',
    };

    var toast = document.createElement("div");
    toast.className = "organic-toast" + (type === "danger" ? " toast-danger" : type === "info" ? " toast-info" : "");
    toast.innerHTML =
      '<div class="toast-icon">' + (iconMap[type] || iconMap.success) + "</div>" +
      '<div class="toast-msg">' + message + "</div>";

    container.appendChild(toast);

    setTimeout(function () {
      toast.classList.add("hiding");
      setTimeout(function () { toast.remove(); }, 320);
    }, 3200);
  }

  // نمایش پیام‌های Django messages
  setTimeout(function () {
    document.querySelectorAll(".dj-toast-message").forEach(function (el) {
      showToast(el.dataset.message, el.dataset.type || "success");
    });
  }, 200);

  /* ---------------- Confirm (همراه با فرم) ---------------- */
  window.organicConfirm = function (message) {
    return window.confirm(message || "آیا مطمئن هستید؟");
  };

  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!window.confirm(form.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });

  /* ---------------- Cart: باز/بسته دراور ---------------- */
  function openCart(e) {
    if (e) { e.preventDefault(); e.stopPropagation(); }
    var drawer = document.getElementById("cartDrawer");
    var overlay = document.getElementById("cartOverlay");
    if (!drawer) return;
    drawer.classList.add("active");
    if (overlay) overlay.classList.add("active");
    drawer.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeCart() {
    var drawer = document.getElementById("cartDrawer");
    var overlay = document.getElementById("cartOverlay");
    if (!drawer) return;
    drawer.classList.remove("active");
    if (overlay) overlay.classList.remove("active");
    drawer.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  window.openCart = openCart;
  window.closeCart = closeCart;

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeCart();
  });

  /* ---------------- Cart: ارسال های AJAX ---------------- */
  function afterCartUpdate(html) {
    var parser = new DOMParser();
    var doc = parser.parseFromString(html, "text/html");

    var newDrawer = doc.getElementById("cartDrawer");
    var curDrawer = document.getElementById("cartDrawer");
    if (newDrawer && curDrawer) {
      curDrawer.innerHTML = newDrawer.innerHTML;
    }

    var newBadge = doc.querySelector(".cart-badge");
    var curBadge = document.querySelector(".cart-badge");
    if (newBadge && curBadge) {
      curBadge.textContent = newBadge.textContent;
    }
  }

  document.addEventListener("submit", function (event) {
    var form = event.target;
    var action = form.getAttribute("action") || "";
    var isCartForm =
      action.indexOf("/cart/add/") !== -1 ||
      action.indexOf("/cart/decrease/") !== -1 ||
      action.indexOf("/cart/remove/") !== -1;

    if (!isCartForm) return;
    // در صفحه سبد، رفتار عادی (redirect) بهتر است
    if (window.location.pathname.indexOf("/cart/detail/") !== -1) return;

    event.preventDefault();
    var isInsideDrawer = form.closest("#cartDrawer") !== null;
    var formData = new FormData(form);

    fetch(action, {
      method: "POST",
      body: formData,
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then(function (res) {
        if (!res.ok) throw new Error("response error");
        return res.text();
      })
      .then(function (html) {
        afterCartUpdate(html);
        if (isInsideDrawer) openCart();
        // پیام toast اگر فرم دیتای مخصوص داشت
        var msg = form.dataset.toast;
        if (msg) showToast(msg, "success");
      })
      .catch(function () {
        // خطا: submit معمولی تا message های Django نمایش داده شوند
        form.submit();
      });
  });

  /* ---------------- Slider next/prev (RTL-aware) ---------------- */
  document.querySelectorAll("[data-slider]").forEach(function (wrapper) {
    var track = wrapper.querySelector("[data-slider-track]");
    var nextBtn = wrapper.querySelector("[data-slider-next]");
    var prevBtn = wrapper.querySelector("[data-slider-prev]");
    if (!track || !nextBtn || !prevBtn) return;

    var step = function () {
      var card = track.querySelector(".product-card, .product-grid-card, [data-slide-item]");
      if (card) return card.getBoundingClientRect().width + 16;
      return 280;
    };

    nextBtn.addEventListener("click", function () {
      track.scrollBy({ left: -step(), behavior: "smooth" });
    });
    prevBtn.addEventListener("click", function () {
      track.scrollBy({ left: step(), behavior: "smooth" });
    });
  });

  /* ---------------- Auto-dismiss alerts ---------------- */
  document.querySelectorAll(".alert-dismissible-custom").forEach(function (alertEl) {
    setTimeout(function () {
      alertEl.style.transition = "opacity .4s ease";
      alertEl.style.opacity = "0";
      setTimeout(function () { alertEl.remove(); }, 450);
    }, 5000);
  });
})();