/* ═══════════════════════════════════════════
   IXOVA — SCROLL ANIMATIONS (fast)
   ═══════════════════════════════════════════ */
(function () {

  /* ── Scroll progress bar (passive, throttled) ── */
  var bar  = document.getElementById('scrollProgress');
  var ticking = false;
  if (bar) {
    window.addEventListener('scroll', function () {
      if (!ticking) {
        requestAnimationFrame(function () {
          var total = document.documentElement.scrollHeight - window.innerHeight;
          bar.style.width = (total > 0 ? (window.scrollY / total) * 100 : 0) + '%';
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });
  }

  /* ── IntersectionObserver reveal ── */
  if (!window.IntersectionObserver) return;

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -30px 0px' });

  /* Auto-tag elements once DOM ready */
  var AUTO_SELECTORS = [
    '.card', '.stat-card', '.opp-card', '.tip-item',
    '.section-header', '.profile-header', '.quote-card',
    '.home-feature', '.page-header'
  ];

  function tagAndObserve() {
    AUTO_SELECTORS.forEach(function (sel) {
      document.querySelectorAll(sel).forEach(function (el, i) {
        if (!el.classList.contains('reveal')) {
          el.classList.add('reveal', 'reveal-d' + Math.min(i + 1, 6));
        }
        observer.observe(el);
      });
    });
    /* Also observe any manually tagged .reveal elements */
    document.querySelectorAll('.reveal:not(.visible)').forEach(function (el) {
      observer.observe(el);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', tagAndObserve);
  } else {
    tagAndObserve();
  }

  /* ── Fast page transition (no delay — just a quick fade) ── */
  var overlay = document.getElementById('pageTransition');
  if (overlay) {
    /* Fade OUT on page load — instant */
    overlay.style.transition = 'opacity 0.15s ease';
    overlay.style.opacity = '0';
    overlay.style.pointerEvents = 'none';

    /* Fade IN on link click — only 150ms then navigate */
    document.addEventListener('click', function (e) {
      var link = e.target.closest('a[href]');
      if (!link) return;
      var href = link.getAttribute('href');
      if (!href || href.startsWith('http') || href.startsWith('#') ||
          href.startsWith('javascript') || href.startsWith('mailto') ||
          href.startsWith('tel') || link.target === '_blank') return;

      e.preventDefault();
      overlay.style.opacity = '1';
      overlay.style.pointerEvents = 'all';
      /* Navigate after just 150ms — feels instant but still smooth */
      setTimeout(function () {
        window.location.href = href;
      }, 150);
    });
  }

})();
