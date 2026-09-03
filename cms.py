#!/usr/bin/env python3
"""Unified CMS - svi jezici u jednom alatu."""

import http.server
import json
import re
import subprocess
import webbrowser
from pathlib import Path
from threading import Timer

ROOT = Path(__file__).parent.resolve()
PORT = 3000

LANGUAGES = {
    'srb': 'Srpski',
    'en':  'English',
    'de':  'Deutsch',
}

LANG_PAGES = {
    'srb': ['index', 'individual', 'akal', 'aura'],
    'en':  ['index', 'individual', 'akal'],
    'de':  ['index', 'individual', 'akal'],
}

PAGES = {
    'index':      {'srb': 'Pocetna',         'en': 'Home',            'de': 'Startseite',    'file': '{lang}/index.html'},
    'individual': {'srb': 'Individualni rad', 'en': 'Individual Work', 'de': 'Einzelarbeit',  'file': '{lang}/individual.html'},
    'akal':       {'srb': 'Akal zajednica',   'en': 'Akal Community',  'de': 'Akal Community','file': '{lang}/akal.html'},
    'aura':       {'srb': 'Aura tretman',     'en': '-',               'de': '-',             'file': 'srb/aura-tretman.html'},
}

PAGE_SECTIONS = {
    'index': [
        ('hero',         'Hero'),
        ('pain',         'Bol / Prepoznavanje'),
        ('about',        'O meni'),
        ('offers',       'Ponude'),
        ('testimonials', 'Utisci'),
        ('booking',      'Zakazivanje'),
    ],
    'individual': [
        ('hero',         'Hero'),
        ('recognition',  'Prepoznavanje'),
        ('about',        'O meni'),
        ('method',       'Metoda'),
        ('whyworks',     'Zasto radi'),
        ('offers',       'Sesije i programi'),
        ('testimonials', 'Utisci'),
        ('cta',          'Poziv na akciju'),
    ],
    'akal': [
        ('hero',    'Hero'),
        ('forwho',  'Za koga'),
        ('inside',  'Sta je ukljuceno'),
        ('changes', 'Sta se menja'),
        ('cta',     'Cena i CTA'),
    ],
    'aura': [
        ('hero',         'Hero'),
        ('recognition',  'Prepoznavanje'),
        ('how',          'Tok sesije'),
        ('testimonials', 'Utisci'),
        ('offer',        'Ponuda'),
        ('cta',          'Poziv na akciju'),
    ],
}

SECTION_KEYS = {
    'index:hero':         ['hero_label','hero_h1','hero_sub','hero_btn_primary','hero_btn_ghost'],
    'index:pain':         ['pain_h2','pain_p1','pain_p2','pain_q1','pain_q2','pain_q3','pain_q4','pain_q5','pain_q6','pain_q7'],
    'index:about':        ['about_h2','about_p1','about_p2','about_p3','about_p4'],
    'index:offers':       ['offers_h2','offers_desc',
                           'o1_name','o1_duration','o1_desc','o1_includes','o1_price_was','o1_price','o1_price_note',
                           'o2_name','o2_duration','o2_desc','o2_includes','o2_price','o2_price_note',
                           'o3_name','o3_duration','o3_desc','o3_includes','o3_price','o3_price_note',
                           'o4_name','o4_duration','o4_desc','o4_price',
                           'akal_name','akal_sub','akal_includes','akal_price','akal_period'],
    'index:testimonials': ['testi_h2','t1_text','t1_author','t1_source','t2_text','t2_author','t2_source',
                           't3_text','t3_author','t3_source','t4_text','t4_author','t4_source',
                           't5_text','t5_author','t5_source','t6_text','t6_author','t6_source',
                           't7_text','t7_author','t7_source','t8_text','t8_author','t8_source',
                           't9_text','t9_author','t9_source','t10_text','t10_author','t10_source'],
    'index:booking':      ['booking_h2','booking_p1','booking_p2','entry_title','entry_desc','entry_price','entry_btn'],

    'individual:hero':         ['hero_eyebrow','hero_h1','hero_sub1','hero_sub2','hero_btn_primary','hero_btn_ghost'],
    'individual:recognition':  ['recog_h2','recog_p1','recog_p2','pain_1','pain_2','pain_3','pain_4','pain_5','pain_closing1','pain_closing2'],
    'individual:about':        ['about_h2','about_p1','about_p2','about_p3','about_closing','about_p4'],
    'individual:method':       ['method_h2','method_intro','step1_title','step1_body','step2_title','step2_body',
                                'step3_title','step3_body','step4_title','step4_body','step5_title','step5_body','method_quote'],
    'individual:whyworks':     ['why_h2','why_p1','why_p2','why_p3','why_closing'],
    'individual:offers':       ['offers_h2','offers_sub1','offers_sub2',
                                'o1_name','o1_duration','o1_desc','o1_includes','o1_price_was','o1_price','o1_price_note','o1_cta',
                                'o2_name','o2_duration','o2_desc','o2_includes','o2_price','o2_price_note','o2_cta',
                                'o3_name','o3_duration','o3_desc','o3_includes','o3_price','o3_price_note','o3_cta',
                                'o4_name','o4_duration','o4_desc','o4_includes','o4_price_was','o4_price','o4_price_note','o4_cta'],
    'individual:testimonials': ['testi_h2','t1_text','t1_author','t1_source','t2_text','t2_author','t2_source',
                                't3_text','t3_author','t3_source','t4_text','t4_author','t4_source',
                                't5_text','t5_author','t5_source','t6_text','t6_author','t6_source'],
    'individual:cta':          ['cta_h2','cta_body','cta_btn','cta_note'],

    'akal:hero':    ['hero_label','hero_h1','hero_p'],
    'akal:forwho':  ['forwho_h2','forwho_p','card1_title','card1_text','card2_title','card2_text',
                     'card3_title','card3_text','card4_title','card4_text'],
    'akal:inside':  ['inside_h2','inc1_title','inc1_text','inc2_title','inc2_text','inc3_title','inc3_text'],
    'akal:changes': ['changes_h2','changes_p','changes_list'],
    'akal:cta':     ['testi_text','testi_author','cta_price','cta_period','cta_p1','cta_p2','cta_btn'],

    'aura:hero':         ['hero_label','hero_h1','hero_sub','hero_btn_primary','hero_btn_ghost'],
    'aura:recognition':  ['recog_h2','recog_intro','rec1_title','rec1_text','rec2_title','rec2_text','rec3_title','rec3_text'],
    'aura:how':          ['how_h2','how_intro','step1_title','step1_text','step2_title','step2_text',
                          'step3_title','step3_text','step4_title','step4_text'],
    'aura:testimonials': ['testi_h2','t1_text','t1_author','t1_source','t2_text','t2_author','t2_source','t3_text','t3_author','t3_source'],
    'aura:offer':        ['offer_intro','offer_name','offer_duration','offer_includes','offer_price_was','offer_price','offer_price_note','offer_btn','offer_note'],
    'aura:cta':          ['cta_h2','cta_body','cta_btn','cta_note'],
}

TEXTAREA_KEYS = {
    'hero_h1','recog_h2','about_h2','about_p1','about_p2','about_p3','about_p4',
    'method_h2','method_intro','why_h2','why_p1','why_p2','why_p3','offers_h2',
    'pain_h2','booking_h2','cta_h2','forwho_h2','inside_h2','changes_h2',
    'changes_p','changes_list','testi_text','hero_p','recog_p1','recog_p2',
    'pain_1','pain_2','pain_3','pain_4','pain_5','pain_closing1','pain_closing2',
    'about_closing','step1_body','step2_body','step3_body','step4_body','step5_body',
    'method_quote','offers_sub1','offers_sub2','o1_desc','o1_includes','o2_desc','o2_includes',
    'o3_desc','o3_includes','o4_desc','o4_includes','akal_includes',
    'o1_price_note','o2_price_note','o3_price_note','booking_p1','booking_p2',
    'entry_desc','card1_text','card2_text','card3_text','card4_text',
    'inc1_text','inc2_text','inc3_text','cta_p1','cta_p2','cta_body',
    'recog_intro','rec1_text','rec2_text','rec3_text','how_intro',
    'step1_text','step2_text','step3_text','step4_text',
    'offer_intro','offer_includes','offer_note','t1_text','t2_text','t3_text',
    't4_text','t5_text','t6_text','t7_text','t8_text','t9_text','t10_text',
    'pain_q1','pain_q2','pain_q3','pain_q4','pain_q5','pain_q6','pain_q7',
    'offers_desc','o4_desc',
}

CMS_PATTERN = re.compile(r'<!--CMS:(\w+)-->(.*?)<!--/CMS-->', re.DOTALL)


def get_file_path(lang, page_id):
    tpl = PAGES[page_id]['file']
    return ROOT / tpl.format(lang=lang)


def read_fields(lang, page_id):
    path = get_file_path(lang, page_id)
    content = path.read_text(encoding='utf-8')
    return {k: v.strip() for k, v in CMS_PATTERN.findall(content)}


def write_fields(lang, page_id, new_fields):
    path = get_file_path(lang, page_id)
    content = path.read_text(encoding='utf-8')
    def replace(m):
        key = m.group(1)
        if key not in new_fields:
            return m.group(0)
        val = new_fields[key]
        if key.endswith('_includes') or key in ('changes_list', 'akal_includes'):
            return f'<!--CMS:{key}-->\n{val}\n        <!--/CMS-->'
        return f'<!--CMS:{key}-->{val}<!--/CMS-->'
    path.write_text(CMS_PATTERN.sub(replace, content), encoding='utf-8')


def git_save(lang, page_id):
    rel = PAGES[page_id]['file'].format(lang=lang)
    subprocess.run(['git', 'add', rel], cwd=ROOT, check=True)
    lang_label = LANGUAGES[lang]
    r = subprocess.run(
        ['git', 'commit', '-m', f'CMS: update {lang_label} content'],
        cwd=ROOT, capture_output=True, text=True
    )
    if r.returncode != 0 and 'nothing to commit' not in (r.stdout + r.stderr):
        raise RuntimeError(r.stderr or r.stdout)
    subprocess.run(['git', 'push'], cwd=ROOT, check=True)


def build_js_data():
    lang_pages = json.dumps(LANG_PAGES, ensure_ascii=False)
    languages = json.dumps(LANGUAGES, ensure_ascii=False)
    pages = json.dumps({k: {l: v[l] for l in ['srb','en','de']} for k, v in PAGES.items()}, ensure_ascii=False)
    sections = json.dumps({k: [[s, l] for s, l in v] for k, v in PAGE_SECTIONS.items()}, ensure_ascii=False)
    sec_keys = json.dumps({k: {sec: SECTION_KEYS.get(f'{k}:{sec}', []) for sec, _ in v} for k, v in PAGE_SECTIONS.items()}, ensure_ascii=False)
    textarea = json.dumps(list(TEXTAREA_KEYS), ensure_ascii=False)
    return lang_pages, languages, pages, sections, sec_keys, textarea


_js = build_js_data()

HTML_UI = (r"""<!DOCTYPE html>
<html lang="sr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CMS - Nemanja Vukoje</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg: #1a1410; --sidebar: #120f0c; --card: #211c17;
  --border: rgba(196,168,130,0.12); --clay: #C4A882; --sand: #E8DDD0;
  --stone: #8A8070; --green: #4CAF50; --red: #e57373;
}
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg); color: var(--sand); min-height: 100vh; display: flex; }

.sidebar {
  width: 240px; flex-shrink: 0; background: var(--sidebar);
  border-right: 1px solid var(--border); position: fixed;
  top: 0; left: 0; height: 100vh; overflow-y: auto; display: flex; flex-direction: column;
}
.sidebar-top { padding: 20px 16px 16px; border-bottom: 1px solid var(--border); }
.sidebar-logo { font-size: 15px; font-weight: 700; color: var(--clay); letter-spacing: 0.5px; margin-bottom: 14px; }
.sidebar-logo span { display: block; font-size: 10px; color: var(--stone); font-weight: 400; margin-top: 2px; }

.lang-tabs { display: flex; gap: 6px; margin-bottom: 12px; }
.lang-tab {
  flex: 1; padding: 6px 0; font-size: 12px; font-weight: 600; letter-spacing: 1px;
  text-align: center; border: 1px solid var(--border); border-radius: 5px;
  cursor: pointer; color: var(--stone); background: none; transition: all 0.15s;
}
.lang-tab:hover { color: var(--sand); border-color: rgba(196,168,130,0.3); }
.lang-tab.active { background: var(--clay); color: #1a1410; border-color: var(--clay); }

.page-select {
  width: 100%; background: rgba(0,0,0,0.35); border: 1px solid var(--border);
  color: var(--sand); font-size: 13px; padding: 8px 10px; border-radius: 5px;
  cursor: pointer; appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%238A8070'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 10px center; padding-right: 28px;
}
.page-select:focus { outline: none; border-color: rgba(196,168,130,0.4); }
.page-select option { background: #211c17; }

.sidebar-sections { flex: 1; padding: 8px 0; }
.sidebar-link {
  display: block; padding: 9px 16px; font-size: 13px; color: var(--stone);
  text-decoration: none; cursor: pointer; border: none; background: none;
  width: 100%; text-align: left; transition: all 0.15s;
}
.sidebar-link:hover { color: var(--sand); background: rgba(196,168,130,0.05); }
.sidebar-link.active { color: var(--clay); background: rgba(196,168,130,0.08); border-left: 2px solid var(--clay); }

.sidebar-bottom { padding: 16px; border-top: 1px solid var(--border); }
.sidebar-save {
  width: 100%; padding: 10px; background: var(--clay); color: #1a1410;
  border: none; border-radius: 6px; font-size: 13px; font-weight: 700;
  cursor: pointer; transition: opacity 0.2s;
}
.sidebar-save:hover { opacity: 0.85; }
.sidebar-save:disabled { opacity: 0.45; cursor: not-allowed; }
.save-status { font-size: 11px; text-align: center; margin-top: 8px; min-height: 16px; color: var(--stone); }
.save-status.ok { color: var(--green); }
.save-status.err { color: var(--red); }

.main { margin-left: 240px; flex: 1; padding: 32px 40px; max-width: 900px; }
.section { display: none; }
.section.active { display: block; }
.section-title { font-size: 22px; font-weight: 600; color: var(--sand); margin-bottom: 24px; }

.card { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 24px; margin-bottom: 16px; }
.card-title { font-size: 11px; font-weight: 700; letter-spacing: 2px; color: var(--clay); text-transform: uppercase; margin-bottom: 16px; }

.field { margin-bottom: 18px; }
.field:last-child { margin-bottom: 0; }
.field label { display: block; font-size: 12px; color: var(--stone); margin-bottom: 6px; font-weight: 500; }
.field input, .field textarea {
  width: 100%; background: rgba(0,0,0,0.25); border: 1px solid var(--border);
  border-radius: 6px; color: var(--sand); font-size: 14px; padding: 10px 12px;
  font-family: inherit; transition: border-color 0.2s; resize: vertical;
}
.field input:focus, .field textarea:focus { outline: none; border-color: rgba(196,168,130,0.4); }
.field textarea { line-height: 1.6; }

.offer-block { border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin-bottom: 16px; }
.offer-block-title { font-size: 13px; font-weight: 600; color: var(--clay); margin-bottom: 16px; padding-bottom: 10px; border-bottom: 1px solid var(--border); }

.empty-state { text-align: center; padding: 80px 20px; color: var(--stone); font-size: 14px; }
</style>
</head>
<body>

<aside class="sidebar">
  <div class="sidebar-top">
    <div class="sidebar-logo">CMS<span>vukojenemanja.com</span></div>
    <div class="lang-tabs" id="langTabs"></div>
    <select class="page-select" id="pageSelect" onchange="changePage(this.value)">
      <option value="">-- Izaberi stranicu --</option>
    </select>
  </div>
  <div class="sidebar-sections" id="sidebarSections"></div>
  <div class="sidebar-bottom">
    <button class="sidebar-save" id="saveBtn" onclick="saveAll()" disabled>Sacuvaj i objavi</button>
    <div class="save-status" id="saveStatus"></div>
  </div>
</aside>

<main class="main" id="mainContent">
  <div class="empty-state">
    <div style="font-size:32px;margin-bottom:16px;">&#8593;</div>
    Izaberi jezik i stranicu
  </div>
</main>

<script>
const LANG_PAGES = """ + _js[0] + r""";
const LANGUAGES = """ + _js[1] + r""";
const PAGES = """ + _js[2] + r""";
const PAGE_SECTIONS = """ + _js[3] + r""";
const SECTION_KEYS = """ + _js[4] + r""";
const TEXTAREA_KEYS = new Set(""" + _js[5] + r""");

let currentLang = 'srb';
let currentPage = '';
let allData = {};

// Build lang tabs
Object.entries(LANGUAGES).forEach(([id, label]) => {
  const btn = document.createElement('button');
  btn.className = 'lang-tab' + (id === 'srb' ? ' active' : '');
  btn.textContent = label;
  btn.onclick = () => changeLang(id);
  document.getElementById('langTabs').appendChild(btn);
});

function changeLang(lang) {
  currentLang = lang;
  currentPage = '';
  allData = {};
  document.querySelectorAll('.lang-tab').forEach((b, i) => {
    b.classList.toggle('active', Object.keys(LANGUAGES)[i] === lang);
  });
  rebuildPageSelect();
  document.getElementById('sidebarSections').innerHTML = '';
  document.getElementById('saveBtn').disabled = true;
  document.getElementById('saveStatus').textContent = '';
  document.getElementById('mainContent').innerHTML = '<div class="empty-state"><div style="font-size:32px;margin-bottom:16px;">&#8593;</div>Izaberi stranicu</div>';
}

function rebuildPageSelect() {
  const sel = document.getElementById('pageSelect');
  sel.innerHTML = '<option value="">-- Izaberi stranicu --</option>';
  LANG_PAGES[currentLang].forEach(pageId => {
    const opt = document.createElement('option');
    opt.value = pageId;
    opt.textContent = PAGES[pageId][currentLang];
    sel.appendChild(opt);
  });
}

function changePage(pageId) {
  currentPage = pageId;
  allData = {};
  document.getElementById('saveBtn').disabled = !pageId;
  document.getElementById('saveStatus').textContent = '';
  document.getElementById('saveStatus').className = 'save-status';
  renderSidebar();
  if (!pageId) {
    document.getElementById('mainContent').innerHTML = '<div class="empty-state"><div style="font-size:32px;margin-bottom:16px;">&#8593;</div>Izaberi stranicu</div>';
    return;
  }
  loadData();
}

function renderSidebar() {
  const el = document.getElementById('sidebarSections');
  if (!currentPage) { el.innerHTML = ''; return; }
  el.innerHTML = PAGE_SECTIONS[currentPage].map(([secId, label]) =>
    `<button class="sidebar-link" data-sec="${secId}" onclick="showSection('${secId}')">${label}</button>`
  ).join('');
}

function loadData() {
  document.getElementById('mainContent').innerHTML = '<div class="empty-state">Ucitavanje...</div>';
  fetch(`/api/data?lang=${currentLang}&page=${currentPage}`)
    .then(r => r.json())
    .then(data => {
      allData = data;
      renderAllSections();
      showSection(PAGE_SECTIONS[currentPage][0][0]);
    })
    .catch(() => setStatus('Greska pri ucitavanju', 'err'));
}

function renderAllSections() {
  const main = document.getElementById('mainContent');
  main.innerHTML = PAGE_SECTIONS[currentPage].map(([secId, label]) =>
    `<div class="section" id="sec-${secId}">` + renderSection(currentPage, secId, label) + '</div>'
  ).join('');
}

function renderSection(pageId, secId, label) {
  const keys = (SECTION_KEYS[pageId] && SECTION_KEYS[pageId][secId]) || [];
  let html = `<div class="section-title">${label}</div>`;
  if (!keys.length) return html + '<p style="color:var(--stone);font-size:13px">Nema polja.</p>';

  if (secId === 'offers') {
    const introKeys = keys.filter(k => !k.match(/^o[1-4]_/) && !k.match(/^akal_/));
    const o1 = keys.filter(k => k.startsWith('o1_'));
    const o2 = keys.filter(k => k.startsWith('o2_'));
    const o3 = keys.filter(k => k.startsWith('o3_'));
    const o4 = keys.filter(k => k.startsWith('o4_'));
    const akal = keys.filter(k => k.startsWith('akal_'));
    if (introKeys.length) html += '<div class="card"><div class="card-title">Uvod</div>' + introKeys.map(fieldHtml).join('') + '</div>';
    if (o1.length) html += offerBlock('1', o1);
    if (o2.length) html += offerBlock('2', o2);
    if (o3.length) html += offerBlock('3', o3);
    if (o4.length) html += offerBlock('4', o4);
    if (akal.length) html += '<div class="offer-block"><div class="offer-block-title">Akal zajednica</div>' + akal.map(fieldHtml).join('') + '</div>';
    return html;
  }

  if (secId === 'testimonials') {
    const h2 = keys.filter(k => k === 'testi_h2');
    const rest = keys.filter(k => k !== 'testi_h2');
    if (h2.length) html += '<div class="card">' + h2.map(fieldHtml).join('') + '</div>';
    const nums = [...new Set(rest.map(k => k.match(/^t(\d+)_/)?.[1]).filter(Boolean))];
    nums.forEach(n => {
      const tg = rest.filter(k => k.startsWith('t' + n + '_'));
      html += `<div class="offer-block"><div class="offer-block-title">Utisak ${n}</div>` + tg.map(fieldHtml).join('') + '</div>';
    });
    return html;
  }

  html += '<div class="card">' + keys.map(fieldHtml).join('') + '</div>';
  return html;
}

function offerBlock(num, keys) {
  const names = { '1': 'Aura / Ponuda 1', '2': 'Ponuda 2', '3': 'Ponuda 3', '4': 'Ponuda 4 (Transform)' };
  return `<div class="offer-block"><div class="offer-block-title">${names[num] || 'Ponuda ' + num}</div>` + keys.map(fieldHtml).join('') + '</div>';
}

function fieldHtml(key) {
  const val = (allData[key] || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  if (TEXTAREA_KEYS.has(key)) {
    const rows = val.length > 200 ? 6 : val.split('\n').length > 3 ? 5 : 3;
    return `<div class="field"><label>${key}</label><textarea data-key="${key}" rows="${rows}">${val}</textarea></div>`;
  }
  return `<div class="field"><label>${key}</label><input type="text" data-key="${key}" value="${val}"></div>`;
}

function showSection(secId) {
  document.querySelectorAll('[data-key]').forEach(el => { allData[el.dataset.key] = el.value; });
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
  const sec = document.getElementById('sec-' + secId);
  if (sec) {
    sec.classList.add('active');
    sec.querySelectorAll('[data-key]').forEach(el => {
      if (allData[el.dataset.key] !== undefined) el.value = allData[el.dataset.key];
    });
  }
  document.querySelectorAll(`[data-sec="${secId}"]`).forEach(l => l.classList.add('active'));
}

function saveAll() {
  document.querySelectorAll('[data-key]').forEach(el => { allData[el.dataset.key] = el.value; });
  const btn = document.getElementById('saveBtn');
  btn.disabled = true; btn.textContent = 'Cuvam...';
  setStatus('', '');
  fetch(`/api/save?lang=${currentLang}&page=${currentPage}`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(allData)
  })
  .then(r => r.json())
  .then(res => {
    if (res.ok) setStatus('Sacuvano i objavljeno!', 'ok');
    else setStatus('Greska: ' + (res.error || 'nepoznata'), 'err');
  })
  .catch(e => setStatus('Greska: ' + e.message, 'err'))
  .finally(() => { btn.disabled = false; btn.textContent = 'Sacuvaj i objavi'; });
}

function setStatus(msg, cls) {
  const el = document.getElementById('saveStatus');
  el.textContent = msg;
  el.className = 'save-status' + (cls ? ' ' + cls : '');
}

rebuildPageSelect();
</script>
</body>
</html>""")


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        if parsed.path == '/api/data':
            params = parse_qs(parsed.query)
            lang = params.get('lang', ['srb'])[0]
            page_id = params.get('page', [''])[0]
            if lang not in LANGUAGES or page_id not in PAGES:
                self._json({})
            else:
                self._json(read_fields(lang, page_id))
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_UI.encode('utf-8'))

    def do_POST(self):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        if parsed.path == '/api/save':
            params = parse_qs(parsed.query)
            lang = params.get('lang', ['srb'])[0]
            page_id = params.get('page', [''])[0]
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                fields = json.loads(body)
                write_fields(lang, page_id, fields)
                git_save(lang, page_id)
                self._json({'ok': True})
            except Exception as e:
                self._json({'ok': False, 'error': str(e)})

    def _json(self, data):
        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(payload))
        self.end_headers()
        self.wfile.write(payload)


if __name__ == '__main__':
    server = http.server.HTTPServer(('localhost', PORT), Handler)
    print(f'CMS -> http://localhost:{PORT}')
    Timer(0.8, lambda: webbrowser.open(f'http://localhost:{PORT}')).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nZatvoren.')
