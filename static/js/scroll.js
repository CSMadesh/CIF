/* ═══════════════════════════════════════════
   IXOVA — SCROLL & PAGE TRANSITION JS
   ═══════════════════════════════════════════ */

(function () {

  /* ── Scroll progress bar ── */
  var bar = document.getElementById('scrollProgress');
  if (bar) {
    window.addEventListener('scroll', function () {
      var scrolled = window.scrollY;
      var total = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = (total > 0 ? (scrolled / total) * 100 : 0) + '%';
    }, { passive: true });
  }

  /* ── IntersectionObserver for .reveal elements ── */
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  function initReveal() {
    document.querySelectorAll('.reveal').forEach(function (el) {
      observer.observe(el);
    });
  }
  initReveal();

  /* ── Auto-tag common elements for reveal ── */
  function autoTag() {
    var selectors = [
      '.card', '.stat-card', '.opp-card',
      '.tip-item', '.section-header',
      '.profile-header', '.quote-card',
      '.home-feature', '.home-stat',
      '.sa-table', '.page-header'
    ];
    selectors.forEach(function (sel) {
      document.querySelectorAll(sel).forEach(function (el, i) {
        if (!el.classList.contains('reveal')) {
          el.classList.add('reveal', 'reveal-d' + Math.min(i + 1, 6));
          observer.observe(el);
        }
      });
    });
  }
  autoTag();

  /* ── Smooth page transition on internal links ── */
  var overlay = document.getElementById('pageTransition');
  if (overlay) {
    document.querySelectorAll('a[href]').forEach(function (link) {
      var href = link.getAttribute('href');
      /* skip external, anchor, javascript links */
      if (!href || href.startsWith('http') || href.startsWith('#') ||
          href.startsWith('javascript') || href.startsWith('mailto')) return;

      link.addEventListener('click', function (e) {
        e.preventDefault();
        var target = href;
        overlay.classList.add('active');
        setTimeout(function () {
          window.location.href = target;
        }, 320);
      });
    });

    /* Fade in on page load */
    overlay.classList.add('active');
    window.addEventListener('load', function () {
      setTimeout(function () {
        overlay.classList.remove('active');
      }, 80);
    });
  }

  /* ── Parallax on hero orbs ── */
  window.addEventListener('scroll', function () {
    var sy = window.scrollY;
    document.querySelectorAll('.home-bg-orb').forEach(function (orb, i) {
      var speed = i % 2 === 0 ? 0.15 : -0.1;
      orb.style.transform = 'translateY(' + (sy * speed) + 'px)';
    });
  }, { passive: true });

})();
