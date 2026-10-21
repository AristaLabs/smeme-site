/* Landing page interactions: guarantees accordion, hero/how-it-works carousel,
   MCP client name rotation, and scroll-reveal. Extracted from
   landing/_scripts.html (M-04 CSP self-host). */
(function () {
  var list = document.querySelector("[data-landing-guarantees]");
  if (!list) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  var durationMs = 500;

  function afterHeightTransition(el, cb) {
    var done = false;
    var timer = window.setTimeout(finish, durationMs + 80);
    function finish() {
      if (done) return;
      done = true;
      el.removeEventListener("transitionend", onEnd);
      window.clearTimeout(timer);
      cb();
    }
    function onEnd(event) {
      if (event.target !== el || event.propertyName !== "height") return;
      finish();
    }
    el.addEventListener("transitionend", onEnd);
  }

  Array.prototype.forEach.call(list.querySelectorAll(".landing-guarantee-item"), function (details) {
    var summary = details.querySelector("summary");
    var wrap = details.querySelector(".landing-guarantee-detail-wrap");
    if (!summary || !wrap) return;

    var animating = false;

    summary.addEventListener("click", function (event) {
      if (animating) {
        event.preventDefault();
        return;
      }
      event.preventDefault();

      if (details.open) {
        animating = true;
        details.classList.add("is-closing");
        wrap.style.height = wrap.scrollHeight + "px";
        void wrap.offsetHeight;
        wrap.style.height = "0px";
        afterHeightTransition(wrap, function () {
          details.open = false;
          details.classList.remove("is-closing");
          wrap.style.height = "";
          animating = false;
        });
        return;
      }

      animating = true;
      details.classList.add("is-opening");
      details.open = true;
      wrap.style.height = "0px";
      var targetHeight = wrap.scrollHeight;
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () {
          wrap.style.height = targetHeight + "px";
          afterHeightTransition(wrap, function () {
            wrap.style.height = "auto";
            details.classList.remove("is-opening");
            animating = false;
          });
        });
      });
    });
  });
})();

(function () {
  function initLandingCarousel(showcase) {
    var cardsEl = showcase.querySelector("[data-landing-carousel-cards]");
    if (!cardsEl) return;

    var cards = Array.prototype.slice.call(
      cardsEl.querySelectorAll(
        ".landing-loop-card, .landing-cowork-exchange"
      )
    );
    var tabs = Array.prototype.slice.call(showcase.querySelectorAll("[data-landing-carousel-tab]"));
    var prevBtn = showcase.querySelector("[data-landing-carousel-prev]");
    var nextBtn = showcase.querySelector("[data-landing-carousel-next]");
    var resumeBtn = showcase.querySelector("[data-landing-carousel-resume]");
    var dotsEl = showcase.querySelector(".landing-hero-dots");
    var count = cards.length;
    var activeIndex = 0;
    var userPaused = false;
    var manual = showcase.hasAttribute("data-landing-carousel-manual");
    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function freeze() {
      if (userPaused) return;
      cardsEl.classList.add("is-frozen");
      showcase.classList.add("is-frozen");
    }

    function unfreeze() {
      cardsEl.classList.remove("is-frozen");
      showcase.classList.remove("is-frozen");
    }

    function pause(fromUser) {
      if (manual) {
        cardsEl.classList.add("is-paused");
        showcase.setAttribute("data-paused", "");
        if (resumeBtn) resumeBtn.hidden = true;
        return;
      }
      if (fromUser) userPaused = true;
      unfreeze();
      cardsEl.classList.add("is-paused");
      showcase.setAttribute("data-paused", "");
      if (resumeBtn) resumeBtn.hidden = !fromUser;
    }

    function resume() {
      userPaused = false;
      unfreeze();
      cardsEl.classList.remove("is-paused");
      showcase.removeAttribute("data-paused");
      showcase.classList.remove("platform-claude", "platform-chatgpt", "platform-copilot");
      if (resumeBtn) resumeBtn.hidden = true;
      cards.forEach(function (card) {
        card.classList.remove("is-active");
        card.removeAttribute("hidden");
        card.setAttribute("tabindex", "-1");
        card.setAttribute("aria-hidden", "false");
      });
      tabs.forEach(function (tab) {
        tab.setAttribute("aria-selected", "false");
      });
    }

    function show(index) {
      activeIndex = (index + count) % count;
      cards.forEach(function (card, i) {
        var on = i === activeIndex;
        card.classList.toggle("is-active", on);
        card.toggleAttribute("hidden", !on);
        card.setAttribute("tabindex", on ? "0" : "-1");
        card.setAttribute("aria-hidden", on ? "false" : "true");
      });
      tabs.forEach(function (tab, i) {
        tab.setAttribute("aria-selected", i === activeIndex ? "true" : "false");
      });

      applyShowcasePlatform(activeIndex);
    }

    function applyShowcasePlatform(idx) {
      var card = cards[idx];
      if (!card) return;
      var platform = card.getAttribute("data-platform") || "claude";
      showcase.classList.remove("platform-claude", "platform-chatgpt", "platform-copilot");
      showcase.classList.add("platform-" + platform);
    }

    function select(index, fromUser) {
      if (!manual) {
        pause(fromUser);
      }
      show(index);
      if (manual) {
        cardsEl.classList.add("is-paused");
        showcase.setAttribute("data-paused", "");
      }
    }

    tabs.forEach(function (tab, i) {
      tab.addEventListener("click", function () {
        if (manual) {
          show(i);
          cardsEl.classList.add("is-paused");
          showcase.setAttribute("data-paused", "");
        } else {
          select(i, true);
        }
      });
    });

    if (prevBtn) {
      prevBtn.addEventListener("click", function () {
        if (manual) {
          show(activeIndex - 1);
        } else {
          select(activeIndex - 1, true);
        }
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener("click", function () {
        if (manual) {
          show(activeIndex + 1);
        } else {
          select(activeIndex + 1, true);
        }
      });
    }
    if (resumeBtn) {
      resumeBtn.addEventListener("click", resume);
    }

    var nav = showcase.querySelector(".landing-hero-nav");

    cardsEl.addEventListener("mouseenter", freeze);
    cardsEl.addEventListener("mouseleave", function () {
      if (!userPaused) unfreeze();
    });
    if (nav) {
      nav.addEventListener("focusin", function () {
        if (!userPaused) freeze();
      });
    }
    showcase.addEventListener("focusout", function (event) {
      if (userPaused || showcase.contains(event.relatedTarget)) return;
      unfreeze();
    });

    if (dotsEl) {
      dotsEl.addEventListener("keydown", function (event) {
        if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
        event.preventDefault();
        var delta = event.key === "ArrowRight" ? 1 : -1;
        if (manual) {
          show(activeIndex + delta);
        } else {
          if (!cardsEl.classList.contains("is-paused")) {
            pause(true);
          }
          show(activeIndex + delta);
        }
        tabs[activeIndex].focus();
      });
    }

    var rail = showcase.querySelector(".landing-hiw-rail");
    if (rail) {
      rail.addEventListener("keydown", function (event) {
        if (event.key !== "ArrowLeft" && event.key !== "ArrowRight" && event.key !== "ArrowUp" && event.key !== "ArrowDown") return;
        event.preventDefault();
        var delta = (event.key === "ArrowRight" || event.key === "ArrowDown") ? 1 : -1;
        show(activeIndex + delta);
        tabs[activeIndex].focus();
      });
    }

    if (manual) {
      show(0);
      cardsEl.classList.add("is-paused");
      showcase.setAttribute("data-paused", "");
      if (resumeBtn) resumeBtn.hidden = true;
    } else if (reduceMotion) {
      select(0, true);
    }
  }

  document.querySelectorAll("[data-landing-carousel]").forEach(initLandingCarousel);
})();

(function () {
  var el = document.querySelector(".landing-hero-claude-name");
  if (!el) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  var clients = ["Claude", "ChatGPT", "Copilot", "... any MCP client"];
  var idx = 0;
  var holdMs = 2350;
  var fadeMs = 220;

  // Measure widest label to keep layout stable while text rotates
  var probe = document.createElement("span");
  probe.style.position = "absolute";
  probe.style.visibility = "hidden";
  probe.style.whiteSpace = "nowrap";
  probe.style.font = getComputedStyle(el).font;
  document.body.appendChild(probe);
  var maxW = 0;
  clients.forEach(function (c) {
    probe.textContent = c;
    maxW = Math.max(maxW, probe.offsetWidth);
  });
  document.body.removeChild(probe);
  if (maxW > 0) el.style.minWidth = maxW + "px";

  function rotate() {
    el.style.transitionDuration = fadeMs + "ms";
    el.style.opacity = "0";
    window.setTimeout(function () {
      idx = (idx + 1) % clients.length;
      el.textContent = clients[idx];
      el.style.opacity = "1";
      window.setTimeout(rotate, holdMs);
    }, fadeMs + 10);
  }

  // Show the first value for a beat, then begin rotating
  window.setTimeout(rotate, holdMs);
})();

(function () {
  var nodes = Array.prototype.slice.call(document.querySelectorAll(".smw-reveal"));
  if (!nodes.length) return;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce || !("IntersectionObserver" in window)) return;

  nodes.forEach(function (n) {
    n.classList.add("smw-reveal-init");
  });
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) {
        e.target.classList.add("smw-reveal-in");
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.14, rootMargin: "0px 0px -8% 0px" });
  nodes.forEach(function (n) {
    io.observe(n);
  });
})();
