"""Saves every commit you authored on Imperial GitLab, as counts per day, to
tools/cache/gitlab.json.

    python3 tools/fetch_gitlab.py

Asks for a personal access token (scope: read_api) without echoing it, walks every
project you're a member of, and keeps only {date: number of your commits}. No code,
project names or token are saved.
"""

import getpass
import json
import os
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get('GITLAB_URL', 'https://gitlab.doc.ic.ac.uk')


def get_all(path, token, **params):
    """Follows GitLab's pagination and returns every item."""
    items, page = [], 1
    while page:
        query = urllib.parse.urlencode({**params, 'per_page': 100, 'page': page})
        req = urllib.request.Request(f'{BASE}/api/v4{path}?{query}', headers={'PRIVATE-TOKEN': token})
        try:
            with urllib.request.urlopen(req) as r:
                items.extend(json.load(r))
                nxt = r.headers.get('X-Next-Page')
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):  # empty or inaccessible repository
                return items
            raise
        page = int(nxt) if nxt else 0
    return items


def main():
    token = os.environ.get('GITLAB_TOKEN') or getpass.getpass(f'GitLab token for {BASE} (read_api, hidden): ').strip()
    req = urllib.request.Request(f'{BASE}/api/v4/user', headers={'PRIVATE-TOKEN': token})
    with urllib.request.urlopen(req) as r:
        me = json.load(r)
    names = {me['name'].lower(), me['username'].lower()}
    emails = {e.lower() for e in [me.get('email'), me.get('public_email'), me.get('commit_email')] if e}
    emails |= {e['email'].lower() for e in get_all('/user/emails', token)}
    print(f'Signed in as {me["username"]}. Matching commits by {", ".join(sorted(emails | names))}')

    projects = get_all('/projects', token, membership='true', simple='true')
    print(f'{len(projects)} projects')
    days, seen = {}, set()
    for i, p in enumerate(projects, 1):
        commits = get_all(f'/projects/{p["id"]}/repository/commits', token, all='true')
        mine = 0
        for c in commits:
            if c['id'] in seen:
                continue
            author = {(c.get('author_email') or '').lower(), (c.get('author_name') or '').lower()}
            if author & (emails | names):
                seen.add(c['id'])
                day = c['authored_date'][:10]
                days[day] = days.get(day, 0) + 1
                mine += 1
        print(f'  [{i}/{len(projects)}] {mine} of your commits')

    os.makedirs(os.path.join(HERE, 'cache'), exist_ok=True)
    with open(os.path.join(HERE, 'cache', 'gitlab.json'), 'w') as f:
        json.dump(dict(sorted(days.items())), f, indent=0)
    span = f'{min(days)} → {max(days)}' if days else 'none'
    print(f'\n{sum(days.values())} commits on {len(days)} days ({span}). Saved tools/cache/gitlab.json')


if __name__ == '__main__':
    main()
