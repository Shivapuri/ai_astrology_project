#!/usr/bin/env python3
"""
generate_agnidevi_learning_style_pdf.py
Generates a publication-grade PDF report for the Cognitive Blueprint & Learning Style Analysis of Agnidevi (Agnes Megyeri).
Uses Playwright with modern print-optimized HTML/CSS.
"""

import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import sync_playwright
from jyotish.generate_jyotish import generate_kala_chart
from jyotish import draw_chart

def main():
    print("Calculating Agnidevi chart...")
    chart = generate_kala_chart(
        name="Agnidevi",
        year=1981,
        month=6,
        day=18,
        hour=21,
        minute=40,
        latitude=47.17266,
        longitude=19.79952,
        timezone_offset=2.0
    )

    # Generate Chart SVGs for D1 and D9
    v_d1 = chart["vargas"]["D1"]
    items_d1 = draw_chart.parse_varga_data(v_d1)
    svg_d1 = draw_chart.generate_north_indian(items_d1, mode="translit", varga_name="D1 - Rasi Chart")
    svg_d1_clean = svg_d1.replace('width="100%"', 'width="280"').replace('height="100%"', 'height="280"')

    v_d9 = chart["vargas"]["D9"]
    items_d9 = draw_chart.parse_varga_data(v_d9)
    svg_d9 = draw_chart.generate_north_indian(items_d9, mode="translit", varga_name="D9 - Navamsa (Swamsa)")
    svg_d9_clean = svg_d9.replace('width="100%"', 'width="280"').replace('height="100%"', 'height="280"')

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Cognitive Blueprint & Learning Style Master Report - Agnidevi</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

  @page {{
    size: A4;
    margin: 13mm 12mm 13mm 12mm;
    @bottom-right {{
      content: counter(page) " / " counter(pages);
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 8pt;
      color: #94a3b8;
    }}
  }}

  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  body {{
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    font-size: 8.7pt;
    line-height: 1.5;
  }}

  .page-break {{
    page-break-before: always;
  }}

  .avoid-break {{
    page-break-inside: avoid;
  }}

  /* Header Banner */
  .header-banner {{
    background: linear-gradient(135deg, #090d16 0%, #111827 50%, #1e1b4b 100%);
    color: #ffffff;
    padding: 18px 22px;
    border-radius: 10px;
    margin-bottom: 16px;
    border-left: 5px solid #f59e0b;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }}

  .header-title {{
    font-family: 'Cinzel', Georgia, serif;
    font-size: 18pt;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #f8fafc;
    margin-bottom: 3px;
  }}

  .header-subtitle {{
    font-size: 9pt;
    color: #fbbf24;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
    margin-bottom: 8px;
  }}

  .meta-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    padding-top: 8px;
    border-top: 1px solid rgba(255, 255, 255, 0.12);
    font-size: 7.8pt;
  }}

  .meta-item .meta-label {{
    color: #94a3b8;
    text-transform: uppercase;
    font-size: 6.8pt;
    letter-spacing: 0.5px;
    font-weight: 600;
  }}

  .meta-item .meta-val {{
    color: #e2e8f0;
    font-weight: 500;
  }}

  /* Section Titles */
  .section-title {{
    font-family: 'Cinzel', Georgia, serif;
    font-size: 12.5pt;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 3px;
    margin-top: 14px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .section-title::before {{
    content: "";
    display: inline-block;
    width: 4px;
    height: 15px;
    background: #f59e0b;
    border-radius: 2px;
  }}

  /* Executive Cards */
  .card-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-bottom: 14px;
  }}

  .info-card {{
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 10px 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  }}

  .info-card.featured {{
    border-left: 4px solid #3b82f6;
    background: #f0f7ff;
  }}

  .info-card.gold {{
    border-left: 4px solid #f59e0b;
    background: #fffdf5;
  }}

  .info-card.purple {{
    border-left: 4px solid #8b5cf6;
    background: #faf5ff;
  }}

  .info-card.green {{
    border-left: 4px solid #10b981;
    background: #f0fdf4;
  }}

  .card-title {{
    font-size: 9pt;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .card-body {{
    font-size: 8pt;
    color: #334155;
    line-height: 1.45;
  }}

  /* Badge styling */
  .badge {{
    display: inline-block;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 7pt;
    font-weight: 700;
    letter-spacing: 0.3px;
    text-transform: uppercase;
  }}

  .badge-tier1 {{
    background: #dcfce7;
    color: #15803d;
    border: 1px solid #86efac;
  }}

  .badge-tier2 {{
    background: #e0e7ff;
    color: #4338ca;
    border: 1px solid #a5b4fc;
  }}

  .badge-tier3 {{
    background: #fef3c7;
    color: #b45309;
    border: 1px solid #fcd34d;
  }}

  .badge-tier4 {{
    background: #fee2e2;
    color: #b91c1c;
    border: 1px solid #fca5a5;
  }}

  /* Tables */
  table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 7.8pt;
  }}

  th {{
    background: #f1f5f9;
    color: #334155;
    font-weight: 700;
    text-align: left;
    padding: 6px 8px;
    border-bottom: 2px solid #cbd5e1;
    font-size: 7.2pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  td {{
    padding: 6px 8px;
    border-bottom: 1px solid #e2e8f0;
    color: #334155;
    vertical-align: top;
  }}

  tr:nth-child(even) td {{
    background: #f8fafc;
  }}

  /* Charts Container */
  .charts-container {{
    display: flex;
    justify-content: space-around;
    gap: 16px;
    margin: 12px 0;
    padding: 12px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
  }}

  .chart-box {{
    text-align: center;
  }}

  .chart-box svg {{
    max-width: 100%;
    height: auto;
  }}

  .chart-caption {{
    font-size: 7.5pt;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    margin-top: 6px;
    letter-spacing: 0.5px;
  }}

  /* Method card detail */
  .technique-box {{
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 7px;
    padding: 9px 12px;
    margin-bottom: 9px;
    border-left: 4px solid #cbd5e1;
  }}

  .technique-box.t1 {{
    border-left-color: #22c55e;
    background: #f0fdf4;
  }}

  .technique-box.t2 {{
    border-left-color: #6366f1;
    background: #f5f3ff;
  }}

  .technique-box.t3 {{
    border-left-color: #f59e0b;
    background: #fffbeb;
  }}

  .technique-box.t4 {{
    border-left-color: #ef4444;
    background: #fef2f2;
  }}

  .technique-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 3px;
  }}

  .technique-title {{
    font-size: 8.8pt;
    font-weight: 700;
    color: #0f172a;
  }}

  .technique-meta {{
    font-size: 7.3pt;
    color: #64748b;
    font-style: italic;
    margin-bottom: 3px;
  }}

  .technique-desc {{
    font-size: 8pt;
    color: #334155;
    line-height: 1.45;
  }}

  .workflow-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin: 10px 0;
  }}

  .workflow-card {{
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 10px;
  }}

  .workflow-step {{
    font-size: 7pt;
    text-transform: uppercase;
    font-weight: 700;
    color: #f59e0b;
    letter-spacing: 0.5px;
  }}

  .workflow-title {{
    font-size: 8.5pt;
    font-weight: 700;
    color: #0f172a;
    margin: 2px 0 5px 0;
  }}

  .footer-note {{
    margin-top: 14px;
    padding-top: 8px;
    border-top: 1px solid #e2e8f0;
    font-size: 7pt;
    color: #94a3b8;
    text-align: center;
  }}
</style>
</head>
<body>

  <!-- ==================== PAGE 1 ==================== -->
  <div class="header-banner">
    <div class="header-subtitle">Astra Precision Astrological Engine • Kala Methodology</div>
    <div class="header-title">Cognitive Blueprint & Learning Strengths Report</div>
    <div class="meta-grid">
      <div class="meta-item">
        <div class="meta-label">Native</div>
        <div class="meta-val">Agnidevi (Agnes Megyeri)</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Birth Date & Time</div>
        <div class="meta-val">18 Jun 1981 • 21:40 CEST</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Coordinates</div>
        <div class="meta-val">47°10' N, 19°48' E (Cegléd, HU)</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">System Baseline</div>
        <div class="meta-val">Tropical / Campanus / Dhruva</div>
      </div>
    </div>
  </div>

  <!-- SECTION 1: EXECUTIVE COGNITIVE PROFILE -->
  <div class="section-title">1. Executive Cognitive Architecture</div>
  
  <div class="card-grid">
    <div class="info-card featured">
      <div class="card-title">
        <span>Cognitive Endurance & Deep Work</span>
        <span class="badge badge-tier1">Core Engine (9.5/10)</span>
      </div>
      <div class="card-body">
        <strong>Exalted Saturn in Libra • Sthana Bala 256.4 • Repeated in D9 & D24:</strong><br>
        Saturn is her rising sign ruler (<em>Lagna Lord</em>), exalted across multiple divisional charts. She possesses marathon concentration and methodical stamina. She builds mastery gradually and permanently, refusing superficial shortcuts.
      </div>
    </div>

    <div class="info-card green">
      <div class="card-title">
        <span>Auditory Receptive Gateway</span>
        <span class="badge badge-tier1">Primary Input (9.0/10)</span>
      </div>
      <div class="card-body">
        <strong>Moon Rank #1 Shadbala (165.1%) • Conjunct Ascendant in Purva Ashadha:</strong><br>
        The receptive feeling mind (<em>Manas</em>) is her strongest planetary force, situated right on her rising degree. Spoken lectures, audiobooks, and discussions effortlessly bypass the cognitive resistance that dense reading sometimes creates.
      </div>
    </div>

    <div class="info-card purple">
      <div class="card-title">
        <span>Visual Systems Architecture</span>
        <span class="badge badge-tier1">Knowledge Modeling (9.0/10)</span>
      </div>
      <div class="card-body">
        <strong>Gemini Karakamsa (Soul Talent) • Jupiter & Saturn in Hasta Nakshatra:</strong><br>
        Her soul's innate talent sign (<em>Karakamsa</em>) sits in airy Gemini, while key planets occupy <em>Hasta</em> (the symbol of the Hand, drafting, and mapping). She understands subjects best through interconnected network graphs, diagrams, and relationship maps.
      </div>
    </div>

    <div class="info-card gold">
      <div class="card-title">
        <span>Forensic Problem-Solving & Teaching</span>
        <span class="badge badge-tier2">Synthesis (8.5/10)</span>
      </div>
      <div class="card-body">
        <strong>Mars in 5th House • Mercury Retrograde • Bhadra Yoga in D24 (10th):</strong><br>
        Active problem-solver who enjoys taking apart complex problems. In her higher scholarship chart (<em>D24 Siddhamsa</em>), Mercury sits in its home sign Gemini in the 10th house, making teaching and clear verbal explanations a primary catalyst for clarity.
      </div>
    </div>
  </div>

  <!-- CHARTS VISUAL SECTION -->
  <div class="avoid-break">
    <div class="section-title">2. Core Astrological Maps (D1 Rasi & D9 Navamsa)</div>
    <div class="charts-container">
      <div class="chart-box">
        {svg_d1_clean}
        <div class="chart-caption">D1 Rasi (Capricorn Lagna 13.7° • Campanus Houses)</div>
      </div>
      <div class="chart-box">
        {svg_d9_clean}
        <div class="chart-caption">D9 Navamsa (Swamsa in Taurus • Karakamsa in Gemini)</div>
      </div>
    </div>
  </div>

  <!-- ==================== PAGE 2 ==================== -->
  <div class="page-break"></div>

  <!-- SECTION 3: MULTI-LAYER CROSS-CONFIRMATION MATRIX -->
  <div class="section-title">3. Multi-Layer Cross-Confirmation Matrix</div>
  <p style="font-size: 8.2pt; color: #475569; margin-bottom: 10px;">
    In classical Jyotish, a single placement is only a hypothesis. For a cognitive trait to be verified as an unshakeable constant, it must pass the <strong>Rule of Multi-Layer Verification</strong> across independent charts, perspectives, and asterisms:
  </p>

  <table>
    <thead>
      <tr>
        <th style="width: 22%;">Cognitive Trait</th>
        <th style="width: 20%;">Main Chart (D1)</th>
        <th style="width: 18%;">Moon View (Chandra)</th>
        <th style="width: 20%;">Soul Chart (D9 / D24)</th>
        <th style="width: 20%;">Nakshatra Layer</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>1. Cognitive Endurance & Depth</strong></td>
        <td>Saturn Exalted in Libra (Lagna Lord, 159.1% Shadbala)</td>
        <td>Saturn in 9th from Moon (higher wisdom & Dharma)</td>
        <td>Saturn Exalted in D9 Libra & Exalted in D24 Libra 2nd house</td>
        <td><strong>Hasta Nakshatra</strong> (disciplined craftsmanship & precision)</td>
      </tr>
      <tr>
        <td><strong>2. Auditory Absorption</strong></td>
        <td>Moon Rank #1 Shadbala (9.91 Rupas / 165.1%)</td>
        <td>Moon in 1st house of baseline self & intuition</td>
        <td>Moon in Mudita (Delighted) Avastha; Bhratrukaraka (Guru)</td>
        <td><strong>Purva Ashadha</strong> (invincible intuitive flow & absorption)</td>
      </tr>
      <tr>
        <td><strong>3. Systems & Visual Logic</strong></td>
        <td>Venus #2 Shadbala (166.6%) in 7th house</td>
        <td>Venus in 7th from Moon with strong relational focus</td>
        <td><strong>Karakamsa in Gemini</strong> (intellectual models); D24 Venus in Gemini</td>
        <td><strong>Hasta Nakshatra</strong> (ruling the Hand, schematic diagrams & maps)</td>
      </tr>
      <tr>
        <td><strong>4. Forensic Problem-Solving</strong></td>
        <td>Mars in 5th House of intellect (Buddhi) in Gemini</td>
        <td>Mars in 5th from Moon (sharp discrimination)</td>
        <td><strong>Virgo Lagna in D24</strong> (methodical analytical scrutiny)</td>
        <td><strong>Ardra Nakshatra</strong> (Sun AK & Merc: transformative breakthrough insight)</td>
      </tr>
      <tr>
        <td><strong>5. Verbal Teaching & Synthesis</strong></td>
        <td>Mercury Retrograde [R] in Cancer (deep inquiry)</td>
        <td>Mercury in 6th from Moon (solving challenges)</td>
        <td><strong>Bhadra Yoga in D24</strong> (Mercury own sign Gemini in 10th house)</td>
        <td><strong>Ardra & Rohini</strong> (blends deep curiosity with fertile delivery)</td>
      </tr>
    </tbody>
  </table>

  <!-- SECTION 4: EXHAUSTIVE STUDY TECHNIQUES EVALUATION (TIER 1) -->
  <div class="section-title">4. Exhaustive Evaluation of Study Techniques & Efficiency</div>

  <!-- TIER 1 -->
  <div class="avoid-break">
    <div style="margin: 8px 0 6px 0; font-weight: 700; color: #15803d; font-size: 8.5pt; text-transform: uppercase; letter-spacing: 0.5px;">
      Tier 1: Superpower Techniques (Highest Cognitive ROI • Efficiency: 9.0 – 10 / 10)
    </div>

    <div class="technique-box t1">
      <div class="technique-header">
        <span class="technique-title">1. High-Density Audio Immersion & Spaced Listening</span>
        <span class="badge badge-tier1">Efficiency: 10 / 10</span>
      </div>
      <div class="technique-meta">Astrological Root: Moon #1 Shadbala (165.1%) • Conjunct Ascendant in Purva Ashadha • Bhratrukaraka</div>
      <div class="technique-desc">
        <strong>Why it works:</strong> The Moon governs the receptive feeling mind (<em>Manas</em>). Located directly on her rising degree, the auditory channel is her fastest pathway into subconscious retention. Listening bypasses the analytical friction of dry reading.<br>
        <strong>Recommended Protocol:</strong> Convert dense articles and books to high-quality Text-to-Speech (TTS). Listen during morning walks, daily chores, or dedicated listening sessions.
      </div>
    </div>

    <div class="technique-box t1">
      <div class="technique-header">
        <span class="technique-title">2. Bi-Directional Graph Note-Taking & Systems Mapping (Obsidian / Mind Maps)</span>
        <span class="badge badge-tier1">Efficiency: 9.5 / 10</span>
      </div>
      <div class="technique-meta">Astrological Root: Karakamsa in Gemini • Jupiter & Saturn in Hasta Nakshatra • D24 Air Trine</div>
      <div class="technique-desc">
        <strong>Why it works:</strong> Gemini and <em>Hasta</em> perceive knowledge as a networked web of concepts rather than disconnected bullet points. Hierarchical folders feel confining; concept graphs reveal organic connections.<br>
        <strong>Recommended Protocol:</strong> Create atomic, single-concept notes linked bi-directionally (<code>[[Topic]]</code>) in Obsidian. Build visual process flowcharts and structural mind maps.
      </div>
    </div>

    <div class="technique-box t1">
      <div class="technique-header">
        <span class="technique-title">3. Primary Classical Source Study (Parampara)</span>
        <span class="badge badge-tier1">Efficiency: 9.0 / 10</span>
      </div>
      <div class="technique-meta">Astrological Root: Exalted Saturn in 8th/9th axis • Jupiter conjunct Saturn • Virgo Lagna in D24</div>
      <div class="technique-desc">
        <strong>Why it works:</strong> Diluted modern summaries feel superficial to her investigative intellect. She thrives when studying authentic root texts and lineage teachings that possess structural depth.<br>
        <strong>Recommended Protocol:</strong> Engage directly with foundational treatises, authentic commentaries, and unbroken teaching traditions. Trace modern ideas back to primary origins.
      </div>
    </div>
  </div>

  <!-- ==================== PAGE 3 ==================== -->
  <div class="page-break"></div>

  <!-- TIER 2 -->
  <div class="avoid-break">
    <div style="margin: 4px 0 6px 0; font-weight: 700; color: #4338ca; font-size: 8.5pt; text-transform: uppercase; letter-spacing: 0.5px;">
      Tier 2: High-Yield Supporting Techniques (Efficiency: 8.0 – 8.9 / 10)
    </div>

    <div class="technique-box t2">
      <div class="technique-header">
        <span class="technique-title">4. The Feynman Technique (Teaching & Formulating Aloud)</span>
        <span class="badge badge-tier2">Efficiency: 8.5 / 10</span>
      </div>
      <div class="technique-meta">Astrological Root: Mercury in Gemini in 10th House of D24 Siddhamsa (Bhadra Yoga)</div>
      <div class="technique-desc">
        <strong>Why it works:</strong> In her chart of higher scholarship, Mercury sits in its own sign in the house of public expression. Explaining a difficult idea in plain English forces her mind to resolve all ambiguity.<br>
        <strong>Recommended Protocol:</strong> After studying a topic, spend 2 minutes summarizing it out loud as if explaining it to an interested beginner, or draft a concise explainer guide.
      </div>
    </div>

    <div class="technique-box t2">
      <div class="technique-header">
        <span class="technique-title">5. Hands-On Problem Solving & Reverse-Engineering</span>
        <span class="badge badge-tier2">Efficiency: 8.5 / 10</span>
      </div>
      <div class="technique-meta">Astrological Root: Mars in 5th House in Gemini • Mercury Retrograde [R]</div>
      <div class="technique-desc">
        <strong>Why it works:</strong> Mars in the 5th gives an energetic, investigative drive. She learns best when theories are immediately tested against real-world examples, case studies, or practical exercises.<br>
        <strong>Recommended Protocol:</strong> Pair abstract study immediately with practical application: test formulas, analyze real chart examples, or solve concrete problem sets.
      </div>
    </div>

    <div class="technique-box t2">
      <div class="technique-header">
        <span class="technique-title">6. Atomized Conceptual Flashcards (Anki via the "Rule of 4")</span>
        <span class="badge badge-tier2">Efficiency: 8.0 / 10</span>
      </div>
      <div class="technique-meta">Astrological Root: Saturn ruling Lagna • Exalted 2nd house in D24</div>
      <div class="technique-desc">
        <strong>Critical Warning:</strong> Flashcards work only if strictly atomized into core pillars. Rote trivia or walls of text cause mental fatigue.<br>
        <strong>Mandatory Protocol:</strong> Atomize complex concepts into exactly 4 sub-cards: (1) Core Meaning, (2) Biology/Physical, (3) People/Relations, (4) Material/Environment. Avoid reverse guessing.
      </div>
    </div>
  </div>

  <!-- TIER 3 & 4 -->
  <div class="avoid-break" style="margin-top: 10px;">
    <div style="margin: 4px 0 6px 0; font-weight: 700; color: #b45309; font-size: 8.5pt; text-transform: uppercase; letter-spacing: 0.5px;">
      Tier 3: Moderate Techniques (Require Conscious Adaptation • Efficiency: 6.0 – 6.5 / 10)
    </div>

    <div class="technique-box t3">
      <div class="technique-header">
        <span class="technique-title">7. Linear Outline Notes & Cornell Notes</span>
        <span class="badge badge-tier3">Efficiency: 6.5 / 10</span>
      </div>
      <div class="technique-desc">
        <strong>Evaluation:</strong> Rigid linear notes feel restrictive to her networked mind. Use linear notes only for real-time capture during live lectures, then migrate the concepts into an Obsidian knowledge graph.
      </div>
    </div>

    <div class="technique-box t3">
      <div class="technique-header">
        <span class="technique-title">8. Multiple-Choice Quizzes & Fact Testing</span>
        <span class="badge badge-tier3">Efficiency: 6.0 / 10</span>
      </div>
      <div class="technique-desc">
        <strong>Evaluation:</strong> Rigid answer keys frustrate an inquiring Mercury Retrograde mind that seeks nuance. Replace multiple-choice tests with open-ended problem solving and case analyses.
      </div>
    </div>
  </div>

  <div class="avoid-break" style="margin-top: 10px;">
    <div style="margin: 4px 0 6px 0; font-weight: 700; color: #b91c1c; font-size: 8.5pt; text-transform: uppercase; letter-spacing: 0.5px;">
      Tier 4: Inefficient / Low-Yield Techniques (Avoid or Drop • Efficiency: 3.0 – 3.5 / 10)
    </div>

    <div class="technique-box t4">
      <div class="technique-header">
        <span class="technique-title">9. Rote Memorization & Fast-Paced Cramming</span>
        <span class="badge badge-tier4">Efficiency: 3.5 / 10</span>
      </div>
      <div class="technique-desc">
        <strong>Evaluation:</strong> Her exalted Saturn intellect demands context, mechanics, and systemic understanding. Cramming isolated trivia triggers cognitive burnout and produces poor long-term retention.
      </div>
    </div>

    <div class="technique-box t4">
      <div class="technique-header">
        <span class="technique-title">10. Unstructured Group Study & Study Circles</span>
        <span class="badge badge-tier4">Efficiency: 3.0 / 10</span>
      </div>
      <div class="technique-desc">
        <strong>Evaluation:</strong> Noisy group study sessions scatter energy and disrupt deep concentration. Her best insights emerge in quiet, uninterrupted solitude (<em>Ekanta</em>).
      </div>
    </div>
  </div>

  <!-- ==================== PAGE 4 ==================== -->
  <div class="page-break"></div>

  <!-- SECTION 5: MASTER COMPARATIVE MATRIX -->
  <div class="avoid-break">
    <div class="section-title">5. Master Comparative Ranking Matrix</div>
    <table>
      <thead>
        <tr>
          <th style="width: 8%;">Rank</th>
          <th style="width: 27%;">Study Technique</th>
          <th style="width: 14%;">Efficiency</th>
          <th style="width: 25%;">Astrological Driver</th>
          <th style="width: 26%;">Primary Recommendation</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>#1</strong></td>
          <td><strong>Auditory Immersion (TTS, Audiobooks)</strong></td>
          <td><span class="badge badge-tier1">10 / 10</span></td>
          <td>Moon #1 Shadbala (165.1%) on Lagna</td>
          <td>Primary intake channel; listen during walks or quiet mornings</td>
        </tr>
        <tr>
          <td><strong>#2</strong></td>
          <td><strong>Graph Notes (Obsidian / Mind Maps)</strong></td>
          <td><span class="badge badge-tier1">9.5 / 10</span></td>
          <td>Gemini Karakamsa & Hasta Nakshatra</td>
          <td>Link atomic concepts into visual relational networks</td>
        </tr>
        <tr>
          <td><strong>#3</strong></td>
          <td><strong>Primary Source & Lineage Study</strong></td>
          <td><span class="badge badge-tier1">9.0 / 10</span></td>
          <td>Exalted Saturn + Jupiter in 8th/9th axis</td>
          <td>Study foundational treatises and classical commentaries directly</td>
        </tr>
        <tr>
          <td><strong>#4</strong></td>
          <td><strong>Feynman Technique (Teaching Aloud)</strong></td>
          <td><span class="badge badge-tier2">8.5 / 10</span></td>
          <td>Mercury in Gemini 10th in D24</td>
          <td>Explain ideas simply in 60 seconds to resolve ambiguities</td>
        </tr>
        <tr>
          <td><strong>#5</strong></td>
          <td><strong>Practical Testing & Problem Solving</strong></td>
          <td><span class="badge badge-tier2">8.5 / 10</span></td>
          <td>Mars in 5th House in Gemini</td>
          <td>Apply rules immediately to real case studies or exercises</td>
        </tr>
        <tr>
          <td><strong>#6</strong></td>
          <td><strong>Atomized Anki (The Rule of 4)</strong></td>
          <td><span class="badge badge-tier2">8.0 / 10</span></td>
          <td>Saturn exalted in D24 2nd house</td>
          <td>Divide entities into 4 distinct cards; zero trivial trivia</td>
        </tr>
        <tr>
          <td><strong>#7</strong></td>
          <td><strong>Linear Outline / Cornell Notes</strong></td>
          <td><span class="badge badge-tier3">6.5 / 10</span></td>
          <td>Virgo D24 Lagna</td>
          <td>Use for live lecture notes only; transfer to graphs afterward</td>
        </tr>
        <tr>
          <td><strong>#8</strong></td>
          <td><strong>Multiple-Choice Quizzes</strong></td>
          <td><span class="badge badge-tier3">6.0 / 10</span></td>
          <td>Mercury Retrograde inquiry</td>
          <td>Replace with open-ended problem solving and case analyses</td>
        </tr>
        <tr>
          <td><strong>#9</strong></td>
          <td><strong>Rote Trivia Cramming</strong></td>
          <td><span class="badge badge-tier4">3.5 / 10</span></td>
          <td>Saturn-ruled Lagna</td>
          <td>Avoid completely; causes cognitive exhaustion without retention</td>
        </tr>
        <tr>
          <td><strong>#10</strong></td>
          <td><strong>Unstructured Group Study</strong></td>
          <td><span class="badge badge-tier4">3.0 / 10</span></td>
          <td>Capricorn Lagna / 8th house focus</td>
          <td>Prioritize quiet solitary study (Ekanta) for deep flow states</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- SECTION 6: THE OPTIMAL DAILY 3-STAGE LEARNING RITUAL -->
  <div class="avoid-break" style="margin-top: 14px;">
    <div class="section-title">6. The Optimal Daily 3-Stage Learning Ritual</div>
    <div class="workflow-grid">
      <div class="workflow-card">
        <div class="workflow-step">Stage 1 • Morning Intake</div>
        <div class="workflow-title">The Receptive Gateway</div>
        <p style="font-size: 8pt; color: #475569;">
          <strong>Target:</strong> Moon in Purva Ashadha on Lagna<br>
          Listen to 30–45 minutes of high-quality audio, lectures, or TTS readings during a morning walk or quiet time. This feeds her subconscious mind without visual fatigue.
        </p>
      </div>

      <div class="workflow-card">
        <div class="workflow-step">Stage 2 • Deep Work Block</div>
        <div class="workflow-title">The Solitary Workshop</div>
        <p style="font-size: 8pt; color: #475569;">
          <strong>Target:</strong> Exalted Saturn & Mars in 5th<br>
          In quiet solitude, dive into primary texts and solve concrete exercises or case studies. Dissect the mechanics, test assumptions, and take notes.
        </p>
      </div>

      <div class="workflow-card">
        <div class="workflow-step">Stage 3 • Evening Synthesis</div>
        <div class="workflow-title">The System Architect</div>
        <p style="font-size: 8pt; color: #475569;">
          <strong>Target:</strong> Gemini Karakamsa & Mercury in D24<br>
          Transfer key takeaways into an Obsidian concept graph or mind map. For core concepts needing long-term memory, create 4 atomized Anki flashcards.
        </p>
      </div>
    </div>
  </div>

  <!-- FOOTER NOTE -->
  <div class="footer-note">
    Astra Precision Astrological Engine • Ernst Wilhelm Kala Methodology • Computed via Swiss Ephemeris • Report Generated for Agnidevi (Agnes Megyeri)
  </div>

</body>
</html>
"""

    output_pdf_path = "/Users/hajnaljanos/PycharmProjects/astra/Agnidevi_Learning_Style_Analysis.pdf"
    
    print("Launching Playwright to render publication-grade PDF...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")
        
        page.pdf(
            path=output_pdf_path,
            format="A4",
            print_background=True,
            margin={
                "top": "14mm",
                "bottom": "14mm",
                "left": "12mm",
                "right": "12mm"
            },
            display_header_footer=True,
            header_template='<div style="font-size: 7pt; color: #94a3b8; width: 100%; text-align: right; padding-right: 12mm; font-family: sans-serif;">Agnidevi (Agnes Megyeri) • Cognitive Blueprint & Learning Strengths Master Report</div>',
            footer_template='<div style="font-size: 7pt; color: #94a3b8; width: 100%; display: flex; justify-content: space-between; padding: 0 12mm; font-family: sans-serif;"><span>Astra Astrological Computation Engine</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>'
        )
        browser.close()

    print(f"PDF generated successfully at: {output_pdf_path}")
    print(f"File size: {os.path.getsize(output_pdf_path)} bytes")

if __name__ == "__main__":
    main()
