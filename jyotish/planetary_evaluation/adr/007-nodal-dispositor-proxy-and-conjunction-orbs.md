# ADR-007: Nodal Dynamics (Rahu & Ketu): Dispositor Proxy, Orbs, and Jñāna vs. Chāṇḍāla

## Context & The Shortcoming in the Naive Model
Rahu (North Node) and Ketu (South Node) are mathematical intersection points (*Chhāyā Grahas* / shadow planets) rather than physical celestial bodies. Consequently:
- They do not have physical mass or independent Shadbala virūpas.
- They do not own classical zodiac signs in Parashari astrology.

In naive software, nodes either cause division-by-zero crashes, are assigned arbitrary flat scores, or all conjunctions with nodes are treated as identical toxic curses.

## Decision
1. **The Dispositor Proxy Protocol:**
   Because nodes reflect the physical foundation of the sign they occupy, Rahu and Ketu inherit their operational capability from their **host dispositor**:
   - **Effective Dignity:** $\text{Host Dignity} \times 0.85$ (+15% boost if placed in strong affinity signs: Taurus, Gemini, Virgo, Aquarius for Rahu; Scorpio, Sagittarius, Pisces for Ketu).
   - **Effective Muscle:** $\text{Host Shadbala} \times 0.90$ (minimum 60% baseline).
2. **Three-Tier Conjunction Orb Bands:**
   The impact of a node on a physical planet depends strictly on degree proximity:
   - **Exact (Intimate) Orb ($< 3^\circ 20'$ / One Navāṁśa):** Nodal possession. Ketu suppresses outer material visibility (biological efficiency reduced to 80%); Rahu causes obsessive psychological fixation.
   - **Moderate Orb ($3^\circ 20' - 10^\circ 00'$):** Standard conjunction pressure.
   - **Wide Orb ($> 10^\circ 00'$):** Minor background atmosphere.
3. **Classical Yoga Differentiation: Guru-Chāṇḍāla vs. Guru-Ketu Jñāna:**
   - **Jupiter + Rahu:** Diagnosed as **Guru-Chāṇḍāla Yoga** (unorthodox doctrine, taboo ambition, rebellion against traditional dogma).
   - **Jupiter + Ketu:** Diagnosed as **Guru-Ketu Jñāna Yoga** (spiritual discernment, esoteric contemplation, detachment from worldly dogma). This is **NOT a malefic dosha**; it is a catalyst for higher spiritual wisdom.

## Proof & Validation
Tests in `tests/test_planetary_evaluation.py` verify that intimate Ketu conjunctions apply the 3°20' Navamsha efficiency drop, while Jupiter-Ketu conjunctions receive the **`🕉️ Jñāna Catalyst`** badge with zero toxic Chāṇḍāla penalty.
