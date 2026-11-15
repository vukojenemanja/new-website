(function () {
  try { if (localStorage.getItem('nv_cookies_ok')) return; } catch(e) {}

  var banner = document.createElement('div');
  banner.id = 'nv-cookie-banner';
  banner.innerHTML =
    'Boravkom na stranici prihvataš korišćenje kolačića za analitiku.' +
    ' <a href="/srb/datenschutz.html">Saznaj više</a>' +
    '<button aria-label="Zatvori">×</button>';

  var style = document.createElement('style');
  style.textContent =
    '#nv-cookie-banner{position:fixed;bottom:0;left:0;right:0;z-index:9999;' +
    'background:var(--bark,#3D2E1E);color:var(--sand,#E8DDD0);' +
    'font-family:"DM Sans",sans-serif;font-size:13px;letter-spacing:0.3px;' +
    'padding:14px 60px 14px 24px;line-height:1.5;border-top:1px solid rgba(196,168,130,0.2);}' +
    '#nv-cookie-banner a{color:var(--clay,#C4A882);text-decoration:underline;margin-left:6px;}' +
    '#nv-cookie-banner a:hover{color:var(--warm,#D4B896);}' +
    '#nv-cookie-banner button{position:absolute;right:20px;top:50%;transform:translateY(-50%);' +
    'background:none;border:none;color:var(--sand,#E8DDD0);font-size:20px;cursor:pointer;' +
    'opacity:0.6;line-height:1;padding:4px 8px;}' +
    '#nv-cookie-banner button:hover{opacity:1;}' +
    '@media(max-width:600px){#nv-cookie-banner{padding:12px 48px 12px 16px;font-size:12px;}}';

  document.head.appendChild(style);
  document.body.appendChild(banner);

  banner.querySelector('button').addEventListener('click', function () {
    try { localStorage.setItem('nv_cookies_ok', '1'); } catch(e) {}
    banner.style.display = 'none';
  });
})();
