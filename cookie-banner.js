(function () {
  var CLARITY_ID = 'ze0v1a5lx7';
  var KEY = 'nv_cookie_consent';

  function loadClarity() {
    if (window._clarityLoaded) return;
    window._clarityLoaded = true;
    (function(c,l,a,r,i,t,y){
      c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
      t=l.createElement(r);t.async=1;t.src='https://www.clarity.ms/tag/'+i;
      y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    })(window,document,'clarity','script',CLARITY_ID);
  }

  var consent;
  try { consent = localStorage.getItem(KEY); } catch(e) {}

  if (consent === 'accepted') { loadClarity(); return; }
  if (consent === 'rejected') { return; }

  var style = document.createElement('style');
  style.textContent =
    '#nv-cb{position:fixed;bottom:0;left:0;right:0;z-index:9999;' +
    'background:var(--bark,#3D2E1E);border-top:1px solid rgba(196,168,130,0.2);padding:20px 24px;}' +
    '#nv-cb-inner{max-width:900px;margin:0 auto;display:flex;align-items:center;gap:24px;flex-wrap:wrap;}' +
    '#nv-cb-text{flex:1;min-width:200px;font-size:13px;line-height:1.6;font-family:"DM Sans",sans-serif;' +
    'color:rgba(232,221,208,0.8);}' +
    '#nv-cb-text a{color:var(--clay,#C4A882);text-decoration:underline;}' +
    '#nv-cb-text a:hover{color:var(--warm,#D4B896);}' +
    '#nv-cb-actions{display:flex;gap:10px;flex-shrink:0;}' +
    '#nv-cb-accept{padding:10px 24px;background:var(--clay,#C4A882);color:var(--bark,#3D2E1E);' +
    'border:none;cursor:pointer;font-family:"DM Sans",sans-serif;font-size:12px;' +
    'letter-spacing:1.5px;text-transform:uppercase;font-weight:500;transition:background 0.2s;}' +
    '#nv-cb-accept:hover{background:var(--warm,#D4B896);}' +
    '#nv-cb-reject{padding:10px 24px;background:transparent;' +
    'color:rgba(232,221,208,0.45);border:1px solid rgba(232,221,208,0.2);cursor:pointer;' +
    'font-family:"DM Sans",sans-serif;font-size:12px;letter-spacing:1.5px;text-transform:uppercase;' +
    'transition:color 0.2s,border-color 0.2s;}' +
    '#nv-cb-reject:hover{color:rgba(232,221,208,0.75);border-color:rgba(232,221,208,0.4);}' +
    '@media(max-width:600px){#nv-cb-inner{flex-direction:column;gap:14px;}' +
    '#nv-cb-actions{width:100%;}#nv-cb-accept,#nv-cb-reject{flex:1;text-align:center;}}';

  var banner = document.createElement('div');
  banner.id = 'nv-cb';
  banner.innerHTML =
    '<div id="nv-cb-inner">' +
      '<div id="nv-cb-text">Koristimo kolačiće za analitiku kako bismo razumeli kako koristiš sajt i poboljšali iskustvo.' +
      ' <a href="/srb/datenschutz.html">Politika privatnosti</a></div>' +
      '<div id="nv-cb-actions">' +
        '<button id="nv-cb-accept">Prihvatam</button>' +
        '<button id="nv-cb-reject">Odbijam</button>' +
      '</div>' +
    '</div>';

  document.head.appendChild(style);
  document.body.appendChild(banner);

  document.getElementById('nv-cb-accept').addEventListener('click', function () {
    try { localStorage.setItem(KEY, 'accepted'); } catch(e) {}
    loadClarity();
    banner.style.display = 'none';
  });

  document.getElementById('nv-cb-reject').addEventListener('click', function () {
    try { localStorage.setItem(KEY, 'rejected'); } catch(e) {}
    banner.style.display = 'none';
  });
})();
