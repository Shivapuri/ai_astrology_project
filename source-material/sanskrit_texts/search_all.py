#!/usr/bin/env python3
"""Convenience CLI runner for Multi-Scripture Jyotisha Search."""
import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from jyotish.scripture_db import main

if __name__ == "__main__":
    main()
