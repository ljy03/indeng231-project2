#!/usr/bin/env python3
"""
Q&A: ask questions against the compiled golf wiki.
Reads all markdown files, finds the most relevant ones, then answers using Claude.
"""

import os
import re
import anthropic

WIKI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wiki')

client = anthropic.Anthropic()

QA_PROMPT = """\
You are a golf expert assistant with access to a curated golf knowledge base.
Answer the user's question using ONLY the wiki articles provided below.
Be specific, cite article titles where relevant, and keep the answer concise (under 200 words).
If the answer cannot be found in the provided articles, say so.

Wiki articles:
---
{context}
---

Question: {question}

Answer:"""


def _load_wiki() -> dict:
    articles = {}
    for fname in os.listdir(WIKI_DIR):
        if fname.endswith('.md'):
            path = os.path.join(WIKI_DIR, fname)
            with open(path, encoding='utf-8') as f:
                articles[fname[:-3]] = f.read()
    return articles


def _rank_articles(question: str, articles: dict, top_k: int = 4) -> list:
    """Simple keyword overlap ranking — no external embeddings needed."""
    q_words = set(re.findall(r'\w+', question.lower()))
    scores = {}
    for slug, text in articles.items():
        words = set(re.findall(r'\w+', text.lower()))
        scores[slug] = len(q_words & words)
    ranked = sorted(scores, key=scores.get, reverse=True)
    # Always include INDEX
    top = [s for s in ranked if s != 'INDEX'][:top_k]
    return top


def ask(question: str) -> str:
    articles = _load_wiki()
    if not articles:
        return 'No wiki articles found. Run compile.py first.'

    relevant_slugs = _rank_articles(question, articles)
    context_parts = []
    for slug in relevant_slugs:
        context_parts.append(f'### {slug.replace("_", " ").title()}\n{articles[slug][:1500]}')
    context = '\n\n'.join(context_parts)

    resp = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=400,
        messages=[{
            'role': 'user',
            'content': QA_PROMPT.format(context=context, question=question)
        }]
    )
    return resp.content[0].text


def interactive():
    print('\nGolf Knowledge Base — Q&A')
    print('Type a question, or "quit" to exit.\n')
    while True:
        q = input('Q: ').strip()
        if not q or q.lower() in ('quit', 'exit', 'q'):
            break
        print(f'A: {ask(q)}\n')


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        print(ask(' '.join(sys.argv[1:])))
    else:
        interactive()
