"""Writes README.md from tools/profile.py, using the graphics in assets/."""

import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import profile as P  # noqa: E402

BASE = 'https://raw.githubusercontent.com/aryan-the-jain/aryan-the-jain/main/assets'


def pic(name, alt, width=None):
    w = f' width="{width}"' if width else ''
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{BASE}/{name}-dark.svg">'
            f'<img src="{BASE}/{name}-light.svg" alt="{html.escape(alt, quote=True)}"{w}></picture>')


def link(href, inner):
    return f'<a href="{html.escape(href, quote=True)}">{inner}</a>'


def row(items, width):
    return '<p align="center">' + '&nbsp;'.join(items) + '</p>'


def build():
    cards = {
        'alongside': 'https://github.com/aryan-the-jain/DRP_07',
        'p2p': 'https://github.com/kkorel/p2p-energy-trading',
        'sarvam': 'https://www.sarvam.ai',
        'eqip': 'https://github.com/aryan-the-jain/EQIP',
    }
    card = lambda k: link(cards[k], pic(f'card-{k}', f'{P.PROJECTS[k]["title"]}: {P.PROJECTS[k]["text"]}', '49%'))
    parts = [
        pic('hero', f'{P.NAME}. {P.TAGLINE} LinkedIn: aryanthejain. Email: aryanthejain@gmail.com.'),
        pic('highlights', 'Highlights: ' + '; '.join(f'{x[1]}, {x[2]}' for x in P.HIGHLIGHTS)),
        pic('now', 'Now: ' + '; '.join(x[1] for x in P.NOW_ITEMS)),
        pic('timeline', 'Experience: ' + '; '.join(f'{r[2]} at {r[1]}' for r in P.EXPERIENCE)),
        pic('impact', 'Bending Spoons, Harvest: ' + '; '.join(' '.join(x) for x in P.IMPACT['stats'])),
        pic('year', 'Work since July 2025, real commits plus estimated private work. ' + '. '.join(
            f'{lane}: ' + ', '.join(item[2] for item in items) for lane, items in P.YEAR_TRACKS)),
        pic('label-work', 'Selected work'),
        '<p>' + card('alongside') + '&nbsp;' + card('p2p') + '</p>',
        '<p>' + card('sarvam') + '&nbsp;' + card('eqip') + '</p>',
        link('https://climatetrace.org', pic('climate', f'{P.CLIMATE["title"]}: {P.CLIMATE["text"]}')),
        pic('systems', 'Built from scratch: ' + '; '.join(f'{x[1]}: {x[2]}' for x in P.SYSTEMS)),
        link('https://scholar.google.com/citations?user=-r_1bb0AAAAJ', pic('research', 'Research: ' + '; '.join(r[0] for r in P.RESEARCH))),
        pic('leadership', 'Leadership and more: ' + '; '.join(f'{x[1]}: {x[2]}' for x in P.LEADERSHIP)),
        pic('stack', 'Stack: ' + ', '.join(ids for _, ids in P.STACK)),
        link(P.SIDE[3], pic('side', f'On the side: {P.SIDE[1]}. {P.SIDE[2]}')),
    ]
    text = '\n\n'.join(parts) + '\n\n<!-- Generated: edit tools/profile.py, then run `python tools/build.py`. -->\n'
    with open(os.path.join(os.path.dirname(HERE), 'README.md'), 'w') as f:
        f.write(text)


if __name__ == '__main__':
    build()
