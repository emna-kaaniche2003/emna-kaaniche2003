#!/usr/bin/env python3
"""Regenerates (1) the toggle-button SVGs in assets/ui/ and (2) the README pages.

Usage (from the repo root):   python3 scripts/build.py

Why this exists: a GitHub README cannot run JavaScript, so a "toggle" is really a
link to another page. Four static views are generated from README.md / README.en.md:
    views/fr-light.md  views/fr-dark.md  views/en-light.md  views/en-dark.md
README.md and README.en.md stay "auto" (they follow the viewer's GitHub theme).
Edit the body of README.md / README.en.md, then re-run this script.
"""
import math, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI = os.path.join(ROOT, 'assets', 'ui')

# ───────────────────────── 1. toggle buttons (SVG) ─────────────────────────
SKIN = {
    'light': dict(track='#F3EFFF', stroke='#E2D9FF', off='#6B6485', shadow='#2A1766', sh=(.025, .035, .045)),
    'dark':  dict(track='#231D40', stroke='#3A2F70', off='#A8A1C2', shadow='#000000', sh=(.10, .14, .18)),
}
W, H, CY, R = 44, 46, 22, 20          # half-pill: 44 wide, track spans y=2..42
DUR, DELAY, EASE = '.55s', '.2s', 'cubic-bezier(.65,0,.35,1)'

def icon(kind, color, sw=1.8, animated=False):
    """Icon centred on (0,0)."""
    if kind == 'sun':
        rays = ''.join(
            f'<line x1="{6.9*math.cos(a):.2f}" y1="{6.9*math.sin(a):.2f}" x2="{9.1*math.cos(a):.2f}" y2="{9.1*math.sin(a):.2f}"/>'
            for a in (i * math.pi / 4 for i in range(8)))
        rays_g = f'<g class="ry">{rays}</g>' if animated else f'<g>{rays}</g>'
        return (f'<g fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round">'
                f'<circle r="3.9"/>{rays_g}</g>')
    if kind == 'moon':
        s = .75
        body = (f'<g transform="translate(-9 -9) scale({s})" fill="none" stroke="{color}" stroke-width="{sw/s:.2f}" '
                f'stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></g>')
        star = (f'<g class="tw" fill="{color}"><circle cx="5.6" cy="-6.4" r=".95"/><circle cx="8.4" cy="-2.6" r=".7"/></g>'
                if animated else '')
        return body + star
    # text label (FR / EN)
    return (f'<text y="4.5" font-family="Helvetica, Arial, sans-serif" font-size="12.5" font-weight="bold" '
            f'letter-spacing=".5" text-anchor="middle" fill="{color}">{kind}</text>')

def half(kind, side, on, skin):
    c = SKIN[skin]
    if side == 'L':
        fill = f'M22 2 H44 V42 H22 A20 20 0 0 1 22 2 Z'
        edge = 'M44 2 H22 A20 20 0 0 0 22 42 H44'
        start, away = 44, 44           # knob arrives from / leaves toward the seam (right side)
    else:
        fill = f'M0 2 H22 A20 20 0 0 1 22 42 H0 Z'
        edge = 'M0 2 H22 A20 20 0 0 1 22 42 H0'
        start, away = -44, -44
    shadow = ''.join(f'<path d="{fill}" transform="translate(0 {dy})" fill="{c["shadow"]}" opacity="{op}"/>'
                     for dy, op in zip((3, 2, 1), c['sh']))
    base = f'<g transform="translate(22 {CY})">{icon(kind, c["off"])}</g>'
    knob = ('<g class="kn"><circle class="hl" r="16" fill="none" stroke="#7C5CF0" stroke-width="1.6"/>'
            '<circle r="16" fill="url(#k)"/>'
            f'{icon(kind, "#fff", animated=on)}</g>')
    if on:
        anim = (f'@keyframes slin{{from{{transform:translateX({start}px)}}to{{transform:translateX(0)}}}}'
                f'.kn{{animation:slin {DUR} {EASE} {DELAY} both}}')
        kn_base = ''
    else:
        anim = (f'@keyframes slout{{from{{transform:translateX(0);opacity:1}}to{{transform:translateX({away}px);opacity:0}}}}'
                f'.kn{{opacity:0;animation:slout {DUR} {EASE} {DELAY} both}}')
    css = (anim +
           ('@keyframes pg{0%{transform:scale(1);opacity:.5}100%{transform:scale(1.28);opacity:0}}'
            '@keyframes sp{to{transform:rotate(360deg)}}@keyframes pu{0%,100%{opacity:.25}50%{opacity:1}}'
            '.hl{opacity:0;transform-box:fill-box;transform-origin:center;animation:pg 2.6s ease-out .8s infinite}'
            '.ry{transform-box:fill-box;transform-origin:center;animation:sp 16s linear infinite}'
            '.tw{animation:pu 2.4s ease-in-out infinite}' if on else '.hl{display:none}') +
           '@media (prefers-reduced-motion:reduce){.kn,.hl,.ry,.tw{animation:none!important}}')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<defs><linearGradient id="k" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5B34D9"/>'
            f'<stop offset="1" stop-color="#A04CE8"/></linearGradient><style>{css}</style></defs>'
            f'{shadow}<path d="{fill}" fill="{c["track"]}"/><path d="{edge}" fill="none" stroke="{c["stroke"]}"/>'
            f'{base}<g transform="translate(22 {CY})">{knob}</g></svg>\n')

def build_ui():
    os.makedirs(UI, exist_ok=True)
    spec = [('lang-fr', 'FR', 'L'), ('lang-en', 'EN', 'R'), ('theme-sun', 'sun', 'L'), ('theme-moon', 'moon', 'R')]
    n = 0
    for name, kind, side in spec:
        for on in (True, False):
            for skin in ('light', 'dark'):
                fn = f'{name}-{"on" if on else "off"}{"-dark" if skin == "dark" else ""}.svg'
                open(os.path.join(UI, fn), 'w', encoding='utf-8').write(half(kind, side, on, skin))
                n += 1
    print(f'assets/ui: {n} SVG written')

# ───────────────────────────── 2. README pages ─────────────────────────────
LABEL = {  # accessible names, in the page language
    'fr': dict(fr='Français', en='English', light='Mode clair', dark='Mode sombre'),
    'en': dict(fr='Français', en='English', light='Light mode', dark='Dark mode'),
}
PIC = re.compile(r'<picture><source media="\(prefers-color-scheme: dark\)" srcset="(?P<dark>[^"]+)">'
                 r'<img (?P<pre>[^>]*?)src="(?P<light>[^"]+)"(?P<rest>[^>]*)/></picture>')

def img(src, alt, prefix):
    return f'<img src="{prefix}assets/ui/{src}.svg" width="{W}" height="{H}" alt="{alt}"/>'

def pic(light_src, dark_src, alt, prefix):
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{prefix}assets/ui/{dark_src}.svg">'
            f'{img(light_src, alt, prefix)}</picture>')

def toggle(lang, theme, links, prefix):
    """theme=None → auto page (follows the viewer's GitHub theme); else 'light'/'dark' forced."""
    L = LABEL[lang]
    def a(href, label, inner): return f'<a href="{href}" title="{label}">{inner}</a>'
    on = lambda c: 'on' if c else 'off'
    fr_on, en_on = lang == 'fr', lang == 'en'
    if theme is None:
        fr = pic(f'lang-fr-{on(fr_on)}', f'lang-fr-{on(fr_on)}-dark', L['fr'], prefix)
        en = pic(f'lang-en-{on(en_on)}', f'lang-en-{on(en_on)}-dark', L['en'], prefix)
        sun = pic('theme-sun-on', 'theme-sun-off-dark', L['light'], prefix)     # light viewer: sun active
        moon = pic('theme-moon-off', 'theme-moon-on-dark', L['dark'], prefix)   # dark viewer: moon active
    else:
        sk = '-dark' if theme == 'dark' else ''
        fr = img(f'lang-fr-{on(fr_on)}{sk}', L['fr'], prefix)
        en = img(f'lang-en-{on(en_on)}{sk}', L['en'], prefix)
        sun = img(f'theme-sun-{on(theme == "light")}{sk}', L['light'], prefix)
        moon = img(f'theme-moon-{on(theme == "dark")}{sk}', L['dark'], prefix)
    return ('<p align="right">' + a(links['fr'], L['fr'], fr) + a(links['en'], L['en'], en) + '&nbsp;&nbsp;&nbsp;'
            + a(links['sun'], L['light'], sun) + a(links['moon'], L['dark'], moon) + '</p>')

START, END = '<!-- toggle:start -->', '<!-- toggle:end -->'

def split(path):
    s = open(path, encoding='utf-8').read()
    if START in s:
        head, rest = s.split(START, 1); _, body = rest.split(END, 1)
        return body.lstrip('\n')
    return s.split('\n', 1)[1].lstrip('\n')          # first run: drop the old "🇫🇷 · 🇬🇧" line

def force_theme(body, theme):
    def repl(m):
        src = m.group('dark') if theme == 'dark' else m.group('light')
        if not src.startswith('http'): src = '../' + src
        return f'<img {m.group("pre")}src="{src}"{m.group("rest")}/>'
    out, n = PIC.subn(repl, body)
    assert '<picture' not in out, 'unhandled <picture> block'
    return out, n

def build_pages():
    bodies = {'fr': split(os.path.join(ROOT, 'README.md')), 'en': split(os.path.join(ROOT, 'README.en.md'))}
    os.makedirs(os.path.join(ROOT, 'views'), exist_ok=True)
    auto = {'fr': 'README.md', 'en': 'README.en.md'}
    for lang in ('fr', 'en'):
        # auto page: follows the viewer's theme; 2 theme links go to the forced views
        t = toggle(lang, None, dict(fr='README.md' if lang == 'en' else '#', en='README.en.md' if lang == 'fr' else '#',
                                    sun=f'views/{lang}-light.md', moon=f'views/{lang}-dark.md'), '')
        open(os.path.join(ROOT, auto[lang]), 'w', encoding='utf-8').write(f'{START}\n{t}\n{END}\n\n{bodies[lang]}')
        for theme in ('light', 'dark'):
            links = dict(fr=f'fr-{theme}.md' if lang == 'en' else '#', en=f'en-{theme}.md' if lang == 'fr' else '#',
                         sun='#' if theme == 'light' else f'{lang}-light.md',
                         moon='#' if theme == 'dark' else f'{lang}-dark.md')
            body, n = force_theme(bodies[lang], theme)
            t = toggle(lang, theme, links, '../')
            open(os.path.join(ROOT, 'views', f'{lang}-{theme}.md'), 'w', encoding='utf-8').write(f'{t}\n\n{body}')
    print('pages: README.md, README.en.md, views/{fr,en}-{light,dark}.md written')

if __name__ == '__main__':
    build_ui(); build_pages()
