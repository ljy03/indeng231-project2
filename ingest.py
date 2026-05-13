#!/usr/bin/env python3
"""
Ingest: fetch raw source content about a topic and save to raw/.
Uses urllib to pull text from URLs; strips HTML tags for clean text.
"""

import os
import re
import time
import urllib.request
import urllib.error
from html.parser import HTMLParser

RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw')

GOLF_SOURCES = [
    ("golf_overview",         "https://en.wikipedia.org/wiki/Golf"),
    ("golf_swing",            "https://en.wikipedia.org/wiki/Golf_swing"),
    ("golf_rules",            "https://en.wikipedia.org/wiki/Rules_of_golf"),
    ("golf_scoring",          "https://en.wikipedia.org/wiki/Golf_terminology"),
    ("masters_tournament",    "https://en.wikipedia.org/wiki/Masters_Tournament"),
    ("us_open_golf",          "https://en.wikipedia.org/wiki/U.S._Open_(golf)"),
    ("the_open_championship", "https://en.wikipedia.org/wiki/The_Open_Championship"),
    ("pga_championship",      "https://en.wikipedia.org/wiki/PGA_Championship"),
    ("tiger_woods",           "https://en.wikipedia.org/wiki/Tiger_Woods"),
    ("rory_mcilroy",          "https://en.wikipedia.org/wiki/Rory_McIlroy"),
    ("golf_clubs_equipment",  "https://en.wikipedia.org/wiki/Golf_club"),
    ("augusta_national",      "https://en.wikipedia.org/wiki/Augusta_National_Golf_Club"),
    ("st_andrews",            "https://en.wikipedia.org/wiki/St_Andrews_Links"),
    ("handicap_system",       "https://en.wikipedia.org/wiki/Golf_handicap"),
    ("short_game",            "https://en.wikipedia.org/wiki/Pitching_(golf)"),
]


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._skip = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'nav', 'footer', 'header'):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'nav', 'footer', 'header'):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            stripped = data.strip()
            if stripped:
                self.parts.append(stripped)


def _fetch_text(url: str, max_chars: int = 15000) -> str:
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (educational research bot)'
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='replace')

    parser = _TextExtractor()
    parser.feed(html)
    text = '\n'.join(parser.parts)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text[:max_chars]


def ingest(sources=None, force=False):
    os.makedirs(RAW_DIR, exist_ok=True)
    sources = sources or GOLF_SOURCES
    fetched = []
    for name, url in sources:
        out_path = os.path.join(RAW_DIR, f'{name}.txt')
        if os.path.exists(out_path) and not force:
            print(f'  [skip] {name} (already fetched)')
            fetched.append(name)
            continue
        try:
            print(f'  [fetch] {name} …', end=' ', flush=True)
            text = _fetch_text(url)
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(f'SOURCE: {url}\n\n{text}')
            print(f'{len(text):,} chars')
            fetched.append(name)
            time.sleep(0.5)
        except Exception as e:
            print(f'ERROR: {e}')
    return fetched


if __name__ == '__main__':
    print('Ingesting golf sources…')
    ingest()
    print('Done.')
