# ADR 004: Unified Engine Architecture

## Status
Accepted

## Context
The Astra project initially contained legacy attempts at building separate `/western/` and `/jyotish/` engines. This created redundant code, split logic for ephemeris fetching, and confusion over which engine handled which calculation (since Kala methodology uses Tropical signs but Vedic techniques).

## Decision
We deprecated the dual-engine approach and unified all core chart generation logic exclusively under the `/jyotish/` directory using a single, unified Swiss Ephemeris (`swisseph`) pipeline.

## Justification
- The Kala methodology is a hybrid system (Tropical Rasis, Sidereal Nakshatras, Vedic Vargas). Splitting it artificially into "Western" and "Vedic" folders contradicts the methodology.
- A single entry point (`generate_jyotish.py`) ensures that Ayanamsa, Julian Day, and House Systems are perfectly synchronized across all calculations.

## Trade-offs
- **Pros:** Drastically simplified codebase. Single source of truth for astronomical calculations. Easier to maintain and test.
- **Cons:** Loss of any standalone "Western-only" pipeline, though this is not required by the project goals.
