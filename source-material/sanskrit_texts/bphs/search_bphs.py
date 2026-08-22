#!/usr/bin/env python3
"""Convenience runner for bphs search."""
import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from jyotish.scripture_db import main

if __name__ == '__main__':
    # Inject scripture key if not explicitly passed
    if '--scripture' not in sys.argv and '-s' not in sys.argv:
        sys.argv.insert(1, '-s')
        sys.argv.insert(2, 'bphs')
    main()
