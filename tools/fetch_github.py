"""Saves your public GitHub contribution counts per day to tools/cache/contributions.json.

    python tools/fetch_github.py   (needs the gh CLI, logged in)

The heatmap uses these real counts and only estimates days GitHub can't see.
"""

import datetime as dt
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import profile as P  # noqa: E402

QUERY = '''query($from: DateTime!, $to: DateTime!) { viewer { contributionsCollection(from: $from, to: $to) {
  contributionCalendar { weeks { contributionDays { date contributionCount } } } } } }'''


def fetch(start, end):
    out = subprocess.run(['gh', 'api', 'graphql', '-f', f'query={QUERY}', '-F', f'from={start}T00:00:00Z', '-F', f'to={end}T23:59:59Z'],
                         check=True, capture_output=True, text=True).stdout
    weeks = json.loads(out)['data']['viewer']['contributionsCollection']['contributionCalendar']['weeks']
    return {d['date']: d['contributionCount'] for w in weeks for d in w['contributionDays']}


def main():
    start, end = dt.date(*P.YEAR_START), dt.date(*P.YEAR_END)
    days = {}
    cursor = start
    while cursor <= end:  # the API allows at most a year per request
        chunk_end = min(end, cursor + dt.timedelta(days=360))
        days.update(fetch(cursor.isoformat(), chunk_end.isoformat()))
        cursor = chunk_end + dt.timedelta(days=1)
    os.makedirs(os.path.join(HERE, 'cache'), exist_ok=True)
    with open(os.path.join(HERE, 'cache', 'contributions.json'), 'w') as f:
        json.dump(dict(sorted(days.items())), f, indent=0)
    active = {k: v for k, v in days.items() if v}
    print(f'{len(days)} days, {len(active)} with contributions, {sum(active.values())} total')
    print(' '.join(f'{k}={v}' for k, v in active.items()))


if __name__ == '__main__':
    main()
