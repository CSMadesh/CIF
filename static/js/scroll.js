/* IXOVA — SCROLL (lightweight, no page transition delay) */
(function () {
  'use strict';

  /* ── Scroll progress bar ── */
  var bar = document.getElementById('scrollProgress');
  if (bar) {
    var rafPending = false;
    window.addEventListener('scroll', function () {
      if (rafPending) return;
      rafPending = true;
      requestAnimationFrame(function () {
        var total = document.documentElement.scrollHeight - window.innerHeight;
        bar.style.width = (total > 0 ? (window.scrollY / total) * 100 : 0) + '%';
        rafPending = false;
      });
    }, { passive: true });
  }

  /* ── Scroll reveal via IntersectionObserver ── */
  if (!window.IntersectionObserver) return;

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -20px 0px' });

  var SELECTORS = '.card,.stat-card,.opp-card,.tip-item,.section-header,.profile-header,.quote-card,.home-feature,.page-header';

  function init() {
    document.querySelectorAll(SELECTORS).forEach(function (el, i) {
      if (!el.classList.contains('reveal')) {
        el.classList.add('reveal', 'reveal-d' + Math.min(i + 1, 6));
      }
      io.observe(el);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
