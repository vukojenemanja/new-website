// ─── Email popup kit ───────────────────────────────────────────────────────
// ConvertKit form ID: zameni YOUR_FORM_ID sa pravim ID-jem tvog forma
// Nas ConvertKit form URL: https://app.convertkit.com/forms/YOUR_FORM_ID/subscriptions
// ───────────────────────────────────────────────────────────────────────────

(function () {
  var FORM_ID = 'YOUR_FORM_ID';         // <-- ovde stavi svoj ConvertKit Form ID
  var STORAGE_KEY = 'nv_popup_hidden';
  var TRIGGER_SCROLL = 0.50;            // 50% stranice
  var TRIGGER_SECONDS = 45;             // 45 sekundi

  // Ne pokazuj ako je vec odradjen
  try {
    if (localStorage.getItem(STORAGE_KEY)) return;
  } catch (e) {}

  var triggered = false;
  var timer = null;

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
    var form = document.getElementById('nv-popup-form');
    var email = document.getElementById('nv-popup-email').value.trim();
    var name = document.getElementById('nv-popup-name').value.trim();
    var btn = document.getElementById('nv-popup-submit');
    var errEl = document.getElementById('nv-popup-error');

    errEl.style.display = 'none';

    var consent = document.getElementById('nv-popup-consent-check');
    if (consent && !consent.checked) {
      errEl.textContent = 'Potrebno je da prihvatis uslove pre prijave.';
      errEl.style.display = 'block';
      return;
    }

    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errEl.textContent = 'Unesi ispravan email.';
      errEl.style.display = 'block';
      return;
    }

    if (FORM_ID === 'YOUR_FORM_ID') {
      // Dev mode: pokazi success bez slanja
      showSuccess();
      return;
    }

    btn.disabled = true;
    btn.textContent = 'Saljem...';

    var data = new URLSearchParams({ email_address: email });
    if (name) data.append('fields[first_name]', name);

    fetch('https://app.convertkit.com/forms/' + FORM_ID + '/subscriptions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: data.toString()
    })
      .then(function (res) {
        if (res.ok || res.status === 200) {
          showSuccess();
        } else {
          throw new Error('server error');
        }
      })
      .catch(function () {
        btn.disabled = false;
        btn.textContent = 'Prijavi se';
        errEl.textContent = 'Doslo je do greske. Pokusaj ponovo ili me kontaktiraj direktno.';
        errEl.style.display = 'block';
      });
  }

  function showSuccess() {
    document.getElementById('nv-popup-form').style.display = 'none';
    document.getElementById('nv-popup-sub').style.display = 'none';
    document.getElementById('nv-popup-success').style.display = 'block';
    try { localStorage.setItem(STORAGE_KEY, '1'); } catch (e) {}
    setTimeout(function () { dismissPopup(true); }, 3500);
  }

  // Init kad se DOM ucita
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

    window.addEventListener('scroll', onScroll, { passive: true });
    timer = setTimeout(showPopup, TRIGGER_SECONDS * 1000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
