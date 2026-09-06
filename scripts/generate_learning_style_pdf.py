#!/usr/bin/env python3
"""
generate_learning_style_pdf.py
Generates a publication-grade PDF report for the Cognitive Blueprint & Learning Style Analysis of Swami Shivapuri.
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
    print("Calculating Swami Shivapuri chart...")
    chart = generate_kala_chart(
        name="Swami Shivapuri",
        year=1983,
        month=11,
        day=10,
        hour=22,
        minute=20,
        latitude=52.20296,
        longitude=8.0448,
        timezone_offset=1.0
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
<title>Cognitive Blueprint & Learning Style Master Report - Swami Shivapuri</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

  @page {{
    size: A4;
    margin: 14mm 12mm 14mm 12mm;
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
    font-size: 9pt;
    line-height: 1.55;
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
    padding: 20px 24px;
    border-radius: 10px;
    margin-bottom: 18px;
    border-left: 5px solid #f59e0b;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }}

  .header-title {{
    font-family: 'Cinzel', Georgia, serif;
    font-size: 19pt;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #f8fafc;
    margin-bottom: 4px;
  }}

  .header-subtitle {{
    font-size: 9.5pt;
    color: #fbbf24;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
    margin-bottom: 10px;
  }}

  .meta-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    padding-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.12);
    font-size: 8pt;
  }}

  .meta-item .meta-label {{
    color: #94a3b8;
    text-transform: uppercase;
    font-size: 7pt;
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
    font-size: 13pt;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 4px;
    margin-top: 16px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .section-title::before {{
    content: "";
    display: inline-block;
    width: 4px;
    height: 16px;
    background: #f59e0b;
    border-radius: 2px;
  }}

  /* Executive Cards */
  .card-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 16px;
  }}

  .info-card {{
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 14px;
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

  .card-title {{
    font-size: 9.5pt;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .card-body {{
    font-size: 8.5pt;
    color: #334155;
    line-height: 1.5;
  }}

  /* Badge styling */
  .badge {{
    display: inline-block;
    padding: 2px 7px;
    border-radius: 4px;
    font-size: 7.5pt;
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
    margin-bottom: 14px;
    font-size: 8pt;
  }}

  th {{
    background: #f1f5f9;
    color: #334155;
    font-weight: 700;
    text-align: left;
    padding: 6px 8px;
    border-bottom: 2px solid #cbd5e1;
    font-size: 7.5pt;
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
    margin: 14px 0;
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
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 10px;
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
    margin-bottom: 4px;
  }}

  .technique-title {{
    font-size: 9pt;
    font-weight: 700;
    color: #0f172a;
  }}

  .technique-meta {{
    font-size: 7.5pt;
    color: #64748b;
    font-style: italic;
    margin-bottom: 4px;
  }}

  .technique-desc {{
    font-size: 8pt;
    color: #334155;
    line-height: 1.45;
  }}

  .bullet-list {{
    padding-left: 16px;
    margin: 4px 0;
  }}

  .bullet-list li {{
    margin-bottom: 3px;
  }}

  .footer-note {{
    margin-top: 14px;
    padding-top: 8px;
    border-top: 1px solid #e2e8f0;
    font-size: 7pt;
    color: #94a3b8;
    text-align: center;
  }}

  .workflow-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin: 12px 0;
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
    margin: 2px 0 6px 0;
  }}
</style>
</head>
<body>

  <!-- HEADER BANNER -->
  <div class="header-banner">
    <div class="header-subtitle">Astra Precision Astrological Engine • Kala Methodology</div>
    <div class="header-title">Cognitive Blueprint & Learning Style Report</div>
    <div class="meta-grid">
      <div class="meta-item">
        <div class="meta-label">Native</div>
        <div class="meta-val">Swami Shivapuri</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Birth Date & Time</div>
        <div class="meta-val">10 Nov 1983 • 22:20 CET</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Coordinates</div>
        <div class="meta-val">52°12' N, 8°02' E (Osnabrück)</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Zodiac / Houses</div>
        <div class="meta-val">Tropical / Campanus / Dhruva</div>
      </div>
    </div>
  </div>

  <!-- SECTION 1: EXECUTIVE COGNITIVE PROFILE -->
  <div class="section-title">1. Executive Cognitive Architecture</div>
  
  <div class="card-grid">
    <div class="info-card featured">
      <div class="card-title">
        <span>Auditory Receptive Gateway</span>
        <span class="badge badge-tier1">Primary Input (10/10)</span>
      </div>
      <div class="card-body">
        <strong>Moon in Shravana Nakshatra (Pada 1) • Rank #1 Shadbala (158.6%) • Atmakaraka:</strong><br>
        Shravana literally translates as <em>"the Ear"</em>, governing learning through listening and oral reception (<em>Shruti</em>). He absorbs ideas with minimal friction when listening to high-density lectures, audiobooks, and podcasts.
      </div>
    </div>

    <div class="info-card gold">
      <div class="card-title">
        <span>Forensic "Detective" Intellect</span>
        <span class="badge badge-tier1">Deep Engine (9.5/10)</span>
      </div>
      <div class="card-body">
        <strong>Scorpio 5th House (Sun, Mercury, Saturn) • Budha-Aditya Yoga:</strong><br>
        The intellect (Mercury) and the soul (Sun) sit in Scorpio's investigative depths, anchored by Saturn's discipline. He disdains superficial summaries and must disassemble concepts to their root mechanics to understand them.
      </div>
    </div>

    <div class="info-card purple">
      <div class="card-title">
        <span>Visual Systems Architecture</span>
        <span class="badge badge-tier2">Knowledge Modeling (9.5/10)</span>
      </div>
      <div class="card-body">
        <strong>D9 Swamsa in Gemini • Trine to Venus in Libra & Mercury in Aquarius:</strong><br>
        His soul chart activates the complete Air Trine. He thinks in relational graphs, schemas, maps, and algorithms. Linear lists feel stifling; multi-dimensional mind maps allow him to see how everything connects.
      </div>
    </div>

    <div class="info-card">
      <div class="card-title">
        <span>Lineage Wisdom & Parampara</span>
        <span class="badge badge-tier2">Epistemology (9.5/10)</span>
      </div>
      <div class="card-body">
        <strong>Jupiter conjunct Ketu in Sagittarius (Own Sign) • Exalted D24:</strong><br>
        Instinctively respects classical treatises and authentic spiritual traditions over modern fads. Higher knowledge must possess philosophical integrity, ethical roots, and cosmic significance.
      </div>
    </div>
  </div>

  <!-- CHARTS VISUAL SECTION -->
  <div class="avoid-break">
    <div class="section-title">2. Core Astrological Maps (D1 Rasi & D9 Navamsa)</div>
    <div class="charts-container">
      <div class="chart-box">
        {svg_d1_clean}
        <div class="chart-caption">D1 Rasi (Campanus Houses & Tropical Signs)</div>
      </div>
      <div class="chart-box">
        {svg_d9_clean}
        <div class="chart-caption">D9 Navamsa (Swamsa in Gemini 26°)</div>
      </div>
    </div>
  </div>

  <!-- PAGE BREAK FOR TECHNIQUE EVALUATION -->
  <div class="page-break"></div>

  <!-- SECTION 3: MULTI-LAYER CROSS-CONFIRMATION MATRIX -->
  <div class="section-title">3. Multi-Layer Cross-Confirmation Matrix</div>
  <p style="font-size: 8.5pt; color: #475569; margin-bottom: 10px;">
    In classical Jyotish, an isolated placement is merely a hint. For a trait to be an unshakeable cognitive constant, it must pass the <strong>Rule of Multi-Layer Verification</strong> across independent charts, perspectives, and star asterisms:
  </p>

  <table>
    <thead>
      <tr>
        <th style="width: 22%;">Cognitive Trait</th>
        <th style="width: 18%;">Main Chart (D1)</th>
        <th style="width: 18%;">Moon View (Chandra)</th>
        <th style="width: 20%;">Soul Chart (D9 / D24)</th>
        <th style="width: 22%;">Nakshatra Layer</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>1. Auditory Receptive Absorption</strong></td>
        <td>Moon #1 Shadbala (9.51 Rupas / 158.6%)</td>
        <td>Moon as Atmakaraka (highest degree 28°35')</td>
        <td>Moon in analytical Virgo in D9 Karakamsa</td>
        <td><strong>Shravana Nakshatra</strong> (symbol: The Ear, ruled by Moon)</td>
      </tr>
      <tr>
        <td><strong>2. Forensic Deep-Dive Intellect</strong></td>
        <td>Scorpio 5th House (Sun + Merc + Sat)</td>
        <td>Sun, Merc, Sat in 11th of intellectual gains</td>
        <td>D9 Moon conjunct Saturn in Virgo</td>
        <td><strong>Ashlesha Lagna</strong> (penetrating insight) & <strong>Vishakha</strong> (Merc/Sun)</td>
      </tr>
      <tr>
        <td><strong>3. Traditional Lineage Wisdom</strong></td>
        <td>Jupiter conjunct Ketu in Sagittarius (Own Sign)</td>
        <td>Jupiter + Ketu in 12th House of contemplation</td>
        <td><strong>Jupiter Exalted</strong> in Cancer 5th House in D24 Siddhamsa</td>
        <td>Mutual Nakshatra Exchange: Merc in Vishakha / Jup in Jyeshtha</td>
      </tr>
      <tr>
        <td><strong>4. Visual Systems Architecture</strong></td>
        <td>Venus in own sign Libra in 3rd House</td>
        <td>Venus in 10th of mastery from Moon</td>
        <td><strong>Gemini Swamsa</strong>; Air Trine: Venus (Libra), Merc (Aquarius)</td>
        <td><strong>Hasta Nakshatra</strong> (Venus): The Hand, drafting, geometry & mapping</td>
      </tr>
      <tr>
        <td><strong>5. Methodical Mastery & Depth</strong></td>
        <td>Saturn in 5th House with Mercury</td>
        <td>Saturn aspecting Moon (50 virupas)</td>
        <td>Saturn in own sign Capricorn in 11th of D24</td>
        <td><strong>Swati Nakshatra</strong> (Saturn): patient self-mastery through discipline</td>
      </tr>
    </tbody>
  </table>

  <!-- SECTION 4: EXHAUSTIVE STUDY TECHNIQUES EVALUATION -->
  <div class="section-title">4. Exhaustive Evaluation of Study Techniques & Efficiency</div>

  <!-- TIER 1 -->
  <div class="avoid-break">
    <div style="margin: 10px 0 6px 0; font-weight: 700; color: #15803d; font-size: 8.5pt; text-transform: uppercase; letter-spacing: 0.5px;">
      Tier 1: Superpower Techniques (Highest Cognitive ROI • Efficiency: 9.5 – 10 / 10)
    </div>

    <div class="technique-box t1">
      <div class="technique-header">
        <span class="technique-title">1. High-Density Audio Immersion & Spaced Audio Listening</span>
        <span class="badge badge-tier1">Efficiency: 10 / 10</span>
      </div>
      <div class="technique-meta">Astrological Root: Moon in Shravana (Pada 1) • Moon Rank #1 Shadbala (158.6%) • Atmakaraka</div>
      <div class="technique-desc">
        <strong>Why it works:</strong> The Moon is the receptive mind (<em>Manas</em>). In Shravana, the auditory nerve is the royal highway to his subconscious memory. Dense written texts can trigger intellectual over-filtering, but listening to spoken explanations bypasses friction.<br>
        <strong>Recommended Protocol:</strong> Use Text-to-Speech (TTS) tools to convert dense articles and PDF books into high-quality audio. Listen during solitary walks or quiet morning sessions. Record your own voice summarizing complex topics and listen back.
      </div>
    </div>

    <div class="technique-box t1">
      <div class="technique-header">
        <span class="technique-title">2. Bi-Directional Graph Note-Taking & Systems Mapping (Obsidian / Zettelkasten)</span>
        <span class="badge badge-tier1">Efficiency: 9.5 / 10</span>
      </div>
      <div class="technique-meta">Astrological Root: Swamsa in Gemini • Full D9 Air Trine (Venus in Libra, Mercury/Rahu in Aquarius)</div>
      <div class="technique-desc">
        <strong>Why it works:</strong> Air signs perceive reality as an interconnected graph of relations, not a flat filing cabinet. Rigid hierarchical folders stifle his creativity. Graph databases (like Obsidian) mirror his organic mental architecture.<br>
        <strong>Recommended Protocol:</strong> Create atomic, single-concept Markdown notes linked bi-directionally (<code>[[Concept]]</code>). Build visual relationship schemas, concept maps, and Maps of Content (MOCs).
      </div>
    </div>

    <div class="technique-box t1">
      <div class="technique-header">
        <span class="technique-title">3. Primary Classical Source Study & Lineage Traditions (Parampara)</span>
        <span class="badge badge-tier1">Efficiency: 9.5 / 10</span>
      </div>
      <div class="technique-meta">Astrological Root: Jupiter + Ketu in Sagittarius • Jupiter Exalted in 5th House of D24 Siddhamsa</div>
      <div class="technique-desc">
        <strong>Why it works:</strong> Pop summaries feel watered-down and intellectually unconvincing. He thrives when engaging directly with ancient root treatises, original commentaries, and unbroken teaching lineages.<br>
        <strong>Recommended Protocol:</strong> Study foundational texts directly (BPHS, Jaimini Sutras, classical commentaries). Always trace modern techniques back to their scriptural and mathematical origins.
      </div>
    </div>
  </div>

  <!-- PAGE BREAK FOR TIER 2 & TIER 3 -->
  <div class="page-break"></div>

  <!-- TIER 2 -->
  <div class="avoid-break">
    <div style="margin: 6px 0 6px 0; font-weight: 700; color: #4338ca; font-size: 8.5pt; text-transform: uppercase; letter-spacing: 0.5px;">
      Tier 2: High-Yield Supporting Techniques (Efficiency: 8.0 – 9.0 / 10)
    </div>

    <div class="technique-box t2">
      <div class="technique-header">
        <span class="technique-title">4. The Feynman Technique (Teaching & Formulating)</span>
        <span class="badge badge-tier2">Efficiency: 9.0 / 10</span>
      </div>
      <div class="technique-meta">Astrological Root: Mercury in Vishakha (ruled by Jupiter) • Mercury 10th House in D24</div>
      <div class="technique-desc">
        <strong>Why it works:</strong> Formulating an idea so simply that an outsider can understand it forces his Scorpio 5th house intellect to clarify all fuzzy edges and resolve every ambiguity.<br>
        <strong>Recommended Protocol:</strong> After studying a topic, write a clear explainer article or verbalize the principle out loud as if teaching a student.
      </div>
    </div>

    <div class="technique-box t2">
      <div class="technique-header">
        <span class="technique-title">5. Reverse-Engineering & Hands-On System Building</span>
        <span class="badge badge-tier2">Efficiency: 8.5 / 10</span>
      </div>
      <div class="technique-meta">Astrological Root: Mars in Virgo in 3rd House • Rahu in Gemini / Aquarius</div>
      <div class="technique-desc">
        <strong>Why it works:</strong> Mars in Virgo grants engineering and craft precision. He learns deeply by testing formulas in code, building spreadsheets, or applying astrological algorithms to 50 real charts.<br>
        <strong>Recommended Protocol:</strong> Turn abstract theoretical rules into verifiable tools, test suites, or mathematical spreadsheets.
      </div>
    </div>

    <div class="technique-box t2">
      <div class="technique-header">
        <span class="technique-title">6. Atomized Conceptual Flashcards (Anki with the "Rule of 4")</span>
        <span class="badge badge-tier2">Efficiency: 8.0 / 10</span>
      </div>
      <div class="technique-meta">Astrological Root: Saturn conjoining Mercury in 5th House • Saturn conjunct Moon in D9 Virgo</div>
      <div class="technique-desc">
        <strong>Critical Warning:</strong> If flashcards contain trivial trivia or walls of text, Saturn will induce burnout and "Anki purgatory." Flashcards work <em>only</em> if strictly atomized into core concept pillars.<br>
        <strong>Mandatory Protocol (The Rule of 4):</strong> Divide complex entities (Planets, Houses, Signs) into exactly 4 cards: (1) Core Psychology, (2) Physical/Biology, (3) People/Relations, (4) Material/Environment. Avoid reverse guessing.
      </div>
    </div>
  </div>

  <!-- TIER 3 & 4 -->
  <div class="avoid-break">
    <div style="margin: 10px 0 6px 0; font-weight: 700; color: #b45309; font-size: 8.5pt; text-transform: uppercase; letter-spacing: 0.5px;">
      Tier 3: Moderate Techniques (Require Conscious Adaptation • Efficiency: 6.0 – 6.5 / 10)
    </div>

    <div class="technique-box t3">
      <div class="technique-header">
        <span class="technique-title">7. Linear Outline Notes & Cornell Notes</span>
        <span class="badge badge-tier3">Efficiency: 6.5 / 10</span>
      </div>
      <div class="technique-desc">
        <strong>Evaluation:</strong> Linear columns are too rigid for his holistic, networked mind. Use linear notes only for real-time capture during live lectures, then immediately migrate the ideas into an Obsidian knowledge graph.
      </div>
    </div>

    <div class="technique-box t3">
      <div class="technique-header">
        <span class="technique-title">8. Multiple-Choice Quizzes & Fact Testing</span>
        <span class="badge badge-tier3">Efficiency: 6.0 / 10</span>
      </div>
      <div class="technique-desc">
        <strong>Evaluation:</strong> Rigid answer keys frustrate a Scorpio 5th house intellect that sees context and nuance. Replace multiple-choice tests with open-ended chart analysis and conceptual problem-solving.
      </div>
    </div>

    <div style="margin: 10px 0 6px 0; font-weight: 700; color: #b91c1c; font-size: 8.5pt; text-transform: uppercase; letter-spacing: 0.5px;">
      Tier 4: Inefficient / Low-Yield Techniques (Avoid or Drop • Efficiency: 2.5 – 3.0 / 10)
    </div>

    <div class="technique-box t4">
      <div class="technique-header">
        <span class="technique-title">9. Rote Memorization & Fast-Paced Cramming</span>
        <span class="badge badge-tier4">Efficiency: 3.0 / 10</span>
      </div>
      <div class="technique-desc">
        <strong>Evaluation:</strong> Saturn in the 5th house refuses to be rushed. Cramming creates cognitive exhaustion and zero permanent retention. Always prioritize slow, methodical mastery.
      </div>
    </div>

    <div class="technique-box t4">
      <div class="technique-header">
        <span class="technique-title">10. Unstructured Group Study & Study Circles</span>
        <span class="badge badge-tier4">Efficiency: 2.5 / 10</span>
      </div>
      <div class="technique-desc">
        <strong>Evaluation:</strong> Group study devolves into conversational tangents. His deep forensic engine requires uninterrupted solitude (<em>Ekanta</em>) to reach productive flow states.
      </div>
    </div>
  </div>

  <!-- SECTION 5: MASTER COMPARATIVE MATRIX -->
  <div class="avoid-break" style="margin-top: 14px;">
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
          <td>Moon in Shravana (#1 Shadbala)</td>
          <td>Primary intake modality; convert texts to audio</td>
        </tr>
        <tr>
          <td><strong>#2</strong></td>
          <td><strong>Graph Notes (Obsidian / Zettelkasten)</strong></td>
          <td><span class="badge badge-tier1">9.5 / 10</span></td>
          <td>Gemini Swamsa; D9 Air Trine</td>
          <td>Link atomic ideas with visual schemas</td>
        </tr>
        <tr>
          <td><strong>#3</strong></td>
          <td><strong>Primary Source & Lineage Study</strong></td>
          <td><span class="badge badge-tier1">9.5 / 10</span></td>
          <td>Jupiter + Ketu; Exalted D24 Jup</td>
          <td>Study root classical texts directly</td>
        </tr>
        <tr>
          <td><strong>#4</strong></td>
          <td><strong>Feynman Technique (Teaching Aloud)</strong></td>
          <td><span class="badge badge-tier2">9.0 / 10</span></td>
          <td>Mercury in Vishakha; D24 10th</td>
          <td>Verbalize concepts simply to test clarity</td>
        </tr>
        <tr>
          <td><strong>#5</strong></td>
          <td><strong>System Building & Reverse-Engineering</strong></td>
          <td><span class="badge badge-tier2">8.5 / 10</span></td>
          <td>Mars in Virgo 3rd; Rahu Gemini</td>
          <td>Code formulas & test real chart data</td>
        </tr>
        <tr>
          <td><strong>#6</strong></td>
          <td><strong>Atomized Anki (The Rule of 4)</strong></td>
          <td><span class="badge badge-tier2">8.0 / 10</span></td>
          <td>Saturn conjunct Mercury 5th</td>
          <td>4 sub-cards per entity; zero trivia cards</td>
        </tr>
        <tr>
          <td><strong>#7</strong></td>
          <td><strong>Cornell & Linear Notes</strong></td>
          <td><span class="badge badge-tier3">6.5 / 10</span></td>
          <td>Virgo 2nd House</td>
          <td>Use for real-time capture only; migrate to graph</td>
        </tr>
        <tr>
          <td><strong>#8</strong></td>
          <td><strong>Multiple-Choice Quizzes</strong></td>
          <td><span class="badge badge-tier3">6.0 / 10</span></td>
          <td>Mercury in Scorpio</td>
          <td>Replace with open-ended case studies</td>
        </tr>
        <tr>
          <td><strong>#9</strong></td>
          <td><strong>Rote Memorization / Cramming</strong></td>
          <td><span class="badge badge-tier4">3.0 / 10</span></td>
          <td>Saturn in 5th House</td>
          <td>Avoid completely; causes mental burnout</td>
        </tr>
        <tr>
          <td><strong>#10</strong></td>
          <td><strong>Unstructured Group Study</strong></td>
          <td><span class="badge badge-tier4">2.5 / 10</span></td>
          <td>Sun in Scorpio; 12th House Moon</td>
          <td>Study in quiet solitary focus (Ekanta)</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- SECTION 6: THE IDEAL DAILY LEARNING RITUAL -->
  <div class="avoid-break" style="margin-top: 10px;">
    <div class="section-title">6. The Optimal Daily 3-Stage Learning Ritual</div>
    <div class="workflow-grid">
      <div class="workflow-card">
        <div class="workflow-step">Stage 1 • Morning Intake</div>
        <div class="workflow-title">The Receptor (Auditory)</div>
        <p style="font-size: 8pt; color: #475569;">
          <strong>Target:</strong> Moon in Shravana<br>
          Listen to 30–60 minutes of high-density audio, spoken lectures, or TTS texts during a quiet walk or breakfast. Let the concepts sink smoothly into subconscious memory.
        </p>
      </div>

      <div class="workflow-card">
        <div class="workflow-step">Stage 2 • Deep Work Block</div>
        <div class="workflow-title">The Detective Workshop</div>
        <p style="font-size: 8pt; color: #475569;">
          <strong>Target:</strong> Scorpio 5th House<br>
          In total solitude, open primary texts and examine real data or code. Dissect the mechanics, run calculations, and test edge cases. Refuse to move on until fully understood.
        </p>
      </div>

      <div class="workflow-card">
        <div class="workflow-step">Stage 3 • Evening Synthesis</div>
        <div class="workflow-title">The Architect's Vault</div>
        <p style="font-size: 8pt; color: #475569;">
          <strong>Target:</strong> Gemini Swamsa & Air Trine<br>
          Translate findings into an atomic Obsidian note with visual diagrams or schemas. If fundamental vocabulary needs permanent recall, create 4 atomized Anki cards.
        </p>
      </div>
    </div>
  </div>

  <!-- FOOTER NOTE -->
  <div class="footer-note">
    Astra Precision Astrological Engine • Ernst Wilhelm Kala Methodology • Computed via Swiss Ephemeris • Report Generated for Swami Shivapuri
  </div>

</body>
</html>
"""

    output_pdf_path = "/Users/hajnaljanos/PycharmProjects/astra/Shivapuri_Learning_Style_Analysis.pdf"
    
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
            header_template='<div style="font-size: 7pt; color: #94a3b8; width: 100%; text-align: right; padding-right: 12mm; font-family: sans-serif;">Swami Shivapuri • Cognitive Blueprint & Learning Style Master Report</div>',
            footer_template='<div style="font-size: 7pt; color: #94a3b8; width: 100%; display: flex; justify-content: space-between; padding: 0 12mm; font-family: sans-serif;"><span>Astra Astrological Computation Engine</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>'
        )
        browser.close()

    print(f"PDF generated successfully at: {output_pdf_path}")
    print(f"File size: {os.path.getsize(output_pdf_path)} bytes")

if __name__ == "__main__":
    main()
