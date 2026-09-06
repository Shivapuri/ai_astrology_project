#!/usr/bin/env python3
"""
generate_first_house_pdf.py
Generates a publication-grade PDF report for the First House (Tanu Bhava) analysis of the Swami Shivapuri chart.
Uses Astra's native calculation engines and Playwright for pixel-perfect PDF rendering.
"""

import os
import sys
import json

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

    # Generate Chart SVGs
    v_data = chart["vargas"]["D1"]
    items = draw_chart.parse_varga_data(v_data)
    svg_north = draw_chart.generate_north_indian(items, mode="translit", varga_name="D1 - Rasi")
    svg_south = draw_chart.generate_south_indian(items, mode="translit", varga_name="D1 - Rasi")

    # Clean up SVG for inline HTML embedding
    # Make sure width and height fit nicely in the layout
    svg_north_clean = svg_north.replace('width="100%"', 'width="340"').replace('height="100%"', 'height="340"')

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>First House (Tanu Bhava) Analysis - Swami Shivapuri</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  @page {{
    size: A4;
    margin: 18mm 14mm 18mm 14mm;
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
    font-size: 9.5pt;
    line-height: 1.55;
  }}

  .header-banner {{
    background: linear-gradient(135deg, #090d16 0%, #111827 50%, #1e1b4b 100%);
    color: #ffffff;
    padding: 22px 24px;
    border-radius: 12px;
    margin-bottom: 20px;
    border-left: 5px solid #f59e0b;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
  }}

  .header-title {{
    font-family: 'Cinzel', Georgia, serif;
    font-size: 20pt;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #f8fafc;
    margin-bottom: 4px;
  }}

  .header-subtitle {{
    font-size: 10pt;
    color: #fbbf24;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
    margin-bottom: 12px;
  }}

  .meta-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    background: rgba(255, 255, 255, 0.05);
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 8pt;
  }}

  .meta-item span.label {{
    display: block;
    color: #94a3b8;
    text-transform: uppercase;
    font-size: 7pt;
    letter-spacing: 0.8px;
    font-weight: 600;
  }}

  .meta-item span.value {{
    color: #f1f5f9;
    font-weight: 600;
    font-size: 8.5pt;
  }}

  h2 {{
    font-family: 'Cinzel', Georgia, serif;
    font-size: 12.5pt;
    color: #0f172a;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 4px;
    margin-top: 18px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  h2::before {{
    content: "";
    display: inline-block;
    width: 4px;
    height: 14px;
    background: #d97706;
    border-radius: 2px;
  }}

  h3 {{
    font-size: 10pt;
    font-weight: 700;
    color: #334155;
    margin-top: 12px;
    margin-bottom: 6px;
  }}

  p {{
    margin-bottom: 8px;
    color: #334155;
    text-align: justify;
  }}

  .highlight-card {{
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #3b82f6;
    border-radius: 8px;
    padding: 12px 14px;
    margin: 12px 0;
    font-size: 9pt;
  }}

  .highlight-card.gold {{
    border-left-color: #f59e0b;
    background: #fffbeb;
  }}

  .highlight-card.emerald {{
    border-left-color: #10b981;
    background: #f0fdf4;
  }}

  .highlight-title {{
    font-weight: 700;
    font-size: 9.5pt;
    color: #0f172a;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  /* Two Column Layout */
  .two-col {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin: 12px 0;
  }}

  .chart-flex {{
    display: flex;
    gap: 16px;
    align-items: center;
    margin: 14px 0;
    background: #f8fafc;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
  }}

  .chart-svg {{
    flex: 0 0 320px;
    text-align: center;
  }}

  .chart-details {{
    flex: 1;
    font-size: 8.5pt;
  }}

  /* Tables */
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0 14px 0;
    font-size: 8.5pt;
    background: #ffffff;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #e2e8f0;
  }}

  th {{
    background: #0f172a;
    color: #f8fafc;
    text-align: left;
    padding: 7px 10px;
    font-weight: 600;
    font-size: 8pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  td {{
    padding: 6px 10px;
    border-bottom: 1px solid #f1f5f9;
    color: #334155;
  }}

  tr:nth-child(even) td {{
    background-color: #f8fafc;
  }}

  tr:last-child td {{
    border-bottom: none;
  }}

  .badge {{
    display: inline-block;
    padding: 2px 7px;
    border-radius: 4px;
    font-size: 7.5pt;
    font-weight: 600;
  }}

  .badge-pos {{
    background: #dcfce7;
    color: #15803d;
    border: 1px solid #bbf7d0;
  }}

  .badge-neg {{
    background: #fee2e2;
    color: #b91c1c;
    border: 1px solid #fecaca;
  }}

  .badge-gold {{
    background: #fef3c7;
    color: #b45309;
    border: 1px solid #fde68a;
  }}

  .badge-blue {{
    background: #e0f2fe;
    color: #0369a1;
    border: 1px solid #bae6fd;
  }}

  .page-break {{
    page-break-before: always;
  }}

  .avoid-break {{
    page-break-inside: avoid;
  }}

  .footer-note {{
    margin-top: 20px;
    padding-top: 10px;
    border-top: 1px solid #e2e8f0;
    font-size: 7.5pt;
    color: #94a3b8;
    text-align: center;
  }}
</style>
</head>
<body>

  <!-- HEADER BANNER -->
  <div class="header-banner">
    <div class="header-subtitle">Vedic Astrological Precision Assessment • Kala Methodology</div>
    <div class="header-title">The First House (Tanu Bhava) Analysis</div>
    <div style="font-size: 8.5pt; color: #cbd5e1; margin-bottom: 12px;">
      Exclusively analyzing the Ascendant, its ruling planet, natural karaka, aspects, and planetary conditions
    </div>
    <div class="meta-grid">
      <div class="meta-item">
        <span class="label">Native</span>
        <span class="value">Swami Shivapuri</span>
      </div>
      <div class="meta-item">
        <span class="label">Date & Time</span>
        <span class="value">Nov 10, 1983 • 22:20 CET</span>
      </div>
      <div class="meta-item">
        <span class="label">Location</span>
        <span class="value">Osnabrück, Germany (52°12'N, 8°02'E)</span>
      </div>
      <div class="meta-item">
        <span class="label">House / Zodiac</span>
        <span class="value">Tropical Signs • Campanus Cusps</span>
      </div>
    </div>
  </div>

  <!-- SECTION 1: THE CORNERSTONE -->
  <div class="avoid-break">
    <h2>1. The Cornerstone: Tanu Bhava & The Solar Merger</h2>
    <p>
      In classical Vedic astrology, the <strong>First House (<em>Tanu Bhava</em>)</strong> represents the personal self, physical body, vitality, innate temperament, and the initial impulse of the soul's destiny. It is classified as both an angular house (<em>Kendra</em>, house of effort and Vishnu's grace) and a trinal house (<em>Kona</em>, house of blessings and Lakshmi's fortune). As taught in <em>The Foundation of Vedic Astrology</em> course by Ryan Kurczak, Tanu Bhava functions as the foundational filter: regardless of how brilliant wealth or career combinations are in other houses, a strong and resilient first house is mandatory to carry those blessings into physical reality.
    </p>
    <div class="highlight-card gold">
      <div class="highlight-title">👑 The Unique Solar Dynamic in Leo Ascendant</div>
      <p style="margin: 0; color: #78350f;">
        For this chart, the Ascendant is <strong>Leo (Simha)</strong>. Therefore, the <strong>Lord of the First House (<em>Lagnadhipati</em>)</strong> and the <strong>Universal Archetype (<em>Karaka</em>)</strong> of vitality, soul force, and physical health are <strong>one and the same planet: The Sun (<em>Surya</em>)</strong>. The condition of the Sun becomes the singular master-key to understanding the native's constitution, self-esteem, and life direction.
      </p>
    </div>
  </div>

  <!-- SECTION 2: ASTRONOMICAL GEOMETRY -->
  <div class="avoid-break">
    <h2>2. Astronomical Framework of the Ascendant</h2>
    <div class="two-col">
      <div class="highlight-card" style="margin: 0;">
        <div class="highlight-title">📍 The Rising Degree (Lagna)</div>
        <p style="margin-bottom: 4px;"><strong>Sign:</strong> Leo (Simha) at <strong>9° 35' 56"</strong></p>
        <p style="margin-bottom: 4px;"><strong>Element & Dosha:</strong> Fixed Fire • <strong>Pitta (Bodily Heat / Agni)</strong></p>
        <p style="margin-bottom: 4px;"><strong>Campanus 1st Cusp:</strong> 9° 36' Leo to 7° 26' Virgo</p>
        <p style="margin: 0;"><strong>Whole Sign 1st House:</strong> Entire Sign of Leo (0° – 30°)</p>
      </div>
      <div class="highlight-card emerald" style="margin: 0;">
        <div class="highlight-title">🐍 Sidereal Equatorial Nakshatra</div>
        <p style="margin-bottom: 4px;"><strong>Nakshatra:</strong> <strong>Ashlesha</strong>, Pada 2 (RA: 112.71°)</p>
        <p style="margin-bottom: 4px;"><strong>Anchor:</strong> Dhruva Galactic Center (Center of Mula)</p>
        <p style="margin-bottom: 4px;"><strong>Presiding Deity:</strong> The <em>Sarpas</em> (Divine Serpents)</p>
        <p style="margin: 0;"><strong>Navamsha Sub-tone:</strong> Capricorn (Makara) — Earthy discipline</p>
      </div>
    </div>
    <p style="margin-top: 8px;">
      <strong>Esoteric Signification:</strong> The Leo rising grants a dignified, upright posture and noble demeanor, while Ashlesha Nakshatra infuses the persona with intense psychological depth, piercing gaze, hypnotic focus, and natural affinity for Kundalini yoga and deep esoteric exploration. Pada 2 anchors this mystic serpent fire in Saturn's pragmatic, enduring Navamsha.
    </p>
  </div>

  <!-- SECTION 3: OCCUPANTS & SVG CHART -->
  <div class="avoid-break">
    <h2>3. Direct Occupants: A Pristine, Uncluttered Window</h2>
    <div class="chart-flex">
      <div class="chart-svg">
        {svg_north_clean}
        <div style="font-size: 7.5pt; color: #64748b; margin-top: 4px;">North Indian D1 Rasi (Top diamond = 1st House Leo)</div>
      </div>
      <div class="chart-details">
        <h3 style="margin-top: 0;">No Planets in House 1 (Whole Sign & Campanus)</h3>
        <p>
          Both in Whole Sign (the full 30° of Leo) and within the 3D Campanus 1st slice (9°36' Leo to 7°26' Virgo), <strong>there are no physical planets placed in the First House</strong>.
        </p>
        <p>
          <strong>Interpretative Meaning:</strong> As taught in the video <em>"1st House Indications in Vedic Astrology"</em>, an empty first house is unencumbered by conflicting planetary agendas. The physical body and self-expression act like clear, unclouded glass, radiating the pure solar dignity of Leo without interference, taking their form strictly through:
        </p>
        <ul style="margin-left: 16px; margin-bottom: 6px; color: #334155;">
          <li><strong>The planetary rays (aspects)</strong> cast directly onto Cusp 1.</li>
          <li><strong>The house and sign placement</strong> of the ruling Sun.</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- SECTION 4: ASPECTS ON CUSP 1 -->
  <div class="avoid-break">
    <h2>4. Planetary Rays (Aspects / Drishti) on the First House</h2>
    <p>
      While no planet resides in the first house, multiple planets beam their energy directly onto the Ascendant degree (Cusp 1 at <strong>9° 36' Leo</strong>). In Ernst Wilhelm's Kala engine, planetary aspects (<em>Drishti</em>) are calculated to exact degree precision and measured in <em>Virupas</em> (where 60 Virupas = 100% full aspect).
    </p>

    <table>
      <thead>
        <tr>
          <th>Aspecting Graha</th>
          <th>Position in Chart</th>
          <th>Aspect Type & Angle</th>
          <th>Force (Virupas)</th>
          <th>Nature</th>
          <th>Psychological & Constitutional Impact</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Jupiter (Guru)</strong></td>
          <td>Sagittarius 14° 28' (5th House)</td>
          <td>Exact 9th Trinal Aspect</td>
          <td><strong>+57.56</strong></td>
          <td><span class="badge badge-pos">Major Benefic</span></td>
          <td><strong>Divine Grace & Protection:</strong> Jupiter is in its Own Sign (Sagittarius), in prime youth (Yuva) and fully awake (Jagrat). This powerful 9th trine shields the brain/head, neutralizes chart afflictions, and bestows wisdom, jovial benevolence, and spiritual purpose.</td>
        </tr>
        <tr>
          <td><strong>Moon (Chandra)</strong></td>
          <td>Capricorn 28° 35' (6th House)</td>
          <td>Benefic Glancing Ray</td>
          <td><strong>+54.49</strong></td>
          <td><span class="badge badge-pos">Benefic</span></td>
          <td><strong>Emotional Receptivity:</strong> Softens the fierce solar fire of Leo, granting intuitive empathy, creative imagination, and natural rapport with the public.</td>
        </tr>
        <tr>
          <td><strong>Mercury (Budha)</strong></td>
          <td>Scorpio 24° 35' (4th House)</td>
          <td>Cognitive Influence</td>
          <td><strong>+22.49</strong></td>
          <td><span class="badge badge-blue">Neutral/Benefic</span></td>
          <td><strong>Mental Dexterity:</strong> Stimulates intellectual curiosity, quick analytical perception, and expressive communication.</td>
        </tr>
        <tr>
          <td><strong>Saturn (Shani)</strong></td>
          <td>Scorpio 8° 31' (4th House)</td>
          <td>Exact 10th Special Glance</td>
          <td><strong>-57.84</strong></td>
          <td><span class="badge badge-neg">Major Malefic</span></td>
          <td><strong>Sober Gravity & Duty:</strong> Saturn sits at 8°31' Scorpio and casts its 10th aspect directly onto 9°36' Leo (<1° orb!). It injects cool, dry Vata energy into the body, causing an initial impression of stoic reserve, deep seriousness, and periodic bouts of heavy responsibility. Positively, it grants immense physical and mental endurance.</td>
        </tr>
        <tr>
          <td><strong>Sun (Surya)</strong></td>
          <td>Scorpio 17° 54' (4th House)</td>
          <td>Natural Malefic Glare</td>
          <td><strong>-19.15</strong></td>
          <td><span class="badge badge-neg">Cruel Ray</span></td>
          <td>Fiery solar intensity; sharpens the ego and commands respect.</td>
        </tr>
      </tbody>
    </table>

    <div class="highlight-card emerald">
      <div class="highlight-title">⚖️ Net Aspect Balance on the First House</div>
      <p style="margin: 0;">
        <strong>Total Positive Force:</strong> +134.55 Virupas • 
        <strong>Total Negative Pressure:</strong> -76.99 Virupas • 
        <strong>Net Drishti Score:</strong> <span class="badge badge-pos" style="font-size: 8.5pt;">+57.56 Virupas (Strong Positive)</span><br>
        <em>Synthesis:</em> The divine grace of Jupiter in its own sign and the receptive Moon heavily outweigh the sobering pressure of Saturn. The native possesses an enduring spiritual and constitutional buffer against life's adversities.
      </p>
    </div>
  </div>

  <!-- SECTION 5: THE SUN (LORD & KARAKA) -->
  <div class="avoid-break">
    <h2>5. The Ruler & Karaka: The Sun in Scorpio</h2>
    <p>
      In Vedic astrology, wherever the Ascendant Lord goes (<em>Paka Lagna</em>), there goes the physical body, the focus of consciousness, and the primary life arena.
    </p>

    <div class="two-col">
      <div class="highlight-card" style="margin: 0;">
        <div class="highlight-title">☀️ Core Astronomical Identity</div>
        <p style="margin-bottom: 4px;"><strong>Sign:</strong> Scorpio (Vrishchika) at <strong>17° 54'</strong></p>
        <p style="margin-bottom: 4px;"><strong>Dignity:</strong> <strong>Great Friend's Sign (Adhi Mitra)</strong></p>
        <p style="margin-bottom: 4px;"><strong>Whole Sign House:</strong> 4th House (Heart, sanctuary, inner peace)</p>
        <p style="margin-bottom: 4px;"><strong>Campanus House:</strong> 5th House (Mantra, discipleship, intellect)</p>
        <p style="margin: 0;"><strong>Nakshatra:</strong> Vishakha, Pada 2 (Ruled by Jupiter)</p>
      </div>
      <div class="highlight-card gold" style="margin: 0;">
        <div class="highlight-title">🧘 Spiritual Placement (Paka Lagna)</div>
        <p style="margin: 0; color: #78350f;">
          Sitting in the <strong>4th House of the inner heart and home sanctuary</strong> on the threshold of the <strong>5th house of spiritual mantra</strong>, the native's life force is drawn away from superficial external status and anchored deeply into internal contemplation, study, and ashram life. The soul finds its vitality in solitude and inner mastery.
        </p>
      </div>
    </div>

    <h3>Shadbala: Six Pillars of Planetary Strength for the Sun</h3>
    <p>
      The Sun achieves a total of <strong>316.8 Virupas (5.28 Rupas)</strong>, fulfilling <strong>81.2%</strong> of its required benchmark. Below is the precise mathematical breakdown:
    </p>

    <table>
      <thead>
        <tr>
          <th>Shadbala Pillar</th>
          <th>Virupas</th>
          <th>Requirement</th>
          <th>% Achieved</th>
          <th>Intuitive Meaning & Astrological Cause</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>1. Sthana Bala (Positional)</strong></td>
          <td><strong>185.6</strong></td>
          <td>165.0</td>
          <td><span class="badge badge-pos">112.5%</span></td>
          <td><strong>Rock-Solid Foundation:</strong> High Kendradi Bala (60) from angular placement, strong divisional dignity in Mars's sign (Saptavarga = 98), and odd-sign sector strength (Ojhayugma = 15).</td>
        </tr>
        <tr>
          <td><strong>2. Dig Bala (Directional)</strong></td>
          <td><strong>10.3</strong></td>
          <td>35.0</td>
          <td><span class="badge badge-neg">29.3%</span></td>
          <td><strong>Inverted Power:</strong> Sun gains peak directional strength at high noon (10th house). Born at night (22:20) near midnight/IC, its power is contemplative and internal rather than public-facing.</td>
        </tr>
        <tr>
          <td><strong>3. Kala Bala (Temporal)</strong></td>
          <td><strong>46.1</strong></td>
          <td>112.0</td>
          <td><span class="badge badge-neg">41.1%</span></td>
          <td><strong>Nocturnal Birth:</strong> As a diurnal planet, the Sun lacks daytime temporal power (Nathonnatha Bala is only 9.64).</td>
        </tr>
        <tr>
          <td><strong>4. Ayana Bala (Equinoctial)</strong></td>
          <td><strong>8.4</strong></td>
          <td>30.0</td>
          <td><span class="badge badge-neg">28.1%</span></td>
          <td>Declination/seasonal score based on solar longitude.</td>
        </tr>
        <tr>
          <td><strong>5. Cheshta Bala (Motional)</strong></td>
          <td><strong>8.4</strong></td>
          <td>50.0</td>
          <td><span class="badge badge-neg">16.9%</span></td>
          <td>For the Sun, motional strength is tied directly to its seasonal Ayana path.</td>
        </tr>
        <tr>
          <td><strong>6. Naisargika Bala (Natural)</strong></td>
          <td><strong>60.0</strong></td>
          <td>60.0</td>
          <td><span class="badge badge-gold">100.0%</span></td>
          <td>Inherent luminosity; the Sun is naturally the brightest archetype in creation.</td>
        </tr>
      </tbody>
    </table>
    <p style="font-size: 8.5pt; color: #64748b;">
      <strong>Potency Ratios (Phalas):</strong> Ishta Phala = <strong>10.54</strong> | Kashta Phala = <strong>49.47</strong> | Subha Phala = <strong>15.94</strong> | Asubha Phala = <strong>44.06</strong><br>
      <em>Explanation:</em> The high Kashta score reveals that the native's confidence and soul purpose are not handed to them on a silver platter. They are forged through conscious effort, overcoming self-doubt, and rigorous spiritual tapas.
    </p>
  </div>

  <div class="page-break"></div>

  <!-- SECTION 6: LAJJITADI AVASTHAS -->
  <div class="avoid-break">
    <h2>6. Psychological & Emotional States (Lajjitadi Avasthas)</h2>
    <p>
      While Shadbala measures raw energetic horsepower, the <strong>Lajjitadi Avasthas</strong> (shame, pride, starvation, delight, and agitation) reveal the emotional contentment and psychological well-being of the planet.
    </p>

    <div class="two-col">
      <div class="highlight-card" style="border-left-color: #ef4444; background: #fff5f5; margin: 0;">
        <div class="highlight-title" style="color: #991b1b;">🍽️ Kshudhita Avastha (The "Starved" Sun)</div>
        <p style="font-size: 8pt; color: #7f1d1d; margin-bottom: 6px;">
          <strong>Astronomical Cause:</strong> Conjoined with enemy <strong>Saturn</strong> in Scorpio, and aspected by enemy <strong>Venus</strong>.
        </p>
        <p style="margin: 0; color: #7f1d1d;">
          <strong>Course Video Explanation:</strong> When Saturn starves the Sun, the native lives with an intense "inner critic." There is a persistent vulnerability to feeling inadequate, questioning one's authority, or feeling like one has not yet done enough. With Venus also contributing starvation, there is a risk of over-relying on outside advisors or compromising core personal truths to please others.
        </p>
      </div>

      <div class="highlight-card emerald" style="margin: 0;">
        <div class="highlight-title" style="color: #065f46;">✨ Mudita Avastha (The "Delighted" Sun)</div>
        <p style="font-size: 8pt; color: #064e3b; margin-bottom: 6px;">
          <strong>Astronomical Cause:</strong> Placed in a friendly sign (Mars's Scorpio), aspected by friend <strong>Mars</strong>, and aspected by friend <strong>Moon</strong>.
        </p>
        <p style="margin: 0; color: #064e3b;">
          <strong>Course Video Explanation:</strong> Mars delights the Sun by imparting sharp logical clarity, martial willpower, courage to take decisive action, and moral conviction. The Moon delights the Sun by providing deep emotional empathy, intuitive imagination, and receptivity to spiritual truth.
        </p>
      </div>
    </div>

    <div class="highlight-card gold" style="margin-top: 12px;">
      <div class="highlight-title">🌿 Synthesis of the Dual State</div>
      <p style="margin: 0; color: #78350f;">
        The Sun is not merely afflicted; it exists in a profound <strong>dynamic polarity</strong>. The native faces internal battles of self-worth and sober realism (Saturn), but possesses the logical courage (Mars) and intuitive emotional richness (Moon) to overcome them. This combination produces deep humility and spiritual maturity rather than superficial arrogance.
      </p>
    </div>

    <h3>Additional Planetary Conditions of the Sun</h3>
    <table>
      <thead>
        <tr>
          <th>Avastha System</th>
          <th>State & Rating</th>
          <th>Significance to First House</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Baladi (Physical Maturity)</strong></td>
          <td><span class="badge badge-pos">Yuva (Adult/Prime) • 1.0</span></td>
          <td>Sitting between 12° and 18° in an even sign, the Sun possesses <strong>100% full adult strength</strong> to execute its karma and manifest its purpose.</td>
        </tr>
        <tr>
          <td><strong>Jagradadi (Conscious Alertness)</strong></td>
          <td><span class="badge badge-blue">Svapna (Dreaming) • 0.5</span></td>
          <td>Alertness is 50%. The native operates strongly through intuitive, subconscious, and reflective dimensions.</td>
        </tr>
        <tr>
          <td><strong>Deeptadi (Luminosity)</strong></td>
          <td><span class="badge badge-neg">Vikala (Agitated)</span></td>
          <td>Agitated by close conjunction with natural malefic Saturn.</td>
        </tr>
        <tr>
          <td><strong>Shayanadi (Activity Mode)</strong></td>
          <td><span class="badge badge-blue">Nidra (Slumber) • Vicheshta</span></td>
          <td>The power is dormant/internalized, favoring spiritual meditation over hectic worldly hustle.</td>
        </tr>
        <tr>
          <td><strong>Divisional Consistency (Vargas)</strong></td>
          <td><span class="badge badge-gold">Adhi Mitra (D1, D9, D30)</span></td>
          <td>In <strong>D1 (Scorpio)</strong>, <strong>D9 (Sagittarius)</strong>, and <strong>D30 (Pisces)</strong>, the Sun consistently lands in a <strong>Great Friend's Sign</strong>, proving unshakeable soul integrity across all life layers.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- SECTION 7: HEALTH & AYURVEDIC SYNTHESIS -->
  <div class="avoid-break">
    <h2>7. Health, Appearance, & Ayurvedic Synthesis</h2>
    <p>
      Following the classical <strong>"Tripod Rule"</strong> (synthesizing the Ascendant, the Moon, and the Sun) taught by Ryan Kurczak:
    </p>

    <div class="two-col">
      <div class="highlight-card" style="margin: 0;">
        <div class="highlight-title">🧘 Physical Appearance & Projection</div>
        <p style="margin: 0;">
          The Leo Ascendant bestows an upright, dignified carriage and broad shoulders. However, because Saturn casts an exact 10th-house glance upon Cusp 1 and conjoins the ruling Sun, the native does not project a boisterous or theatrical persona. Instead, they project a <strong>contemplative, disciplined, and stoic monastic presence</strong>. People perceive them as mature, serious, and deeply observant.
        </p>
      </div>
      <div class="highlight-card emerald" style="margin: 0;">
        <div class="highlight-title">🩺 Biological Tissues & Dosha</div>
        <p style="margin: 0;">
          The fiery Leo constitution (<strong>Pitta</strong>) is tempered by Saturn's coolness and dryness (<strong>Vata</strong>). The Sun governs <strong>bone structure</strong>, Mars governs <strong>muscle</strong>, and Saturn governs <strong>nerves and connective tissue</strong>. The primary physical vulnerability is nervous exhaustion or heart/chest tension from overworking or carrying excessive responsibility. The brain and head are exceptionally protected by Jupiter.
        </p>
      </div>
    </div>
  </div>

  <!-- SUMMARY MATRIX -->
  <div class="avoid-break" style="margin-top: 14px;">
    <h2>8. Comprehensive First House Master Matrix</h2>
    <table>
      <thead>
        <tr>
          <th>Astrological Parameter</th>
          <th>Calculated Placement</th>
          <th>Core Interpretation</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Rising Sign (Lagna)</strong></td>
          <td>Leo (Simha) at 9° 36'</td>
          <td>Noble, self-directed, commanding integrity, Pitta constitution.</td>
        </tr>
        <tr>
          <td><strong>Sidereal Nakshatra</strong></td>
          <td>Ashlesha, Pada 2 (Dhruva GC)</td>
          <td>Deep psychological intuition, Kundalini affinity, Saturnian discipline in D9.</td>
        </tr>
        <tr>
          <td><strong>Direct Occupants</strong></td>
          <td>None</td>
          <td>Unencumbered, pure solar lens radiating authentic Leo energy.</td>
        </tr>
        <tr>
          <td><strong>Key Benefic Aspect</strong></td>
          <td>Jupiter (+57.56 Virupas)</td>
          <td>Exact 9th trine from own sign; shields the head, mind, and spiritual destiny.</td>
        </tr>
        <tr>
          <td><strong>Key Malefic Aspect</strong></td>
          <td>Saturn (-57.84 Virupas)</td>
          <td>Exact 10th glance (<1° orb); imparts seriousness, endurance, and stoic duty.</td>
        </tr>
        <tr>
          <td><strong>Ruler & Natural Karaka</strong></td>
          <td>Sun (Surya) in Scorpio at 17° 54'</td>
          <td>Great Friend's sign; placed in 4th WS / 5th Campanus (inner sanctuary & mantra).</td>
        </tr>
        <tr>
          <td><strong>Shadbala Profile</strong></td>
          <td>316.8 Virupas (Sthana = 112.5%)</td>
          <td>High structural stability; low temporal/directional power (internalized solar flame).</td>
        </tr>
        <tr>
          <td><strong>Psychological Mood</strong></td>
          <td>Kshudhita & Mudita</td>
          <td>Starved by Saturn (self-criticism) balanced by Delighted by Mars & Moon (courage & vision).</td>
        </tr>
        <tr>
          <td><strong>Overall Verdict</strong></td>
          <td><strong>Fortified & Sanctified</strong></td>
          <td>A chart built for deep spiritual sadhana, contemplation, and inner mastery.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="footer-note">
    Astra Precision Astrological Engine • Ernst Wilhelm Kala Methodology • Computed via Swiss Ephemeris • Report Generated for Swami Shivapuri
  </div>

</body>
</html>
"""

    output_pdf_path = "/Users/hajnaljanos/PycharmProjects/astra/Shivapuri_First_House_Analysis.pdf"
    
    print("Launching Playwright to render PDF...")
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
            header_template='<div style="font-size: 7pt; color: #94a3b8; width: 100%; text-align: right; padding-right: 14mm; font-family: sans-serif;">Swami Shivapuri • First House (Tanu Bhava) Analysis</div>',
            footer_template='<div style="font-size: 7pt; color: #94a3b8; width: 100%; display: flex; justify-content: space-between; padding: 0 14mm; font-family: sans-serif;"><span>Astra Jyotish Engine</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>'
        )
        browser.close()

    print(f"PDF generated successfully at: {output_pdf_path}")
    print(f"File size: {os.path.getsize(output_pdf_path)} bytes")

if __name__ == "__main__":
    main()
