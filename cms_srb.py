#!/usr/bin/env python3
"""Srpski CMS - edituje sve stranice na srpskom jeziku."""

import http.server
import json
import re
import subprocess
import webbrowser
from pathlib import Path
from threading import Timer

ROOT = Path(__file__).parent.resolve()
PORT = 3001

PAGES = {
    'index':      {'label': 'Početna',        'file': 'srb/index.html'},
    'individual': {'label': 'Individualni rad','file': 'srb/individual.html'},
    'akal':       {'label': 'Akal zajednica', 'file': 'srb/akal.html'},
    'aura':       {'label': 'Aura tretman',   'file': 'srb/aura-tretman.html'},
}

# Sections shown per page (ordered for sidebar)
PAGE_SECTIONS = {
    'index': [
        ('hero',          'Hero'),
        ('pain',          'Bol / Prepoznavanje'),
        ('about',         'O meni'),
        ('offers',        'Ponude'),
        ('testimonials',  'Utisci'),
        ('booking',       'Zakazivanje'),
    ],
    'individual': [
        ('hero',          'Hero'),
        ('recognition',   'Prepoznavanje'),
        ('about',         'O meni'),
        ('method',        'Metoda'),
        ('whyworks',      'Zašto radi'),
        ('offers',        'Sesije i programi'),
        ('testimonials',  'Utisci'),
        ('cta',           'Poziv na akciju'),
    ],
    'akal': [
        ('hero',          'Hero'),
        ('forwho',        'Za koga'),
        ('inside',        'Šta je uključeno'),
        ('changes',       'Šta se menja'),
        ('cta',           'Cena i CTA'),
    ],
    'aura': [
        ('hero',          'Hero'),
        ('recognition',   'Prepoznavanje'),
        ('how',           'Tok sesije'),
        ('testimonials',  'Utisci'),
        ('offer',         'Ponuda'),
        ('cta',           'Poziv na akciju'),
    ],
}

# Which field keys belong to which section (prefix match or explicit list)
SECTION_KEYS = {
    # index.html
    'index:hero':         ['hero_label','hero_h1','hero_sub','hero_btn_primary','hero_btn_ghost'],
    'index:pain':         ['pain_h2','pain_p1','pain_p2','pain_q1','pain_q2','pain_q3','pain_q4','pain_q5','pain_q6','pain_q7'],
    'index:about':        ['about_h2','about_p1','about_p2','about_p3','about_p4'],
    'index:offers':       ['offers_h2','offers_desc','o1_name','o1_duration','o1_desc','o1_includes','o1_price_was','o1_price','o1_price_note',
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
    'akal:hero':     ['hero_label','hero_h1','hero_p'],
    'akal:forwho':   ['forwho_h2','forwho_p','card1_title','card1_text','card2_title','card2_text',
                      'card3_title','card3_text','card4_title','card4_text'],
    'akal:inside':   ['inside_h2','inc1_title','inc1_text','inc2_title','inc2_text','inc3_title','inc3_text'],
    'akal:changes':  ['changes_h2','changes_p','changes_list'],
    'akal:cta':      ['testi_text','testi_author','cta_price','cta_period','cta_p1','cta_p2','cta_btn'],

    # aura-tretman.html
    'aura:hero':         ['hero_label','hero_h1','hero_sub','hero_btn_primary','hero_btn_ghost'],
    'aura:recognition':  ['recog_h2','recog_intro','rec1_title','rec1_text','rec2_title','rec2_text','rec3_title','rec3_text'],
    'aura:how':          ['how_h2','how_intro','step1_title','step1_text','step2_title','step2_text',
                          'step3_title','step3_text','step4_title','step4_text'],
    'aura:testimonials': ['testi_h2','t1_text','t1_author','t1_source','t2_text','t2_author','t2_source','t3_text','t3_author','t3_source'],
    'aura:offer':        ['offer_intro','offer_name','offer_duration','offer_includes','offer_price_was','offer_price','offer_price_note','offer_btn','offer_note'],
    'aura:cta':          ['cta_h2','cta_body','cta_btn','cta_note'],
}

FIELD_LABELS = {
    # common
    'hero_label': 'Label (gornji mali tekst)', 'hero_h1': 'Naslov (HTML dozvoljeno)',
    'hero_sub': 'Podnaslov', 'hero_sub1': 'Podnaslov 1', 'hero_sub2': 'Podnaslov 2 (italic)',
    'hero_btn_primary': 'Dugme - primarno', 'hero_btn_ghost': 'Dugme - sekundarno',
    'hero_eyebrow': 'Eyebrow (gornji tekst)', 'hero_p': 'Paragraf',
    # index
    'pain_h2': 'Naslov', 'pain_p1': 'Paragraf 1', 'pain_p2': 'Paragraf 2',
    'pain_q1': 'Citat 1', 'pain_q2': 'Citat 2', 'pain_q3': 'Citat 3', 'pain_q4': 'Citat 4',
    'pain_q5': 'Citat 5', 'pain_q6': 'Citat 6', 'pain_q7': 'Citat 7',
    'about_h2': 'Naslov', 'about_p1': 'Paragraf 1', 'about_p2': 'Paragraf 2',
    'about_p3': 'Paragraf 3', 'about_p4': 'Paragraf 4', 'about_closing': 'Zaključna rečenica',
    'offers_h2': 'Naslov', 'offers_desc': 'Opis', 'offers_sub1': 'Opis 1', 'offers_sub2': 'Opis 2 (italic)',
    'akal_name': 'Naziv zajednice', 'akal_sub': 'Podnaslov', 'akal_includes': 'Uključeno (HTML li elementi)',
    'akal_price': 'Cena', 'akal_period': 'Period',
    'testi_h2': 'Naslov sekcije', 'booking_h2': 'Naslov',
    'booking_p1': 'Paragraf 1', 'booking_p2': 'Paragraf 2',
    'entry_title': 'Naziv ponude', 'entry_desc': 'Opis', 'entry_price': 'Cena', 'entry_btn': 'Dugme',
    # individual recognition
    'recog_h2': 'Naslov', 'recog_p1': 'Paragraf 1', 'recog_p2': 'Paragraf 2',
    'pain_1': 'Tačka 1', 'pain_2': 'Tačka 2', 'pain_3': 'Tačka 3', 'pain_4': 'Tačka 4', 'pain_5': 'Tačka 5',
    'pain_closing1': 'Zaključak 1', 'pain_closing2': 'Zaključak 2',
    # method
    'method_h2': 'Naslov', 'method_intro': 'Uvod', 'method_quote': 'Citat',
    'step1_title': 'Korak 01 - Naslov', 'step1_body': 'Korak 01 - Tekst',
    'step2_title': 'Korak 02 - Naslov', 'step2_body': 'Korak 02 - Tekst',
    'step3_title': 'Korak 03 - Naslov', 'step3_body': 'Korak 03 - Tekst',
    'step4_title': 'Korak 04 - Naslov', 'step4_body': 'Korak 04 - Tekst',
    'step5_title': 'Korak 05 - Naslov', 'step5_body': 'Korak 05 - Tekst',
    # why works
    'why_h2': 'Naslov', 'why_p1': 'Paragraf 1', 'why_p2': 'Paragraf 2',
    'why_p3': 'Paragraf 3', 'why_closing': 'Zaključak',
    # cta
    'cta_h2': 'Naslov', 'cta_body': 'Tekst', 'cta_btn': 'Dugme', 'cta_note': 'Napomena',
    'cta_price': 'Cena', 'cta_period': 'Period', 'cta_p1': 'Paragraf 1', 'cta_p2': 'Paragraf 2',
    # akal
    'forwho_h2': 'Naslov', 'forwho_p': 'Paragraf',
    'card1_title': 'Kartica 1 - Naslov', 'card1_text': 'Kartica 1 - Tekst',
    'card2_title': 'Kartica 2 - Naslov', 'card2_text': 'Kartica 2 - Tekst',
    'card3_title': 'Kartica 3 - Naslov', 'card3_text': 'Kartica 3 - Tekst',
    'card4_title': 'Kartica 4 - Naslov', 'card4_text': 'Kartica 4 - Tekst',
    'inside_h2': 'Naslov',
    'inc1_title': 'Stavka 1 - Naslov', 'inc1_text': 'Stavka 1 - Tekst',
    'inc2_title': 'Stavka 2 - Naslov', 'inc2_text': 'Stavka 2 - Tekst',
    'inc3_title': 'Stavka 3 - Naslov', 'inc3_text': 'Stavka 3 - Tekst',
    'changes_h2': 'Naslov', 'changes_p': 'Paragraf', 'changes_list': 'Lista (HTML li elementi)',
    'testi_text': 'Tekst utiska', 'testi_author': 'Autor',
    # aura
    'recog_intro': 'Intro', 'rec1_title': 'Stavka 1 - Naslov', 'rec1_text': 'Stavka 1 - Tekst',
    'rec2_title': 'Stavka 2 - Naslov', 'rec2_text': 'Stavka 2 - Tekst',
    'rec3_title': 'Stavka 3 - Naslov', 'rec3_text': 'Stavka 3 - Tekst',
    'how_h2': 'Naslov', 'how_intro': 'Uvod',
    'step1_text': 'Korak 01 - Tekst', 'step2_text': 'Korak 02 - Tekst',
    'step3_text': 'Korak 03 - Tekst', 'step4_text': 'Korak 04 - Tekst',
    'offer_intro': 'Uvod', 'offer_name': 'Naziv', 'offer_duration': 'Trajanje',
    'offer_includes': 'Uključeno (HTML li elementi)', 'offer_price_was': 'Stara cena',
    'offer_price': 'Cena', 'offer_price_note': 'Napomena uz cenu',
    'offer_btn': 'Dugme', 'offer_note': 'Napomena ispod kartice',
}

# Multiline fields (textarea)
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


def read_fields(page_id):
    path = ROOT / PAGES[page_id]['file']
    content = path.read_text(encoding='utf-8')
    return {k: v.strip() for k, v in CMS_PATTERN.findall(content)}


def write_fields(page_id, new_fields):
    path = ROOT / PAGES[page_id]['file']
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


def git_save(page_id):
    rel = PAGES[page_id]['file']
    subprocess.run(['git', 'add', rel], cwd=ROOT, check=True)
    label = PAGES[page_id]['label']
    r = subprocess.run(
        ['git', 'commit', '-m', f'CMS: azuriranje srpskog teksta'],
        cwd=ROOT, capture_output=True, text=True
    )
    if r.returncode != 0 and 'nothing to commit' not in (r.stdout + r.stderr):
        raise RuntimeError(r.stderr or r.stdout)
    subprocess.run(['git', 'push'], cwd=ROOT, check=True)


def build_sections_js():
    """Build JS object mapping page+section to list of field keys."""
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


HTML_UI = r"""<!DOCTYPE html>
<html lang="sr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CMS - Srpski sajt</title>
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

.page-select {
  width: 100%; background: rgba(0,0,0,0.35); border: 1px solid var(--border);
  color: var(--sand); font-size: 13px; padding: 8px 10px; border-radius: 5px;
  cursor: pointer; appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%238A8070'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 10px center;
  padding-right: 28px;
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

.empty-state { text-align: center; padding: 80px 20px; color: var(--stone); font-size: 14px; }
</style>
</head>
<body>

<aside class="sidebar">
  <div class="sidebar-top">
    <div class="sidebar-logo">CMS Srpski<span>Izaberi stranicu:</span></div>
    <select class="page-select" id="pageSelect" onchange="changePage(this.value)">
      <option value="">-- Izaberi stranicu --</option>
    </select>
  </div>
  <div class="sidebar-sections" id="sidebarSections"></div>
  <div class="sidebar-bottom">
    <button class="sidebar-save" id="saveBtn" onclick="saveAll()" disabled>Sačuvaj i objavi</button>
    <div class="save-status" id="saveStatus"></div>
  </div>
</aside>

<main class="main" id="mainContent">
  <div class="empty-state">
    <div style="font-size:32px;margin-bottom:16px;">↑</div>
    Izaberi stranicu iz padajućeg menija
  </div>
</main>

<script>
const PAGES = """ + build_pages_js() + r""";
const PAGE_SECTIONS = """ + build_page_sections_js() + r""";
const SECTION_KEYS = """ + build_sections_js() + r""";
const FIELD_LABELS = """ + build_labels_js() + r""";
const TEXTAREA_KEYS = new Set(""" + build_textarea_js() + r""");

let currentPage = '';
let currentSection = '';
let allData = {};

// Init page selector
Object.entries(PAGES).forEach(([id, label]) => {
  const opt = document.createElement('option');
  opt.value = id; opt.textContent = label;
  document.getElementById('pageSelect').appendChild(opt);
});

function changePage(pageId) {
  currentPage = pageId;
  allData = {};
  document.getElementById('saveBtn').disabled = !pageId;
  document.getElementById('saveStatus').textContent = '';
  document.getElementById('saveStatus').className = 'save-status';
  renderSidebar();
  if (!pageId) {
    document.getElementById('mainContent').innerHTML = '<div class="empty-state"><div style="font-size:32px;margin-bottom:16px;">↑</div>Izaberi stranicu iz padajućeg menija</div>';
    return;
  }
  loadData(pageId);
}

function renderSidebar() {
  const el = document.getElementById('sidebarSections');
  if (!currentPage) { el.innerHTML = ''; return; }
  el.innerHTML = PAGE_SECTIONS[currentPage].map(([secId, label]) =>
    `<button class="sidebar-link" data-sec="${secId}" onclick="showSection('${secId}')">${label}</button>`
  ).join('');
}

function loadData(pageId) {
  document.getElementById('mainContent').innerHTML = '<div class="empty-state">Učitavanje...</div>';
  fetch('/api/data?page=' + pageId)
    .then(r => r.json())
    .then(data => {
      allData = data;
      const firstSec = PAGE_SECTIONS[pageId][0][0];
      renderAllSections();
      showSection(firstSec);
    })
    .catch(() => setStatus('Greška pri učitavanju', 'err'));
}

function renderAllSections() {
  const sections = PAGE_SECTIONS[currentPage];
  const main = document.getElementById('mainContent');
  main.innerHTML = sections.map(([secId, label]) =>
    `<div class="section" id="sec-${secId}">` + renderSection(currentPage, secId, label) + '</div>'
  ).join('');
}

function renderSection(pageId, secId, label) {
  const keys = SECTION_KEYS[pageId][secId] || [];
  if (!keys.length) return `<div class="section-title">${label}</div><p style="color:var(--stone);font-size:13px">Nema polja za ovu sekciju.</p>`;

  let html = `<div class="section-title">${label}</div>`;

  // Group offer keys into blocks
  if (secId === 'offers' && (pageId === 'individual' || pageId === 'index')) {
    const introKeys = keys.filter(k => !k.match(/^o[1-4]_/) && !k.match(/^akal_/));
    const o1 = keys.filter(k => k.startsWith('o1_'));
    const o2 = keys.filter(k => k.startsWith('o2_'));
    const o3 = keys.filter(k => k.startsWith('o3_'));
    const o4 = keys.filter(k => k.startsWith('o4_'));
    const akal = keys.filter(k => k.startsWith('akal_'));

    if (introKeys.length) html += '<div class="card"><div class="card-title">Uvod</div>' + introKeys.map(k => fieldHtml(k)).join('') + '</div>';
    if (o1.length) html += offerBlock('1', o1);
    if (o2.length) html += offerBlock('2', o2);
    if (o3.length) html += offerBlock('3', o3);
    if (o4.length) html += offerBlock('4', o4);
    if (akal.length) html += '<div class="offer-block"><div class="offer-block-title">Akal zajednica</div>' + akal.map(k => fieldHtml(k)).join('') + '</div>';
    return html;
  }

  // Testimonials grouping
  if (secId === 'testimonials') {
    const h2keys = keys.filter(k => k === 'testi_h2');
    const tkeys = keys.filter(k => k !== 'testi_h2');
    if (h2keys.length) html += '<div class="card">' + h2keys.map(k => fieldHtml(k)).join('') + '</div>';
    // Group by tN_
    const nums = [...new Set(tkeys.map(k => k.match(/^t(\d+)_/)?.[1]).filter(Boolean))];
    nums.forEach(n => {
      const tg = tkeys.filter(k => k.startsWith('t' + n + '_'));
      html += `<div class="offer-block"><div class="offer-block-title">Utisak ${n}</div>` + tg.map(k => fieldHtml(k)).join('') + '</div>';
    });
    return html;
  }

  // Default: all in one card
  html += '<div class="card">' + keys.map(k => fieldHtml(k)).join('') + '</div>';
  return html;
}

function offerBlock(num, keys) {
  const names = { '1': 'Aura tretman / Ponuda 1', '2': 'Ponuda 2', '3': 'Ponuda 3', '4': 'Ponuda 4 (Transform)' };
  return `<div class="offer-block"><div class="offer-block-title">${names[num] || 'Ponuda ' + num}</div>` + keys.map(k => fieldHtml(k)).join('') + '</div>';
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
  // Save current values before switching
  document.querySelectorAll('[data-key]').forEach(el => { allData[el.dataset.key] = el.value; });

  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
  const sec = document.getElementById('sec-' + secId);
  if (sec) {
    sec.classList.add('active');
    // Re-fill values (in case re-rendered)
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
  btn.disabled = true; btn.textContent = 'Čuvam...';
  setStatus('', '');
  fetch('/api/save?page=' + currentPage, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(allData)
  })
  .then(r => r.json())
  .then(res => {
    if (res.ok) setStatus('Sačuvano i objavljeno!', 'ok');
    else setStatus('Greška: ' + (res.error || 'nepoznata'), 'err');
  })
  .catch(e => setStatus('Greška: ' + e.message, 'err'))
  .finally(() => { btn.disabled = false; btn.textContent = 'Sačuvaj i objavi'; });
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
            page_id = params.get('page', [''])[0]
            if page_id not in PAGES:
                self._json({})
            else:
                self._json(read_fields(page_id))
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
            page_id = params.get('page', [''])[0]
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                fields = json.loads(body)
                write_fields(page_id, fields)
                git_save(page_id)
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
    print(f'CMS srpski -> http://localhost:{PORT}')
    Timer(0.8, lambda: webbrowser.open(f'http://localhost:{PORT}')).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nZatvoren.')
