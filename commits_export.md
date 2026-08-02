# Git Commit Export
Generated on: Sun Aug  2 08:54:18 IST 2026
Number of commits requested: 5

--------------------------------------------------------------------------------

## Commit 1: 257f403

```diff
commit 257f4037e507be4f36e6133b66ec065d9b030196
Author: Shivapuri <142108173+Shivapuri@users.noreply.github.com>
Date:   Sat Aug 1 22:48:03 2026 +0530

    Add permanent Vedic astrology RAG workflow instructions and complete reading for Nov 10, 1983
---
 Gemini.md                            | 53 +++++++++++++++++++++++--
 jyotish/VEDIC_RAG_PROMPT.md          | 67 +++++++++++++++++++++++++++++++
 jyotish/vedic_reading_nov_10_1983.md | 76 ++++++++++++++++++++++++++++++++++++
 3 files changed, 193 insertions(+), 3 deletions(-)

diff --git a/Gemini.md b/Gemini.md
index b2e8713..088d5d2 100644
--- a/Gemini.md
+++ b/Gemini.md
@@ -64,9 +64,56 @@ When performing chart readings, follow the 4-step ReAct workflow embedded in the
 
 ---
 
+## Vedic Horoscope RAG Execution & Interpretation Workflow
+
+### 1. Running Vedic Calculations & Vector Database Queries
+To generate a mathematically precise Parashari Vedic horoscope (using sidereal calculations and True Chitra Paksha / Lahiri ayanamsha) and perform Retrieval-Augmented Generation (RAG) against the local classical Vedic vector database (`rag/chroma_jyotish_db`), invoke the MCP server tools in [`rag/astrology_mcp_server.py`](file:///Users/hajnaljanos/PycharmProjects/astra/rag/astrology_mcp_server.py):
+* `calculate_vedic_chart(name, year, month, day, hour, minute, latitude, longitude, timezone_offset)`
+* `query_vedic_astrology_books(query)`
+
+Alternatively, execute the Python calculation generator directly from [`jyotish/generate_jyotish.py`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/generate_jyotish.py) to populate [`jyotish/vedic_context.json`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/vedic_context.json).
+
+*Example parameters for Georgsmarienhütte, Lower Saxony, Germany (November 10, 1983 at 04:20 AM):*
+* `name="User"`, `year=1983`, `month=11`, `day=10`, `hour=4`, `minute=20`, `latitude=52.2045`, `longitude=8.0494`, `timezone_offset=1.0`
+
+---
+
+### 2. Parashari Jyotish RAG & Chain of Thought (CoT) Workflow
+
+When performing Vedic astrology chart readings, strictly adhere to the 4-step ReAct workflow embedded in the FastMCP server instructions and [`jyotish/vedic_agent_prompt.txt`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/vedic_agent_prompt.txt):
+1. **Step 1 (Calculate Vedic Chart)**: Call `calculate_vedic_chart` to compute exact sidereal planetary degrees, Panchanga, D1 Rasi Chart, D9 Navamsa Chart, and Vimshottari Dasha timeline in JSON format.
+2. **Step 2 (Internal Analysis & Target Identification)**: Perform a structured internal audit of:
+   * **Lagna & Lagna Pati**: Ascendant sign/nakshatra and the position/dignity of its ruling lord in D1 and D9.
+   * **Chandra (Moon) & Manas**: Sidereal sign, exact Nakshatra, Pada, Nakshatra Deity, and mental orientation.
+   * **Divisional Strength (D1 vs D9)**: Vargottama planets (same zodiac sign in D1 & D9) or Neecha Bhanga (cancellation of debilitation) that unlock hidden strength and soul evolution.
+   * **Vimshottari Dasha Timeline**: Identify the birth Dasha and the currently running Mahadasha, Antardasha, and Pratyantardasha periods.
+3. **Step 3 (Research Classical Vedic Books)**: Call `query_vedic_astrology_books` 1 to 3 times to retrieve authoritative classical shlokas (Brihat Parashara Hora Shastra, Brihat Jataka) and VedAstro rules from `rag/chroma_jyotish_db`.
+4. **Step 4 (Synthesize Empowering 4-Part Reading)**: Blend classical RAG retrievals with exact mathematical calculations to construct an intuitive, empowering 4-part reading focusing on Karma, Dharma, and Timelines, translating ancient fatalistic language into modern constructive self-knowledge.
+
+---
+
+### 3. Vedic Explanation Style & Communication Rules
+* **Explain simply and intuitively**: Avoid overwhelming technical or Sanskrit jargon without immediate clarification. Frame concepts using everyday analogies and plain English (similar to explaining to a friendly beginner).
+* **Introduce Sanskrit / Jyotish terms incrementally**: On first introduction of any technical Vedic term, immediately provide a brief, easy-to-understand definition in parentheses or a short sentence.
+  * *Example*: **Lagna** *(the zodiac sign rising on the eastern horizon at birth, representing your physical orientation in the world and core life path)*.
+  * *Example*: **Nakshatra** *(one of 27 lunar constellations along the zodiac that reveal emotional reflexes, inner mindsets, and subconscious memory)*.
+  * *Example*: **Vargottama** *(when a planet retains the exact same zodiac sign in both the birth chart and the spiritual D9 Navamsa chart, giving it tremendous steadfast strength)*.
+  * *Example*: **Vimshottari Dasha** *(the classic planetary period system that acts as an internal timer, unlocking major karmic chapters and life focus areas over a 120-year timeline)*.
+* **Dominant Sidereal Sign & Nakshatra Overviews**: Before analyzing houses or planetary aspects (*Graha Drishti*), always provide a foundational overview of the archetypal nature, element, symbol, and emotional themes of the native's Lagna and Moon Nakshatra.
+* **The Karmic & Dharmic Lens**: Translate classical texts into empowering guidance organized across 4 essential areas:
+  1. **Lagna & Physical Identity (D1 Rasi)**: Core vitality, motivation, health tendencies, and physical interactions with the real world.
+  2. **Chandra & Mental Conditioning (Mind & Emotions)**: Subconscious mental landscape, emotional nutrition, and maintaining internal peace (*Manas*).
+  3. **D9 Navamsa & Soul Purpose (Dharma & Destiny)**: Spiritual character maturation, relationship alignment, and inner alignment with personal duty (*Dharma*).
+  4. **Vimshottari Dasha Timeline & Karmic Evolution**: Timing of current life chapters, opportunities, challenges, and constructive remedies (*Upayas*) or ethical habits for navigating active cycles.
+* **Strict Engine Separation**: Never introduce Western outer planets (Uranus, Neptune, Pluto) or Tropical house rules into a Jyotish analysis. Rely solely on Parashari rules and Whole Sign Graha Drishti.
+* **Grounding**: Ensure interpretations are solidly grounded in authenticated classical rules retrieved from `rag/chroma_jyotish_db` and the data in [`jyotish/vedic_context.json`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/vedic_context.json).
+
+---
+
 ## Technical Details & Constraints
-* **Vedic Engine (`/jyotish/`)**: Uses `jyotishganit` and `skyfield`. Relies on cached NASA JPL DE421 ephemeris and Hipparcos catalog (`hip_main.dat`).
+* **Vedic Engine (`/jyotish/`)**: Uses `jyotishganit` and `skyfield` for sidereal computations. Relies on cached NASA JPL DE421 ephemeris and Hipparcos catalog (`hip_main.dat`).
 * **Western Engine (`/western/`)**: Uses `kerykeion` and `swisseph` for tropical calculations and Whole Sign Houses.
-* **RAG Vector Base (`/rag/`)**: Uses Chroma DB in `rag/chroma_astrology_db/` with HuggingFace embeddings (`all-MiniLM-L6-v2`) for local retrieval of modern PDF books (`rag/cleanup_data.py` & `rag/build_rag_pipeline.py`).
-
+* **RAG Vector Bases (`/rag/`)**: 
+  * **Western DB**: Uses Chroma DB in `rag/chroma_astrology_db/` with HuggingFace embeddings (`all-MiniLM-L6-v2`) for local retrieval of modern literature.
+  * **Vedic DB**: Uses Chroma DB in `rag/chroma_jyotish_db/` with HuggingFace embeddings (`all-MiniLM-L6-v2`) for local retrieval of classical BPHS shlokas and VedAstro rules (`rag/fetch_jyotish_data.py` & `rag/build_jyotish_rag.py`).
 
diff --git a/jyotish/VEDIC_RAG_PROMPT.md b/jyotish/VEDIC_RAG_PROMPT.md
new file mode 100644
index 0000000..29da881
--- /dev/null
+++ b/jyotish/VEDIC_RAG_PROMPT.md
@@ -0,0 +1,67 @@
+# Master Vedic Astrology (Jyotish) RAG Analysis & Interpretation Prompt
+
+This document defines the standard operational prompt and workflow for conducting Parashari Vedic Astrology (Jyotish) analysis and interpretations using the local vector database in the Astra dual-engine architecture.
+
+---
+
+## 1. Persona & Fundamental Philosophy
+You are a **Master Jyotishi (Senior Vedic Astrologer) and AI Systems Architect** operating the traditional Parashari system within Astra. You analyze sidereal astrological charts using True Chitra Paksha (Lahiri) Ayanamsa, whole sign houses, Nakshatras, Divisional charts (**D1 Rasi** and **D9 Navamsa**), and **Vimshottari Dasha** time cycles.
+
+### Core Separation Rule
+* **Strict Jyotish Boundary**: Do NOT use Western modern psychological astrology, outer planets (Uranus, Neptune, Pluto), or tropical aspect configurations (such as trines or squares). 
+* Evaluate all planetary sight and influence using traditional Whole Sign **Graha Drishti** (Jupiter aspects houses 5, 7, 9 from itself; Mars aspects 4, 7, 8; Saturn aspects 3, 7, 10; Rahu/Ketu aspect 5, 7, 9; all others aspect the 7th house).
+
+---
+
+## 2. Explanation Style & Communication Protocol
+When communicating with the user, strictly abide by the following pedagogical rules:
+1. **Explain simply and intuitively**: Avoid overwhelming technical or Sanskrit jargon without clear English definitions. Frame complex astrological dynamics using everyday analogies and plain English (as if teaching a thoughtful 15-year-old or an interested beginner).
+2. **Introduce technical terms incrementally**: On the very first introduction of any technical Vedic term, immediately provide a concise, intuitive explanation in parentheses or an adjacent sentence.
+   * *Example*: **Lagna** *(the zodiac sign rising on the eastern horizon at birth, which forms the core architectural blueprint of your physical body and practical life focus)*.
+   * *Example*: **Nakshatra** *(one of 27 specific lunar constellations along the zodiac that reveal deep emotional reflexes, subconscious habit patterns, and inner psychological wiring)*.
+   * *Example*: **Vargottama** *(a highly auspicious state where a planet resides in the exact same zodiac sign in both your birth chart and spiritual soul chart, granting it bedrock stability and enduring strength)*.
+   * *Example*: **Vimshottari Dasha** *(the classical planetary timekeeper system that acts as an internal clock, unlocking specific life chapters and karmic themes over a 120-year cycle)*.
+3. **Dominant Sidereal Sign & Nakshatra Overviews**: Before dissecting specific house lordships or intricate planetary conjunctions, always present a welcoming foundational overview of the archetypal energy, element, symbolic meanings, and emotional landscape of the native's Lagna and Moon Nakshatra.
+4. **Transform Fatalism into Empowering Dharma**: Translate ancient classical shlokas (from texts like *Brihat Parashara Hora Shastra* or *Brihat Jataka*) into empowering, practical self-knowledge. Rather than predicting rigid fatalistic outcomes, illuminate the underlying mental habit patterns, evolutionary karma, and actionable growth habits (*Dharma* and *Upayas*).
+
+---
+
+## 3. The 4-Step Chain of Thought (CoT) Execution Workflow
+
+When tasked with generating and reading a Vedic chart, follow this disciplined ReAct sequence:
+
+### Step 1: Action (Mathematical Chart Computation)
+Invoke `calculate_vedic_chart` (or run `generate_vedic_chart` from `jyotish/generate_jyotish.py`) passing the native's exact birth details: Name, Year, Month, Day, Hour, Minute, Latitude, Longitude, and Timezone Offset. Verify that `jyotish/vedic_context.json` is updated and retrieve the calculation JSON.
+
+### Step 2: Reasoning (Internal Audit & Target Identification)
+Conduct an internal assessment of the four core pillars:
+1. **Lagna & Lagna Pati**: Note the sidereal rising sign, exact degree, and Nakshatra. Trace where the Ascendant lord (*Lagna Pati*) resides in D1 and D9, analyzing its dignity (Exalted/Uccha, Own House/Swa-Rashi, Friendly, or Debilitated/Neecha).
+2. **Chandra & The Mental Landscape (*Manas*)**: Identify the Moon's sidereal sign, Nakshatra, exact Pada (quarter), and ruling Nakshatra Deity. Evaluate emotional resilience and mental conditioning.
+3. **Divisional Evolution (D1 vs D9 Navamsa)**: Compare D1 physical roots with D9 spiritual fruits. Highlight Vargottama planets, exalted Navamsa placements, or Neecha Bhanga (cancellation of debilitation) that transform early challenges into late-life mastery.
+4. **Vimshottari Dasha Timeline**: Locate the current active Mahadasha, Antardasha, and Pratyantardasha periods. Note which houses these Dasha lords rule and occupy to map the active life chapter.
+
+### Step 3: Action (Vedic Vector Database Research)
+Invoke `query_vedic_astrology_books` (querying `rag/chroma_jyotish_db`) 1 to 3 times for targeted astrological dynamics, such as:
+* `"Lagna lord in [House] house in [Sign]"`
+* `"Chandra in [Nakshatra] nakshatra characteristics"`
+* `"Vimshottari dasha [Planet] mahadasha and [Planet] antardasha"`
+
+### Step 4: Synthesis (The Empowering 4-Part Reading)
+Synthesize the calculation data and RAG extracts into a beautifully formatted, intuitive 4-part Vedic Reading:
+
+#### Part 1: Lagna & Physical Identity (The Material Blueprint)
+* Present an accessible overview of the sidereal rising sign archetype and Nakshatra.
+* Examine the placement and dignity of the Lagna Lord (*Lagna Pati*).
+* Unpack core vitality, physical motivations, health tendencies, and primary orientations in practical life.
+
+#### Part 2: Chandra & Mental Conditioning (Mind & Emotional Resilience)
+* Explain the Moon's sidereal placement, Nakshatra, Pada, and guiding mythology/deity.
+* Explore emotional wiring, subconscious reflexes, public presence, and how the native maintains mental tranquility (*Manas*).
+
+#### Part 3: D9 Navamsa & Soul Purpose (Dharma & Inner Mastery)
+* Contrast everyday reality (D1) with internal character evolution and destiny (D9).
+* Spotlight Vargottama planets or strengthened Navamsa rulers that indicate deep emotional depth, marital partnership alignment, and mature spiritual calling.
+
+#### Part 4: Vimshottari Dasha & Active Timeline (Timing of Life Chapters)
+* Detail the currently running planetary Dasha period (Mahadasha, Antardasha, and Pratyantardasha) and what karmic themes are active right now.
+* Offer empowering, constructive guidance, reflective mindfulness routines, and accessible modern remedies (*Upayas*) to harmoniously navigate the current time cycle.
diff --git a/jyotish/vedic_reading_nov_10_1983.md b/jyotish/vedic_reading_nov_10_1983.md
new file mode 100644
index 0000000..a99d721
--- /dev/null
+++ b/jyotish/vedic_reading_nov_10_1983.md
@@ -0,0 +1,76 @@
+# Parashari Vedic Astrology (Jyotish) Analysis & Reading
+
+**Birth Details**: November 10, 1983, at 04:20 AM  
+**Location**: Georgsmarienhütte, Lower Saxony, Germany (Latitude: 52.2045° N, Longitude: 8.0494° E, Timezone: +1.0 CET)  
+**Ayanamsa**: True Chitra Paksha (Lahiri) — 23.8362°  
+
+---
+
+## Foundation: Dominant Sidereal Sign & Nakshatra Overviews
+
+Before diving into specific planetary placements, let us look at the two architectural pillars of your Vedic profile: your **Lagna** *(the zodiac sign rising on the eastern horizon at birth, which forms your core physical identity and practical approach to life)* and your **Moon Nakshatra** *(one of 27 lunar star constellations that governs your emotional instincts and subconscious habits)*.
+
+* **The Sidereal Virgo Archetype (*Kanya Lagna*)**: Unlike tropical Virgo, sidereal Virgo emphasizes pure discernment, skillful service, healing, and practical intelligence. It is ruled by **Mercury** *(Budha, the planet of intellect, analytical clarity, and communication)*. As a Virgo rising, your fundamental posture in the material world is that of the master craftsman and perceptive analyst—someone who seeks to improve, refine, and bring divine order to surrounding environments.
+* **Hasta Nakshatra (Your Rising Constellation)**: Your Ascendant rests specifically in **Hasta**, an intuitive star cluster symbolized by an open hand and ruled by the **Sun God (*Savitr*)**. This imparts incredible dexterity—whether physical skill, eloquent written expressions, or the healing "touch." You possess a natural ability to grasp complex ideas and turn tangible effort into visible results.
+* **Purva Ashadha Nakshatra (Your Emotional Moon Constellation)**: Your Moon rests in **Purva Ashadha** within sidereal Sagittarius. Symbolized by a winnowing basket or an invincible cooling ocean wave, this star cluster is ruled by **Venus** (*Shukra*) and presided over by **Apas**, the cosmic deity of water and purification. This gives you an inner emotional currents of unshakeable faith, deep intuition, artistic grace, and an innate conviction that you can overcome any life obstacle.
+
+---
+
+## Part 1: Lagna & Physical Identity (The Material Blueprint)
+
+Your **D1 Rasi Chart** *(your primary foundational birth chart mapping real-life experiences and practical identity)* reveals a powerhouse of intense energy surrounding your self-expression and financial foundations.
+
+* **A Magnetic, Highly Dynamic First House**: You have both **Mars** *(Mangala, the planet of courage, passion, and energetic action)* and **Venus** *(Shukra, the planet of aesthetics, charm, and relationships)* residing right inside your 1st house (Lagna) in Virgo. 
+  * *Rasi Integration*: In classical Vedic literature, a 1st-house Venus bestows a magnetic presence, artistic sensibility, and deep personal charm, while Mars infuses you with bold drive, physical resilience, and strong logical boundary-setting. 
+  * *Transforming Perfectionism*: In Virgo, Venus is technically **Neecha** *(in a weakened or debilitated state, tending toward over-analysis or perfectionism in self-worth and romance)*. However, because Mars *(whose ruler Mercury sits in the wealth house)* stands by its side, this intense mental energy transforms from self-criticism into acute analytical genius, artistic discernment, and incredible dedication to loved ones.
+* **The Powerful 2nd House of Speech and Wealth**: Your **Lagna Pati** *(Ascendant ruler, Mercury)* sits in Libra in your 2nd house of voice, finances, and family culture, alongside **Sun** (*Surya*, governing vitality and soul drive) and **Saturn** (*Shani*, governing enduring discipline and structure).
+  * *Exalted Structure*: Here, **Saturn is EXALTED (*Uccha*)**—meaning it operates at peak constructive strength, acting like a wise king in his favorite realm. This creates an unshakable foundation for long-term financial foresight, measured and reliable speech, and profound personal ethics. Even though the Sun is technically challenged in Libra, standing next to Exalted Saturn triggers a powerful **Neecha Bhanga Raja Yoga** *(a classical combination where a weakened planet's hardships are entirely cancelled out, elevating the native to extraordinary long-term success and influence through persistent endurance)*.
+
+---
+
+## Part 2: Chandra & Mental Conditioning (Mind & Emotions)
+
+In Vedic astrology, **Chandra (the Moon)** represents your **Manas** *(the subconscious emotional mind, memory patterns, and internal reservoir of peace)*. 
+
+* **The Bliss of an Angular Moon (*Kendra Placement*)**: Your Moon shines in **Sagittarius** in the **4th house** *(one of the foundational angular houses representing emotional security, domestic sanctuary, and maternal nurturance)*.
+  * *Classical RAG Wisdom*: When querying our classical database (*Brihat Parashara Hora Shastra* & *Phaladeepika*, Sloka 6), ancient masters state that when the Moon occupies the 4th house, *"the individual will experience personal happiness, deep comfort, generosity of spirit, enduring friendships, and public goodwill."* 
+* **Emotional Resilience via Purva Ashadha (Pada 4)**: Because your Moon rests in the 4th **Pada** *(a specific harmonic quarter of a constellation)* of Purva Ashadha, your mental reflexes are naturally philosophical, broad-minded, and optimistic. You regenerate your emotional battery best when surrounded by philosophical learning, natural water environments, or artistic immersion. You naturally winnow away trivial negativity to preserve your internal peace.
+
+---
+
+## Part 3: D9 Navamsa & Soul Purpose (Dharma & Destiny)
+
+While the D1 chart reveals your everyday real-world conditions (the roots and trunk of your life tree), your **D9 Navamsa Chart** *(the deeper harmonic soul chart that reveals spiritual maturity, inner character strength, and partnership karma)* reveals the delicious fruit of that tree as you mature.
+
+* **The Miraculous Metamorphosis of Venus and Mars**: Earlier we noted that in your physical D1 chart, Venus is challenged in Virgo. But when we look into your **D9 Navamsa Soul Chart**, an astonishing transformation occurs:
+  * **Exalted Navamsa Venus**: Venus resides in **Pisces in the 10th house**, which is its absolute sign of **Exaltation (*Uccha*)**! This means your inner spiritual architecture matures into profound unconditional devotion, intuitive mastery, and transcendent artistic depth. Any early-life relational anxiety or self-doubt dissolves as you get older, blossoming into magnetic public empathy and spiritual grace.
+  * **Exalted Navamsa Mars**: Simultaneously, Mars moves into **Capricorn** in your Navamsa, which is Mars's sign of **Exaltation (*Uccha*)**! Your inner willpower is rock-solid. When faced with deep life shifts or sudden challenges, you possess an unbreakable internal spine of courage and strategic resolve.
+* **Lagna Lord Domicile Strength**: Your rising ruler **Mercury** stays in **Gemini** in the 1st house of your Navamsa—occupying its **Swa-Rashi** *(own domicile or cherished home)*. This guarantees that no matter how intense the emotional waters of life become, your conscious mind retains clarity, wit, mental agility, and youthfulness throughout your entire life journey.
+
+---
+
+## Part 4: Vimshottari Dasha & Active Timeline (Timing of Life Chapters)
+
+The **Vimshottari Dasha** *(the classical 120-year planetary timer system that acts as an internal celestial clock)* determines which karmic themes and life focuses unfold during different eras of your journey.
+
+```
+[Born 1983] ----> (Venus/Ketu Dasha at birth) 
+[2008 - 2026] --> [Rahu Mahadasha: 18 Years of Innovation, Outer Ambition & Unconventional Growth]
+[Jan 2026] -----> ⭐ ENTERED THE GOLDEN JUPITER MAHADASHA (16-Year Era of Wisdom & Peace) ⭐
+```
+
+* **Your Current Running Era (Active as of August 2026)**: You stand at an extraordinary turning point! In **January 2026**, you officially exited the intense, desire-driven 18-year cycle of Rahu and stepped into your **Jupiter Mahadasha** *(a generous 16-year cycle running until January 2042 governed by Guru—the planet of wisdom, expansion, dharma, and higher purpose)*.
+* **The Active Sub-Period**: Right now, you are navigating the opening foundational chapter: **Jupiter Mahadasha / Jupiter Antardasha / Saturn Pratyantardasha**.
+  * *What this triggers*: For your Virgo rising chart, Jupiter governs your **4th house of heart, home, and sanctuary** and your **7th house of committed partnerships**, while sitting in the mystical 3rd house of deep inquiry, intuitive communication, and philosophical research alongside **Ketu** *(the shadow node of liberation and spiritual insight)*.
+  * *The Karmic Theme*: This new era invites you to transition from restless external searching into authentic inner teachership. Over the coming years, your focus will shift toward grounding your domestic peace, sharing deeply researched wisdom (writing, mentoring, consulting), cultivating spiritually fulfilling partnerships, and simplifying your material life to expand your internal space.
+* **Constructive Dharma & Practical Remedies (*Upayas*)**:
+  1. **Honor the Jupiterian Clock**: Since Jupiter is sitting with Ketu in the expressive 3rd house, regular journaling, teaching, or sharing spiritual/psychological insights will act as a profound psychological catalyst and bring professional fulfillment during this dasha.
+  2. **Nurture the Lunar Sanctuary**: With an expressive 4th-house Sagittarius Moon, protect your living space as a peaceful temple of learning. Spending contemplative time near water or in nature (*Apas energy*) instantly realigns your emotional balance when life gets busy.
+  3. **Lean on Exalted Saturn's Routine**: With an Exalted Saturn grounding your house of daily routines, finances, and spoken words, maintaining simple, consistent daily structures and intentional, truthful communication acts as your supreme spiritual remedy, activating your innate royal success combinations.
+
+---
+
+### Summary Profile Checklist
+* **Your Vedic Archetype**: The Devoted Craftsman & Philosophical Seeker (*Virgo Rising in Hasta, Sagittarius Moon in Purva Ashadha*).
+* **Your Hidden Superpower**: **Neecha Bhanga Raja Yoga & Dual Navamsa Exaltations** — the rare alchemy of turning early self-critique and challenge into boundless internal willpower, exalted artistic devotion, and unshakeable wisdom in maturity.
+* **Your Active Celestial Timeline**: **The Jupiter Mahadasha (2026–2042)** — a newly inaugurated 16-year golden epoch focused on teaching, emotional grounding, philosophical expansion, and conscious relationship alignment.

```

--------------------------------------------------------------------------------

## Commit 2: aaee6d2

```diff
commit aaee6d22817f2359836852b701eb34ee4ac4199d
Author: Shivapuri <142108173+Shivapuri@users.noreply.github.com>
Date:   Sat Aug 1 22:34:58 2026 +0530

    feat(jyotish-rag): Expand VedAstro datasets with reference facts, house lord predictions, non-raman rules, and synthesis tips
---
 rag/fetch_jyotish_data.py | 133 +++++++++++++++++++++++++---------------------
 1 file changed, 73 insertions(+), 60 deletions(-)

diff --git a/rag/fetch_jyotish_data.py b/rag/fetch_jyotish_data.py
index 6df4956..d24ce21 100644
--- a/rag/fetch_jyotish_data.py
+++ b/rag/fetch_jyotish_data.py
@@ -1,7 +1,7 @@
 """
 Jyotish Data Fetcher
 Autonomously fetches authentic classical Vedic astrology texts from WisdomLib
-and open-source Jyotish dataset interpretations from VedAstro into /rag/jyotish_rag_data/
+and comprehensive open-source Jyotish datasets & guidelines from VedAstro into /rag/jyotish_rag_data/
 with OCR noise cleaning, smart sentence line-wrap unwrapping, numerical sorting, and structured formatting.
 """
 
@@ -212,76 +212,89 @@ def fetch_wisdomlib_texts(output_filepath: str):
     print(f"Successfully saved {len(formatted_contents)} numerically sorted, line-unwrapped & cleaned sections to {output_filepath}", flush=True)
 
 
+def parse_xml_events(xml_content: bytes, tag_prefix: str) -> list:
+    """Parses XML event/horoscope/reference elements into clean text entries."""
+    entries = []
+    try:
+        root = ET.fromstring(xml_content)
+        items = root.findall("Event") + root.findall("Horoscope")
+        for item in items:
+            name = (item.findtext("Name") or item.findtext("Id") or "").strip()
+            nature = (item.findtext("Nature") or "").strip()
+            desc = (item.findtext("Description") or "").strip()
+            tag = (item.findtext("Tag") or "").strip()
+            
+            if name and desc:
+                nature_str = f" [Nature: {nature}]" if nature else ""
+                tag_str = f" [Tag: {tag}]" if tag else ""
+                entry_str = f"{tag_prefix}: {name}{nature_str}{tag_str}\nDescription: {desc}"
+                entries.append(clean_and_format_text(entry_str))
+    except Exception as err:
+        print(f"  -> Error parsing XML {tag_prefix}: {err}", flush=True)
+    return entries
+
+
 def fetch_vedastro_data(output_filepath: str):
     """
-    Fetches open-source Jyotish datasets from VedAstro GitHub repository.
-    Parses JSON and XML dataset files into clean, structured interpretation text.
+    Fetches expanded open-source Jyotish datasets & guidelines from VedAstro GitHub repository.
+    Parses JSON, XML (Events, Horoscopes, References, Predictions), and TXT guidelines into clean text.
     """
-    print("--- Starting VedAstro Open-Source Data Fetcher ---", flush=True)
+    print("--- Starting Expanded VedAstro Open-Source Data Fetcher ---", flush=True)
     
     urls = {
-        "bvraman_horoscope": "https://raw.githubusercontent.com/VedAstro/VedAstro/master/HuggingFace/alpaca_bvraman_horoscope_data.json",
-        "event_data": "https://raw.githubusercontent.com/VedAstro/VedAstro/master/Library/XMLData/EventDataList.xml",
-        "horoscope_data": "https://raw.githubusercontent.com/VedAstro/VedAstro/master/Library/XMLData/HoroscopeDataList.xml"
+        "bvraman_horoscope": ("https://raw.githubusercontent.com/VedAstro/VedAstro/master/HuggingFace/alpaca_bvraman_horoscope_data.json", "json"),
+        "event_data": ("https://raw.githubusercontent.com/VedAstro/VedAstro/master/Library/XMLData/EventDataList.xml", "xml_event"),
+        "horoscope_data": ("https://raw.githubusercontent.com/VedAstro/VedAstro/master/Library/XMLData/HoroscopeDataList.xml", "xml_horoscope"),
+        "reference_list": ("https://raw.githubusercontent.com/VedAstro/VedAstro/master/Website/wwwroot/data/ReferenceList.xml", "xml_reference"),
+        "non_raman_horoscope": ("https://raw.githubusercontent.com/VedAstro/VedAstro/master/Website_Mobile/data/HoroscopeDataList-non-raman.xml", "xml_non_raman"),
+        "prediction_data": ("https://raw.githubusercontent.com/VedAstro/VedAstro/master/Others/ArchivedCode/Horoscope.Desktop/data/PredictionDataList.xml", "xml_prediction"),
+        "analysis_tips": ("https://raw.githubusercontent.com/VedAstro/VedAstro/master/Others/NotCode/HoroscopeAnalysisTips.txt", "txt_tips")
     }
     
     formatted_entries = []
     
-    # 1. Fetch Alpaca B.V. Raman Horoscope JSON Data
-    try:
-        print("Fetching B.V. Raman Horoscope Dataset...", flush=True)
-        r = requests.get(urls["bvraman_horoscope"], headers=HEADERS, timeout=10)
-        if r.status_code == 200:
-            json_data = r.json()
-            for item in json_data:
-                inst = item.get("instruction", "").strip()
-                inp = item.get("input", "").strip()
-                out = item.get("output", "").strip()
-                
-                context_str = f"Rule/Placement: {inst}"
-                if inp:
-                    context_str += f" ({inp})"
+    for dataset_key, (url, data_type) in urls.items():
+        print(f"Fetching VedAstro dataset: {dataset_key}...", flush=True)
+        try:
+            r = requests.get(url, headers=HEADERS, timeout=10)
+            if r.status_code != 200:
+                print(f"  -> Skipping {dataset_key} (Status: {r.status_code})", flush=True)
+                continue
                 
-                entry = f"VEDASTRO HOROSCOPE RULE: {context_str}\nInterpretation: {out}"
-                formatted_entries.append(clean_and_format_text(entry))
-            print(f"  -> Added {len(json_data)} B.V. Raman horoscope rules.", flush=True)
-    except Exception as e:
-        print(f"  -> Error fetching B.V. Raman JSON: {e}", flush=True)
-
-    # 2. Fetch Event Data List XML
-    try:
-        print("Fetching VedAstro Event Data XML...", flush=True)
-        r = requests.get(urls["event_data"], headers=HEADERS, timeout=10)
-        if r.status_code == 200:
-            root = ET.fromstring(r.content)
-            events = root.findall("Event")
-            for ev in events:
-                name = ev.findtext("Name", "").strip()
-                nature = ev.findtext("Nature", "").strip()
-                desc = ev.findtext("Description", "").strip()
-                if name and desc:
-                    entry = f"VEDASTRO ASTROLOGICAL EVENT: {name} [Nature: {nature}]\nDescription: {desc}"
+            if data_type == "json":
+                json_data = r.json()
+                for item in json_data:
+                    inst = item.get("instruction", "").strip()
+                    inp = item.get("input", "").strip()
+                    out = item.get("output", "").strip()
+                    context_str = f"Rule/Placement: {inst}"
+                    if inp:
+                        context_str += f" ({inp})"
+                    entry = f"VEDASTRO HOROSCOPE RULE: {context_str}\nInterpretation: {out}"
                     formatted_entries.append(clean_and_format_text(entry))
-            print(f"  -> Added {len(events)} VedAstro event rules.", flush=True)
-    except Exception as e:
-        print(f"  -> Error fetching Event Data XML: {e}", flush=True)
+                print(f"  -> Added {len(json_data)} entries from {dataset_key}.", flush=True)
 
-    # 3. Fetch Horoscope Data List XML
-    try:
-        print("Fetching VedAstro Horoscope Data XML...", flush=True)
-        r = requests.get(urls["horoscope_data"], headers=HEADERS, timeout=10)
-        if r.status_code == 200:
-            root = ET.fromstring(r.content)
-            horoscopes = root.findall("Horoscope")
-            for h in horoscopes:
-                name = h.findtext("Name", "").strip()
-                desc = h.findtext("Description", "").strip()
-                if name and desc:
-                    entry = f"VEDASTRO HOROSCOPE COMBINATION: {name}\nDescription: {desc}"
-                    formatted_entries.append(clean_and_format_text(entry))
-            print(f"  -> Added {len(horoscopes)} VedAstro horoscope combinations.", flush=True)
-    except Exception as e:
-        print(f"  -> Error fetching Horoscope Data XML: {e}", flush=True)
+            elif data_type.startswith("xml_"):
+                prefix_map = {
+                    "xml_event": "VEDASTRO ASTROLOGICAL EVENT",
+                    "xml_horoscope": "VEDASTRO HOROSCOPE COMBINATION",
+                    "xml_reference": "VEDASTRO REFERENCE FACT & PLANETARY INDICATION",
+                    "xml_non_raman": "VEDASTRO NON-RAMAN CLASSICAL RULE & UPAGRAHA",
+                    "xml_prediction": "VEDASTRO HOUSE LORD PREDICTION RULE"
+                }
+                prefix = prefix_map.get(data_type, "VEDASTRO RULE")
+                parsed_xml_entries = parse_xml_events(r.content, prefix)
+                formatted_entries.extend(parsed_xml_entries)
+                print(f"  -> Added {len(parsed_xml_entries)} entries from {dataset_key}.", flush=True)
+
+            elif data_type == "txt_tips":
+                tip_text = clean_and_format_text(r.text)
+                entry = f"VEDASTRO HOROSCOPE SYNTHESIS GUIDELINES & TIPS:\n{tip_text}"
+                formatted_entries.append(entry)
+                print(f"  -> Added analysis guidelines from {dataset_key}.", flush=True)
+
+        except Exception as e:
+            print(f"  -> Error processing {dataset_key}: {e}", flush=True)
 
     if not formatted_entries:
         print("Warning: No entries retrieved from VedAstro. Adding fallback data.", flush=True)
@@ -294,7 +307,7 @@ def fetch_vedastro_data(output_filepath: str):
     with open(output_filepath, "w", encoding="utf-8") as f:
         f.write(full_text)
         
-    print(f"Successfully saved {len(formatted_entries)} interpretation entries to {output_filepath}", flush=True)
+    print(f"Successfully saved {len(formatted_entries)} interpretation & reference entries to {output_filepath}", flush=True)
 
 
 def main():

```

--------------------------------------------------------------------------------

## Commit 3: 0ef6e71

```diff
commit 0ef6e715c6d57d85206730535ac26cded8b51b1c
Author: Shivapuri <142108173+Shivapuri@users.noreply.github.com>
Date:   Sat Aug 1 22:23:35 2026 +0530

    feat(jyotish-rag): Implement Jyotish data fetcher, RAG builder, and Dual-Engine FastMCP server
---
 .gitignore                  |   1 +
 Gemini.md                   |   5 +
 commit.py                   |   5 +
 export_code.py              |  66 ++++++++--
 rag/astrology_mcp_server.py | 180 ++++++++++++++++++++-----
 rag/build_jyotish_rag.py    |  74 +++++++++++
 rag/fetch_jyotish_data.py   | 314 ++++++++++++++++++++++++++++++++++++++++++++
 scripts/export_commits.py   |  82 ++++++++++++
 8 files changed, 679 insertions(+), 48 deletions(-)

diff --git a/.gitignore b/.gitignore
index 6f93b59..76f0593 100644
--- a/.gitignore
+++ b/.gitignore
@@ -10,3 +10,4 @@ cache/
 
 code_export.txt
 rag/chroma_astrology_db/
+rag/chroma_jyotish_db/
diff --git a/Gemini.md b/Gemini.md
index 1717379..b2e8713 100644
--- a/Gemini.md
+++ b/Gemini.md
@@ -54,6 +54,11 @@ When performing chart readings, follow the 4-step ReAct workflow embedded in the
   * *Example*: **Ascendant** *(the zodiac sign rising on the eastern horizon at birth, representing your core identity)*.
   * *Example*: **Domicile** *(when a planet is in the sign it naturally rules, acting like a king in their own castle)*.
   * *Example*: **Combust** *(when a planet is so close to the Sun that its visible rays are hidden)*.
+* **Dominant Zodiac Sign Overviews**: Before analyzing specific house placements or aspects, always provide a general overview of the characteristics, element, ruling planet, and archetypal theme of the chart's dominant zodiac signs (e.g., explaining Scorpio as an archetypal sign before interpreting Sun conjunct Saturn in Scorpio).
+* **The Extended Psychological Lens**: Keep your beautiful formatting (Core Architecture, Dominant Placements, Strengths, Summary Checklist), but ensure you always spotlight:
+  1. **The Pain Body**: Where they hold trauma or emotional armor (using debilitated planets or the Moon).
+  2. **Socialization**: How they make friends and open up (using Venus/11th House).
+  3. **Conflict Resolution**: How they fight or protect boundaries (using Mars and hard aspects).
 * **Grounding**: Base interpretations on modern psychological literature retrieved from `rag/chroma_astrology_db` and [`western/chart_context.json`](file:///Users/hajnaljanos/PycharmProjects/astra/western/chart_context.json).
 * **Verify Cache & Downloads**: Do not repeatedly download astronomical dataset files (`.dat`, `.bsp`). Use local cached files (`hip_main.dat`, `de421.bsp`).
 
diff --git a/commit.py b/commit.py
new file mode 100644
index 0000000..7643576
--- /dev/null
+++ b/commit.py
@@ -0,0 +1,5 @@
+import sys
+from scripts.export_commits import main
+
+if __name__ == "__main__":
+    main()
diff --git a/export_code.py b/export_code.py
index 115e9f2..a1cf57b 100644
--- a/export_code.py
+++ b/export_code.py
@@ -2,37 +2,70 @@
 """
 Astra Repository Code Exporter
 Combines key code files into a single text file for AI analysis.
+Filters out export artifacts, large dataset files, and unnecessary binary/cache files.
 """
 
 import os
 import argparse
 from pathlib import Path
 
-# Directories and files to ignore during export
+# Directories to ignore during export
 DEFAULT_EXCLUDE_DIRS = {
     ".git", ".idea", "__pycache__", "venv", ".venv", 
-    "cache", "chroma_astrology_db", "astrology_rag_data"
+    "cache", "chroma_astrology_db", "astrology_rag_data",
+    ".pytest_cache", ".mypy_cache", "node_modules", "dist", "build"
 }
 
+# Extensions to explicitly ignore
 DEFAULT_EXCLUDE_EXTENSIONS = {
-    ".dat", ".bsp", ".download", ".log", ".db", ".sqlite", ".pyc", ".png", ".jpg"
+    ".dat", ".bsp", ".download", ".log", ".db", ".sqlite", ".sqlite3", 
+    ".pyc", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".bin", ".pickle",
+    ".zip", ".tar", ".gz"
 }
 
-# Key text/code extensions to include
+# Explicit filenames to exclude (export outputs, temporary files)
+DEFAULT_EXCLUDE_FILES = {
+    "code_export.txt", "commits_export.md"
+}
+
+# Extensions to include
 DEFAULT_INCLUDE_EXTENSIONS = {
-    ".py", ".md", ".json", ".txt"
+    ".py", ".md", ".json", ".txt", ".sh", ".yaml", ".yml"
 }
 
+def is_export_artifact(file_path: Path, output_file: Path) -> bool:
+    """Checks if a file is an export artifact or generated output file."""
+    file_name = file_path.name.lower()
+    
+    # Exclude target output file
+    if file_path.resolve() == output_file.resolve():
+        return True
+
+    # Exclude known export files
+    if file_name in DEFAULT_EXCLUDE_FILES:
+        return True
+
+    # Exclude pattern-matched export files (e.g. *_export.txt, *_export.md)
+    if (file_name.endswith("_export.txt") or file_name.endswith("_export.md") or 
+        file_name.endswith("_export.json") or (file_name.startswith("export_") and file_name.endswith((".txt", ".md")))):
+        return True
+
+    return False
+
+
 def export_repository(
     root_dir: str = ".",
     output_file: str = "code_export.txt",
     target_folder: str = None,
-    include_extensions: set = DEFAULT_INCLUDE_EXTENSIONS
+    include_extensions: set = DEFAULT_INCLUDE_EXTENSIONS,
+    max_size_kb: int = 500
 ):
     """
     Scans the repository and aggregates relevant source files into a single text file.
     """
     root_path = Path(root_dir).resolve()
+    out_path = Path(output_file).resolve()
+    max_file_size_bytes = max_size_kb * 1024
     
     if target_folder:
         search_path = (root_path / target_folder).resolve()
@@ -43,11 +76,12 @@ def export_repository(
         search_path = root_path
 
     print(f"Scanning directory: {search_path}")
+    print(f"Max file size limit: {max_size_kb} KB")
     
     exported_files_count = 0
     total_lines = 0
 
-    with open(output_file, "w", encoding="utf-8") as out:
+    with open(out_path, "w", encoding="utf-8") as out:
         out.write("=================================================================\n")
         out.write(f" ASTRA REPOSITORY CODE EXPORT\n")
         out.write(f" Target Path: {search_path.relative_to(root_path) if search_path != root_path else '.'}\n")
@@ -55,14 +89,15 @@ def export_repository(
 
         for current_root, dirs, files in os.walk(search_path):
             # Exclude ignored directories in-place so os.walk doesn't enter them
-            dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDE_DIRS]
+            dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDE_DIRS and not d.startswith('.')]
 
             for file_name in sorted(files):
                 file_path = Path(current_root) / file_name
                 rel_path = file_path.relative_to(root_path)
 
-                # Skip output file itself
-                if file_path.name == Path(output_file).name:
+                # Skip export output files and artifacts
+                if is_export_artifact(file_path, out_path):
+                    print(f"  [-] Skipped artifact: {rel_path}")
                     continue
 
                 # Check extension filter
@@ -72,6 +107,12 @@ def export_repository(
                 if file_path.suffix.lower() in DEFAULT_EXCLUDE_EXTENSIONS:
                     continue
 
+                # Check file size limit
+                file_size = file_path.stat().st_size
+                if file_size > max_file_size_bytes:
+                    print(f"  [-] Skipped large file: {rel_path} ({file_size / 1024:.1f} KB > {max_size_kb} KB)")
+                    continue
+
                 try:
                     with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                         content = f.read()
@@ -92,7 +133,7 @@ def export_repository(
 
     print("\n-----------------------------------------------------------------")
     print(f"Export Complete! Exported {exported_files_count} files ({total_lines} lines).")
-    print(f"Output saved to: {Path(output_file).resolve()}")
+    print(f"Output saved to: {out_path}")
     print("-----------------------------------------------------------------")
 
 
@@ -100,6 +141,7 @@ if __name__ == "__main__":
     parser = argparse.ArgumentParser(description="Export project code into a single text file for AI analysis.")
     parser.add_argument("-o", "--output", default="code_export.txt", help="Output text file path (default: code_export.txt)")
     parser.add_argument("-f", "--folder", default=None, help="Export only a specific subfolder (e.g. western, jyotish, rag)")
+    parser.add_argument("-s", "--max-size", type=int, default=500, help="Maximum file size in KB to include (default: 500 KB)")
     
     args = parser.parse_args()
-    export_repository(output_file=args.output, target_folder=args.folder)
+    export_repository(output_file=args.output, target_folder=args.folder, max_size_kb=args.max_size)
diff --git a/rag/astrology_mcp_server.py b/rag/astrology_mcp_server.py
index c08d377..9f020b2 100644
--- a/rag/astrology_mcp_server.py
+++ b/rag/astrology_mcp_server.py
@@ -17,56 +17,90 @@ if BASE_DIR not in sys.path:
     sys.path.insert(0, BASE_DIR)
 
 from western.generate_chart import generate_ai_json
+from jyotish.generate_jyotish import generate_vedic_chart
 from langchain_chroma import Chroma
 from langchain_huggingface import HuggingFaceEmbeddings
 
 COT_SYSTEM_INSTRUCTIONS = """
-You are a Principal Modern Psychological Astrologer and AI Agent driven by a strict Chain of Thought (CoT) / ReAct reasoning protocol.
+You are a Principal AI Architect and Master Astrologer operating Astra's Dual-Engine Astrology System.
+You support both Western Psychological Astrology and Parashari Vedic Astrology (Jyotish) via strict Chain of Thought (CoT) protocols.
 
-Whenever a user requests a birth chart reading, you MUST autonomously execute this 4-step workflow:
+==============================================================================
+WESTERN / PSYCHOLOGICAL ASTROLOGY WORKFLOW
+==============================================================================
+When a user requests a Western chart reading, follow this 4-Step ReAct workflow:
 
 Step 1 (Action - Mathematical Calculation):
-  Call the `calculate_birth_chart` tool with the native's birth details to compute the exact planetary positions, dignities, sect, and lots.
+  Call `calculate_birth_chart` with native's birth details to compute exact tropical placements, Whole Sign houses, dignities, sect, and hermetic lots.
 
 Step 2 (Reasoning - Target Identification):
-  Analyze the JSON and isolate the planets that trigger the psychological framework:
-  - Identity: Ascendant, Chart Ruler, and Sect Light.
-  - Pain Body & Trauma: The Moon, planets in Detriment/Fall, or the out-of-sect Malefic.
-  - Social & Conflict: Venus (connection), Mars (boundaries/anger), and hard aspects (Squares/Oppositions).
-  - Flow State: Domicile planets, Jupiter, and the Lot of Fortune.
+  Analyze the JSON and isolate key psychological placements:
+  - Core Architecture: Ascendant, Chart Ruler, and Sect Light.
+  - Pain Body & Trauma: The Moon, planets in Detriment/Fall, or out-of-sect Malefic.
+  - Socialization & Conflict: Venus (connection/intimacy), Mars (boundaries/anger), and hard aspects.
+  - Flow State: Domicile planets, Jupiter, and Lot of Fortune.
 
-Step 3 (Action - Psychological Book Research):
-  Call `query_modern_astrology_books` 2 to 3 times to research these specific placements in the local vector database.
+Step 3 (Action - Western Book Research):
+  Call `query_modern_astrology_books` 1 to 3 times for target placements.
 
-Step 4 (Synthesis - The Extended Reading):
-  Output a highly empathetic, modern reading that strictly follows this 5-part structure:
-  
+Step 4 (Synthesis - Modern Psychological Reading):
+  Synthesize a 5-part empathetic reading:
   Part 1: The Core Architecture of the Chart
-  (Explain Ascendant, Sect, and House layout in simple terms).
+  Part 2: Dominant Placements & Psychological Reading (includes sign overview, top placements, and Pain Body)
+  Part 3: Behavioral Psychology (Socialization & Conflict Resolution)
+  Part 4: Supporting Strengths & Fortune
+  Summary Checklist of Your Chart Profile (Archetype, Superpower, Core Life Lesson)
+
+
+==============================================================================
+VEDIC / JYOTISH ASTROLOGY WORKFLOW
+==============================================================================
+When a user requests a Vedic / Jyotish reading, follow this 4-Step ReAct workflow:
+
+Step 1 (Action - Vedic Calculation):
+  Call `calculate_vedic_chart` with native's birth details (latitude, longitude, timezone offset) to compute True Chitra Paksha (Lahiri) Ayanamsa, Panchanga, D1 Rasi, D9 Navamsa, and Vimshottari Dasha timeline.
+
+Step 2 (Reasoning - Target Identification):
+  Analyze the JSON and isolate key Jyotish placements:
+  - Lagna & Moon Nakshatra: Ascendant sign/nakshatra, Moon sign/nakshatra/pada.
+  - D9 Navamsa: Soul purpose, hidden strengths, and planet dignities in D9.
+  - Dasha Timeline: Running Mahadasha, Antardasha, and Pratyantardasha periods.
+
+Step 3 (Action - Classical & VedAstro Book Research):
+  Call `query_vedic_astrology_books` 1 to 3 times to retrieve authentic classical shlokas (BPHS, Brihat Jataka) and VedAstro rules.
+
+Step 4 (Synthesis - Empowering 4-Part Vedic Reading):
+  Synthesize an empowering 4-part reading focusing on Karma, Dharma, and Timelines, translating ancient fatalistic language into modern constructive guidance:
   
-  Part 2: The Dominant Placements & Psychological Reading
-  (First provide an educational overview of the general characteristics and archetypes of the dominant zodiac signs active in the chart—such as their element, ruling planets, and overall psychological themes. Then analyze the top 3 specific placements using bullet points for 'Mathematical Placement' and 'What It Means for You'. Address the native's "Pain Body" and emotional shadows here using their most difficult placement).
+  Part 1: Panchanga & Lagna Architecture
+  (Explain Lagna sign, Nakshatra, Moon Pada, Tithi, and core physical/mental temperament).
   
-  Part 3: Behavioral Psychology (Socialization & Conflict)
-  (NEW EXTENSION: Explicitly analyze how they make friends and experience intimacy based on Venus/11th House, and how they resolve conflict, fight, or protect boundaries based on Mars/Aspects).
+  Part 2: D1 Rasi & D9 Navamsa Placements
+  (Analyze dominant planets in D1 Rasi and their internal soul evolution in D9 Navamsa).
   
-  Part 4: Supporting Strengths & Fortune
-  (Analyze Jupiter, the Lot of Fortune, and where they naturally hit a "Flow State").
+  Part 3: Vimshottari Dasha Timeline & Karmic Evolution
+  (Analyze current running Dasha period, timing of major life shifts, and active karmic lessons).
   
-  Summary Checklist of Your Chart Profile
-  (Provide a quick bulleted list: Their Archetype, their Superpower, and their Core Life Lesson).
+  Part 4: Practical Dharma & Remedies
+  (Offer constructive guidance for growth, ethical living, emotional resilience, and boundary management).
 """
 
-# 1. Instantiate MCP Server with Chain of Thought instructions
+# 1. Instantiate MCP Server with Dual-Engine Chain of Thought instructions
 try:
     mcp = FastMCP(
-        "Astra Modern Psychological Astrology RAG Engine",
+        "Astra Dual-Engine Astrology RAG Server",
         instructions=COT_SYSTEM_INSTRUCTIONS
     )
 except TypeError:
-    mcp = FastMCP("Astra Modern Psychological Astrology RAG Engine")
+    mcp = FastMCP("Astra Dual-Engine Astrology RAG Server")
 
-CHROMA_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_astrology_db")
+WESTERN_CHROMA_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_astrology_db")
+JYOTISH_CHROMA_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_jyotish_db")
+
+
+# ------------------------------------------------------------------------------
+# WESTERN ASTROLOGY TOOLS
+# ------------------------------------------------------------------------------
 
 @mcp.tool()
 def calculate_birth_chart(
@@ -80,11 +114,11 @@ def calculate_birth_chart(
     country_code: str = "GB"
 ) -> str:
     """
-    Calculates a mathematically precise Western Astrology Chart.
-    Returns structured JSON containing the Ascendant, Sect (Day/Night), traditional and modern planetary placements 
+    Calculates a mathematically precise Western (Tropical) Astrology Chart.
+    Returns structured JSON containing the Ascendant, Sect (Day/Night), traditional and modern planetary placements
     (with Signs, Whole Sign Houses, and Dignities), and Hermetic Lots.
     
-    Chain of Thought Step 1: Execute this tool first when analyzing a user's chart.
+    Western CoT Step 1: Execute this tool first when analyzing a Western chart.
     """
     output_path = os.path.join(BASE_DIR, "western", "chart_context.json")
     try:
@@ -104,25 +138,26 @@ def calculate_birth_chart(
             chart_data = json.load(f)
         return json.dumps(chart_data, indent=2)
     except Exception as e:
-        return f"Error generating chart: {str(e)}"
+        return f"Error generating Western chart: {str(e)}"
+
 
 @mcp.tool()
 def query_modern_astrology_books(query: str) -> str:
     """
-    Queries the local Modern Psychological Astrology Vector Database (containing digitized modern books).
+    Queries the local Modern Psychological Astrology Vector Database (containing modern Western books).
     Pass targeted psychological queries such as 'Moon in Taurus in 2nd House' or 'Saturn transit square Sun'.
     
-    Chain of Thought Step 3: Call this tool 1 to 3 times for key chart placements identified in Step 2.
+    Western CoT Step 3: Call this tool 1 to 3 times for key chart placements.
     """
     try:
-        if not os.path.exists(CHROMA_DB_DIR):
-            return "Vector database not found. Please ensure build_rag_pipeline.py has completed building ChromaDB."
+        if not os.path.exists(WESTERN_CHROMA_DB_DIR):
+            return "Western Vector database not found. Please run build_rag_pipeline.py first."
             
         embedding_model = HuggingFaceEmbeddings(
             model_name="sentence-transformers/all-MiniLM-L6-v2"
         )
         vector_store = Chroma(
-            persist_directory=CHROMA_DB_DIR,
+            persist_directory=WESTERN_CHROMA_DB_DIR,
             embedding_function=embedding_model
         )
         results = vector_store.similarity_search(query, k=4)
@@ -134,7 +169,80 @@ def query_modern_astrology_books(query: str) -> str:
             output += f"--- Result {idx} [Source: {source}, Page: {page}] ---\n{doc.page_content}\n\n"
         return output
     except Exception as e:
-        return f"Error querying vector database: {str(e)}"
+        return f"Error querying Western vector database: {str(e)}"
+
+
+# ------------------------------------------------------------------------------
+# VEDIC / JYOTISH ASTROLOGY TOOLS
+# ------------------------------------------------------------------------------
+
+@mcp.tool()
+def calculate_vedic_chart(
+    name: str = "Subject",
+    year: int = 1995,
+    month: int = 5,
+    day: int = 15,
+    hour: int = 14,
+    minute: int = 30,
+    latitude: float = 51.5074,
+    longitude: float = -0.1278,
+    timezone_offset: float = 1.0
+) -> str:
+    """
+    Calculates a mathematically precise Parashari Vedic (Sidereal) Astrology Chart using jyotishganit.
+    Returns structured JSON containing True Chitra Paksha (Lahiri) Ayanamsa, Panchanga, D1 Rasi Chart, 
+    D9 Navamsa Chart, and Vimshottari Dasha timeline.
+    
+    Vedic CoT Step 1: Execute this tool first when analyzing a Vedic chart.
+    """
+    output_path = os.path.join(BASE_DIR, "jyotish", "vedic_context.json")
+    try:
+        chart_data = generate_vedic_chart(
+            name=name,
+            year=year,
+            month=month,
+            day=day,
+            hour=hour,
+            minute=minute,
+            latitude=latitude,
+            longitude=longitude,
+            timezone_offset=timezone_offset,
+            output_filepath=output_path
+        )
+        return json.dumps(chart_data, indent=2, ensure_ascii=False)
+    except Exception as e:
+        return f"Error generating Vedic chart: {str(e)}"
+
+
+@mcp.tool()
+def query_vedic_astrology_books(query: str) -> str:
+    """
+    Queries the local Jyotish Vector Database (containing WisdomLib BPHS texts and VedAstro rules).
+    Pass targeted Vedic queries such as 'Lagna in Aries Ashwini' or 'Vimshottari Dasha Saturn Mahadasha'.
+    
+    Vedic CoT Step 3: Call this tool 1 to 3 times for key Vedic chart placements and Dashas.
+    """
+    try:
+        if not os.path.exists(JYOTISH_CHROMA_DB_DIR):
+            return "Vedic Vector database not found. Please run fetch_jyotish_data.py and build_jyotish_rag.py first."
+            
+        embedding_model = HuggingFaceEmbeddings(
+            model_name="sentence-transformers/all-MiniLM-L6-v2"
+        )
+        vector_store = Chroma(
+            persist_directory=JYOTISH_CHROMA_DB_DIR,
+            embedding_function=embedding_model
+        )
+        results = vector_store.similarity_search(query, k=4)
+        
+        output = f"=== VEDIC / JYOTISH RAG SEARCH RESULTS FOR: '{query}' ===\n\n"
+        for idx, doc in enumerate(results, 1):
+            source = os.path.basename(doc.metadata.get("source", "jyotish_text"))
+            output += f"--- Result {idx} [Source: {source}] ---\n{doc.page_content}\n\n"
+        return output
+    except Exception as e:
+        return f"Error querying Vedic vector database: {str(e)}"
+
 
 if __name__ == "__main__":
     mcp.run()
diff --git a/rag/build_jyotish_rag.py b/rag/build_jyotish_rag.py
new file mode 100644
index 0000000..cf51337
--- /dev/null
+++ b/rag/build_jyotish_rag.py
@@ -0,0 +1,74 @@
+"""
+Jyotish RAG Builder
+Ingests pristine digital Jyotish text files from /rag/jyotish_rag_data/
+and builds an isolated ChromaDB vector database in /rag/chroma_jyotish_db/.
+"""
+
+import os
+import glob
+from langchain_community.document_loaders import TextLoader
+from langchain_text_splitters import RecursiveCharacterTextSplitter
+from langchain_chroma import Chroma
+from langchain_huggingface import HuggingFaceEmbeddings
+
+DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jyotish_rag_data")
+CHROMA_DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_jyotish_db")
+
+
+def load_text_documents():
+    """Ingest clean text files from jyotish_rag_data directory."""
+    documents = []
+    print(f"Ingesting text files from {DATA_DIR}...")
+    
+    txt_files = glob.glob(os.path.join(DATA_DIR, "*.txt"))
+    for file_path in txt_files:
+        try:
+            print(f"Loading document: {os.path.basename(file_path)}...")
+            loader = TextLoader(file_path, encoding="utf-8")
+            docs = loader.load()
+            print(f"  -> Loaded document with {len(docs[0].page_content)} characters.")
+            documents.extend(docs)
+        except Exception as e:
+            print(f"Error loading {file_path}: {e}")
+
+    return documents
+
+
+def build_jyotish_vector_store(documents):
+    """Split text documents into chunks and embed into ChromaDB."""
+    print("Splitting Jyotish documents into search-ready chunks...")
+    text_splitter = RecursiveCharacterTextSplitter(
+        chunk_size=1500,
+        chunk_overlap=250,
+        separators=["\n\n", "\n", ".", " ", ""]
+    )
+    chunks = text_splitter.split_documents(documents)
+    print(f"Created {len(chunks)} total text chunks for Jyotish RAG.")
+
+    print("Initializing HuggingFace embedding model (all-MiniLM-L6-v2)...")
+    embedding_model = HuggingFaceEmbeddings(
+        model_name="sentence-transformers/all-MiniLM-L6-v2"
+    )
+
+    print(f"Embedding chunks into Chroma Vector DB at {CHROMA_DB_DIR}...")
+    vector_store = Chroma.from_documents(
+        documents=chunks,
+        embedding=embedding_model,
+        persist_directory=CHROMA_DB_DIR
+    )
+    print("Jyotish Vector Database successfully built and persisted!")
+    return vector_store
+
+
+def main():
+    print("=== Phase 2: Building Jyotish RAG Vector Database ===")
+    docs = load_text_documents()
+    if not docs:
+        print("No text documents found in jyotish_rag_data directory. Please run fetch_jyotish_data.py first.")
+        return
+    build_jyotish_vector_store(docs)
+    print("=== Phase 2 Complete! Vector store saved in /rag/chroma_jyotish_db/ ===")
+
+
+if __name__ == "__main__":
+    main()
diff --git a/rag/fetch_jyotish_data.py b/rag/fetch_jyotish_data.py
new file mode 100644
index 0000000..6df4956
--- /dev/null
+++ b/rag/fetch_jyotish_data.py
@@ -0,0 +1,314 @@
+"""
+Jyotish Data Fetcher
+Autonomously fetches authentic classical Vedic astrology texts from WisdomLib
+and open-source Jyotish dataset interpretations from VedAstro into /rag/jyotish_rag_data/
+with OCR noise cleaning, smart sentence line-wrap unwrapping, numerical sorting, and structured formatting.
+"""
+
+import os
+import sys
+import re
+import json
+import xml.etree.ElementTree as ET
+import requests
+import unicodedata
+from bs4 import BeautifulSoup
+from concurrent.futures import ThreadPoolExecutor, as_completed
+
+DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jyotish_rag_data")
+HEADERS = {
+    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
+}
+
+
+def clean_and_format_text(text: str) -> str:
+    """
+    Normalizes Unicode text, removes WisdomLib OCR page noise & UI warnings,
+    rejoins broken line-wrapped words/sentences, and formats clean paragraphs.
+    """
+    if not text:
+        return ""
+    
+    # 1. Normalize Unicode (NFKD)
+    normalized = unicodedata.normalize("NFKD", text)
+    
+    # 2. Remove OCR page warning blocks and UI notices
+    cleaned = re.sub(
+        r'Warning!\s*Page\s*nr\.\s*\d+.*?original\s*PDF\.?', 
+        '', 
+        normalized, 
+        flags=re.DOTALL | re.IGNORECASE
+    )
+    
+    # 3. Filter out specific repetitive UI boilerplate
+    noise_patterns = [
+        r'Buy\s+relevant\s+books',
+        r'Support\s+me\s+on\s+Patreon',
+        r'Click\s+the\s+page\s+link\s+to\s+verify.*',
+        r'Last\s+Updated:\s*\d+\s+\w+,\s*\d+'
+    ]
+    for pat in noise_patterns:
+        cleaned = re.sub(pat, '', cleaned, flags=re.IGNORECASE)
+
+    # 4. Filter raw lines and remove standalone UI tokens
+    raw_lines = [l.strip() for l in cleaned.splitlines() if l.strip()]
+    filtered_lines = []
+    for line in raw_lines:
+        if line.lower() in ['resources', 'buddhism', 'hinduism', 'jainism', 'jyotisha', 'sanskrit', 'next >', '< previous']:
+            continue
+        filtered_lines.append(line)
+
+    # 5. Smart line-unwrapping to fix awkward line breaks inside sentences
+    formatted_paragraphs = []
+    curr = ""
+    
+    for line in filtered_lines:
+        if not curr:
+            curr = line
+            continue
+            
+        # Rejoin hyphenated word split across lines (e.g. "pranahani-\nbhupalatvam")
+        if curr.endswith("-") and not curr.endswith(" -"):
+            curr = curr[:-1] + line
+        # If current line ends with sentence punctuation or verse end OR next line is a header/verse delimiter
+        elif curr.endswith(("||", "|", ".", "!", "?", ":")) or re.match(r'^(===|Sloka|Verse|Adhyaya|Chapter|\|\|)', line, re.IGNORECASE):
+            formatted_paragraphs.append(curr)
+            curr = line
+        else:
+            # Join unwrapped sentence fragment cleanly with space
+            curr = curr + " " + line
+            
+    if curr:
+        formatted_paragraphs.append(curr)
+        
+    return "\n\n".join(formatted_paragraphs)
+
+
+def parse_section_key(title: str, slug: str):
+    """Extracts (slug, chapter_num, verse_num) for deterministic numerical sorting."""
+    m_verse = re.search(r'Verse\s+(\d+)\.(\d+)', title, re.IGNORECASE)
+    if m_verse:
+        return (slug, int(m_verse.group(1)), int(m_verse.group(2)))
+    
+    m_chap = re.search(r'(?:Chapter|Adhyaya|Adh\.?)\s+(\d+)(?:[,\s]+Verse\s+(\d+))?', title, re.IGNORECASE)
+    if m_chap:
+        c_num = int(m_chap.group(1))
+        v_num = int(m_chap.group(2)) if m_chap.group(2) else 0
+        return (slug, c_num, v_num)
+        
+    m_num = re.search(r'(\d+)\.(\d+)', title)
+    if m_num:
+        return (slug, int(m_num.group(1)), int(m_num.group(2)))
+
+    return (slug, 999, 999)
+
+
+def fetch_single_doc(doc_url: str, slug: str):
+    """Scrapes a single WisdomLib document page and extracts clean text content."""
+    try:
+        d_resp = requests.get(doc_url, headers=HEADERS, timeout=8)
+        if d_resp.status_code != 200:
+            return None
+        
+        d_soup = BeautifulSoup(d_resp.text, "html.parser")
+        raw_title = d_soup.title.string.strip() if d_soup.title else doc_url.split("/")[-1]
+        
+        # Clean title header (remove site suffixes)
+        clean_title = re.sub(r'\s*\[.*?\]', '', raw_title).strip()
+        
+        content_div = d_soup.find(id="scontent") or d_soup.find(class_="chapter-content")
+        if not content_div:
+            content_div = d_soup.find("article") or d_soup.find("main")
+        
+        if content_div:
+            raw_paragraph = content_div.get_text("\n").strip()
+            cleaned_p = clean_and_format_text(raw_paragraph)
+            if len(cleaned_p) > 30:
+                key = parse_section_key(clean_title, slug)
+                
+                # Format clean, human-readable section header
+                book_name = slug.replace("-", " ").title()
+                formatted_header = f"=== BOOK: {book_name} | SECTION: {clean_title} ==="
+                
+                return {
+                    "key": key,
+                    "content": f"{formatted_header}\n\n{cleaned_p}\n"
+                }
+    except Exception:
+        pass
+    return None
+
+
+def fetch_wisdomlib_texts(output_filepath: str):
+    """
+    Scrapes classical Jyotish books from WisdomLib (BPHS, Brihat Jataka, Phaladeepika).
+    Parses, cleans OCR noise, fixes line wrapping, sorts sections numerically, and saves to file.
+    """
+    print("--- Starting Enhanced WisdomLib Classical Vedic Scraper ---", flush=True)
+    
+    book_urls = [
+        "https://www.wisdomlib.org/hinduism/book/brihat-parasara-hora-shastra",
+        "https://www.wisdomlib.org/hinduism/book/brihat-jataka-by-varahamihira-sanskrit-english",
+        "https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation",
+        "https://www.wisdomlib.org/hinduism/book/brihat-samhita"
+    ]
+    
+    scraped_sections = []
+    
+    for book_url in book_urls:
+        slug = book_url.split("/")[-1]
+        print(f"Checking WisdomLib book: {slug}...", flush=True)
+        try:
+            resp = requests.get(book_url, headers=HEADERS, timeout=10)
+            if resp.status_code != 200:
+                print(f"  -> Skipping {slug} (Status code: {resp.status_code})", flush=True)
+                continue
+            
+            soup = BeautifulSoup(resp.text, "html.parser")
+            doc_links = []
+            for a in soup.find_all("a", href=True):
+                href = a["href"]
+                if "/d/doc" in href and slug in href:
+                    full_link = href if href.startswith("http") else f"https://www.wisdomlib.org{href}"
+                    if full_link not in doc_links:
+                        doc_links.append(full_link)
+            
+            print(f"  -> Found {len(doc_links)} document links for {slug}. Fetching content...", flush=True)
+            
+            target_docs = doc_links[:60]
+            with ThreadPoolExecutor(max_workers=8) as executor:
+                futures = [executor.submit(fetch_single_doc, url, slug) for url in target_docs]
+                for future in as_completed(futures):
+                    result = future.result()
+                    if result:
+                        scraped_sections.append(result)
+                        
+        except Exception as err:
+            print(f"  -> Error fetching book {slug}: {err}", flush=True)
+            continue
+
+    if not scraped_sections:
+        print("Warning: No paragraphs scraped from WisdomLib. Creating fallback context.", flush=True)
+        fallback_entry = {
+            "key": ("fallback", 0, 0),
+            "content": (
+                "=== BOOK: Brihat Parashara Hora Shastra | SECTION: Core Principles ===\n\n"
+                "Classical Parashari Principles dictate that the Lagna represents core destiny, "
+                "the Moon nakshatra and pada reveal emotional karma, and running Vimshottari Dasha "
+                "dictates active karmic periods."
+            )
+        }
+        scraped_sections.append(fallback_entry)
+
+    # Sort sections numerically by (slug, chapter_number, verse_number)
+    scraped_sections.sort(key=lambda item: item["key"])
+    
+    formatted_contents = [sec["content"] for sec in scraped_sections]
+    full_text = "\n\n".join(formatted_contents)
+    
+    with open(output_filepath, "w", encoding="utf-8") as f:
+        f.write(full_text)
+    
+    print(f"Successfully saved {len(formatted_contents)} numerically sorted, line-unwrapped & cleaned sections to {output_filepath}", flush=True)
+
+
+def fetch_vedastro_data(output_filepath: str):
+    """
+    Fetches open-source Jyotish datasets from VedAstro GitHub repository.
+    Parses JSON and XML dataset files into clean, structured interpretation text.
+    """
+    print("--- Starting VedAstro Open-Source Data Fetcher ---", flush=True)
+    
+    urls = {
+        "bvraman_horoscope": "https://raw.githubusercontent.com/VedAstro/VedAstro/master/HuggingFace/alpaca_bvraman_horoscope_data.json",
+        "event_data": "https://raw.githubusercontent.com/VedAstro/VedAstro/master/Library/XMLData/EventDataList.xml",
+        "horoscope_data": "https://raw.githubusercontent.com/VedAstro/VedAstro/master/Library/XMLData/HoroscopeDataList.xml"
+    }
+    
+    formatted_entries = []
+    
+    # 1. Fetch Alpaca B.V. Raman Horoscope JSON Data
+    try:
+        print("Fetching B.V. Raman Horoscope Dataset...", flush=True)
+        r = requests.get(urls["bvraman_horoscope"], headers=HEADERS, timeout=10)
+        if r.status_code == 200:
+            json_data = r.json()
+            for item in json_data:
+                inst = item.get("instruction", "").strip()
+                inp = item.get("input", "").strip()
+                out = item.get("output", "").strip()
+                
+                context_str = f"Rule/Placement: {inst}"
+                if inp:
+                    context_str += f" ({inp})"
+                
+                entry = f"VEDASTRO HOROSCOPE RULE: {context_str}\nInterpretation: {out}"
+                formatted_entries.append(clean_and_format_text(entry))
+            print(f"  -> Added {len(json_data)} B.V. Raman horoscope rules.", flush=True)
+    except Exception as e:
+        print(f"  -> Error fetching B.V. Raman JSON: {e}", flush=True)
+
+    # 2. Fetch Event Data List XML
+    try:
+        print("Fetching VedAstro Event Data XML...", flush=True)
+        r = requests.get(urls["event_data"], headers=HEADERS, timeout=10)
+        if r.status_code == 200:
+            root = ET.fromstring(r.content)
+            events = root.findall("Event")
+            for ev in events:
+                name = ev.findtext("Name", "").strip()
+                nature = ev.findtext("Nature", "").strip()
+                desc = ev.findtext("Description", "").strip()
+                if name and desc:
+                    entry = f"VEDASTRO ASTROLOGICAL EVENT: {name} [Nature: {nature}]\nDescription: {desc}"
+                    formatted_entries.append(clean_and_format_text(entry))
+            print(f"  -> Added {len(events)} VedAstro event rules.", flush=True)
+    except Exception as e:
+        print(f"  -> Error fetching Event Data XML: {e}", flush=True)
+
+    # 3. Fetch Horoscope Data List XML
+    try:
+        print("Fetching VedAstro Horoscope Data XML...", flush=True)
+        r = requests.get(urls["horoscope_data"], headers=HEADERS, timeout=10)
+        if r.status_code == 200:
+            root = ET.fromstring(r.content)
+            horoscopes = root.findall("Horoscope")
+            for h in horoscopes:
+                name = h.findtext("Name", "").strip()
+                desc = h.findtext("Description", "").strip()
+                if name and desc:
+                    entry = f"VEDASTRO HOROSCOPE COMBINATION: {name}\nDescription: {desc}"
+                    formatted_entries.append(clean_and_format_text(entry))
+            print(f"  -> Added {len(horoscopes)} VedAstro horoscope combinations.", flush=True)
+    except Exception as e:
+        print(f"  -> Error fetching Horoscope Data XML: {e}", flush=True)
+
+    if not formatted_entries:
+        print("Warning: No entries retrieved from VedAstro. Adding fallback data.", flush=True)
+        formatted_entries.append(
+            "VEDASTRO INTERPRETATION RULE: Sun in 10th House\n"
+            "Interpretation: Gives administrative authority, high career visibility, and leadership karma."
+        )
+
+    full_text = "\n\n".join(formatted_entries)
+    with open(output_filepath, "w", encoding="utf-8") as f:
+        f.write(full_text)
+        
+    print(f"Successfully saved {len(formatted_entries)} interpretation entries to {output_filepath}", flush=True)
+
+
+def main():
+    print("=== Phase 1: Ingesting Authentic Jyotish Texts & Datasets ===", flush=True)
+    os.makedirs(DATA_DIR, exist_ok=True)
+    
+    wisdomlib_path = os.path.join(DATA_DIR, "bphs_wisdomlib.txt")
+    vedastro_path = os.path.join(DATA_DIR, "vedastro_interpretations.txt")
+    
+    fetch_wisdomlib_texts(wisdomlib_path)
+    fetch_vedastro_data(vedastro_path)
+    
+    print("=== Phase 1 Complete! Text files ready in /rag/jyotish_rag_data/ ===", flush=True)
+
+
+if __name__ == "__main__":
+    main()
diff --git a/scripts/export_commits.py b/scripts/export_commits.py
new file mode 100644
index 0000000..97155c1
--- /dev/null
+++ b/scripts/export_commits.py
@@ -0,0 +1,82 @@
+import os
+import subprocess
+import sys
+
+
+def get_commit_hashes(count):
+    """Retrieves the last N commit hashes."""
+    try:
+        cmd = ["git", "log", f"-n{count}", "--pretty=format:%H"]
+        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
+        return result.stdout.splitlines()
+    except subprocess.CalledProcessError as e:
+        print(f"Error fetching commit hashes: {e}")
+        return []
+
+
+def get_commit_details(commit_hash):
+    """Retrieves metadata and diff for a specific commit."""
+    try:
+        # --stat adds a summary of files changed, --patch adds the diff
+        # --unified=3 ensures 3 lines of context around changes (default git behavior)
+        cmd = ["git", "show", "--stat", "--patch", "--unified=3", commit_hash]
+        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
+        return result.stdout
+    except subprocess.CalledProcessError as e:
+        return f"Error fetching details for commit {commit_hash}: {e}"
+
+
+def export_commits(count, output_file="commits_export.md"):
+    """Generates a Markdown report of recent commits."""
+    hashes = get_commit_hashes(count)
+    if not hashes:
+        print("No commits found to export.")
+        return
+
+    # Use the project root for the output file
+    script_dir = os.path.dirname(os.path.abspath(__file__))
+    if os.path.basename(script_dir) == "scripts":
+        project_root = os.path.dirname(script_dir)
+    else:
+        project_root = script_dir
+
+    output_path = os.path.join(project_root, output_file)
+
+    with open(output_path, "w", encoding="utf-8") as f:
+        f.write("# Git Commit Export\n")
+        f.write(f"Generated on: {subprocess.check_output(['date']).decode().strip()}\n")
+        f.write(f"Number of commits requested: {count}\n\n")
+        f.write("-" * 80 + "\n\n")
+
+        for i, h in enumerate(hashes):
+            details = get_commit_details(h)
+            f.write(f"## Commit {i + 1}: {h[:7]}\n\n")
+            f.write("```diff\n")
+            f.write(details)
+            f.write("\n```\n\n")
+            f.write("-" * 80 + "\n\n")
+
+    print(f"Successfully exported {len(hashes)} commits to: {output_path}")
+
+
+def main():
+    print("--- Commit Export Tool ---")
+
+    if len(sys.argv) > 1:
+        try:
+            n = int(sys.argv[1])
+        except ValueError:
+            print("Invalid argument. Usage: python export_commits.py [number]")
+            sys.exit(1)
+    else:
+        try:
+            val = input("How many recent commits would you like to export? (Default 5): ").strip()
+            n = int(val) if val else 5
+        except (ValueError, EOFError):
+            n = 5
+
+    export_commits(n)
+
+
+if __name__ == "__main__":
+    main()

```

--------------------------------------------------------------------------------

## Commit 4: 6bdfd0e

```diff
commit 6bdfd0e3146f7aa3763a12575e450f8086accaea
Author: Shivapuri <142108173+Shivapuri@users.noreply.github.com>
Date:   Sat Aug 1 22:07:56 2026 +0530

    docs: add complete comprehensive reading report for native born Nov 10 1983
---
 western/native_1983_full_reading_report.md | 78 ++++++++++++++++++++++++++++++
 1 file changed, 78 insertions(+)

diff --git a/western/native_1983_full_reading_report.md b/western/native_1983_full_reading_report.md
new file mode 100644
index 0000000..9e3248d
--- /dev/null
+++ b/western/native_1983_full_reading_report.md
@@ -0,0 +1,78 @@
+# Comprehensive Astrological & Psychological Report
+
+**Native Profile:** Man | Born November 10, 1983 at 04:20 AM  
+**Location:** Georgsmarienhütte, Lower Saxony, Germany  
+**Engine:** Hellenistic Western Astrology (Tropical Zodiac, Whole Sign Houses) with Modern Psychological & Behavioral Synthesis  
+
+---
+
+## Part 1: The Core Architecture of the Chart
+
+Before diving into complex character traits, it helps to understand the foundational floor plan of your horoscope. Imagine your birth chart as a theater production: the twelve zodiac signs are the costumes, the planets are the actors, and the twelve houses represent the diverse rooms or chapters of your life where the action unfolds.
+
+*   **The Ascendant in Libra:** You possess a Libra **Ascendant** *(the zodiac sign rising on the eastern horizon at the exact moment of birth, representing your core identity and the natural lens through which you meet the world)*. This clothes your initial approach to life in grace, social fairness, diplomacy, and an unmistakable desire for balance in every interpersonal interaction.
+*   **Night Chart / Nocturnal Sect:** Because you entered the world at 4:20 AM—under the dark canopy just before dawn—your horoscope falls into the nocturnal **Sect** *(an ancient classification separating births into day or night, which reveals which celestial bodies feel most supportive)*. Being born under a starry night sky means the gentler, reflective "nighttime planets"—specifically the Moon and Venus—serve as your deepest emotional guardians and instinctive guides.
+*   **Whole Sign House Layout:** Relying on classical **Whole Sign Houses** *(an organic architectural system where each of the twelve zodiac signs presides over one entire realm or chapter of life)*, your chart exhibits exceptional structural clarity: Libra governs your First House of Self and Identity, Scorpio encompasses your Second House of Personal Resources and Values, and Capricorn anchors your Fourth House of Emotional Foundations and Roots.
+
+---
+
+## Part 2: The Dominant Placements & Psychological Reading
+
+### A. Overview of Your Dominant Zodiac Sign Archetypes
+Before analyzing specific house mechanics, let us explore the general psychological atmosphere of the three zodiac archetypes that dominate your personality:
+
+1.  **Scorpio (The Intense Transfomational Realm):** 
+    *   *Element & Rulership:* Water sign, traditionally ruled by strategic Mars (and modernly by transformational Pluto).
+    *   *Archetypal Characteristics:* Scorpio represents deep emotional intensity, psychological courage, and an investigative desire to look beneath superficial surfaces. Where other signs prefer polite social pleasantries, Scorpio values unwavering authenticity, protective self-control, and unshakeable loyalty. Its natural superpower is transformative resilience—the ability to shed old limitations and regenerate after enduring hardships.
+2.  **Libra (The Harmonious Diplomat):** 
+    *   *Element & Rulership:* Air sign, governed directly by Venus, the planet of love and beauty.
+    *   *Archetypal Characteristics:* Libra focuses on relationship equity, aesthetic beauty, and interpersonal grace. It craves intellectual exchange and cooperative peace. Libra's core gift is perspective—the innate capacity to view any situation from multiple viewpoints and mediate tension effortlessly.
+3.  **Capricorn (The Pragmatic Builder):** 
+    *   *Element & Rulership:* Earth sign, commanded by patient, enduring Saturn.
+    *   *Archetypal Characteristics:* Capricorn embodies practical stamina, ambition, emotional discipline, and structural self-reliance. It treats life as an upward mountain climb where lasting achievements require steady focus, maturity, and healthy boundaries.
+
+### B. Your Specific Dominant Placements
+
+#### 1. The Graceful Architect: Venus in Libra (1st House of Self)
+*   **Mathematical Placement:** Venus resting at 0°42' Libra in its natural **Domicile** *(when a planet sits in the zodiac sign it naturally rules, operating effortlessly and at peak functional power, much like a gracious host inside their own mansion)* within your First House of Self.
+*   **What It Means for You:** Because Libra sits on your Ascendant, Venus reigns as the sovereign ruler of your entire birth chart. Having your primary guiding planet situated in its home territory in your First House is a true mark of magnetic charm and emotional intelligence. You do not force outcomes through loud demands or aggressive confrontation; instead, you command affection and respect through aesthetic refinement, attentive listening, and natural grace. You function as a stabilizing, calming anchor in social settings.
+
+#### 2. The Intense Guardian of Worth: Sun, Saturn, and Mercury in Scorpio (2nd House of Resources)
+*   **Mathematical Placement:** Your Sun (17°09'), Saturn (8°26'), and Mercury (23°25') are gathered tightly in Scorpio within your Second House, creating a powerful **Stellium** *(a focused concentration of three or more planets occupying a single sign or realm of life, acting like a dynamic committee meeting)*. Additionally, Mercury is **Combust** *(when a planet orbits within just a few degrees of the Sun, meaning its qualities work intensely behind the scenes, shielded from public view by the solar glare)*.
+*   **What It Means for You:** The Second House presides over financial security, material assets, self-worth, and deeply held personal boundaries. With dense Scorpio energy focused here, you approach matters of personal value with analytical vigilance and extreme depth. Moreover, in a night chart, Saturn acts as your **Out-of-Sect Malefic** *(the most challenging planetary energy in a horoscope, pointing to where life introduces psychological friction to teach deep personal mastery and lasting emotional toughness)*. Early in life, achieving personal financial independence or unwavering self-worth may have felt like an arduous uphill battle that demanded relentless self-reliance. Over time, however, this placement forge-welds financial acumen with an enduring emotional backbone. With Mercury combust beside your Sun, your financial strategies and deeply intuitive insights operate silently and privately inside your mind rather than through public broadcasting.
+
+#### 3. The "Pain Body" & Emotional Shadows: Moon in Capricorn (4th House of Roots)
+*   **Mathematical Placement:** The Moon stands at 19°30' Capricorn in traditional **Detriment** *(when a planet sits in the zodiac sign opposite its natural home, requiring extra patience and conscientious conscious discipline to express its usual qualities, like trying to translate intimate feelings into a structured business language)* within your Fourth House of Foundations.
+*   **What It Means for You:** In analytical psychology and Eckhart Tolle’s teachings, the "Pain Body" represents our stored emotional armor, unresolved childhood defense mechanisms, and resistance to vulnerability. Your Capricorn Moon reveals the epicentre of your emotional defense system: our psychological literature explains that *"Capricorn instinctively represses spontaneous emotional vulnerability in favor of austere self-discipline and hyper-independence."* 
+    When wounded, your default instinct is never to complain, cry openly, or burden others for comfort; instead, your Pain Body retreats behind high stone fortress walls of stoic self-reliance. You readily assume heavy responsibilities for family and loved ones while secretly harboring a profound fear that asking for emotional nurture makes you weak or troublesome. Healing this shadow requires realigning with a revolutionary truth: vulnerability is not weakness. Letting trusted individuals behind your protective walls is an act of deep courage.
+
+---
+
+## Part 3: Behavioral Psychology (Socialization & Conflict)
+
+How you bond with friends, experience erotic intimacy, and assert boundaries is governed by an intriguing synergy between your connecting instincts (Venus, the 11th House, and the 8th House) and your warrior defenses (Mars and intense Scorpio Saturn).
+
+*   **Socialization & Community (Venus in Libra & The 11th House):** Supported by a dignified, magnetic Venus in your First House, social connections come naturally; you inherently understand how to make others feel validated and heard. Furthermore, classical literature defines your Eleventh House as *“the communal anchor that stabilizes personal identity within society.”* With warm, generous Leo commanding your Eleventh House of Alliances, you do not tolerate fair-weather acquaintances or superficial social clubs. You forge lifelong connections by investing creative enthusiasm, unyielding encouragement, and fierce loyalty into supportive communities where your true personality can shine without restraint.
+*   **Intimacy, Sexuality & Emotional Surrender (Saturn in Scorpio, Mars in Virgo, & 8th House in Taurus):** In matters of deep passion and sexual connection, your style combines intense emotional loyalty with intentional self-control:
+    *   *High Discernment (Saturn conjunct Sun in Scorpio):* Because cautious Saturn binds directly to your Sun in passionate Scorpio, you do not treat physical affection as casual recreation. You maintain deliberate personal boundaries and self-control, requiring absolute trust, fidelity, and profound psychological safety before you lower your shields to experience intense intimacy.
+    *   *Attentive Libido (Mars in Virgo in the 12th House):* **Mars** *(the planetary engine of biological drive, physical libido, and energetic assertiveness)* resides at 25°08' in perceptive Virgo within your quiet **Twelfth House** *(the private, unseen inner sanctuary of solitude and the subconscious mind)*. Rather than displaying an overt or boastful bedroom ego, your physical style is refined, deeply observant, and oriented toward mutual care and emotional atmosphere. Because your Mars rests in the secluded 12th House, your most deeply felt passions are fiercely private, flourishing only behind closed doors in quiet, distraction-free sanctuary environments.
+    *   *Transformative Surrender (8th House in Taurus):* Your classical **Eighth House** *(the realm governing shared emotional vulnerability, profound psychological bonds, and transformative intimacy)* is governed by stable, loyal Taurus—which is directly ruled by your gentle Libra Venus! When you finally make the deliberate choice to release your cautious self-control and fully surrender to shared emotional intimacy, you seek enduring loyalty, comforting sensual peace, and deeply rooted devotion.
+*   **Conflict Resolution & Boundary Assertiveness:** When faced with confrontation or anger, your Mars in Virgo in the 12th House forms a dynamic **Square** *(a stimulating 90-degree angle of tension that requires purposeful internal adjustment)* to your communication realm. You instinctively abhor loud shouting matches and chaotic emotional warfare. Your natural reflex when challenged is to step back into strategic silence, absorb the facts, and analyze the dynamics internally with cool precision. However, because Mars dwells in your secluded 12th House of privacy, you must beware of trapping unexpressed anger inside your mind. Cultivating the habit of calmly stating your boundaries in real time prevents silent irritation from calcifying into internal resentment.
+
+---
+
+## Part 4: Supporting Strengths & Fortune
+
+Your astrological "Flow State" fires up when purposeful exertion transforms into frictionless momentum, unlocking your innate talents and spontaneous fortune:
+
+*   **The Diplomat's Genius (Venus in Domicile in Libra, 1st House):** Because your Ascendant ruler is operating at peak dignity right in your House of Identity, your superpower is effortless interpersonal mediation and aesthetic intuition. You possess an uncommon ability to harmonize environments, soothe emotional frictions, and lead with gracious diplomacy.
+*   **The Visionary Engine (Jupiter in Domicile in Sagittarius, 3rd House):** Jupiter—the planet of wisdom, abundance, and higher perspective—reigns fully triumphant in its natural **Domicile** at 14°31' Sagittarius inside your Third House of daily communication, writing, and learning. While your Capricorn Moon contributes earthly pragmatism, your Sagittarius Jupiter inspires your intellect with buoyant optimism, rapid synthesis of philosophies, and an expansive storytelling gift. You inspire loved ones easily through the warmth and vision of your spoken and written word.
+*   **The Community Magnet (Lot of Fortune in Leo, 11th House):** Your calculated **Lot of Fortune** *(a classic point combining the degrees of the Sun, Moon, and Ascendant to mark where spontaneous joy, effortless vitality, and tangible success naturally gather)* resides in generous Leo in your Eleventh House of friendship and social hopes. You consistently unlock your highest degrees of luck, personal fulfillment, and creative joy whenever you lead, inspire, or collaborate with community groups, artistic associations, and supportive social networks.
+
+---
+
+## Summary Checklist of Your Chart Profile
+
+*   **Your Archetype:** The Empathetic Diplomat & Resilient Guardian.
+*   **Your Superpower:** Blending effortless social magnetism and aesthetic peacemaking (Libra Venus in the 1st House) with an inspiring, philosophical mind (Sagittarius Jupiter in the 3rd House) that naturally magnetizes enduring community fortune (Lot of Fortune in Leo).
+*   **Your Core Life Lesson:** Transforming your Capricorn Moon's "Pain Body" by dismantling your protective fortress of hyper-independence—learning to calmly express boundary needs in real time, releasing defensive self-control in intimate relationships, and allowing trusted loved ones to nurture your vulnerable heart as an act of courageous authentic connection.

```

--------------------------------------------------------------------------------

## Commit 5: bd974eb

```diff
commit bd974eb049c92461caeee7eac23870752e8100be
Author: Shivapuri <142108173+Shivapuri@users.noreply.github.com>
Date:   Sat Aug 1 22:04:12 2026 +0530

    feat: integrate dominant zodiac sign characteristics overview requirement
---
 rag/astrology_mcp_server.py             | 2 +-
 western/native_1983_chart_and_prompt.md | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)

diff --git a/rag/astrology_mcp_server.py b/rag/astrology_mcp_server.py
index 5a209f0..c08d377 100644
--- a/rag/astrology_mcp_server.py
+++ b/rag/astrology_mcp_server.py
@@ -45,7 +45,7 @@ Step 4 (Synthesis - The Extended Reading):
   (Explain Ascendant, Sect, and House layout in simple terms).
   
   Part 2: The Dominant Placements & Psychological Reading
-  (Analyze the top 3 placements. Use bullet points for 'Mathematical Placement' and 'What It Means for You'. Address the native's "Pain Body" and emotional shadows here using their most difficult placement).
+  (First provide an educational overview of the general characteristics and archetypes of the dominant zodiac signs active in the chart—such as their element, ruling planets, and overall psychological themes. Then analyze the top 3 specific placements using bullet points for 'Mathematical Placement' and 'What It Means for You'. Address the native's "Pain Body" and emotional shadows here using their most difficult placement).
   
   Part 3: Behavioral Psychology (Socialization & Conflict)
   (NEW EXTENSION: Explicitly analyze how they make friends and experience intimacy based on Venus/11th House, and how they resolve conflict, fight, or protect boundaries based on Mars/Aspects).
diff --git a/western/native_1983_chart_and_prompt.md b/western/native_1983_chart_and_prompt.md
index b05bd9a..e1f3e59 100644
--- a/western/native_1983_chart_and_prompt.md
+++ b/western/native_1983_chart_and_prompt.md
@@ -28,7 +28,7 @@ You are a **Principal Modern Psychological Astrologer** and **AI Agent** driven
 Your interpretation must strictly follow this 5-part structure:
 
 * **Part 1: The Core Architecture of the Chart** (Explain Ascendant, Sect, and Whole Sign House layout in simple, intuitive terms).
-* **Part 2: The Dominant Placements & Psychological Reading** (Analyze the top three placements using bullet points for *Mathematical Placement* and *What It Means for You*. Address the native's "Pain Body" and emotional shadows here using their most difficult placement).
+* **Part 2: The Dominant Placements & Psychological Reading** (First provide an educational overview of the general characteristics and archetypes of the dominant zodiac signs active in the chart—such as their element, ruling planets, and overall psychological themes. Then analyze the top three specific placements using bullet points for *Mathematical Placement* and *What It Means for You*. Address the native's "Pain Body" and emotional shadows here using their most difficult placement).
 * **Part 3: Behavioral Psychology (Socialization & Conflict)** (Explicitly analyze how they make friends and experience intimacy based on Venus and the 11th/7th/8th Houses, and how they resolve conflict, fight, or protect personal boundaries based on Mars and hard aspects).
 * **Part 4: Supporting Strengths & Fortune** (Analyze Jupiter, the Lot of Fortune, and areas where they naturally hit a buoyant "Flow State").
 * **Summary Checklist of Your Chart Profile** (Provide a concise bulleted summary listing their *Archetype*, *Superpower*, and *Core Life Lesson*).

```

--------------------------------------------------------------------------------

