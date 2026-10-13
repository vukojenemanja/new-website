// ─── Email popup kit ───────────────────────────────────────────────────────
// ConvertKit form ID: app.convertkit.com/forms/10004467/edit
// ───────────────────────────────────────────────────────────────────────────

(function () {
  var FORM_ID = '10004467';
  var STORAGE_KEY = 'nv_popup_hidden';
  var TRIGGER_SCROLL = 0.50;
  var TRIGGER_SECONDS = 45;
  var TWO_DAYS_MS = 2 * 24 * 60 * 60 * 1000;

  try {
    var stored = localStorage.getItem(STORAGE_KEY);
    if (stored === '1') return;
    if (stored && (Date.now() - parseInt(stored, 10)) < TWO_DAYS_MS) return;
  } catch (e) {}

  var triggered = false;
  var timer = null;

  var lang = (document.documentElement.lang || 'sr').toLowerCase().slice(0, 2);
  var L = lang === 'de' ? {
    btnSoul: 'Seelenzahl entdecken', btnList: 'Anmelden', btnSending: 'Sende...',
    errConsent: 'Bitte akzeptiere die Bedingungen, um dich anzumelden.',
    errEmail: 'Bitte gib eine gültige E-Mail-Adresse ein.',
    errDob: 'Bitte wähle dein Geburtsdatum.',
    errServer: 'Ein Fehler ist aufgetreten. Bitte versuche es erneut oder kontaktiere mich direkt.'
  } : lang === 'en' ? {
    btnSoul: 'Discover my number', btnList: 'Join the list', btnSending: 'Sending...',
    errConsent: 'Please accept the terms before signing up.',
    errEmail: 'Please enter a valid email.',
    errDob: 'Please select your date of birth.',
    errServer: 'Something went wrong. Please try again or contact me directly.'
  } : {
    btnSoul: 'Otkrij broj', btnList: 'Prijavi se na listu', btnSending: 'Saljem...',
    errConsent: 'Potrebno je da prihvatiš uslove pre prijave.',
    errEmail: 'Unesi ispravan email.',
    errDob: 'Izaberi datum rođenja.',
    errServer: 'Došlo je do greške. Pokušaj ponovo ili me kontaktiraj direktno.'
  };

  // ── Soul broj kalkulacija ──────────────────────────────────────────────
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
      var s = 0, tmp = n;
      while (tmp > 0) { s += tmp % 10; tmp = Math.floor(tmp / 10); }
      n = s;
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
      if (btn) btn.textContent = L.btnSoul;
    } else {
      wrap.style.display = 'none';
      if (btn) btn.textContent = L.btnList;
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
    } else {
      try { localStorage.setItem(STORAGE_KEY, String(Date.now())); } catch (e) {}
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
      errEl.textContent = L.errConsent;
      errEl.style.display = 'block';
      return;
    }

    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errEl.textContent = L.errEmail;
      errEl.style.display = 'block';
      return;
    }

    var dob = '';
    if (wantsSoul()) {
      var dobEl = document.getElementById('nv-popup-dob');
      dob = dobEl ? dobEl.value.trim() : '';
      soul = calcSoul(dob);
      if (!soul) {
        errEl.textContent = L.errDob;
        errEl.style.display = 'block';
        return;
      }
    }

    btn.disabled = true;
    btn.textContent = L.btnSending;

    var body = { api_key: 'nEJIDKEJbs0n5gTauo6pjQ', email: email, tags: [24330687] };
    if (name) body.first_name = name;
    var fields = {};
    if (dob) fields.date_of_birth = dob;
    if (soul) fields.soul_number = String(soul);
    if (Object.keys(fields).length) body.fields = fields;

    fetch('https://api.convertkit.com/v3/forms/' + FORM_ID + '/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
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
        btn.textContent = wantsSoul() ? L.btnSoul : L.btnList;
        errEl.textContent = L.errServer;
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
      if (numEl) numEl.textContent = soul;
      var pdfPath = lang === 'de'
        ? 'https://vukojenemanja.com/pdfs/seelenzahl/Seelenzahl_' + soul + '.pdf'
        : lang === 'en'
          ? 'https://vukojenemanja.com/pdfs/soul-number/Soul_Number_' + soul + '.pdf'
          : 'https://vukojenemanja.com/pdfs/broj-duse/Broj_Duse_' + soul + '.pdf';
      if (linkEl) linkEl.href = pdfPath;
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
