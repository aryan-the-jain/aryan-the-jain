"""Builds the profile graphics in assets/ from tools/profile.py.

    pip install pillow fonttools
    python tools/build.py

Every SVG comes in a light and a dark version and embeds subsetted fonts, so it
renders the same everywhere GitHub shows it.
"""

import base64
import io
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
    s.add('<g class="f d4">')
    for chip in P.CHIPS:
        cx += s.chip(cx, 352, chip, 15) + 10
    s.add('</g>')
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
    W, H = 1280, 270
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


def main():
    os.makedirs(ASSETS, exist_ok=True)
    built = []
    for theme in THEMES:
        built.append(save('hero', theme, hero(theme)))
        built.append(save('timeline', theme, timeline(theme)))
        built.append(save('impact', theme, impact(theme)))
        built.append(save('climate', theme, climate(theme)))
        built.append(save('systems', theme, systems(theme)))
        for key, d in P.PROJECTS.items():
            built.append(save(f'card-{key}', theme, card(theme, key, d)))
    for path in built:
        print(f'{os.path.getsize(path) / 1024:6.1f} KB  {os.path.relpath(path, ROOT)}')


if __name__ == '__main__':
    main()
