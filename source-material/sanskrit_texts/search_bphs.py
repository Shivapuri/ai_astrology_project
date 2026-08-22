#!/usr/bin/env python3
"""Convenience runner for BPHS search."""
import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from jyotish.bphs_db import main

if __name__ == "__main__":
    main()
