# ADR-008: Lajjitadi Avasthas Utilizing Natural Friendship (Naisargika)

## Context
When evaluating the states (Avasthas) of a planet, most dignity-based conditions (such as Jagradadi or Deeptadi) rely on the 5-fold Compound Friendship (Panchadha) to determine the final state.

## Decision
The Lajjitadi Avasthas (Ashamed, Proud, Starved, Thirsty, Delighted, Agitated) in the Astra engine are programmed to **strictly bypass Compound Friendship** and evaluate conjunctions, aspects, and sign placements using **Natural Friendship (Naisargika Maitri)**.

## Rationale
1. **Textual Basis:** BPHS Ch 45 Verses 11-17 outlines these conditions based on the innate, archetypal relationship between planets (e.g., Jupiter is the natural delighter; Saturn is the natural starver). 
2. **Behavioral Logic:** Lajjitadi deals with the psychological pressure of *who is in the room* (conjunction) and *who is staring* (Rasi aspect). If a natural enemy is staring at a planet, the planet feels "Starved" or "Agitated" due to their clashing elemental natures, regardless of whether they happen to be in a temporary truce (Temporary Friendship) due to distance in the sky.
3. **Ernst Wilhelm's Standard:** Kala software explicitly calculates Lajjitadi states using natural inborn relationships.
