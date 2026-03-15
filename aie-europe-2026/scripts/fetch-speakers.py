#!/usr/bin/env python3
"""Fetch and display AI Engineer Europe 2026 speakers.

Usage:
    python scripts/fetch-speakers.py                    # All speakers
    python scripts/fetch-speakers.py --search Google    # Search by name/company
    python scripts/fetch-speakers.py --company          # Group by company
    python scripts/fetch-speakers.py --with-github      # Only speakers with GitHub
"""

import argparse
import json
import sys
from collections import Counter
from urllib.request import urlopen

SPEAKERS_URL = 'https://ai.engineer/europe/speakers.json'


def fetch_speakers() -> dict:
    with urlopen(SPEAKERS_URL) as resp:
        return json.loads(resp.read())


def main():
    parser = argparse.ArgumentParser(description='Query AIE Europe 2026 speakers')
    parser.add_argument('--search', type=str, help='Search speakers by name or company')
    parser.add_argument('--company', action='store_true', help='Group speakers by company')
    parser.add_argument('--with-github', action='store_true', help='Only show speakers with GitHub')
    parser.add_argument('--json', action='store_true', help='Output raw JSON')
    args = parser.parse_args()

    data = fetch_speakers()
    speakers = data['speakers']

    if args.search:
        term = args.search.lower()
        speakers = [s for s in speakers
                    if term in s.get('name', '').lower()
                    or term in (s.get('company') or '').lower()
                    or term in (s.get('role') or '').lower()]

    if args.with_github:
        speakers = [s for s in speakers if s.get('github')]

    if args.json:
        print(json.dumps(speakers, indent=2))
        return

    if args.company:
        companies = Counter(s.get('company') for s in speakers if s.get('company'))
        for company, count in companies.most_common():
            print(f"  {company}: {count}")
        print(f"\n{len(companies)} companies, {len(speakers)} speakers")
        return

    print(f"{len(speakers)} speakers (of {data['totalSpeakers']} total)\n")
    for s in speakers:
        talks = ', '.join(t['title'] for t in s.get('talks', []) if t.get('title'))
        company = f" @ {s['company']}" if s.get('company') else ''
        role = f" ({s['role']})" if s.get('role') else ''
        github = f" [GH: {s['github']}]" if s.get('github') else ''
        print(f"  {s['name']}{role}{company}{github}")
        if talks:
            print(f"    Talks: {talks}")


if __name__ == '__main__':
    main()
