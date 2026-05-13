#!/usr/bin/env python3
"""
Golf Knowledge Base — entry point.

Usage:
    python run.py               # ingest + compile (build the wiki)
    python run.py --qa          # interactive Q&A against the wiki
    python run.py --ask "..."   # single question
    python run.py --compile     # recompile wiki only (skip ingest)
    python run.py --force       # force re-fetch and re-compile everything
"""

import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description='Golf Knowledge Base')
    parser.add_argument('--qa',      action='store_true', help='Interactive Q&A mode')
    parser.add_argument('--ask',     type=str,            help='Ask a single question')
    parser.add_argument('--compile', action='store_true', help='Compile wiki only')
    parser.add_argument('--force',   action='store_true', help='Re-fetch and re-compile')
    args = parser.parse_args()

    if args.qa:
        from qa import interactive
        interactive()
        return

    if args.ask:
        from qa import ask
        print(ask(args.ask))
        return

    if not args.compile:
        from ingest import ingest
        print('=== Step 1: Ingesting sources ===')
        ingest(force=args.force)

    from compile import compile_wiki
    print('\n=== Step 2: Compiling wiki ===')
    compile_wiki(force=args.force)

    print('\nDone! Wiki is in wiki/  — run with --qa to ask questions.')


if __name__ == '__main__':
    main()
