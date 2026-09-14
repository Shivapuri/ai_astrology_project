"""
jyotish/yogas/lunar_solar_yogas.py
Lunar (Chandra) and Solar (Ravi) Yogas.
Scripture: BPHS Ch. 37-38, Phaladeepika Ch. 6, Verses 5-13, 19-20, 42-43.
"""

from typing import List, Dict, Any
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_planets_data, get_aspect_score,
    NATURAL_BENEFICS, NATURAL_MALEFICS,
    audit_trishadaya_interference, audit_combustion, audit_shadbala_muscle
)

def detect_lunar_and_solar_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Scans chart for classical Lunar and Solar yogas."""
    detected = []
    planets_data = get_planets_data(chart)
    planet_houses = {p: get_house_of_planet(chart, p) for p in planets_data}
    
    moon_house = planet_houses.get("Moon", 0)
    sun_house = planet_houses.get("Sun", 0)
    
    # -------------------------------------------------------------
    # 1. LUNAR YOGAS (CHANDRA YOGAS)
    # -------------------------------------------------------------
    if moon_house > 0:
        # A. Flanking Planets: 2nd and 12th from Moon
        h2_moon = (moon_house % 12) + 1
        h12_moon = ((moon_house - 2) % 12) + 1
        
        planets_in_h2 = [p for p in planets_data if planet_houses.get(p) == h2_moon and p not in ("Sun", "Rahu", "Ketu", "Moon")]
        planets_in_h12 = [p for p in planets_data if planet_houses.get(p) == h12_moon and p not in ("Sun", "Rahu", "Ketu", "Moon")]
        
        # Durudhara (Both 2nd and 12th occupied)
        if planets_in_h2 and planets_in_h12:
            benefics_flanking = [p for p in planets_in_h2 + planets_in_h12 if p in NATURAL_BENEFICS]
            malefics_flanking = [p for p in planets_in_h2 + planets_in_h12 if p in NATURAL_MALEFICS]
            
            score = 85.0
            pos = [f"Planets flank Moon in 2nd ({planets_in_h2}) and 12th ({planets_in_h12}). Mind is well-supported on both sides."]
            breakers = []
            if benefics_flanking:
                pos.append(f"Benefics flanking ({benefics_flanking}) bring charm, generosity, and financial stability.")
                score += 10.0
            if malefics_flanking:
                breakers.append(YogaBreakerDetail(
                    factor="Malefics Flanking Moon",
                    culprit_planet=", ".join(malefics_flanking),
                    description=f"Malefics in 2nd/12th from Moon ({malefics_flanking}) produce emotional anxiety and financial drain.",
                    penalty=20.0
                ))
                score -= 20.0
                
            detected.append(YogaInstance(
                id="durudhara_yoga",
                name="Durudharā Yoga",
                category=YogaCategory.LUNAR,
                status=YogaStatus.PURE if score >= 75 else YogaStatus.STAINED,
                plausibility_score=round(score, 1),
                participating_planets=["Moon"] + planets_in_h2 + planets_in_h12,
                participating_houses=[moon_house, h2_moon, h12_moon],
                scripture_ref="Phaladeepika 6.5-7, BPHS 37.1-2",
                archetype="The Emotionally Anchored Mind: Flanked by resources (2nd) and philosophical detachment (12th).",
                manifestation_effects=[
                    "Endows high material comfort, generous disposition, and verbal eloquence.",
                    "Enjoyment of vehicles, landed property, and consistent resource acquisition."
                ],
                positive_factors=pos,
                breakers=breakers
            ))
            
        elif planets_in_h2:
            # Sunapha Yoga
            score = 80.0
            detected.append(YogaInstance(
                id="sunapha_yoga",
                name="Sunaphā Yoga",
                category=YogaCategory.LUNAR,
                status=YogaStatus.PURE,
                plausibility_score=round(score, 1),
                participating_planets=["Moon"] + planets_in_h2,
                participating_houses=[moon_house, h2_moon],
                scripture_ref="Phaladeepika 6.5, BPHS 37.1",
                archetype="Resourceful Mind: Planets in the 2nd from the Moon provide self-reliance and steady earnings.",
                manifestation_effects=["Self-made prosperity, intelligent speech, and comfortable livelihood."],
                positive_factors=[f"Planets in 2nd from Moon: {', '.join(planets_in_h2)}."],
                breakers=[]
            ))
            
        elif planets_in_h12:
            # Anapha Yoga
            score = 80.0
            detected.append(YogaInstance(
                id="anapha_yoga",
                name="Anaphā Yoga",
                category=YogaCategory.LUNAR,
                status=YogaStatus.PURE,
                plausibility_score=round(score, 1),
                participating_planets=["Moon"] + planets_in_h12,
                participating_houses=[moon_house, h12_moon],
                scripture_ref="Phaladeepika 6.6, BPHS 37.1",
                archetype="Generous & Peaceful Mind: Planets in the 12th from the Moon give detachment from pettiness and good health.",
                manifestation_effects=["Generosity, self-control, freedom from chronic illness, and moral contentment."],
                positive_factors=[f"Planets in 12th from Moon: {', '.join(planets_in_h12)}."],
                breakers=[]
            ))
            
        else:
            # Kemadruma Yoga (Isolated Moon)
            # Check cancellations (Kemadruma Bhanga):
            # 1. Any planet in Kendra from Lagna
            # 2. Any planet in Kendra from Moon
            kendra_planets_lagna = [p for p in planets_data if planet_houses.get(p) in (1, 4, 7, 10) and p != "Moon"]
            kendra_planets_moon = [
                p for p in planets_data
                if p != "Moon" and ((planet_houses.get(p, 0) - moon_house) % 12 + 1) in (1, 4, 7, 10)
            ]
            is_cancelled = bool(kendra_planets_lagna or kendra_planets_moon)
            
            cancellation_reasons = []
            if kendra_planets_lagna:
                cancellation_reasons.append(f"Cancelled by planets in Kendra from Lagna: {', '.join(kendra_planets_lagna)}.")
            if kendra_planets_moon:
                cancellation_reasons.append(f"Cancelled by planets in Kendra from Chandra: {', '.join(kendra_planets_moon)}.")
                
            score = 45.0 if is_cancelled else 20.0
            status = YogaStatus.RESCUED if is_cancelled else YogaStatus.BROKEN
            
            breakers = [YogaBreakerDetail(
                factor="Moon Isolation (No flanking planets)",
                culprit_planet="Moon",
                description="No planets reside in 2nd or 12th from the Moon, creating subjective feelings of emotional isolation and vulnerability.",
                penalty=50.0
            )]
            
            detected.append(YogaInstance(
                id="kemadruma_yoga",
                name="Kemadruma Yoga" + (" (Rescued / Bhaṅga)" if is_cancelled else ""),
                category=YogaCategory.LUNAR,
                status=status,
                plausibility_score=round(score, 1),
                participating_planets=["Moon"],
                participating_houses=[moon_house],
                scripture_ref="Phaladeepika 6.7, BPHS 37.11-13",
                archetype="The Solitary Mind: Moon sits isolated without flanking planets, feeling lack of an emotional safety net.",
                manifestation_effects=[
                    "Feelings of psychological isolation, melancholy, or having to fend for oneself." if not is_cancelled
                    else "Initial emotional isolation transformed into deep independence and resilience through angular support."
                ],
                positive_factors=cancellation_reasons,
                breakers=breakers
            ))
            
        # B. Gaja Kesari Yoga (Jupiter in Kendra from Moon)
        jup_house = get_house_of_planet(chart, "Jupiter")
        if jup_house > 0:
            diff_mj = (jup_house - moon_house) % 12 + 1
            if diff_mj in (1, 4, 7, 10):
                score = 85.0
                pos = [
                    f"Jupiter in House {jup_house} is in Kendra (H{diff_mj}) from the Moon.",
                    "The Guru of Wisdom directly fortifies the experiential feeling mind (Manas)."
                ]
                breakers = []
                breakers.extend(audit_combustion(["Jupiter"], chart))
                breakers.extend(audit_trishadaya_interference(["Jupiter", "Moon"], chart))
                
                # Check if Jupiter or Moon in Dusthana
                if moon_house in (6, 8, 12) or jup_house in (6, 8, 12):
                    breakers.append(YogaBreakerDetail(
                        factor="Dusthana Involvement",
                        culprit_planet="House",
                        description=f"Occurs in Dusthana (Moon H{moon_house}, Jupiter H{jup_house}), shifting results from public pomp to spiritual seclusion.",
                        penalty=20.0
                    ))
                    
                for b in breakers:
                    score -= b.penalty
                score = max(10.0, min(100.0, score))
                
                status = YogaStatus.PURE if score >= 75 else (YogaStatus.STAINED if score >= 50 else YogaStatus.RESCUED)
                
                detected.append(YogaInstance(
                    id="gaja_kesari_yoga",
                    name="Gaja Kesarī Yoga",
                    category=YogaCategory.LUNAR,
                    status=status,
                    plausibility_score=round(score, 1),
                    participating_planets=["Moon", "Jupiter"],
                    participating_houses=[moon_house, jup_house],
                    scripture_ref="BPHS 37.3-4, Phaladeepika 6.19",
                    archetype="The Elephant & The Lion: Fuses moral integrity with fearless intellect, commanding lasting respect.",
                    manifestation_effects=[
                        "Noble character, broad-minded philosophical wisdom, moral authority, and public reverence.",
                        "Protects against chronic depression and despair; natural counselor and patron."
                    ],
                    positive_factors=pos,
                    breakers=breakers
                ))
                
        # C. Chandra Mangala Yoga (Moon + Mars)
        mars_house = planet_houses.get("Mars", 0)
        if mars_house > 0:
            is_cm_conj = (mars_house == moon_house)
            aspect_mm = get_aspect_score(chart, "Mars", "Moon")
            is_cm_aspect = aspect_mm >= 30.0
            
            if is_cm_conj or is_cm_aspect:
                score = 80.0
                pos = [f"Moon and Mars combine (House {moon_house}" + (")" if is_cm_conj else f" via {aspect_mm:.0f} Virupa aspect)")]
                breakers = []
                breakers.extend(audit_trishadaya_interference(["Moon", "Mars"], chart))
                for b in breakers:
                    score -= b.penalty
                    
                detected.append(YogaInstance(
                    id="chandra_mangala_yoga",
                    name="Candra-Maṅgala Yoga",
                    category=YogaCategory.LUNAR,
                    status=YogaStatus.PURE if score >= 75 else YogaStatus.STAINED,
                    plausibility_score=round(score, 1),
                    participating_planets=["Moon", "Mars"],
                    participating_houses=[moon_house, mars_house],
                    scripture_ref="BPHS 37.8, Phaladeepika 6.20",
                    archetype="Energetic Wealth & Vigor: Unites the emotional mind with Martian drive, fostering commercial hustle.",
                    manifestation_effects=[
                        "Exceptional commercial acumen, enterprise, and capacity to generate liquid assets.",
                        "Dynamic emotional drive, though can cause occasional emotional heat or impulsiveness."
                    ],
                    positive_factors=pos,
                    breakers=breakers
                ))
                
        # D. Chandradhi Yoga (Benefics in 6th, 7th, 8th from Moon)
        h6_m = ((moon_house + 4) % 12) + 1
        h7_m = ((moon_house + 5) % 12) + 1
        h8_m = ((moon_house + 6) % 12) + 1
        
        adhi_benefics = [
            p for p in ("Mercury", "Jupiter", "Venus")
            if get_house_of_planet(chart, p) in (h6_m, h7_m, h8_m)
        ]
        if len(adhi_benefics) >= 2:
            score = 75.0 + len(adhi_benefics) * 8.0
            detected.append(YogaInstance(
                id="candradhi_yoga",
                name="Candrādhi Yoga",
                category=YogaCategory.LUNAR,
                status=YogaStatus.PURE if score >= 75 else YogaStatus.STAINED,
                plausibility_score=round(score, 1),
                participating_planets=["Moon"] + adhi_benefics,
                participating_houses=[moon_house, h6_m, h7_m, h8_m],
                scripture_ref="Phaladeepika 6.42-43, BPHS 37.9-10",
                archetype="The Configuration of Command: Surrounds the emotional center with cultural, diplomatic, and intellectual buffers.",
                manifestation_effects=[
                    "Conquers rivals through superior diplomacy, intellect, and grace rather than brute violence.",
                    "Creates high military commanders, diplomats, prime ministers, and elite leaders."
                ],
                positive_factors=[f"Natural benefics ({', '.join(adhi_benefics)}) occupy houses 6, 7, 8 from the Moon."],
                breakers=[]
            ))
            
    # -------------------------------------------------------------
    # 2. SOLAR YOGAS (RAVI YOGAS)
    # -------------------------------------------------------------
    if sun_house > 0:
        # A. Budhaditya Yoga (Sun + Mercury)
        merc_house = get_house_of_planet(chart, "Mercury")
        if merc_house == sun_house and "Mercury" in planets_data:
            sun_lon = planets_data["Sun"].get("longitude", 0.0)
            merc_lon = planets_data["Mercury"].get("longitude", 0.0)
            dist = abs(merc_lon - sun_lon) % 360.0
            if dist > 180.0:
                dist = 360.0 - dist
                
            score = 85.0
            pos = [f"Sun and Mercury conjoined in House {sun_house} (Separation: {dist:.1f}°)."]
            breakers = []
            
            if dist < 3.0:
                breakers.append(YogaBreakerDetail(
                    factor="Deep Combustion of Mercury",
                    culprit_planet="Sun",
                    description=f"Mercury is within {dist:.1f}° of the Sun. Intellectual illumination can get overwhelmed by ego or restlessness.",
                    penalty=25.0
                ))
                score -= 25.0
            elif dist >= 3.0 and dist <= 14.0:
                pos.append("Optimal illumination orb (3° to 14°): Mercury absorbs solar brilliance without being incinerated.")
                score += 5.0
                
            detected.append(YogaInstance(
                id="budhaditya_yoga",
                name="Budhāditya Yoga",
                category=YogaCategory.SOLAR,
                status=YogaStatus.PURE if score >= 75 else YogaStatus.STAINED,
                plausibility_score=round(score, 1),
                participating_planets=["Sun", "Mercury"],
                participating_houses=[sun_house],
                scripture_ref="BPHS 38.1, Phaladeepika 6.8",
                archetype="The Solar Intellect: The Sun's soul-force illuminates Mercury's analytical brilliance.",
                manifestation_effects=[
                    "High intelligence, administrative tact, verbal eloquence, and scholarly distinction.",
                    "Respected in scientific, governmental, or educational circles."
                ],
                positive_factors=pos,
                breakers=breakers
            ))
            
        # B. Vesi, Vosi, Ubhayachari Yogas
        h2_sun = (sun_house % 12) + 1
        h12_sun = ((sun_house - 2) % 12) + 1
        planets_in_h2_s = [p for p in planets_data if planet_houses.get(p) == h2_sun and p not in ("Moon", "Rahu", "Ketu", "Sun")]
        planets_in_h12_s = [p for p in planets_data if planet_houses.get(p) == h12_sun and p not in ("Moon", "Rahu", "Ketu", "Sun")]
        
        if planets_in_h2_s and planets_in_h12_s:
            detected.append(YogaInstance(
                id="ubhayachari_yoga",
                name="Ubhayacarī Yoga",
                category=YogaCategory.SOLAR,
                status=YogaStatus.PURE,
                plausibility_score=85.0,
                participating_planets=["Sun"] + planets_in_h2_s + planets_in_h12_s,
                participating_houses=[sun_house, h2_sun, h12_sun],
                scripture_ref="Phaladeepika 6.10, BPHS 38.4",
                archetype="Balanced Solar Aura: Planets flank both sides of the Sun, conferring charm and royal favor.",
                manifestation_effects=["Harmonious personality, articulateness, fame, and royal favor."],
                positive_factors=[f"Flanked in 2nd ({', '.join(planets_in_h2_s)}) and 12th ({', '.join(planets_in_h12_s)}) from Sun."],
                breakers=[]
            ))
        elif planets_in_h2_s:
            detected.append(YogaInstance(
                id="vesi_yoga",
                name="Veśi Yoga",
                category=YogaCategory.SOLAR,
                status=YogaStatus.PURE,
                plausibility_score=80.0,
                participating_planets=["Sun"] + planets_in_h2_s,
                participating_houses=[sun_house, h2_sun],
                scripture_ref="Phaladeepika 6.8, BPHS 38.2",
                archetype="Articulate Expression: Planets in 2nd from Sun support speech and memory.",
                manifestation_effects=["Steady memory, articulate communication, and financial stability."],
                positive_factors=[f"Planets in 2nd from Sun: {', '.join(planets_in_h2_s)}."],
                breakers=[]
            ))
        elif planets_in_h12_s:
            detected.append(YogaInstance(
                id="vosi_yoga",
                name="Vośi Yoga",
                category=YogaCategory.SOLAR,
                status=YogaStatus.PURE,
                plausibility_score=80.0,
                participating_planets=["Sun"] + planets_in_h12_s,
                participating_houses=[sun_house, h12_sun],
                scripture_ref="Phaladeepika 6.9, BPHS 38.3",
                archetype="Charitable Nobility: Planets in 12th from Sun bestow spiritual inclination and broad reputation.",
                manifestation_effects=["Charitable nature, spiritual inclinations, and honorable reputation."],
                positive_factors=[f"Planets in 12th from Sun: {', '.join(planets_in_h12_s)}."],
                breakers=[]
            ))

    # -------------------------------------------------------------
    # 3. MAHABHAGYA YOGA (Supreme Fortune / Great Good Fortune)
    # -------------------------------------------------------------
    # Phaladeepika 6.10-11, BPHS 38.4-5
    # Male: Day birth, Ascendant, Sun, Moon all in Odd (Male) signs
    # Female: Night birth, Ascendant, Sun, Moon all in Even (Female) signs
    d1 = chart.get("vargas", {}).get("D1", {})
    lagna_sign = d1.get("lagna", {}).get("sign", "")
    sun_sign = d1.get("grahas", {}).get("Sun", {}).get("sign", "")
    moon_sign = d1.get("grahas", {}).get("Moon", {}).get("sign", "")
    
    ODD_SIGNS = {"Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"}
    EVEN_SIGNS = {"Taurus", "Cancer", "Virgo", "Scorpio", "Capricorn", "Pisces"}
    
    is_day_birth = sun_house in (7, 8, 9, 10, 11, 12)
    
    is_male_mb = is_day_birth and (lagna_sign in ODD_SIGNS) and (sun_sign in ODD_SIGNS) and (moon_sign in ODD_SIGNS)
    is_female_mb = (not is_day_birth) and (lagna_sign in EVEN_SIGNS) and (sun_sign in EVEN_SIGNS) and (moon_sign in EVEN_SIGNS)
    
    if is_male_mb:
        detected.append(YogaInstance(
            id="mahabhagya_yoga",
            name="Mahābhāgya Yoga",
            category=YogaCategory.SOLAR,
            status=YogaStatus.PURE,
            plausibility_score=92.0,
            participating_planets=["Sun", "Moon"],
            participating_houses=[sun_house, moon_house, 1],
            scripture_ref="Phaladeepika 6.10-11, BPHS 38.4-5",
            archetype="Supreme Good Fortune: Harmonious solar-lunar alignment in masculine signs under daylight, creating royal charisma and immense fortune.",
            manifestation_effects=[
                "Endows massive public renown, boundless fortune, generous disposition, and regal authority.",
                "Grants robust vitality, long life, and spotless reputation; pleases the eyes of the public."
            ],
            positive_factors=[
                f"Day birth with Ascendant ({lagna_sign}), Sun ({sun_sign}), and Moon ({moon_sign}) all in masculine (odd) signs."
            ],
            breakers=[]
        ))
    elif is_female_mb:
        detected.append(YogaInstance(
            id="mahabhagya_yoga",
            name="Mahābhāgya Yoga",
            category=YogaCategory.LUNAR,
            status=YogaStatus.PURE,
            plausibility_score=92.0,
            participating_planets=["Sun", "Moon"],
            participating_houses=[sun_house, moon_house, 1],
            scripture_ref="Phaladeepika 6.10-11, BPHS 38.4-5",
            archetype="Supreme Good Fortune: Harmonious lunar alignment in feminine signs during nighttime, creating graceful prosperity.",
            manifestation_effects=[
                "Endows profound virtue, high material prosperity, spotless character, and enduring good fortune.",
                "Commands deep societal affection, domestic harmony, and longevity."
            ],
            positive_factors=[
                f"Night birth with Ascendant ({lagna_sign}), Sun ({sun_sign}), and Moon ({moon_sign}) all in feminine (even) signs."
            ],
            breakers=[]
        ))

    # -------------------------------------------------------------
    # 4. VARISHTHA, MADHYA, ADHAMA YOGAS (Solar-Lunar Angular Relationship)
    # -------------------------------------------------------------
    # Phaladeepika 6.14-15:
    # Kendra (1, 4, 7, 10) from Sun -> Varishtha Yoga (Foremost / Superior)
    # Panaphara (2, 5, 8, 11) from Sun -> Madhya Yoga (Moderate / Middling)
    # Apoklima (3, 6, 9, 12) from Sun -> Adhama Yoga (Deficient / Interiorized)
    SIGN_ORDER = {
        "Aries": 1, "Taurus": 2, "Gemini": 3, "Cancer": 4,
        "Leo": 5, "Virgo": 6, "Libra": 7, "Scorpio": 8,
        "Sagittarius": 9, "Capricorn": 10, "Aquarius": 11, "Pisces": 12
    }
    s_idx = SIGN_ORDER.get(sun_sign, 0)
    m_idx = SIGN_ORDER.get(moon_sign, 0)
    
    if s_idx > 0 and m_idx > 0:
        moon_from_sun = ((m_idx - s_idx) % 12) + 1
        
        if moon_from_sun in (1, 4, 7, 10):
            score = 85.0
            pos = [f"Moon is in House/Sign {moon_from_sun} (Kendra) from Sun ({moon_sign} from {sun_sign})."]
            breakers = []
            if moon_from_sun == 7:
                pos.append("Moon is 7th from Sun (Full Moon proximity / high Paksha Bala), conferring peak radiance and vitality.")
                score += 5.0
            detected.append(YogaInstance(
                id="varishtha_yoga",
                name="Variṣṭha Yoga",
                category=YogaCategory.LUNAR,
                status=YogaStatus.PURE,
                plausibility_score=round(score, 1),
                participating_planets=["Moon", "Sun"],
                participating_houses=[moon_house, sun_house],
                scripture_ref="Phaladeepika 6.14-15",
                archetype="Foremost Angular Radiance: Moon in an angle (Kendra) from the Sun, magnifying wealth, reputation, and worldly influence.",
                manifestation_effects=[
                    "Abundant wealth, vehicles, fame, happiness, learning, and broad public stature.",
                    "Significantly multiplies and accelerates the fruits of other positive yogas in the horoscope."
                ],
                positive_factors=pos,
                breakers=breakers
            ))
        elif moon_from_sun in (2, 5, 8, 11):
            detected.append(YogaInstance(
                id="madhya_yoga",
                name="Madhya Yoga",
                category=YogaCategory.LUNAR,
                status=YogaStatus.PURE,
                plausibility_score=75.0,
                participating_planets=["Moon", "Sun"],
                participating_houses=[moon_house, sun_house],
                scripture_ref="Phaladeepika 6.14-15",
                archetype="Balanced Succedent Position: Moon in a Panaphara house from the Sun.",
                manifestation_effects=[
                    "Moderate wealth, steady fortune, and middling public recognition."
                ],
                positive_factors=[f"Moon is in House/Sign {moon_from_sun} (Panaphara) from Sun ({moon_sign} from {sun_sign})."],
                breakers=[]
            ))
        elif moon_from_sun in (3, 6, 9, 12):
            detected.append(YogaInstance(
                id="adhama_yoga",
                name="Adhama Yoga",
                category=YogaCategory.LUNAR,
                status=YogaStatus.STAINED,
                plausibility_score=65.0,
                participating_planets=["Moon", "Sun"],
                participating_houses=[moon_house, sun_house],
                scripture_ref="Phaladeepika 6.14-15",
                archetype="Interiorized Cadent Position: Moon in an Apoklima house from the Sun, directing awareness away from external display.",
                manifestation_effects=[
                    "Meager material accumulation or disinterest in ostentatious wealth.",
                    "Fosters inner contemplation, ascetic tendency, and quiet scholarship rather than flamboyant commercial display."
                ],
                positive_factors=[f"Moon is in House/Sign {moon_from_sun} (Apoklima) from Sun ({moon_sign} from {sun_sign})."],
                breakers=[
                    YogaBreakerDetail(
                        factor="Cadent Separation from Sun",
                        culprit_planet="Moon",
                        description=f"Moon is cadent ({moon_from_sun}th) from Sun, reducing worldly drive and outward commercial pomp.",
                        penalty=10.0
                    )
                ]
            ))

    return detected
