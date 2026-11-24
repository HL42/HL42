#!/usr/bin/env python3
"""Render actual public GitHub events. No writes to GitHub; stdlib only."""
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.parse import quote
import argparse, json, os, re, urllib.request

REPO = re.compile(r'HL42/[A-Za-z0-9_.-]+\Z')
SHA = re.compile(r'[0-9a-f]{40}\Z')
START, END = '<!-- ACTIVITY:START -->', '<!-- ACTIVITY:END -->'

def select_events(raw):
    if not isinstance(raw, list):
        raise ValueError('GitHub events response must be a list; preserve previous snapshot.')
    events, seen = [], set()
    for event in raw:
        if not isinstance(event, dict):
            continue
        repo = event.get('repo', {}).get('name', '')
        if not isinstance(repo, str) or not REPO.fullmatch(repo) or repo == 'HL42/HL42':
            continue
        if event.get('actor', {}).get('login', '').lower() != 'hl42':
            continue
        try:
            at = datetime.strptime(event['created_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        except (KeyError, TypeError, ValueError):
            continue
        payload = event.get('payload') or {}
        event_id = str(event.get('id', ''))
        if not event_id or event_id in seen:
            continue
        url = 'https://github.com/' + repo
        kind = event.get('type')
        if kind == 'PushEvent':
            head = payload.get('head', '')
            if isinstance(head, str) and SHA.fullmatch(head):
                url += '/commit/' + head
                label = 'push ' + head[:7]
            else:
                label = 'push (commit SHA unavailable)'
                url += '/commits'
        elif kind == 'CreateEvent':
            ref_type, ref = payload.get('ref_type'), payload.get('ref')
            if ref_type == 'branch' and isinstance(ref, str):
                label = 'created branch ' + ref
                url += '/tree/' + quote(ref, safe='')
            elif ref_type == 'repository':
                label = 'created repository'
            else:
                continue
        else:
            continue
        seen.add(event_id)
        events.append({'id': event_id, 'at': at.strftime('%Y-%m-%d %H:%M UTC'), 'sort': at.isoformat(), 'repo': repo, 'label': label, 'url': url})
    return sorted(events, key=lambda e: (e['sort'], e['id']), reverse=True)[:5]

def render(events, fetched_at):
    header = '<samp>Public event snapshot · fetched ' + escape(fetched_at) + '<br>Source: GitHub public Events API · timestamps in UTC</samp>'
    lines = [header]
    for e in events:
        lines.append('<samp>' + escape(e['at']) + '<br><a href="' + escape(e['url'], quote=True) + '">' + escape(e['repo'] + ' · ' + e['label']) + '</a></samp>')
    if not events:
        lines.append('<samp>No eligible public push/branch events returned. This does not mean no work was done.</samp>')
    return '\n\n'.join(lines)

def update(root, raw, fetched_at):
    events = select_events(raw)
    path = root / 'README.md'
    text = path.read_text()
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) > text.index(END):
        raise ValueError('Expected exactly one ordered activity marker pair; refusing to modify README.')
    before, rest = text.split(START)
    _, after = rest.split(END)
    snapshot = {'source': 'https://api.github.com/users/HL42/events/public?per_page=100', 'fetched_at': fetched_at, 'scope': 'public push and branch-creation events; excludes Profile maintenance; not complete contribution history', 'events': events}
    path.write_text(before + START + '\n\n' + render(events, fetched_at) + '\n\n' + END + after)
    (root / 'activity.json').write_text(json.dumps(snapshot, indent=2) + '\n')
    return len(events)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--from-file', type=Path, help='Use a saved actual API response for reproducible offline builds')
    p.add_argument('--fetched-at', help='Original response capture time; only valid with --from-file')
    args = p.parse_args()
    if args.fetched_at and not args.from_file:
        p.error('--fetched-at requires --from-file')
    if args.from_file:
        raw = json.loads(args.from_file.read_text())
    else:
        headers = {'User-Agent': 'HL42-profile-activity', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
        if os.environ.get('GH_TOKEN'):
            headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
        with urllib.request.urlopen(urllib.request.Request('https://api.github.com/users/HL42/events/public?per_page=100', headers=headers), timeout=30) as response:
            raw = json.load(response)
    fetched_at = args.fetched_at or datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    root = Path(__file__).resolve().parents[1]
    print(f'Updated {update(root, raw, fetched_at)} actual public events locally. No remote writes.')

if __name__ == '__main__':
    main()
