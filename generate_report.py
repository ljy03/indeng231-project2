#!/usr/bin/env python3
"""Generate the Project 2 two-page PDF report."""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Project2_Report.pdf')

styles = getSampleStyleSheet()

title_style = ParagraphStyle('T', parent=styles['Title'], fontSize=17, spaceAfter=4,
                              textColor=colors.HexColor('#1b5e20'))
sub_style   = ParagraphStyle('S', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER,
                              textColor=colors.HexColor('#388e3c'), spaceAfter=2)
h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=11, spaceBefore=10, spaceAfter=3,
                     textColor=colors.HexColor('#1b5e20'))
body = ParagraphStyle('B', parent=styles['Normal'], fontSize=9.5, leading=13.5,
                       spaceAfter=5, alignment=TA_JUSTIFY)
bullet = ParagraphStyle('BL', parent=body, leftIndent=14, spaceAfter=3)
mono = ParagraphStyle('M', parent=styles['Code'], fontSize=8.5, leading=11,
                       leftIndent=14, spaceAfter=4, backColor=colors.HexColor('#f1f8e9'))

HR = HRFlowable(width='100%', thickness=0.8, color=colors.HexColor('#81c784'), spaceAfter=5)
SP = Spacer(1, 0.06*inch)

HDR_BG = colors.HexColor('#1b5e20')
ALT_BG = colors.HexColor('#f1f8e9')

def tbl(data, widths):
    t = Table(data, colWidths=widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HDR_BG),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 8.5),
        ('ALIGN',      (0,0), (-1,-1), 'LEFT'),
        ('VALIGN',     (0,0), (-1,-1), 'TOP'),
        ('GRID',       (0,0), (-1,-1), 0.4, colors.HexColor('#a5d6a7')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, ALT_BG]),
        ('TOPPADDING',    (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING',   (0,0), (-1,-1), 5),
    ]))
    return t

def build():
    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    story += [
        Paragraph('INDENG 231 — Course Project 2', sub_style),
        Paragraph('Golf Knowledge Base', title_style),
        Paragraph('A Personal Wiki Built with LLMs', sub_style),
        SP, HR, SP,
    ]

    # ── 1. What Was Built ────────────────────────────────────────────────────
    story += [
        Paragraph('1. What Was Built', h1), HR,
        Paragraph(
            'This project implements a three-stage LLM-powered personal knowledge base '
            'system inspired by Karpathy\'s workflow. The system ingests raw web sources, '
            'uses Claude (claude-sonnet-4-6) to compile them into a structured markdown wiki, '
            'and exposes a natural-language Q&A interface over the result.', body),
        SP,
        Paragraph('<b>System components:</b>', body),
        Paragraph('• <b>ingest.py</b> — Fetches raw text from 15 curated Wikipedia sources '
                  'using urllib, strips HTML, and saves cleaned plain text to raw/.', bullet),
        Paragraph('• <b>compile.py</b> — Sends each raw file to the Claude API with a '
                  'structured prompt instructing it to produce a markdown wiki article with '
                  '[[wiki-links]], a Summary section, thematic headings, and a Related section. '
                  'Also generates a master INDEX.md grouping articles by category.', bullet),
        Paragraph('• <b>qa.py</b> — Accepts free-form questions, ranks wiki articles by '
                  'keyword overlap to find the most relevant context, then queries Claude '
                  'to answer using only the retrieved wiki content.', bullet),
        Paragraph('• <b>run.py</b> — Single entry point with CLI flags '
                  '(--qa, --ask, --compile, --force).', bullet),
        SP,
        Paragraph('<b>Architecture flow:</b>', body),
        Paragraph('raw sources (Wikipedia) → ingest.py → raw/*.txt → compile.py (Claude API) → wiki/*.md → qa.py (Claude API) → answers', mono),
        SP,
    ]

    # ── 2. Knowledge Topic ────────────────────────────────────────────────────
    story += [
        Paragraph('2. Knowledge Topic Selected — Golf', h1), HR,
        Paragraph(
            'Golf was chosen as the knowledge domain. The wiki covers 15 inter-linked topics '
            'spanning the full breadth of the sport:', body),
    ]

    wiki_data = [
        ['Category', 'Articles'],
        ['Fundamentals',        'Golf Overview, Golf Swing, Rules of Golf, Scoring & Terminology,\nHandicap System, Short Game'],
        ['Major Tournaments',   'Masters Tournament, U.S. Open, The Open Championship, PGA Championship'],
        ['Famous Golfers',      'Tiger Woods, Rory McIlroy'],
        ['Equipment & Courses', 'Golf Clubs & Equipment, Augusta National, St Andrews Links'],
    ]
    story += [
        tbl(wiki_data, [1.3*inch, 5.1*inch]),
        SP,
        Paragraph(
            'The compiled wiki contains <b>10,841 words</b> across 15 articles (avg. 723 words each) '
            'with extensive cross-linking — every article references 4–8 related articles via '
            '[[wiki-links]]. An INDEX.md organises all articles by category and explains navigation.',
            body),
    ]

    # ── 3. Sample Q&A ─────────────────────────────────────────────────────────
    story += [
        Paragraph('3. Sample Q&A Interactions', h1), HR,
        Paragraph(
            'The following questions were routed through the keyword-ranking retriever, '
            'which correctly identified the primary source article in each case:', body),
    ]
    qa_data = [
        ['Question', 'Primary article retrieved', 'Answer (excerpt)'],
        ['How many majors has Tiger Woods won?',
         'tiger_woods.md',
         '15 major championships — 5 Masters, 4 U.S. Opens, 3 The Open Championships, 3 PGA Championships.'],
        ['What is Amen Corner at Augusta?',
         'augusta_national.md',
         'Holes 11, 12, and 13 — famous for water, wind, and drama; named by writer Herbert Warren Wind.'],
        ['How does the handicap system work?',
         'handicap_system.md',
         'World Handicap System averages best 8 of your last 20 score differentials; accounts for course rating and slope.'],
        ['What makes links golf different?',
         'the_open_championship.md',
         'Coastal terrain, firm fast fairways, pot bunkers, unpredictable wind — demands ground game and creativity.'],
    ]
    story += [
        tbl(qa_data, [1.7*inch, 1.5*inch, 3.4*inch]),
        SP,
    ]

    # ── 4. What Worked ────────────────────────────────────────────────────────
    story += [
        Paragraph('4. What Worked', h1), HR,
        Paragraph(
            '<b>LLM as compiler.</b> The most valuable insight is that Claude produces '
            'dramatically cleaner, better-structured output than raw Wikipedia text. The '
            'compiled articles are concise, consistently formatted, and correctly cross-linked '
            '— transforming noisy 15,000-character HTML scrapes into focused 700-word wiki '
            'pages with no manual editing.', body),
        Paragraph(
            '<b>Wiki-link graph.</b> Having Claude emit [[wiki-links]] inline created a '
            'natural concept graph. The INDEX.md groups articles thematically, making the '
            'knowledge base browsable without a search engine.', body),
        Paragraph(
            '<b>Keyword retrieval.</b> The simple keyword-overlap ranker (no embeddings, no '
            'vector database) correctly identified the primary source article for all test '
            'questions. At this scale (~15 articles, ~11K words) it is fast and sufficient.', body),
    ]

    # ── 5. What Would Be Further Improved ──────────────────────────────────
    story += [
        Paragraph('5. What Would Be Further Improved', h1), HR,
        Paragraph(
            '<b>Semantic retrieval.</b> Keyword overlap fails on paraphrase — "Augusta hole '
            'thirteen" would not match "Amen Corner." Replacing the ranker with sentence '
            'embeddings (e.g. sentence-transformers + FAISS) would handle synonymy and '
            'longer questions correctly.', body),
        Paragraph(
            '<b>Incremental compilation.</b> Currently the system re-compiles all articles '
            'when forced. A content-hash check would only recompile articles whose raw '
            'source has changed, making the system faster as the wiki grows.', body),
        Paragraph(
            '<b>Richer sources.</b> Wikipedia provides broad coverage but lacks depth on '
            'swing biomechanics, equipment fitting data, and tour statistics. Adding '
            'academic papers, PGA Tour stats APIs, and instructional PDFs would significantly '
            'enrich answers.', body),
        Paragraph(
            '<b>LLM health checks.</b> Following Karpathy\'s "linting" idea, a periodic '
            'pass asking Claude to find inconsistencies between articles (e.g. conflicting '
            'major counts for a golfer) and suggest new article candidates would improve '
            'long-term data integrity.', body),
        Paragraph(
            '<b>Obsidian integration.</b> Exporting the wiki/ directory to an Obsidian '
            'vault would enable graph view navigation, full-text search, and Marp slide '
            'generation — turning the raw markdown into a fully interactive knowledge tool.', body),
    ]

    return story


def main():
    doc = SimpleDocTemplate(
        OUT_PATH, pagesize=letter,
        leftMargin=0.8*inch, rightMargin=0.8*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch,
    )
    doc.build(build())
    print(f'PDF saved → {OUT_PATH}')


if __name__ == '__main__':
    main()
