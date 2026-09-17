# 🧭 Architecture Decision Records (ADRs) — Planetary Evaluation & Master Graha Diagnostics

This directory documents the foundational architectural and astrological decisions implemented in Astra's **Planetary Evaluation & Master Graha Diagnostics Engine** (`jyotish/planetary_evaluation/planetary_evaluation.py`). 

Each decision addresses specific shortcomings discovered through deep real-life case studies, establishing a holistic, scripturally faithful approach to chart diagnosis.

---

## 📚 Table of Decisions

| ADR | Title & Core Subject | Real-Life Case Study | Classical Basis |
| :---: | :--- | :--- | :--- |
| [**001**](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/planetary_evaluation/adr/001-nine-tier-archetype-and-neutral-tilt.md) | **9-Tier Archetype Spectrum & Neutral Tilt**<br>Expanding 4 quadrants to 9 tiers; tilting neutral signs to 54.9% to prevent false dictators. | **Shivapuri Baba**<br>(Mars in Virgo: Sage misdiagnosed as Armed Dictator) | *BPHS* Ch. 45<br>Vic DiCara Matrix |
| [**002**](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/planetary_evaluation/adr/002-strict-neecha-bhanga-exclusivity.md) | **Strict Neecha Bhanga Exclusivity**<br>Restricting debility cancellation strictly to classical signs of fall; enemy signs are never fallen. | **Swami Hari Om Puri**<br>(Mars in Virgo: Enemy sign denied false Neecha Bhanga) | *Phaladeepika* Ch. 6<br>*BPHS* Ch. 41 |
| [**003**](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/planetary_evaluation/adr/003-functional-ascendant-and-chandal-resynthesis.md) | **Ascendant Functional Roles & Chandal Resynthesis**<br>Filtering planets through rising signs; preserving executive horsepower while flagging ideological fanaticism. | **Heinrich Himmler**<br>(Jupiter Moolatrikona H11 conjoined Rahu & Saturn) | *BPHS* Ch. 34<br>*Phaladeepika* 6.34 |
| [**004**](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/planetary_evaluation/adr/004-graha-yuddha-and-venus-invariance.md) | **Graha Yuddha & Venus Invariance Rule**<br>Planetary war threshold ($\le 1^\circ 00'$); Venus never loses; Northern latitude determines victor. | **Adolf Hitler**<br>(Venus vs. Mars in Taurus: Venus wins, Mars Nipidita) | *Phaladeepika* 4.2<br>*Brihat Samhita* |
| [**005**](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/planetary_evaluation/adr/005-recursive-drishti-dampening.md) | **Option A: Recursive Drishti Dampening**<br>Dampening benefic aspect light by 50% when the casting benefic is debilitated. | **Debilitated Benefics**<br>(Jupiter in Capricorn / Venus in Virgo) | Qualitative Drishti |
| [**006**](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/planetary_evaluation/adr/006-inherent-dignity-vs-house-field.md) | **Inherent Character vs. Situational House Field**<br>Decoupling core archetypal character (Dignity + Muscle) from situational house terrain. | **Swami Dayalpuri**<br>(Exalted Jupiter in 8th House remains Generous King) | *Phaladeepika* Ch. 3 & 4<br>DiCara Foundations |
| [**007**](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/planetary_evaluation/adr/007-nodal-dispositor-proxy-and-conjunction-orbs.md) | **Nodal Dispositor Proxy & Conjunction Orbs**<br>Inheriting host foundation; 3°20' Navamsha possession; distinguishing Guru-Chāṇḍāla from Guru-Ketu Jñāna. | **Rahu & Ketu**<br>(Shadow nodes acting as catalytic amplifiers) | *Phaladeepika* 4.5<br>BPHS Nodal Yogas |
| [**008**](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/planetary_evaluation/adr/008-baladi-avastha-biological-efficiency.md) | **Bālādi Avasthās & Biological Efficiency**<br>Odd/even sign degree progression from infancy to dormancy; operational efficiency scaling. | **Late-Degree Grahas**<br>(Exhaustion in Mrita Avastha throttling manifestation) | *Phaladeepika* 3.10 |
| [**009**](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/planetary_evaluation/adr/009-audit-metered-twice-decoupling.md) | **Decoupling Additive Modifiers & Audit Harmonization**<br>Removing retrograde double-counting; eliminating Lajjitadi additive stacking; math receipts. | **Independent Audit**<br>(Harmonizing mathematical modifiers with single truth) | Algorithmic Integrity |
| [**010**](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/planetary_evaluation/adr/010-aspect-vision-badges-and-twenty-virupa-rule.md) | **Aspect Vision Badges & the 3-Tier Virūpa Filter**<br>Decisive force ($\ge 45$v in cell), subtle background (20–44v in tooltip), negligible (&lt; 20v ignored). | **Cluttered Aspect Fields**<br>(Minor glances obscuring dominant rays & qualitative gaze) | *BPHS* Ch. 26 & 28<br>Dṛṣṭi Foundations |

---
*Maintained by the Astra Astrological Computing Core.*
