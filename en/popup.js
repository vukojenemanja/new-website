// ─── Email popup kit (English) ──────────────────────────────────────────────
// ConvertKit form ID: app.kit.com/forms/designers/10008772/edit
// PDF toggle: set to true when Soul_Number_X.pdf files are uploaded
// ───────────────────────────────────────────────────────────────────────────

(function () {
  var FORM_ID = '10008772';
  var STORAGE_KEY = 'nv_popup_hidden';
  var TRIGGER_SCROLL = 0.50;
  var TRIGGER_SECONDS = 45;
  var PDF_READY = true;

  try {
    if (localStorage.getItem(STORAGE_KEY)) return;
  } catch (e) {}

  var triggered = false;
  var timer = null;

  // ── Soul number calculation ───────────────────────────────────────────────
  function calcSoul(dobStr) {
    var s = dobStr.trim();
    var day;
    if (/^\d{4}-\d{2}-\d{2}$/.test(s)) {
      day = parseInt(s.split('-')[2], 10);
    } else {
      day = parseInt(s.split('.')[0], 10);
    }
    if (isNaN(day) || day < 1 || day > 31) return null;
    var n = day;
    while (n > 11) {
      var s2 = 0, tmp = n;
      while (tmp > 0) { s2 += tmp % 10; tmp = Math.floor(tmp / 10); }
      n = s2;
    }
    return n;
  }

  function wantsSoul() {
    var ch = document.getElementById('nv-popup-soul-check');
    return ch ? ch.checked : false;
  }

  function updateDobVisibility() {
    var wrap = document.getElementById('nv-popup-dob-wrap');
    var btn = document.getElementById('nv-popup-submit');
    if (!wrap) return;
    if (wantsSoul()) {
      wrap.style.display = 'block';
      if (btn) btn.textContent = 'Discover my number';
    } else {
      wrap.style.display = 'none';
      if (btn) btn.textContent = 'Join the list';
    }
  }

  function showPopup() {
    if (triggered) return;
    triggered = true;
    clearTimeout(timer);
    document.getElementById('nv-popup-overlay').classList.add('open');
    document.body.style.overflow = 'hidden';
    window.removeEventListener('scroll', onScroll);
  }

  function hidePopup() {
    document.getElementById('nv-popup-overlay').classList.remove('open');
    document.body.style.overflow = '';
  }

  function dismissPopup(forever) {
    hidePopup();
    if (forever) {
      try { localStorage.setItem(STORAGE_KEY, '1'); } catch (e) {}
    }
  }

  function onScroll() {
    var scrolled = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight);
    if (scrolled >= TRIGGER_SCROLL) showPopup();
  }

  function onOverlayClick(e) {
    if (e.target === document.getElementById('nv-popup-overlay')) dismissPopup(false);
  }

  function onSubmit(e) {
    e.preventDefault();
    var email = document.getElementById('nv-popup-email').value.trim();
    var name = document.getElementById('nv-popup-name').value.trim();
    var btn = document.getElementById('nv-popup-submit');
    var errEl = document.getElementById('nv-popup-error');
    var consent = document.getElementById('nv-popup-consent-check');
    var soul = null;

    errEl.style.display = 'none';

    if (consent && !consent.checked) {
      errEl.textContent = 'Please agree to the terms before signing up.';
      errEl.style.display = 'block';
      return;
    }

    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errEl.textContent = 'Please enter a valid email address.';
      errEl.style.display = 'block';
      return;
    }

    var dob = '';
    if (wantsSoul()) {
      var dobEl = document.getElementById('nv-popup-dob');
      dob = dobEl ? dobEl.value.trim() : '';
      soul = calcSoul(dob);
      if (!soul) {
        errEl.textContent = 'Please select your date of birth.';
        errEl.style.display = 'block';
        return;
      }
    }

    btn.disabled = true;
    btn.textContent = 'Sending...';

    var data = new URLSearchParams({ email_address: email });
    if (name) data.append('fields[first_name]', name);
    if (dob) data.append('fields[date_of_birth]', dob);
    if (soul) data.append('fields[soul_number]', soul);
    data.append('tags[]', '24330689');

    fetch('https://app.convertkit.com/forms/' + FORM_ID + '/subscriptions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: data.toString()
    })
      .then(function (res) {
        if (res.ok || res.status === 200) {
          showSuccess(soul, name);
        } else {
          throw new Error('server error');
        }
      })
      .catch(function () {
        btn.disabled = false;
        btn.textContent = wantsSoul() ? 'Discover my number' : 'Join the list';
        errEl.textContent = 'Something went wrong. Please try again or contact me directly.';
        errEl.style.display = 'block';
      });
  }

  function showSuccess(soul, name) {
    document.getElementById('nv-popup-form').style.display = 'none';
    document.getElementById('nv-popup-sub').style.display = 'none';
    var sEl = document.getElementById('nv-popup-success');
    sEl.style.display = 'block';

    var soulResult = document.getElementById('nv-popup-soul-result');
    var newsletterResult = document.getElementById('nv-popup-newsletter-result');

    if (soul) {
      var numEl = document.getElementById('nv-popup-soul-num');
      var linkEl = document.getElementById('nv-popup-soul-link');
      var linkWrap = document.getElementById('nv-popup-soul-link-wrap');
      if (numEl) numEl.textContent = soul;
      if (PDF_READY) {
        if (linkEl) linkEl.href = 'https://vukojenemanja.com/pdfs/soul-number/Soul_Number_' + soul + '.pdf';
        if (linkWrap) linkWrap.style.display = 'block';
      } else {
        if (linkWrap) linkWrap.style.display = 'none';
      }
      if (soulResult) soulResult.style.display = 'block';
      if (newsletterResult) newsletterResult.style.display = 'none';
    } else {
      if (soulResult) soulResult.style.display = 'none';
      if (newsletterResult) newsletterResult.style.display = 'block';
    }

    try { localStorage.setItem(STORAGE_KEY, '1'); } catch (e) {}
  }

  function init() {
    var overlay = document.getElementById('nv-popup-overlay');
    if (!overlay) return;

    document.getElementById('nv-popup-close').addEventListener('click', function () {
      dismissPopup(false);
    });

    overlay.addEventListener('click', onOverlayClick);
    document.getElementById('nv-popup-form').addEventListener('submit', onSubmit);
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') dismissPopup(false);
    });

    var soulCheck = document.getElementById('nv-popup-soul-check');
    if (soulCheck) {
      soulCheck.addEventListener('change', updateDobVisibility);
      updateDobVisibility();
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    timer = setTimeout(showPopup, TRIGGER_SECONDS * 1000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
