"""Builds the profile graphics in assets/ from tools/profile.py.

    pip install pillow fonttools
    python tools/fetch_github.py   # optional: refresh real contribution counts
    python tools/build.py          # graphics + README.md

Every SVG comes in a light and a dark version and embeds subsetted fonts, so it
renders the same everywhere GitHub shows it.
"""

import base64
import io
import json
import math
import os
import random
import sys
from collections import defaultdict
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont
from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, 'assets')
LOGOS = os.path.join(ASSETS, 'logos')
sys.path.insert(0, HERE)
import profile as P  # noqa: E402

FONTS = {
    'r': ('inter-400.woff', 'AJ Inter', 400),
    'm': ('inter-500.woff', 'AJ Inter', 500),
    's': ('inter-600.woff', 'AJ Inter', 600),
    'b': ('inter-800.woff', 'AJ Inter', 800),
    'mono': ('mono-500.woff', 'AJ Mono', 500),
}

THEMES = {
    'dark': dict(bg='#0a0a0a', panel='#0d0d0d', border='#232323', text='#f2f2f2', muted='#8f8f8f',
                 faint='#2e2e2e', grid='#ffffff', gridop='0.07', chip='#151515', chipline='#2a2a2a'),
    'light': dict(bg='#ffffff', panel='#fbfbfb', border='#e6e6e6', text='#0a0a0a', muted='#6b6b6b',
                  faint='#e2e2e2', grid='#000000', gridop='0.06', chip='#f3f3f3', chipline='#e2e2e2'),
}
TILE_BG, TILE_LINE, TILE_INK = '#0d0d0d', '#343434', '#f2f2f2'
MONTHS = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()

_pil = {}


def measure(s, font, size, ls=0):
    key = (font, size)
    if key not in _pil:
        _pil[key] = ImageFont.truetype(os.path.join(HERE, 'fonts', FONTS[font][0]), size)
    return _pil[key].getlength(s) + ls * max(0, len(s) - 1)


def wrap(text, font, size, width):
    lines, line = [], ''
    for word in text.split():
        trial = f'{line} {word}'.strip()
        if measure(trial, font, size) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def logo_uri(name):
    with open(os.path.join(LOGOS, f'{name}.png'), 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()


class Svg:
    def __init__(self, w, h, theme, title):
        self.w, self.h, self.t, self.title = w, h, THEMES[theme], title
        self.parts, self.defs, self.css = [], [], []
        self.used = defaultdict(set)

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, font='r', size=16, fill=None, anchor='start', ls=0, cls='', opacity=None):
        self.used[font].update(s)
        fam, weight = FONTS[font][1], FONTS[font][2]
        attrs = f'x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-weight="{weight}" font-size="{size}" fill="{fill or self.t["text"]}"'
        if anchor != 'start':
            attrs += f' text-anchor="{anchor}"'
        if ls:
            attrs += f' letter-spacing="{ls}"'
        if cls:
            attrs += f' class="{cls}"'
        if opacity is not None:
            attrs += f' opacity="{opacity}"'
        self.add(f'<text {attrs}>{escape(s)}</text>')

    def chip(self, x, y, label, size=14, ls=1.5, pad=14, h=30):
        w = measure(label, 'mono', size, ls) + pad * 2
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="{h / 2}" fill="{self.t["chip"]}" stroke="{self.t["chipline"]}"/>')
        self.text(x + pad, y + h / 2 + size * 0.36, label, 'mono', size, self.t['text'], ls=ls)
        return w

    def tag(self, x, y, label, size=14):
        w = measure(label, 'mono', size) + 24
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="30" rx="8" fill="none" stroke="{self.t["chipline"]}"/>')
        self.text(x + 12, y + 20, label, 'mono', size, self.t['muted'])
        return w

    def panel(self, rx=24):
        self.add(f'<rect x="0.5" y="0.5" width="{self.w - 1}" height="{self.h - 1}" rx="{rx}" fill="{self.t["panel"]}" stroke="{self.t["border"]}"/>')

    def icon(self, spec, x, y, s):
        if not spec.startswith('glyph:'):
            self.add(f'<image x="{x}" y="{y}" width="{s}" height="{s}" href="{logo_uri(spec)}"/>')
            return
        r = s * 0.24
        self.add(f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{s - 1}" height="{s - 1}" rx="{r}" fill="{TILE_BG}" stroke="{TILE_LINE}"/>')
        self.add(f'<g transform="translate({x} {y}) scale({s / 100})" fill="none" stroke="{TILE_INK}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">{GLYPHS[spec[6:]]}</g>')

    def font_faces(self):
        out = []
        for key, chars in self.used.items():
            file, fam, weight = FONTS[key]
            font = TTFont(os.path.join(HERE, 'fonts', file))
            opts = subset.Options()
            opts.flavor = 'woff'
            opts.layout_features = ['kern', 'liga', 'calt', 'tnum']
            sub = subset.Subsetter(opts)
            sub.populate(text=''.join(sorted(chars)) + ' ')
            sub.subset(font)
            buf = io.BytesIO()
            font.flavor = 'woff'
            font.save(buf)
            b64 = base64.b64encode(buf.getvalue()).decode()
            out.append(f"@font-face{{font-family:'{fam}';font-weight:{weight};src:url(data:font/woff;base64,{b64}) format('woff')}}")
        return ''.join(out)

    def render(self):
        css = self.font_faces() + ''.join(self.css)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" role="img">'
                f'<title>{escape(self.title)}</title><style>{css}</style><defs>{"".join(self.defs)}</defs>{"".join(self.parts)}</svg>')


# 100x100 line icons for glyph tiles
GLYPHS = {
    'stealth': '<circle cx="50" cy="50" r="22"/><path d="M50 28 A22 22 0 0 1 50 72 Z" fill="#f2f2f2"/>',
    'watchbot': '<path d="M22 50 C34 32 66 32 78 50 C66 68 34 68 22 50 Z"/><circle cx="50" cy="50" r="8" fill="#f2f2f2"/>',
    'alongside': '<circle cx="40" cy="50" r="17"/><circle cx="60" cy="50" r="17"/>',
    'bolt': '<path d="M55 22 L32 56 H50 L45 78 L68 44 H50 Z" fill="#f2f2f2"/>',
    'scales': '<path d="M50 26 V74 M36 74 H64 M28 36 H72"/><path d="M28 36 L20 54 H36 Z M72 36 L64 54 H80 Z"/>',
    'board': ''.join(f'<rect x="{26 + c * 12}" y="{26 + r * 12}" width="12" height="12" fill="{"#f2f2f2" if (r + c) % 2 == 0 else "none"}" stroke="none"/>'
                     for r in range(4) for c in range(4)) + '<rect x="26" y="26" width="48" height="48"/>',
    'chip': '<rect x="32" y="32" width="36" height="36" rx="4"/><path d="M40 26 V32 M50 26 V32 M60 26 V32 M40 68 V74 M50 68 V74 M60 68 V74 M26 40 H32 M26 50 H32 M26 60 H32 M68 40 H74 M68 50 H74 M68 60 H74"/>',
    'terminal': '<rect x="24" y="30" width="52" height="40" rx="5"/><path d="M34 44 L42 50 L34 56 M48 58 H62"/>',
    'trophy': '<path d="M36 26 H64 V42 C64 52 57 58 50 58 C43 58 36 52 36 42 Z M36 32 H26 C26 42 31 46 37 46 M64 32 H74 C74 42 69 46 63 46 M50 58 V68 M38 74 H62 M42 68 H58 V74 H42 Z"/>',
    'rocket': '<path d="M50 22 C62 32 64 48 58 64 H42 C36 48 38 32 50 22 Z"/><circle cx="50" cy="42" r="5"/><path d="M42 58 L32 68 V74 L42 66 M58 58 L68 68 V74 L58 66 M46 70 L50 80 L54 70"/>',
    'globe': '<circle cx="50" cy="50" r="24"/><path d="M26 50 H74 M50 26 C38 38 38 62 50 74 M50 26 C62 38 62 62 50 74"/>',
    'medal': '<circle cx="50" cy="58" r="15"/><path d="M40 22 L46 44 M60 22 L54 44 M40 22 H60"/><path d="M45 58 L49 62 L56 54"/>',
    'agents': '<circle cx="50" cy="30" r="7"/><circle cx="30" cy="66" r="7"/><circle cx="70" cy="66" r="7"/><path d="M46 36 L34 60 M54 36 L66 60 M37 66 H63"/>',
    'people': '<circle cx="38" cy="38" r="9"/><circle cx="64" cy="40" r="7"/><path d="M22 72 C22 60 30 54 38 54 C46 54 54 60 54 72 M56 72 C56 62 60 56 66 56 C72 56 78 62 78 72"/>',
    'cap': '<path d="M50 30 L80 44 L50 58 L20 44 Z"/><path d="M34 51 V64 C42 72 58 72 66 64 V51 M80 44 V60"/>',
    'linkedin': '<path d="M34 44 V70 M34 32 V33"/><path d="M48 70 V44 M48 54 C48 46 54 43 59 43 C65 43 68 47 68 54 V70"/>',
    'book': '<path d="M50 32 C42 26 30 26 24 30 V72 C30 68 42 68 50 74 C58 68 70 68 76 72 V30 C70 26 58 26 50 32 Z M50 32 V74"/>',
    'orcid': '<circle cx="50" cy="50" r="26"/><path d="M40 40 V64 M40 32 V33 M50 40 V64 H55 C63 64 67 58 67 52 C67 46 63 40 55 40 Z"/>',
    'star': '<path d="M50 24 L57 41 L76 42 L61 54 L66 72 L50 62 L34 72 L39 54 L24 42 L43 41 Z"/>',
    'note': '<path d="M42 70 V32 L72 26 V62"/><circle cx="35" cy="70" r="8"/><circle cx="65" cy="62" r="8"/>',
    'target': '<circle cx="50" cy="50" r="24"/><circle cx="50" cy="50" r="13"/><circle cx="50" cy="50" r="3" fill="#f2f2f2"/>',
    'mail': '<rect x="22" y="30" width="56" height="40" rx="5"/><path d="M24 33 L50 54 L76 33"/>',
    'phone': '<rect x="34" y="20" width="32" height="60" rx="7"/><path d="M45 70 H55"/>',
    'paper': '<path d="M32 22 H58 L70 34 V78 H32 Z M58 22 V34 H70 M40 46 H62 M40 56 H62 M40 66 H54"/>',
    'braces': '<path d="M42 28 C34 28 36 40 36 44 C36 48 30 50 30 50 C30 50 36 52 36 56 C36 60 34 72 42 72 M58 28 C66 28 64 40 64 44 C64 48 70 50 70 50 C70 50 64 52 64 56 C64 60 66 72 58 72"/>',
}

# Only decorative parts animate. Content never starts hidden, because some
# viewers freeze SVG animations at their first frame.
FADE_CSS = ''


def save(name, theme, svg):
    path = os.path.join(ASSETS, f'{name}-{theme}.svg')
    with open(path, 'w') as f:
        f.write(svg.render())
    return path


# --------------------------------------------------------------------------- hero

def hero(theme):
    W, H = 1280, 440
    s = Svg(W, H, theme, f'{P.NAME}: {P.TAGLINE}')
    t = s.t
    s.css.append(FADE_CSS)
    s.css.append('@keyframes breathe{50%{opacity:.25}}.n{animation:breathe 4s ease-in-out infinite}'
                 '@keyframes blink{50%{opacity:0}}.caret{animation:blink 1.1s steps(1) infinite}'
                 '@keyframes ring{0%{r:6px;opacity:.6}100%{r:22px;opacity:0}}.ring{animation:ring 2.8s ease-out infinite}')
    s.defs.append(f'<pattern id="dots" width="26" height="26" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1.3" fill="{t["grid"]}" fill-opacity="{t["gridop"]}"/></pattern>')
    s.defs.append('<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".35" stop-color="#fff" stop-opacity="1"/></linearGradient>'
                  f'<mask id="netmask"><rect x="600" y="0" width="{W - 600}" height="{H}" fill="url(#fade)"/></mask>'
                  f'<clipPath id="clip"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24"/></clipPath>')
    s.panel()
    s.add(f'<g clip-path="url(#clip)"><rect width="{W}" height="{H}" fill="url(#dots)"/>')

    # A small multi-agent network, with messages travelling between agents.
    rnd = random.Random(11)
    nodes = []
    while len(nodes) < 18:
        p = (rnd.uniform(720, 1230), rnd.uniform(48, H - 48))
        if all(math.dist(p, q) > 70 for q in nodes):
            nodes.append(p)
    edges = set()
    for i, p in enumerate(nodes):
        for j in sorted(range(len(nodes)), key=lambda k: math.dist(p, nodes[k]))[1:3]:
            edges.add(tuple(sorted((i, j))))
    edges = sorted(edges)
    g = [f'<g mask="url(#netmask)">']
    for i, j in edges:
        (x1, y1), (x2, y2) = nodes[i], nodes[j]
        g.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{t["text"]}" stroke-opacity=".16" stroke-width="1.2"/>')
    for k, (i, j) in enumerate(edges[::2]):
        (x1, y1), (x2, y2) = nodes[i], nodes[j]
        if k % 2:
            x1, y1, x2, y2 = x2, y2, x1, y1
        dur = 2.4 + (k % 5) * 0.5
        g.append(f'<circle r="2.6" fill="{t["text"]}"><animateMotion dur="{dur}s" begin="{k * 0.37:.2f}s" repeatCount="indefinite" path="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" dur="{dur}s" begin="{k * 0.37:.2f}s" repeatCount="indefinite"/></circle>')
    hubs = {2, 7, 12, 15}
    for k, (x, y) in enumerate(nodes):
        if k in hubs:
            g.append(f'<circle class="ring" cx="{x:.1f}" cy="{y:.1f}" r="6" fill="none" stroke="{t["text"]}" stroke-width="1.2" style="animation-delay:{k * 0.4:.1f}s"/>')
            g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{t["text"]}"/>')
        else:
            g.append(f'<circle class="n" cx="{x:.1f}" cy="{y:.1f}" r="{3 + (k % 3) * 0.8:.1f}" fill="{t["text"]}" style="animation-delay:{(k * 0.53) % 4:.2f}s"/>')
    g.append('</g></g>')
    s.add(''.join(g))

    x = 64
    s.text(x, 104, P.KICKER, 'mono', 16, t['muted'], ls=3, cls='f d1')
    s.text(x - 4, 200, P.NAME, 'b', 104, t['text'], ls=-4, cls='f d2')
    lines = wrap(P.TAGLINE, 'r', 27, 620)
    for i, line in enumerate(lines):
        s.text(x, 256 + i * 38, line, 'r', 27, t['muted'], cls='f d3')
    end = x + measure(lines[-1], 'r', 27) + 8
    s.add(f'<rect class="caret" x="{end:.1f}" y="{256 + (len(lines) - 1) * 38 - 24}" width="13" height="30" fill="{t["text"]}"/>')
    cx = x
    for glyph, label in P.CONTACTS:
        w = measure(label, 'mono', 15) + 58
        s.add(f'<rect x="{cx:.1f}" y="346" width="{w:.1f}" height="38" rx="19" fill="{t["chip"]}" stroke="{t["chipline"]}"/>')
        s.add(f'<g transform="translate({cx + 12:.1f} 353) scale(0.24)" fill="none" stroke="{t["text"]}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">{GLYPHS[glyph]}</g>')
        s.text(cx + 44, 370, label, 'mono', 15, t['text'])
        cx += w + 10
    return s


# ----------------------------------------------------------------------- timeline

def timeline(theme):
    rows = P.EXPERIENCE
    W, top, rh = 1280, 118, 66
    H = top + len(rows) * rh + 28
    s = Svg(W, H, theme, 'Experience timeline: ' + '; '.join(f'{r[2]} at {r[1]}' for r in rows))
    t = s.t
    s.css.append(FADE_CSS)
    s.css.append('@keyframes ping{0%{r:5px;opacity:.7}100%{r:16px;opacity:0}}.ping{animation:ping 2.2s ease-out infinite}')
    s.panel()
    x0, x1 = 470, 1196
    tmin, tmax = 2020.75, 2027.0
    now = P.NOW[0] + (P.NOW[1] - 0.5) / 12

    def X(ym):
        return x0 + (ym - tmin) / (tmax - tmin) * (x1 - x0)

    def T(d):
        return d[0] + (d[1] - 1) / 12

    s.text(48, 62, 'EXPERIENCE', 'mono', 16, t['text'], ls=3)
    s.text(W - 48, 62, f'{rows[-1][3][0]} → NOW', 'mono', 16, t['muted'], 'end', ls=3)
    for yr in range(2021, 2027):
        xx = X(yr)
        s.add(f'<line x1="{xx:.1f}" y1="{top - 14}" x2="{xx:.1f}" y2="{H - 24}" stroke="{t["faint"]}" stroke-dasharray="2 5"/>')
        s.text(xx, top - 24, str(yr), 'mono', 14, t['muted'], 'middle')
    xn = X(now)
    s.add(f'<line x1="{xn:.1f}" y1="{top - 14}" x2="{xn:.1f}" y2="{H - 24}" stroke="{t["text"]}" stroke-opacity=".5" stroke-dasharray="4 4"/>')
    s.text(xn, top - 24, 'NOW', 'mono', 14, t['text'], 'middle', ls=1)

    for i, (logo, org, role, start, end, kind) in enumerate(rows):
        y = top + i * rh
        if i:
            s.add(f'<line x1="40" y1="{y}" x2="{W - 40}" y2="{y}" stroke="{t["faint"]}" stroke-opacity=".6"/>')
        s.add(f'<g class="f" style="animation-delay:{0.08 * i:.2f}s">')
        s.icon(logo, 48, y + 11, 44)
        s.text(108, y + 30, org, 's', 20, t['text'])
        s.text(108, y + 52, role, 'r', 16, t['muted'])
        s.add('</g>')
        a, b = X(T(start)), X(T(end) + 1 / 12 if end else now)
        cy = y + rh / 2
        if kind == 'study':
            s.add(f'<rect class="bar" style="animation-delay:{0.3 + 0.08 * i:.2f}s" x="{a:.1f}" y="{cy - 5}" width="{b - a:.1f}" height="10" rx="5" fill="none" stroke="{t["text"]}" stroke-width="2"/>')
        else:
            s.add(f'<rect class="bar" style="animation-delay:{0.3 + 0.08 * i:.2f}s" x="{a:.1f}" y="{cy - 5}" width="{max(b - a, 10):.1f}" height="10" rx="5" fill="{t["text"]}"/>')
        if end is None:
            s.add(f'<circle class="ping" cx="{b:.1f}" cy="{cy}" r="5" fill="none" stroke="{t["text"]}" stroke-width="1.5"/><circle cx="{b:.1f}" cy="{cy}" r="5" fill="{t["text"]}"/>')
        if end is None:
            label = f'{MONTHS[start[1] - 1]} {start[0]} – now'
        elif start[0] == end[0]:
            label = f'{MONTHS[start[1] - 1]}–{MONTHS[end[1] - 1]} {end[0]}'
        else:
            label = f'{MONTHS[start[1] - 1]} {start[0]} – {MONTHS[end[1] - 1]} {end[0]}'
        if b + 14 + measure(label, 'mono', 13) < W - 40:
            s.text(b + 14, cy + 5, label, 'mono', 13, t['muted'])
        else:
            s.text(a - 14, cy + 5, label, 'mono', 13, t['muted'], 'end')
    return s


# ------------------------------------------------------------------------- impact

def impact(theme):
    d = P.IMPACT
    W = 1280
    bullets = [wrap(b, 'r', 17.5, W - 130) for b in d.get('bullets', [])]
    H = 270 + (30 + sum(len(b) * 26 + 14 for b in bullets) if bullets else 0)
    s = Svg(W, H, theme, d['title'] + ': ' + '; '.join(' '.join(x) for x in d['stats']))
    t = s.t
    s.css.append(FADE_CSS)
    s.panel()
    s.icon(d['logo'], 48, 34, 38)
    s.text(102, 59, d['title'], 'mono', 16, t['text'], ls=3)
    s.text(W - 48, 59, d['subtitle'], 'mono', 14, t['muted'], 'end', ls=2)
    s.add(f'<line x1="48" y1="96" x2="{W - 48}" y2="96" stroke="{t["faint"]}"/>')
    cw = (W - 96) / len(d['stats'])
    for i, (big, label, sub) in enumerate(d['stats']):
        x = 48 + i * cw + (0 if i == 0 else 36)
        if i:
            s.add(f'<line x1="{48 + i * cw:.1f}" y1="122" x2="{48 + i * cw:.1f}" y2="238" stroke="{t["faint"]}"/>')
        s.add(f'<g class="f d{i + 2}">')
        s.text(x, 186, big, 'b', 66, t['text'], ls=-2)
        s.text(x, 218, label, 's', 19, t['text'])
        s.text(x, 242, sub, 'r', 16, t['muted'])
        s.add('</g>')
    if bullets:
        y = 290
        s.add(f'<line x1="48" y1="{y - 18}" x2="{W - 48}" y2="{y - 18}" stroke="{t["faint"]}"/>')
        for lines in bullets:
            y += 12
            s.add(f'<rect x="50" y="{y + 1}" width="8" height="8" rx="2" fill="{t["text"]}"/>')
            for line in lines:
                s.text(76, y + 12, line, 'r', 17.5, t['muted'])
                y += 26
            y += 2
    return s


# -------------------------------------------------------------------------- cards

def card(theme, key, d):
    W, H = 600, 400
    s = Svg(W, H, theme, f'{d["title"]}: {d["text"]}')
    t = s.t
    s.panel(22)
    s.icon(d['icon'], 36, 36, 56)
    s.text(W - 36, 70, '↗', 'm', 28, t['muted'], 'end')
    s.text(36, 146, d['title'], 'b', 36, t['text'], ls=-1)
    s.chip(36, 166, d['badge'], 13, 1.5, 12, 28)
    for i, line in enumerate(wrap(d['text'], 'r', 18.5, W - 72)[:5]):
        s.text(36, 234 + i * 27, line, 'r', 18.5, t['muted'])
    x = 36
    for tag in d['tags']:
        x += s.tag(x, H - 58, tag) + 8
    return s


def climate(theme):
    d = P.CLIMATE
    W, H = 1280, 420
    s = Svg(W, H, theme, f'{d["title"]}: {d["text"]}')
    t = s.t
    s.css.append(FADE_CSS)
    s.panel(22)
    s.icon(d['icon'], 40, 40, 56)
    s.text(40, 154, d['title'], 'b', 40, t['text'], ls=-1)
    s.chip(40, 176, d['badge'], 13, 1.5, 12, 28)
    for i, line in enumerate(wrap(d['text'], 'r', 19, 600)[:4]):
        s.text(40, 244 + i * 28, line, 'r', 19, t['muted'])
    x = 40
    for tag in d['tags']:
        x += s.tag(x, H - 60, tag) + 8
    # 2x2 stats on the right
    gx, gy, cw, ch = 730, 64, 255, 150
    s.add(f'<line x1="{gx - 34}" y1="44" x2="{gx - 34}" y2="{H - 44}" stroke="{t["faint"]}"/>')
    for i, (big, label) in enumerate(d['stats']):
        cx, cy = gx + (i % 2) * cw, gy + (i // 2) * ch
        s.add(f'<g class="f d{i + 2}">')
        s.text(cx, cy + 72, big, 'b', 60, t['text'], ls=-2)
        s.text(cx, cy + 104, label, 'r', 18, t['muted'])
        s.add('</g>')
    return s


def systems(theme):
    W, H = 1280, 330
    s = Svg(W, H, theme, 'Built from scratch: ' + '; '.join(f'{x[1]}: {x[2]}' for x in P.SYSTEMS))
    t = s.t
    s.css.append(FADE_CSS)
    s.panel()
    s.text(48, 62, 'BUILT FROM SCRATCH', 'mono', 16, t['text'], ls=3)
    s.text(W - 48, 62, 'IMPERIAL COURSEWORK  ·  CODE PRIVATE', 'mono', 14, t['muted'], 'end', ls=2)
    s.add(f'<line x1="48" y1="90" x2="{W - 48}" y2="90" stroke="{t["faint"]}"/>')
    cw = (W - 96) / len(P.SYSTEMS)
    for i, (icon, title, text) in enumerate(P.SYSTEMS):
        x = 48 + i * cw + (0 if i == 0 else 28)
        if i:
            s.add(f'<line x1="{48 + i * cw:.1f}" y1="116" x2="{48 + i * cw:.1f}" y2="{H - 36}" stroke="{t["faint"]}"/>')
        s.add(f'<g class="f d{i + 1}">')
        s.icon(icon, x, 118, 48)
        s.text(x, 202, title, 's', 21, t['text'])
        for j, line in enumerate(wrap(text, 'r', 16.5, cw - 52)[:4]):
            s.text(x, 230 + j * 23, line, 'r', 16.5, t['muted'])
        s.add('</g>')
    return s


def header(s, label, right=None, y=62):
    t = s.t
    s.text(48, y, label, 'mono', 16, t['text'], ls=3)
    if right:
        s.text(s.w - 48, y, right, 'mono', 14, t['muted'], 'end', ls=2)
    s.add(f'<line x1="48" y1="{y + 28}" x2="{s.w - 48}" y2="{y + 28}" stroke="{t["faint"]}"/>')


def highlights(theme):
    W, H = 1280, 150
    s = Svg(W, H, theme, 'Highlights: ' + '; '.join(f'{a}, {b}' for _, a, b in P.HIGHLIGHTS))
    t = s.t
    s.panel()
    cw = (W - 64) / len(P.HIGHLIGHTS)
    for i, (glyph, title, sub) in enumerate(P.HIGHLIGHTS):
        x = 32 + i * cw + 16
        if i:
            s.add(f'<line x1="{32 + i * cw:.1f}" y1="34" x2="{32 + i * cw:.1f}" y2="{H - 34}" stroke="{t["faint"]}"/>')
        s.icon('glyph:' + glyph, x, 47, 56)
        room = cw - 74 - 28
        size = 16
        while size > 12 and measure(sub, 'r', size) > room:
            size -= 0.5
        s.text(x + 74, 72, title, 'b', 23, t['text'], ls=-0.5)
        s.text(x + 74, 98, sub, 'r', size, t['muted'])
    return s


def flow_chips(s, x0, y, items, max_x, size=14):
    x = x0
    for item in items:
        w = measure(item, 'mono', size) + 26
        if x + w > max_x:
            x, y = x0, y + 40
        s.add(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="30" rx="15" fill="{s.t["chip"]}" stroke="{s.t["chipline"]}"/>')
        s.text(x + 13, y + 20, item, 'mono', size, s.t['text'])
        x += w + 8
    return y + 30


def now_block(theme):
    W = 1280
    # Lay out first to know the height.
    rows = []
    for glyph, title, text, chips in P.NOW_ITEMS:
        lines = wrap(text, 'r', 18, W - 220) if text else []
        rows.append((glyph, title, lines, chips))
    def chips_height(chips):
        if not chips:
            return 0
        x, rows_ = 132, 1
        for c in chips:
            w = measure(c, 'mono', 14) + 34
            if x + w > W - 48:
                x, rows_ = 132, rows_ + 1
            x += w
        return rows_ * 40
    H = 112 + sum(56 + len(l) * 26 + chips_height(c) + 22 for _, _, l, c in rows) + 10
    s = Svg(W, H, theme, 'Now: ' + '; '.join(r[1] for r in P.NOW_ITEMS))
    t = s.t
    s.panel()
    header(s, 'NOW')
    y = 116
    for i, (glyph, title, lines, chips) in enumerate(rows):
        if i:
            s.add(f'<line x1="132" y1="{y - 12}" x2="{W - 48}" y2="{y - 12}" stroke="{t["faint"]}" stroke-opacity=".7"/>')
        s.icon('glyph:' + glyph, 48, y, 56)
        s.text(132, y + 24, title, 's', 21, t['text'])
        yy = y + 52
        for line in lines:
            s.text(132, yy, line, 'r', 18, t['muted'])
            yy += 26
        if chips:
            yy = flow_chips(s, 132, yy - 16, chips, W - 48) + 10
        y = max(yy, y + 56) + 22
    return s


def label(theme, text, right=''):
    W, H = 1280, 64
    s = Svg(W, H, theme, text)
    t = s.t
    s.text(4, 40, text, 'mono', 17, t['text'], ls=3)
    w = measure(text, 'mono', 17, 3)
    s.add(f'<line x1="{w + 24:.1f}" y1="34" x2="{W - 4 - (measure(right, "mono", 14, 2) + 20 if right else 0):.1f}" y2="34" stroke="{t["faint"]}"/>')
    if right:
        s.text(W - 4, 40, right, 'mono', 14, t['muted'], 'end', ls=2)
    return s


def research(theme):
    W = 1280
    chip_w = lambda v: measure(v, 'mono', 12, 1.5) + 24
    items = [(wrap(title, 's', 20, W - 132 - 48 - chip_w(venue) - 32), authors, venue) for title, authors, venue in P.RESEARCH]
    H = 112 + sum(len(tl) * 28 + 70 for tl, _, _ in items) + 10
    s = Svg(W, H, theme, 'Research: ' + '; '.join(r[0] for r in P.RESEARCH))
    t = s.t
    s.panel()
    header(s, 'RESEARCH', 'GOOGLE SCHOLAR  ↗')
    y = 118
    for i, (tl, authors, venue) in enumerate(items):
        if i:
            s.add(f'<line x1="132" y1="{y - 16}" x2="{W - 48}" y2="{y - 16}" stroke="{t["faint"]}" stroke-opacity=".7"/>')
        s.icon('glyph:paper', 48, y - 2, 56)
        for j, line in enumerate(tl):
            s.text(132, y + 20 + j * 28, line, 's', 20, t['text'])
        yy = y + 20 + len(tl) * 28
        s.text(132, yy, authors, 'r', 16, t['muted'])
        s.chip(W - 48 - measure(venue, 'mono', 12, 1.5) - 24, y + 2, venue, 12, 1.5, 12, 26)
        y = yy + 46
    return s


def leadership(theme):
    W = 1280
    cols = 3
    cw = (W - 96) / cols
    cells = [(g, title, wrap(text, 'r', 16.5, cw - 120)) for g, title, text in P.LEADERSHIP]
    rows = math.ceil(len(cells) / cols)
    row_h = [max(64 + len(c[2]) * 23 for c in cells[r * cols:(r + 1) * cols]) + 24 for r in range(rows)]
    H = 112 + sum(row_h) + 8
    s = Svg(W, H, theme, 'Leadership and more: ' + '; '.join(f'{a}: {b}' for _, a, b in P.LEADERSHIP))
    t = s.t
    s.panel()
    header(s, 'LEADERSHIP & MORE')
    y = 116
    for r in range(rows):
        for c in range(cols):
            k = r * cols + c
            if k >= len(cells):
                break
            glyph, title, lines = cells[k]
            x = 48 + c * cw
            s.icon('glyph:' + glyph, x, y, 52)
            s.text(x + 70, y + 22, title, 's', 19, t['text'])
            for j, line in enumerate(lines):
                s.text(x + 70, y + 48 + j * 23, line, 'r', 16.5, t['muted'])
        y += row_h[r]
        if r < rows - 1:
            s.add(f'<line x1="48" y1="{y - 12}" x2="{W - 48}" y2="{y - 12}" stroke="{t["faint"]}" stroke-opacity=".7"/>')
    return s


def skill_icons(ids):
    cache = os.path.join(HERE, 'cache')
    os.makedirs(cache, exist_ok=True)
    path = os.path.join(cache, ids.replace(',', '-') + '.svg')
    if not os.path.exists(path):
        import urllib.request
        req = urllib.request.Request(f'https://skillicons.dev/icons?i={ids}&theme=dark', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as r, open(path, 'wb') as f:
            f.write(r.read())
    with open(path, 'rb') as f:
        return 'data:image/svg+xml;base64,' + base64.b64encode(f.read()).decode(), len(ids.split(','))


def stack(theme):
    W = 1280
    H = 112 + len(P.STACK) * 104 + 6
    s = Svg(W, H, theme, 'Stack: ' + '; '.join(ids for _, ids in P.STACK))
    t = s.t
    s.defs.append('<filter id="mono"><feColorMatrix type="saturate" values="0"/></filter>')
    s.panel()
    header(s, 'STACK')
    y = 120
    for name, ids in P.STACK:
        uri, n = skill_icons(ids)
        s.text(48, y + 40, name, 'mono', 13, t['muted'], ls=2)
        icon, gap = 60, 12
        s.add(f'<image x="300" y="{y + 8}" width="{n * icon + (n - 1) * gap}" height="{icon}" href="{uri}" filter="url(#mono)"/>')
        y += 104
    return s


def side(theme):
    glyph, title, text, _ = P.SIDE
    W, H = 1280, 112
    s = Svg(W, H, theme, f'On the side: {title}. {text}')
    t = s.t
    s.panel(22)
    s.icon(glyph, 32, 28, 56)
    s.text(110, 50, 'ON THE SIDE', 'mono', 13, t['muted'], ls=2)
    s.text(110, 80, title, 's', 21, t['text'])
    s.text(110 + measure(title, 's', 21) + 16, 80, text, 'r', 17, t['muted'])
    s.text(W - 36, 66, '↗', 'm', 24, t['muted'], 'end')
    return s


def year(theme):
    import datetime as dt
    W = 1280
    end = dt.date(*P.YEAR_END)
    start = dt.date(*P.YEAR_START)
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)  # weeks start on Sunday
    days = (end - start).days + 1
    weeks = math.ceil(days / 7)
    gx, gy = 168, 142
    pitch = int((W - gx - 48) // weeks)
    gap = 3
    cell = pitch - gap
    lane_hs = [40, 54]  # main line, alongside line (room for two-line labels)
    lanes_top = gy + 7 * (cell + gap) + 30
    H = lanes_top + sum(lane_hs) + 66
    s = Svg(W, H, theme, 'Work since July 2025. ' + '. '.join(
        f'{lane}: ' + ', '.join(item[2] for item in items) for lane, items in P.YEAR_TRACKS))
    t = s.t
    levels = (['#161616', '#3a3a3a', '#6e6e6e', '#a8a8a8', '#f2f2f2'] if theme == 'dark'
              else ['#ededed', '#c9c9c9', '#8c8c8c', '#4a4a4a', '#0a0a0a'])
    s.panel()
    first = dt.date(*P.YEAR_START)
    header(s, f'WORK  ·  {MONTHS[first.month - 1].upper()} {first.year} → NOW', 'PUBLIC + PRIVATE')

    gitlab = {}
    gl_cache = os.path.join(HERE, 'cache', 'gitlab.json')
    if os.path.exists(gl_cache):
        with open(gl_cache) as f:
            gitlab = json.load(f)
    periods = [(dt.date(*a), dt.date(*b), wd, we) for a, b, wd, we, src in P.YEAR_PERIODS
               if not (gitlab and src == 'gitlab')]

    terms = [(dt.date(*a), dt.date(*b)) for a, b in P.YEAR_TERMS]

    def intensity(d):
        extra = P.YEAR_COURSEWORK if not gitlab and any(a <= d <= b for a, b in terms) else 0
        for a, b, wd, we in periods:
            if a <= d <= b:
                return min(1, (wd if d.weekday() < 5 else we) + extra)
        return P.YEAR_BACKGROUND + extra

    rnd = random.Random(2026)
    month_done = set()
    real = {}
    cache = os.path.join(HERE, 'cache', 'contributions.json')
    if os.path.exists(cache):
        with open(cache) as f:
            real = json.load(f)

    def real_level(n):
        return 0 if n == 0 else 1 if n <= 2 else 2 if n <= 6 else 3 if n <= 14 else 4
    for i in range(days):
        d = start + dt.timedelta(days=i)
        col, row = i // 7, i % 7
        x, y = gx + col * (cell + gap), gy + row * (cell + gap)
        p = intensity(d)
        # Busy periods mean most days have commits, at varying volumes.
        v = p * (0.25 + rnd.random()) if rnd.random() < p + 0.05 else 0
        lvl = 0 if v < 0.12 else 1 if v < 0.3 else 2 if v < 0.5 else 3 if v < 0.74 else 4
        key = d.isoformat()
        lvl = max(lvl, real_level(real.get(key, 0) + gitlab.get(key, 0)))
        s.add(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{levels[lvl]}"/>')
        if d.day <= 7 and row == 0 and (d.year, d.month) not in month_done:
            month_done.add((d.year, d.month))
            s.text(x, gy - 14, MONTHS[d.month - 1], 'mono', 13, t['muted'])
    for row, name in ((1, 'Mon'), (3, 'Wed'), (5, 'Fri')):
        s.text(gx - 14, gy + row * (cell + gap) + 13, name, 'mono', 12, t['muted'], 'end')
    xt = gx + ((days - 1) // 7) * (cell + gap)
    yt = gy + ((days - 1) % 7) * (cell + gap)
    s.add(f'<rect x="{xt - 3}" y="{yt - 3}" width="{cell + 6}" height="{cell + 6}" rx="6" fill="none" stroke="{t["text"]}" stroke-width="1.5"/>')

    # Parallel tracks under the grid, on the same time axis.
    def X(d):
        return gx + (d - start).days / 7 * (cell + gap)

    x_end = gx + weeks * (cell + gap) - gap
    y = lanes_top
    for k, (lane, items) in enumerate(P.YEAR_TRACKS):
        lane_h = lane_hs[min(k, 1)]
        main = k == 0
        s.text(gx - 14, y + lane_h / 2 + 4, lane, 'mono', 11, t['muted'], 'end', ls=1)
        for a, b, label in items:
            x1, x2 = X(dt.date(*a)), min(X(dt.date(*b)) + cell, x_end)
            bh = 26 if main else 46
            by = y + (lane_h - bh) / 2
            size = 13 if main else 12.5
            font = 's' if main else 'm'
            if main:
                s.add(f'<rect x="{x1:.1f}" y="{by:.1f}" width="{x2 - x1:.1f}" height="{bh}" rx="7" fill="{t["text"]}"/>')
                inside = measure(label, font, size) + 20 <= x2 - x1
                ink, tx = (t['panel'], x1 + 10) if inside else (t['text'], x2 + 8)
                s.text(tx, by + 17.5, label, font, size, ink)
            else:
                s.add(f'<rect x="{x1 + 0.75:.1f}" y="{by + 0.75:.1f}" width="{x2 - x1 - 1.5:.1f}" height="{bh - 1.5}" rx="7" fill="none" stroke="{t["text"]}" stroke-opacity=".55" stroke-width="1.5"/>')
                lines = wrap(label, font, size, x2 - x1 - 18)[:2]
                top = by + bh / 2 - (len(lines) - 1) * 8 + 4.5
                for j, line in enumerate(lines):
                    s.text(x1 + 10, top + j * 16, line, font, size, t['text'])
        y += lane_h

    # Legend and note
    ly = H - 30
    note = ('GitHub and Imperial GitLab days are exact. Sarvam and Bending Spoons work is estimated.' if gitlab
            else 'Public GitHub days are exact. Private work (Sarvam, Imperial GitLab, Bending Spoons) is estimated.')
    s.text(48, ly, note, 'r', 14, t['muted'])
    lx = W - 48 - 5 * (14 + 4) - measure('More', 'mono', 12)
    s.text(lx - 10 - 0, ly, 'Less', 'mono', 12, t['muted'], 'end')
    for k, c in enumerate(levels):
        s.add(f'<rect x="{lx + k * 18:.1f}" y="{ly - 12}" width="14" height="14" rx="3" fill="{c}"/>')
    s.text(lx + 5 * 18 + 4, ly, 'More', 'mono', 12, t['muted'])
    return s


def main():
    os.makedirs(ASSETS, exist_ok=True)
    built = []
    for theme in THEMES:
        built.append(save('hero', theme, hero(theme)))
        built.append(save('highlights', theme, highlights(theme)))
        built.append(save('now', theme, now_block(theme)))
        built.append(save('label-work', theme, label(theme, 'SELECTED WORK')))
        built.append(save('research', theme, research(theme)))
        built.append(save('leadership', theme, leadership(theme)))
        built.append(save('stack', theme, stack(theme)))
        built.append(save('side', theme, side(theme)))
        built.append(save('year', theme, year(theme)))
        built.append(save('timeline', theme, timeline(theme)))
        built.append(save('impact', theme, impact(theme)))
        built.append(save('climate', theme, climate(theme)))
        built.append(save('systems', theme, systems(theme)))
        for key, d in P.PROJECTS.items():
            built.append(save(f'card-{key}', theme, card(theme, key, d)))
    for path in built:
        print(f'{os.path.getsize(path) / 1024:6.1f} KB  {os.path.relpath(path, ROOT)}')
    import readme
    readme.build()
    print('README.md written')


if __name__ == '__main__':
    main()
