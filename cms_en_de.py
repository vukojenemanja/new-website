#!/usr/bin/env python3
"""EN/DE CMS - edits English and German pages."""

import http.server
import json
import re
import subprocess
import webbrowser
from pathlib import Path
from threading import Timer

ROOT = Path(__file__).parent.resolve()
PORT = 3002

LANGUAGES = {
    'en': 'English',
    'de': 'Deutsch',
}

PAGES = {
    'index':      {'label': 'Home / Startseite',    'file': '{lang}/index.html'},
    'individual': {'label': 'Individual / Einzelarbeit', 'file': '{lang}/individual.html'},
    'akal':       {'label': 'Akal Community',        'file': '{lang}/akal.html'},
}

PAGE_SECTIONS = {
    'index': [
        ('hero',         'Hero'),
        ('pain',         'Pain / Recognition'),
        ('about',        'About'),
        ('offers',       'Offers'),
        ('testimonials', 'Testimonials'),
        ('booking',      'Booking'),
    ],
    'individual': [
        ('hero',         'Hero'),
        ('recognition',  'Recognition'),
        ('about',        'About'),
        ('method',       'Method'),
        ('whyworks',     'Why it works'),
        ('offers',       'Sessions & Packages'),
        ('testimonials', 'Testimonials'),
        ('cta',          'Call to Action'),
    ],
    'akal': [
        ('hero',    'Hero'),
        ('forwho',  'Who is this for'),
        ('inside',  'What\'s included'),
        ('changes', 'What shifts'),
        ('cta',     'Price & CTA'),
    ],
}

SECTION_KEYS = {
    # index.html
    'index:hero':         ['hero_label','hero_h1','hero_sub','hero_btn_primary','hero_btn_ghost'],
    'index:pain':         ['pain_h2','pain_p1','pain_p2','pain_q1','pain_q2','pain_q3','pain_q4','pain_q5','pain_q6','pain_q7'],
    'index:about':        ['about_h2','about_p1','about_p2','about_p3','about_p4'],
    'index:offers':       ['offers_h2','offers_desc',
                           'o1_name','o1_duration','o1_desc','o1_includes','o1_price_was','o1_price','o1_price_note',
                           'o2_name','o2_duration','o2_desc','o2_includes','o2_price','o2_price_note',
                           'o3_name','o3_duration','o3_desc','o3_includes','o3_price','o3_price_note',
                           'o4_name','o4_duration','o4_desc','o4_price_was','o4_price',
                           'akal_name','akal_sub','akal_includes','akal_price','akal_period'],
    'index:testimonials': ['testi_h2','t1_text','t1_author','t1_source','t2_text','t2_author','t2_source',
                           't3_text','t3_author','t3_source','t4_text','t4_author','t4_source',
                           't5_text','t5_author','t5_source','t6_text','t6_author','t6_source',
                           't7_text','t7_author','t7_source','t8_text','t8_author','t8_source',
                           't9_text','t9_author','t9_source','t10_text','t10_author','t10_source'],
    'index:booking':      ['booking_h2','booking_p1','booking_p2','entry_title','entry_desc','entry_price','entry_btn'],

    # individual.html
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

    # akal.html
    'akal:hero':    ['hero_label','hero_h1','hero_p'],
    'akal:forwho':  ['forwho_h2','forwho_p','card1_title','card1_text','card2_title','card2_text',
                     'card3_title','card3_text','card4_title','card4_text'],
    'akal:inside':  ['inside_h2','inc1_title','inc1_text','inc2_title','inc2_text','inc3_title','inc3_text'],
    'akal:changes': ['changes_h2','changes_p','changes_list'],
    'akal:cta':     ['testi_text','testi_author','cta_price','cta_period','cta_p1','cta_p2','cta_btn'],
}

FIELD_LABELS = {
    # hero
    'hero_label': 'Label (small top text)', 'hero_h1': 'Heading (HTML allowed)',
    'hero_sub': 'Subheading', 'hero_sub1': 'Subheading 1', 'hero_sub2': 'Subheading 2 (italic)',
    'hero_btn_primary': 'Button - primary', 'hero_btn_ghost': 'Button - secondary',
    'hero_eyebrow': 'Eyebrow (top text)', 'hero_p': 'Paragraph',
    # index pain
    'pain_h2': 'Heading', 'pain_p1': 'Paragraph 1', 'pain_p2': 'Paragraph 2',
    'pain_q1': 'Quote 1', 'pain_q2': 'Quote 2', 'pain_q3': 'Quote 3', 'pain_q4': 'Quote 4',
    'pain_q5': 'Quote 5', 'pain_q6': 'Quote 6', 'pain_q7': 'Quote 7',
    # about
    'about_h2': 'Heading', 'about_p1': 'Paragraph 1', 'about_p2': 'Paragraph 2',
    'about_p3': 'Paragraph 3', 'about_p4': 'Paragraph 4', 'about_closing': 'Closing sentence',
    # offers
    'offers_h2': 'Heading', 'offers_desc': 'Description', 'offers_sub1': 'Description 1', 'offers_sub2': 'Description 2 (italic)',
    'akal_name': 'Community name', 'akal_sub': 'Subtitle', 'akal_includes': 'Includes (HTML li items)',
    'akal_price': 'Price', 'akal_period': 'Period',
    'testi_h2': 'Section heading', 'booking_h2': 'Heading',
    'booking_p1': 'Paragraph 1', 'booking_p2': 'Paragraph 2',
    'entry_title': 'Offer title', 'entry_desc': 'Description', 'entry_price': 'Price', 'entry_btn': 'Button',
    # individual recognition
    'recog_h2': 'Heading', 'recog_p1': 'Paragraph 1', 'recog_p2': 'Paragraph 2',
    'pain_1': 'Point 1', 'pain_2': 'Point 2', 'pain_3': 'Point 3', 'pain_4': 'Point 4', 'pain_5': 'Point 5',
    'pain_closing1': 'Closing 1', 'pain_closing2': 'Closing 2',
    # method
    'method_h2': 'Heading', 'method_intro': 'Intro', 'method_quote': 'Quote',
    'step1_title': 'Step 01 - Title', 'step1_body': 'Step 01 - Text',
    'step2_title': 'Step 02 - Title', 'step2_body': 'Step 02 - Text',
    'step3_title': 'Step 03 - Title', 'step3_body': 'Step 03 - Text',
    'step4_title': 'Step 04 - Title', 'step4_body': 'Step 04 - Text',
    'step5_title': 'Step 05 - Title', 'step5_body': 'Step 05 - Text',
    # why works
    'why_h2': 'Heading', 'why_p1': 'Paragraph 1', 'why_p2': 'Paragraph 2',
    'why_p3': 'Paragraph 3', 'why_closing': 'Closing',
    # cta
    'cta_h2': 'Heading', 'cta_body': 'Text', 'cta_btn': 'Button', 'cta_note': 'Note',
    'cta_price': 'Price', 'cta_period': 'Period', 'cta_p1': 'Paragraph 1', 'cta_p2': 'Paragraph 2',
    # akal
    'forwho_h2': 'Heading', 'forwho_p': 'Paragraph',
    'card1_title': 'Card 1 - Title', 'card1_text': 'Card 1 - Text',
    'card2_title': 'Card 2 - Title', 'card2_text': 'Card 2 - Text',
    'card3_title': 'Card 3 - Title', 'card3_text': 'Card 3 - Text',
    'card4_title': 'Card 4 - Title', 'card4_text': 'Card 4 - Text',
    'inside_h2': 'Heading',
    'inc1_title': 'Item 1 - Title', 'inc1_text': 'Item 1 - Text',
    'inc2_title': 'Item 2 - Title', 'inc2_text': 'Item 2 - Text',
    'inc3_title': 'Item 3 - Title', 'inc3_text': 'Item 3 - Text',
    'changes_h2': 'Heading', 'changes_p': 'Paragraph', 'changes_list': 'List (HTML li items)',
    'testi_text': 'Testimonial text', 'testi_author': 'Author',
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
    't1_text','t2_text','t3_text','t4_text','t5_text','t6_text',
    't7_text','t8_text','t9_text','t10_text',
    'pain_q1','pain_q2','pain_q3','pain_q4','pain_q5','pain_q6','pain_q7',
    'offers_desc','o4_desc',
}

CMS_PATTERN = re.compile(r'<!--CMS:(\w+)-->(.*?)<!--/CMS-->', re.DOTALL)


def get_file_path(lang, page_id):
    return ROOT / PAGES[page_id]['file'].format(lang=lang)


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
    r = subprocess.run(
        ['git', 'commit', '-m', 'CMS: update EN/DE content'],
        cwd=ROOT, capture_output=True, text=True
    )
    if r.returncode != 0 and 'nothing to commit' not in (r.stdout + r.stderr):
        raise RuntimeError(r.stderr or r.stdout)
    subprocess.run(['git', 'push'], cwd=ROOT, check=True)


def build_sections_js():
    data = {}
    for page_id, sections in PAGE_SECTIONS.items():
        data[page_id] = {}
        for sec_id, _ in sections:
            key = f'{page_id}:{sec_id}'
            data[page_id][sec_id] = SECTION_KEYS.get(key, [])
    return json.dumps(data, ensure_ascii=False)


def build_labels_js():
    return json.dumps(FIELD_LABELS, ensure_ascii=False)


def build_textarea_js():
    return json.dumps(list(TEXTAREA_KEYS), ensure_ascii=False)


def build_pages_js():
    pages = {k: v['label'] for k, v in PAGES.items()}
    return json.dumps(pages, ensure_ascii=False)


def build_page_sections_js():
    data = {k: [[s, l] for s, l in v] for k, v in PAGE_SECTIONS.items()}
    return json.dumps(data, ensure_ascii=False)


def build_languages_js():
    return json.dumps(LANGUAGES, ensure_ascii=False)


HTML_UI = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CMS - English / Deutsch</title>
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
  width: 230px; flex-shrink: 0; background: var(--sidebar);
  border-right: 1px solid var(--border); position: fixed;
  top: 0; left: 0; height: 100vh; overflow-y: auto; display: flex; flex-direction: column;
}
.sidebar-top { padding: 20px 16px 16px; border-bottom: 1px solid var(--border); }
.sidebar-logo { font-size: 14px; font-weight: 700; color: var(--clay); letter-spacing: 0.5px; margin-bottom: 12px; }
.sidebar-logo span { display: block; font-size: 10px; color: var(--stone); font-weight: 400; margin-top: 2px; }

.lang-select, .page-select {
  width: 100%; background: rgba(0,0,0,0.35); border: 1px solid var(--border);
  color: var(--sand); font-size: 13px; padding: 8px 10px; border-radius: 5px;
  cursor: pointer; appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%238A8070'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 10px center;
  padding-right: 28px; margin-bottom: 8px;
}
.lang-select:focus, .page-select:focus { outline: none; border-color: rgba(196,168,130,0.4); }
.lang-select option, .page-select option { background: #211c17; }

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

.main { margin-left: 230px; flex: 1; padding: 32px 40px; max-width: 900px; }
.section { display: none; }
.section.active { display: block; }
.section-title { font-size: 22px; font-weight: 600; color: var(--sand); margin-bottom: 6px; }
.section-desc { font-size: 13px; color: var(--stone); margin-bottom: 28px; }

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
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.three-col { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }

.offer-block { border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin-bottom: 16px; }
.offer-block-title { font-size: 13px; font-weight: 600; color: var(--clay); margin-bottom: 16px; padding-bottom: 10px; border-bottom: 1px solid var(--border); }

.lang-badge { display: inline-block; font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;
  background: rgba(196,168,130,0.15); color: var(--clay); border-radius: 4px; padding: 3px 8px; margin-left: 8px; }

.empty-state { text-align: center; padding: 80px 20px; color: var(--stone); font-size: 14px; }
</style>
</head>
<body>

<aside class="sidebar">
  <div class="sidebar-top">
    <div class="sidebar-logo">CMS EN / DE<span>Select language and page:</span></div>
    <select class="lang-select" id="langSelect" onchange="changeLang(this.value)">
      <option value="">-- Language --</option>
    </select>
    <select class="page-select" id="pageSelect" onchange="changePage(this.value)">
      <option value="">-- Page --</option>
    </select>
  </div>
  <div class="sidebar-sections" id="sidebarSections"></div>
  <div class="sidebar-bottom">
    <button class="sidebar-save" id="saveBtn" onclick="saveAll()" disabled>Save &amp; publish</button>
    <div class="save-status" id="saveStatus"></div>
  </div>
</aside>

<main class="main" id="mainContent">
  <div class="empty-state">
    <div style="font-size:32px;margin-bottom:16px;">↑</div>
    Select language and page from the dropdowns
  </div>
</main>

<script>
const PAGES = """ + build_pages_js() + r""";
const PAGE_SECTIONS = """ + build_page_sections_js() + r""";
const SECTION_KEYS = """ + build_sections_js() + r""";
const FIELD_LABELS = """ + build_labels_js() + r""";
const TEXTAREA_KEYS = new Set(""" + build_textarea_js() + r""");
const LANGUAGES = """ + build_languages_js() + r""";

let currentLang = '';
let currentPage = '';
let currentSection = '';
let allData = {};

// Init language selector
Object.entries(LANGUAGES).forEach(([id, label]) => {
  const opt = document.createElement('option');
  opt.value = id; opt.textContent = label;
  document.getElementById('langSelect').appendChild(opt);
});

// Init page selector
Object.entries(PAGES).forEach(([id, label]) => {
  const opt = document.createElement('option');
  opt.value = id; opt.textContent = label;
  document.getElementById('pageSelect').appendChild(opt);
});

function changeLang(lang) {
  currentLang = lang;
  if (currentPage && currentLang) {
    loadData();
  } else {
    showEmptyState();
  }
}

function changePage(pageId) {
  currentPage = pageId;
  allData = {};
  document.getElementById('saveBtn').disabled = !pageId || !currentLang;
  document.getElementById('saveStatus').textContent = '';
  document.getElementById('saveStatus').className = 'save-status';
  renderSidebar();
  if (!pageId || !currentLang) {
    showEmptyState();
    return;
  }
  loadData();
}

function showEmptyState() {
  document.getElementById('mainContent').innerHTML = '<div class="empty-state"><div style="font-size:32px;margin-bottom:16px;">↑</div>Select language and page from the dropdowns</div>';
  document.getElementById('sidebarSections').innerHTML = '';
  document.getElementById('saveBtn').disabled = true;
}

function renderSidebar() {
  const el = document.getElementById('sidebarSections');
  if (!currentPage) { el.innerHTML = ''; return; }
  const langLabel = LANGUAGES[currentLang] || '';
  el.innerHTML = PAGE_SECTIONS[currentPage].map(([secId, label]) =>
    `<button class="sidebar-link" data-sec="${secId}" onclick="showSection('${secId}')">${label}</button>`
  ).join('');
}

function loadData() {
  document.getElementById('mainContent').innerHTML = '<div class="empty-state">Loading...</div>';
  document.getElementById('saveBtn').disabled = true;
  fetch('/api/data?lang=' + currentLang + '&page=' + currentPage)
    .then(r => r.json())
    .then(data => {
      allData = data;
      renderSidebar();
      renderAllSections();
      const firstSec = PAGE_SECTIONS[currentPage][0][0];
      showSection(firstSec);
      document.getElementById('saveBtn').disabled = false;
    })
    .catch(() => setStatus('Error loading data', 'err'));
}

function renderAllSections() {
  const sections = PAGE_SECTIONS[currentPage];
  const langLabel = LANGUAGES[currentLang] || currentLang.toUpperCase();
  const main = document.getElementById('mainContent');
  main.innerHTML = `<div style="margin-bottom:24px;font-size:12px;color:var(--stone)">Editing: <strong style="color:var(--clay)">${PAGES[currentPage]}</strong> <span class="lang-badge">${langLabel}</span></div>` +
    sections.map(([secId, label]) =>
      `<div class="section" id="sec-${secId}">` + renderSection(currentPage, secId, label) + '</div>'
    ).join('');
}

function renderSection(pageId, secId, label) {
  const keys = SECTION_KEYS[pageId][secId] || [];
  if (!keys.length) return `<div class="section-title">${label}</div><p style="color:var(--stone);font-size:13px">No fields for this section.</p>`;

  let html = `<div class="section-title">${label}</div>`;

  if (secId === 'offers' && (pageId === 'individual' || pageId === 'index')) {
    const introKeys = keys.filter(k => !k.match(/^o[1-4]_/) && !k.match(/^akal_/));
    const o1 = keys.filter(k => k.startsWith('o1_'));
    const o2 = keys.filter(k => k.startsWith('o2_'));
    const o3 = keys.filter(k => k.startsWith('o3_'));
    const o4 = keys.filter(k => k.startsWith('o4_'));
    const akal = keys.filter(k => k.startsWith('akal_'));

    if (introKeys.length) html += '<div class="card"><div class="card-title">Intro</div>' + introKeys.map(k => fieldHtml(k)).join('') + '</div>';
    if (o1.length) html += offerBlock('1', o1);
    if (o2.length) html += offerBlock('2', o2);
    if (o3.length) html += offerBlock('3', o3);
    if (o4.length) html += offerBlock('4', o4);
    if (akal.length) html += '<div class="offer-block"><div class="offer-block-title">Akal Community</div>' + akal.map(k => fieldHtml(k)).join('') + '</div>';
    return html;
  }

  if (secId === 'testimonials') {
    const h2keys = keys.filter(k => k === 'testi_h2');
    const tkeys = keys.filter(k => k !== 'testi_h2');
    if (h2keys.length) html += '<div class="card">' + h2keys.map(k => fieldHtml(k)).join('') + '</div>';
    const nums = [...new Set(tkeys.map(k => k.match(/^t(\d+)_/)?.[1]).filter(Boolean))];
    nums.forEach(n => {
      const tg = tkeys.filter(k => k.startsWith('t' + n + '_'));
      html += `<div class="offer-block"><div class="offer-block-title">Testimonial ${n}</div>` + tg.map(k => fieldHtml(k)).join('') + '</div>';
    });
    return html;
  }

  html += '<div class="card">' + keys.map(k => fieldHtml(k)).join('') + '</div>';
  return html;
}

function offerBlock(num, keys) {
  const names = { '1': 'Aura Treatment / Offer 1', '2': 'Offer 2', '3': 'Offer 3', '4': 'Offer 4 (Transform)' };
  return `<div class="offer-block"><div class="offer-block-title">${names[num] || 'Offer ' + num}</div>` + keys.map(k => fieldHtml(k)).join('') + '</div>';
}

function fieldHtml(key) {
  const label = FIELD_LABELS[key] || key;
  const val = (allData[key] || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  if (TEXTAREA_KEYS.has(key)) {
    const rows = val.length > 200 ? 6 : val.split('\n').length > 3 ? 5 : 3;
    return `<div class="field"><label>${label}</label><textarea data-key="${key}" rows="${rows}">${val}</textarea></div>`;
  }
  return `<div class="field"><label>${label}</label><input type="text" data-key="${key}" value="${val}"></div>`;
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
  currentSection = secId;
  document.querySelectorAll(`[data-sec="${secId}"]`).forEach(l => l.classList.add('active'));
}

function saveAll() {
  document.querySelectorAll('[data-key]').forEach(el => { allData[el.dataset.key] = el.value; });
  const btn = document.getElementById('saveBtn');
  btn.disabled = true; btn.textContent = 'Saving...';
  setStatus('', '');
  fetch('/api/save?lang=' + currentLang + '&page=' + currentPage, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(allData)
  })
  .then(r => r.json())
  .then(res => {
    if (res.ok) setStatus('Saved and published!', 'ok');
    else setStatus('Error: ' + (res.error || 'unknown'), 'err');
  })
  .catch(e => setStatus('Error: ' + e.message, 'err'))
  .finally(() => { btn.disabled = false; btn.textContent = 'Save & publish'; });
}

function setStatus(msg, cls) {
  const el = document.getElementById('saveStatus');
  el.textContent = msg;
  el.className = 'save-status' + (cls ? ' ' + cls : '');
}
</script>
</body>
</html>"""


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        if parsed.path == '/api/data':
            params = parse_qs(parsed.query)
            lang = params.get('lang', [''])[0]
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
            lang = params.get('lang', [''])[0]
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
    print(f'CMS EN/DE -> http://localhost:{PORT}')
    Timer(0.8, lambda: webbrowser.open(f'http://localhost:{PORT}')).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')
