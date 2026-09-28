"""
tests/test_prominence_engine.py
Tests for Sage Parāśara's Planetary Prominence & Graha Yuddha Engine.

Validates:
1. Declination calculation and Northern vs. Southern declination checks.
2. Graha Yuddha (Planetary War) rules:
   - Venusian immunity (Venus never loses).
   - Northern declination victory for other classical planets.
   - Precise point transfer (|Rw - Rl|).
3. The 8 Parāśarī Opportunity Vectors (purging Jaimini Karakas):
   - Sudarśana Cakra Alignment & Aspects
   - Sensitive Cusp Doors
   - Ascendant Lord Sovereign & Aspect
   - Sphuṭa Dṛṣṭi Volume
   - House Prominence & Stage Sharing
   - Dispositor Tree & Final Dispositor
   - Nodal Amplification
   - Birth Daśā Lord
4. Ranking leaderboard and #1 Chart Commander (Kārakādhipati) designation.
"""

import pytest
from jyotish.report.prominence import (
    calculate_declination,
    resolve_graha_yuddha,
    compute_planetary_prominence,
    ZODIAC_SIGNS
)


def test_declination_calculation():
    """Verify that Northern declinations are positive and Southern are negative."""
    # Sun at 0° Aries (Vernal Equinox) has near 0° declination
    dec_equinox = calculate_declination("Sun", 0.0, 0.0)
    assert abs(dec_equinox) < 0.5

    # Sun at 90° (Cancer 0° / Summer Solstice) has max Northern declination (+23.44°)
    dec_solstice_n = calculate_declination("Sun", 90.0, 0.0)
    assert 23.0 < dec_solstice_n < 24.0

    # Sun at 270° (Capricorn 0° / Winter Solstice) has max Southern declination (-23.44°)
    dec_solstice_s = calculate_declination("Sun", 270.0, 0.0)
    assert -24.0 < dec_solstice_s < -23.0


def test_graha_yuddha_venusian_immunity():
    """Verify that Venus never loses a planetary war, even against higher northern declination."""
    # Place Mars at 50.0° (Taurus) and Venus at 50.5° (Taurus) - separation 0.5°
    d1_grahas = {
        "Mars": {"longitude": 50.0, "latitude": 2.0},  # Higher latitude -> higher declination
        "Venus": {"longitude": 50.5, "latitude": -1.0}
    }
    shadbala_data = {
        "Mars": {"Total_Rupas": 6.0},
        "Venus": {"Total_Rupas": 4.0}
    }

    adjusted_rupas, war_events = resolve_graha_yuddha(d1_grahas, shadbala_data)
    assert len(war_events) == 1
    event = war_events[0]

    assert event["winner"] == "Venus"
    assert event["loser"] == "Mars"
    assert "Venusian Immunity" in event["reason"]
    # Point transfer: |6.0 - 4.0| = 2.0
    assert event["point_transfer"] == 2.0
    assert adjusted_rupas["Venus"] == 6.0  # 4.0 + 2.0
    assert adjusted_rupas["Mars"] == 4.0   # 6.0 - 2.0


def test_graha_yuddha_northern_declination_victory():
    """Verify that between other planets, the one with higher northern declination wins."""
    # Mars at 90.0° (Cancer 0°, high North ~ +23°) vs Saturn at 90.4° (Cancer, lower latitude)
    d1_grahas = {
        "Mars": {"longitude": 90.0, "latitude": 1.5},
        "Saturn": {"longitude": 90.4, "latitude": -2.0}
    }
    shadbala_data = {
        "Mars": {"Total_Rupas": 5.0},
        "Saturn": {"Total_Rupas": 7.0}
    }

    adjusted_rupas, war_events = resolve_graha_yuddha(d1_grahas, shadbala_data)
    assert len(war_events) == 1
    event = war_events[0]

    assert event["winner"] == "Mars"
    assert event["loser"] == "Saturn"
    assert "higher northern declination" in event["reason"]

    # Difference: |5.0 - 7.0| = 2.0
    # Winner Mars: 5.0 + 2.0 = 7.0
    # Loser Saturn: 7.0 - 2.0 = 5.0
    assert adjusted_rupas["Mars"] == 7.0
    assert adjusted_rupas["Saturn"] == 5.0


def test_parashari_prominence_opportunity_vectors_and_commander():
    """Verify the 8 Parāśarī opportunity vectors and designation of Chart Commander."""
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Aries", "longitude": 12.0, "degree_0_to_30": 12.0},
            "grahas": {
                # Sun in Leo (H5) in domicile -> Root dispositor of Leo occupants
                "Sun": {"sign": "Leo", "longitude": 132.0, "degree_0_to_30": 12.0, "ruled_houses": [5]},
                # Mars in Leo (H5) -> ruled by Sun, shares stage with Sun, is Lagna Lord!
                "Mars": {"sign": "Leo", "longitude": 133.0, "degree_0_to_30": 13.0, "ruled_houses": [1, 8]},
                # Jupiter in Sagittarius (H9) in domicile -> Kona placement, rules 9th and 12th
                "Jupiter": {"sign": "Sagittarius", "longitude": 252.0, "degree_0_to_30": 12.0, "ruled_houses": [9, 12]},
                # Saturn in Libra (H7) exalted in Kendra, close to Rahu
                "Saturn": {"sign": "Libra", "longitude": 200.0, "degree_0_to_30": 20.0, "ruled_houses": [10, 11]},
                # Moon at 12.0° Aries (H1) -> Exactly conjunct Ascendant degree!
                "Moon": {"sign": "Aries", "longitude": 12.0, "degree_0_to_30": 12.0, "ruled_houses": [4]},
                # Venus in Taurus (H2) in domicile
                "Venus": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0, "ruled_houses": [2, 7]},
                # Mercury in Virgo (H6) in domicile
                "Mercury": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0, "ruled_houses": [3, 6]},
                # Rahu in Libra (H7) close to Saturn
                "Rahu": {"sign": "Libra", "longitude": 202.0, "degree_0_to_30": 22.0, "ruled_houses": []},
                "Ketu": {"sign": "Aries", "longitude": 22.0, "degree_0_to_30": 22.0, "ruled_houses": []}
            },
            "cusps": [{"longitude": i * 30.0, "sign": ZODIAC_SIGNS[i], "degree_0_to_30": 0.0} for i in range(12)]
        }
    }

    mock_shadbala = {
        "Sun": {"Total_Rupas": 6.5},
        "Moon": {"Total_Rupas": 7.0},
        "Mars": {"Total_Rupas": 6.0},
        "Mercury": {"Total_Rupas": 7.0},
        "Jupiter": {"Total_Rupas": 8.0},
        "Venus": {"Total_Rupas": 6.0},
        "Saturn": {"Total_Rupas": 7.5},
        "Rahu": {"Total_Rupas": 5.0},
        "Ketu": {"Total_Rupas": 5.0}
    }

    # Starting Mahadasha lord is Jupiter
    vimshottari_at_birth = {"mahadasha": "Jupiter"}

    res = compute_planetary_prominence(
        vargas_data=mock_vargas,
        shadbala_data=mock_shadbala,
        advanced_aspects={"planets": {}},
        vimshottari_at_birth=vimshottari_at_birth
    )

    board = {item["planet"]: item for item in res["leaderboard"]}

    # 1. Moon has Ascendant conjunction + Ascendant degree resonance
    moon_reasons = board["Moon"]["opportunity_reasons"]
    assert any("Sudarśana: Ascendant Conjunction" in r for r in moon_reasons)
    assert any("Cusp Door: Ascendant Degree Resonance" in r for r in moon_reasons)

    # 2. Mars is Lagna Lord and shares stage in H5 with Sun, plus full H1 ownership
    mars_reasons = board["Mars"]["opportunity_reasons"]
    assert any("Lagna Lord: Primary Sovereign" in r for r in mars_reasons)
    assert any("Stage Sharing" in r for r in mars_reasons)
    assert any("Lordship Prominence (H1, H8" in r for r in mars_reasons)

    # 3. Saturn has Nodal Amplification with Rahu (separation 2.0°)
    saturn_reasons = board["Saturn"]["opportunity_reasons"]
    assert any("Nodal Amplification: Conjunct Rāhu" in r for r in saturn_reasons)

    # 4. Jupiter has Birth Daśā Lord bonus
    jupiter_reasons = board["Jupiter"]["opportunity_reasons"]
    assert any("Birth Daśā Lord: Starting Life Ruler" in r for r in jupiter_reasons)

    # 5. Commander is designated and matches Rank #1
    commander = res["chart_commander"]
    assert commander is not None
    assert commander["rank"] == 1
    assert commander["prominence_score"] >= res["leaderboard"][1]["prominence_score"]


def test_ascendant_aspect_jupiter_opposition():
    """Verify that Jupiter in 7th house casting 180° aspect onto Ascendant degree gains aspect points."""
    # Ascendant at 10.0° Aries. Jupiter at 10.0° Libra (190° longitude, exactly 180° across)
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Aries", "longitude": 10.0, "degree_0_to_30": 10.0},
            "grahas": {
                "Jupiter": {"sign": "Libra", "longitude": 190.0, "degree_0_to_30": 10.0, "ruled_houses": [9, 12]},
                "Mars": {"sign": "Aries", "longitude": 10.0, "degree_0_to_30": 10.0, "ruled_houses": [1, 8]},
            },
            "cusps": [{"longitude": i * 30.0, "sign": ZODIAC_SIGNS[i], "degree_0_to_30": 0.0} for i in range(12)]
        }
    }
    mock_shadbala = {"Jupiter": {"Total_Rupas": 6.5}, "Mars": {"Total_Rupas": 5.0}}

    res = compute_planetary_prominence(vargas_data=mock_vargas, shadbala_data=mock_shadbala)
    board = {item["planet"]: item for item in res["leaderboard"]}
    jup_reasons = board["Jupiter"]["opportunity_reasons"]

    # Jupiter must gain the Aspect onto Ascendant bonus!
    assert any("Sudarśana: Aspect onto Ascendant" in r for r in jup_reasons)


def test_cyclical_cusp_door_wrap():
    """Verify that degree separation across 0°/30° boundary (e.g. 0.5° vs 29.5°) wraps cyclically."""
    # Ascendant at 0.5° Aries. Sun at 29.5° Leo (separation in 30° span is 1.0°, well within 3.5°)
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Aries", "longitude": 0.5, "degree_0_to_30": 0.5},
            "grahas": {
                "Sun": {"sign": "Leo", "longitude": 149.5, "degree_0_to_30": 29.5, "ruled_houses": [5]},
                "Mars": {"sign": "Aries", "longitude": 0.5, "degree_0_to_30": 0.5, "ruled_houses": [1, 8]},
            },
            "cusps": [{"longitude": i * 30.0, "sign": ZODIAC_SIGNS[i], "degree_0_to_30": 0.0} for i in range(12)]
        }
    }
    mock_shadbala = {"Sun": {"Total_Rupas": 6.0}, "Mars": {"Total_Rupas": 5.0}}

    res = compute_planetary_prominence(vargas_data=mock_vargas, shadbala_data=mock_shadbala)
    board = {item["planet"]: item for item in res["leaderboard"]}
    sun_reasons = board["Sun"]["opportunity_reasons"]

    # Sun must match Ascendant degree door via cyclical wrap!
    assert any("Cusp Door: Ascendant Degree Resonance" in r for r in sun_reasons)


def test_terminating_dispositor_chains():
    """Verify that multiple terminating dispositors each gain points for planets routing into them."""
    # Venus in Taurus (own sign), Jupiter in Libra (ruled by Venus).
    # Mars in Aries (own sign), Sun in Scorpio (ruled by Mars).
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
            "grahas": {
                "Venus": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0, "ruled_houses": [2, 7]},
                "Jupiter": {"sign": "Libra", "longitude": 195.0, "degree_0_to_30": 15.0, "ruled_houses": [9, 12]},
                "Mars": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0, "ruled_houses": [1, 8]},
                "Sun": {"sign": "Scorpio", "longitude": 225.0, "degree_0_to_30": 15.0, "ruled_houses": [5]},
            },
            "cusps": [{"longitude": i * 30.0, "sign": ZODIAC_SIGNS[i], "degree_0_to_30": 0.0} for i in range(12)]
        }
    }
    mock_shadbala = {p: {"Total_Rupas": 5.5} for p in ["Venus", "Jupiter", "Mars", "Sun"]}

    res = compute_planetary_prominence(vargas_data=mock_vargas, shadbala_data=mock_shadbala)
    board = {item["planet"]: item for item in res["leaderboard"]}

    # Venus is final dispositor for Jupiter
    venus_reasons = board["Venus"]["opportunity_reasons"]
    assert any("Final Dispositor for [Jupiter]" in r for r in venus_reasons)

    # Mars is final dispositor for Sun
    mars_reasons = board["Mars"]["opportunity_reasons"]
    assert any("Final Dispositor for [Sun]" in r for r in mars_reasons)


def test_nodal_magnetism_for_rahu_and_ketu():
    """Verify that Rahu and Ketu receive Nodal Magnetism bonuses when hosting classical planets."""
    # Place Sun and Mercury within 5° of Rahu in Gemini
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Aries", "longitude": 10.0, "degree_0_to_30": 10.0},
            "grahas": {
                "Rahu": {"sign": "Gemini", "longitude": 70.0, "degree_0_to_30": 10.0, "ruled_houses": []},
                "Sun": {"sign": "Gemini", "longitude": 72.0, "degree_0_to_30": 12.0, "ruled_houses": [5]},
                "Mercury": {"sign": "Gemini", "longitude": 74.0, "degree_0_to_30": 14.0, "ruled_houses": [3, 6]},
                "Ketu": {"sign": "Sagittarius", "longitude": 250.0, "degree_0_to_30": 10.0, "ruled_houses": []}
            },
            "cusps": [{"longitude": i * 30.0, "sign": ZODIAC_SIGNS[i], "degree_0_to_30": 0.0} for i in range(12)]
        }
    }
    mock_shadbala = {"Rahu": {"Total_Rupas": 5.0}, "Sun": {"Total_Rupas": 5.0}, "Mercury": {"Total_Rupas": 5.0}, "Ketu": {"Total_Rupas": 5.0}}

    res = compute_planetary_prominence(vargas_data=mock_vargas, shadbala_data=mock_shadbala)
    board = {item["planet"]: item for item in res["leaderboard"]}

    rahu_reasons = board["Rahu"]["opportunity_reasons"]
    assert any("Nodal Magnetism: Hosting [Sun, Mercury]" in r for r in rahu_reasons)


def test_dynamic_ruled_houses_fallback_and_dual_kendra():
    """
    Verify:
    1. If ruled_houses is not pre-populated, it is dynamically computed on the fly.
    2. Dual Kendra rulers (e.g. Jupiter ruling H4 and H7 for Virgo rising) get independent credits (+0.20 total).
    """
    # Virgo Lagna: Jupiter rules Sagittarius (H4) and Pisces (H7).
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0},
            "grahas": {
                # Deliberately OMIT "ruled_houses" to test dynamic calculation fallback!
                "Jupiter": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0},
                "Sun": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0}
            }
        }
    }
    mock_shadbala = {"Jupiter": {"Total_Rupas": 6.5}, "Sun": {"Total_Rupas": 5.0}}

    res = compute_planetary_prominence(vargas_data=mock_vargas, shadbala_data=mock_shadbala)
    board = {item["planet"]: item for item in res["leaderboard"]}

    jup_reasons = board["Jupiter"]["opportunity_reasons"]
    # Should dynamically calculate ruled = [4, 7] and award H4 (+0.10) + H7 (+0.10) = +0.20
    assert any("Lordship Prominence (H4, H7, +0.20)" in r for r in jup_reasons)


def test_conjunction_to_lagna_lord():
    """Verify that a planet conjunct the Lagna Lord within 10° receives conjunction credit."""
    # Aries Lagna -> Mars is Lagna Lord at 15.0° Aries.
    # Sun is conjunct Mars at 18.0° Aries (3.0° separation).
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
            "grahas": {
                "Mars": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
                "Sun": {"sign": "Aries", "longitude": 18.0, "degree_0_to_30": 18.0}
            }
        }
    }
    mock_shadbala = {"Mars": {"Total_Rupas": 5.0}, "Sun": {"Total_Rupas": 5.0}}

    res = compute_planetary_prominence(vargas_data=mock_vargas, shadbala_data=mock_shadbala)
    board = {item["planet"]: item for item in res["leaderboard"]}

    sun_reasons = board["Sun"]["opportunity_reasons"]
    assert any("Lagna Lord Conjunction (3.0°" in r for r in sun_reasons)


def test_swakshetra_root_anchor_labeling():
    """Verify that a solitary own-sign planet is labeled Swakshetra Root Anchor (+0.05)."""
    # Sun in Leo (own sign), no other planets in Leo
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
            "grahas": {
                "Sun": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0},
                "Moon": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0}  # Exalted in Taurus, ruled by Venus
            }
        }
    }
    mock_shadbala = {"Sun": {"Total_Rupas": 5.0}, "Moon": {"Total_Rupas": 6.0}}

    res = compute_planetary_prominence(vargas_data=mock_vargas, shadbala_data=mock_shadbala)
    board = {item["planet"]: item for item in res["leaderboard"]}

    sun_reasons = board["Sun"]["opportunity_reasons"]
    assert any("Swakshetra Root Anchor (+0.05)" in r for r in sun_reasons)


def test_calibrated_dispositor_scaling_and_double_counting_prevention():
    """
    Verify that:
    1. If a planet is already credited as direct dispositor of Moon/Sun/Lagna Lord,
       those planets are excluded from the Final Dispositor per-dependent scaling.
    2. Final Dispositor bonus is capped at +0.15 max.
    3. Mars in H8 with Moon does not accumulate an inflated +1.05 bonus.
    """
    # Virgo Ascendant (Lagna Lord = Mercury).
    # Mars in Aries (own sign, H8). Moon in Aries (disposited directly by Mars).
    # All other 5 classical planets in Aries or Scorpio (so all 6 classical planets terminate into Mars).
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0},
            "grahas": {
                "Mars": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0, "ruled_houses": [3, 8]},
                "Moon": {"sign": "Aries", "longitude": 20.0, "degree_0_to_30": 20.0, "ruled_houses": [11]},
                "Sun": {"sign": "Aries", "longitude": 10.0, "degree_0_to_30": 10.0, "ruled_houses": [12]},
                "Mercury": {"sign": "Scorpio", "longitude": 220.0, "degree_0_to_30": 10.0, "ruled_houses": [1, 10]},
                "Jupiter": {"sign": "Aries", "longitude": 5.0, "degree_0_to_30": 5.0, "ruled_houses": [4, 7]},
                "Venus": {"sign": "Scorpio", "longitude": 225.0, "degree_0_to_30": 15.0, "ruled_houses": [2, 9]},
                "Saturn": {"sign": "Scorpio", "longitude": 230.0, "degree_0_to_30": 20.0, "ruled_houses": [5, 6]}
            },
            "cusps": [{"longitude": (165.0 + i * 30.0) % 360.0, "sign": ZODIAC_SIGNS[(5 + i) % 12], "degree_0_to_30": 15.0} for i in range(12)]
        }
    }
    mock_shadbala = {p: {"Total_Rupas": 6.0} for p in ["Mars", "Moon", "Sun", "Mercury", "Jupiter", "Venus", "Saturn"]}

    res = compute_planetary_prominence(vargas_data=mock_vargas, shadbala_data=mock_shadbala)
    board = {item["planet"]: item for item in res["leaderboard"]}
    mars_reasons = board["Mars"]["opportunity_reasons"]

    # 1. Mars is direct dispositor of Lagna Lord (Mercury in Scorpio), Sun, and Moon
    assert any("Dispositor of Lagna Lord Mercury (+0.10)" in r for r in mars_reasons)
    assert any("Dispositor of the Sun (+0.05)" in r for r in mars_reasons)
    assert any("Dispositor of the Moon (+0.05)" in r for r in mars_reasons)

    # 2. Final Dispositor bonus with 3 uncredited dependents (Jupiter, Venus, Saturn) = 0.05 + 3*0.02 = +0.11
    assert any("Final Dispositor for" in r and "(+0.11)" in r for r in mars_reasons)


def test_differentiated_vimshopaka_scores():
    """Verify that Vimshopaka scores are dynamically populated and not stuck at 12.0."""
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
            "grahas": {
                "Sun": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
                "Moon": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0},
                "Mars": {"sign": "Capricorn", "longitude": 285.0, "degree_0_to_30": 15.0}
            },
            "cusps": [{"longitude": i * 30.0, "sign": ZODIAC_SIGNS[i], "degree_0_to_30": 0.0} for i in range(12)]
        }
    }
    mock_shadbala = {"Sun": {"Total_Rupas": 5.0}, "Moon": {"Total_Rupas": 5.0}, "Mars": {"Total_Rupas": 5.0}}
    mock_vimshopaka = {
        "scores": {
            "Dasavarga": {
                "Sun": 16.5,
                "Moon": 18.0,
                "Mars": 14.2
            }
        }
    }

    res = compute_planetary_prominence(
        vargas_data=mock_vargas,
        shadbala_data=mock_shadbala,
        vimshopaka_data=mock_vimshopaka
    )
    board = {item["planet"]: item for item in res["leaderboard"]}

    assert board["Sun"]["vimshopak_score"] == 16.5
    assert board["Moon"]["vimshopak_score"] == 18.0
    assert board["Mars"]["vimshopak_score"] == 14.2
    # Verify they are not all 12.0
    scores = {item["planet"]: item["vimshopak_score"] for item in res["leaderboard"]}
    assert len(set(scores.values())) > 1


def test_steve_jobs_chart_commander_and_prominence_rankings():
    """
    Verify Steve Jobs's chart against Vic DiCara's actual Prominence report:
    1. #1 Chart Commander is Jupiter (tallest bar).
    2. #2 planet is Saturn (second tallest bar).
    3. Mars is moderate (not outranking Jupiter or Saturn).
    """
    from jyotish.generate_jyotish import generate_kala_chart
    chart = generate_kala_chart("Steve Jobs", 1955, 2, 24, 19, 15, 37.7749, -122.4194, -8.0)
    rep = chart["report"]
    leaderboard = rep["planetary_rankings"]["leaderboard"]
    cmd = rep["planetary_rankings"]["chart_commander"]

    # 1. Jupiter is #1 Chart Commander
    assert cmd["planet"] == "Jupiter"
    assert leaderboard[0]["planet"] == "Jupiter"

    # 2. Saturn is #2
    assert leaderboard[1]["planet"] == "Saturn"

    # 3. Mars does NOT outrank Jupiter or Saturn
    mars_entry = next(p for p in leaderboard if p["planet"] == "Mars")
    assert mars_entry["rank"] > 2
    assert mars_entry["prominence_score"] < leaderboard[0]["prominence_score"]


