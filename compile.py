#!/usr/bin/env python3
"""
Compile: use Claude to turn raw source files into linked markdown wiki pages.
Each raw file becomes one wiki article with backlinks, summaries, and concepts.
An index file (wiki/INDEX.md) is maintained for Q&A navigation.
"""

import os
import re
import anthropic

RAW_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw')
WIKI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wiki')

client = anthropic.Anthropic()

ARTICLE_PROMPT = """\
You are building a personal golf knowledge-base wiki. I will give you raw scraped text \
about a golf topic. Your job is to write a clean, well-structured markdown wiki article.

Rules:
- Use proper markdown headings (## for sections, ### for subsections).
- Include a one-paragraph **Summary** at the top.
- Link related concepts using [[wiki-links]] — e.g. [[Masters Tournament]], [[Tiger Woods]], \
[[Golf Swing]]. Use the exact title of the target article.
- End with a ## Related section listing backlinks.
- Keep the article focused, factual, and under 800 words.
- Do NOT reproduce large raw text verbatim — synthesise and summarise.

Article title: {title}

Raw source text (may be noisy — extract the useful parts):
---
{raw_text}
---

Write the markdown article now:"""

INDEX_PROMPT = """\
You are maintaining the index for a golf knowledge-base wiki.
Below is a list of all wiki article titles with their one-line summaries.
Write a single markdown file (wiki/INDEX.md) that:
- Has a top-level # Golf Knowledge Base heading
- Has a brief intro paragraph (2–3 sentences) about the scope of this wiki
- Groups articles under logical ## Category headings (e.g. Fundamentals, Major Tournaments, \
Famous Golfers, Equipment & Courses, Rules & Scoring)
- Lists each article as a markdown link: [[Article Title]] — one-line summary
- Ends with a ## How to Use section (2–3 sentences on navigating the wiki)

Articles:
{article_list}

Write the INDEX.md now:"""


def _slug_to_title(slug: str) -> str:
    return slug.replace('_', ' ').title()


def _compile_article(slug: str, raw_text: str) -> str:
    title = _slug_to_title(slug)
    resp = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=1200,
        messages=[{
            'role': 'user',
            'content': ARTICLE_PROMPT.format(title=title, raw_text=raw_text[:8000])
        }]
    )
    return resp.content[0].text


def _compile_index(summaries: dict) -> str:
    article_list = '\n'.join(
        f'- {title}: {summary}' for title, summary in summaries.items()
    )
    resp = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=1000,
        messages=[{
            'role': 'user',
            'content': INDEX_PROMPT.format(article_list=article_list)
        }]
    )
    return resp.content[0].text


def _extract_summary(markdown: str) -> str:
    """Pull the first paragraph after the Summary heading."""
    m = re.search(r'(?:##\s*Summary\s*\n+)(.+?)(?:\n\n|\n##)', markdown, re.DOTALL)
    if m:
        return m.group(1).strip().replace('\n', ' ')[:150]
    lines = [l for l in markdown.split('\n') if l and not l.startswith('#')]
    return lines[0][:150] if lines else ''


def compile_wiki(force=False):
    os.makedirs(WIKI_DIR, exist_ok=True)
    raw_files = sorted(f for f in os.listdir(RAW_DIR) if f.endswith('.txt'))

    summaries = {}

    for fname in raw_files:
        slug = fname[:-4]
        title = _slug_to_title(slug)
        out_path = os.path.join(WIKI_DIR, f'{slug}.md')

        if os.path.exists(out_path) and not force:
            print(f'  [skip] {title}')
            with open(out_path, encoding='utf-8') as f:
                md = f.read()
            summaries[title] = _extract_summary(md)
            continue

        print(f'  [compile] {title} …', end=' ', flush=True)
        with open(os.path.join(RAW_DIR, fname), encoding='utf-8') as f:
            raw = f.read()

        md = _compile_article(slug, raw)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(md)
        summaries[title] = _extract_summary(md)
        print('ok')

    print('  [index] Building INDEX.md …', end=' ', flush=True)
    index_md = _compile_index(summaries)
    with open(os.path.join(WIKI_DIR, 'INDEX.md'), 'w', encoding='utf-8') as f:
        f.write(index_md)
    print('ok')

    print(f'Wiki compiled: {len(raw_files)} articles + index')
    return summaries


if __name__ == '__main__':
    print('Compiling wiki…')
    compile_wiki()
    print('Done.')
