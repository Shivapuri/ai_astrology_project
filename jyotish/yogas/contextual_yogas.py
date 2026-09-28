"""
jyotish/yogas/contextual_yogas.py
Contextual & Macro Setup Yogas Engine.

Evaluates the ~25 foundational contextual setup yogas that define the native's
macrocosmic life canvas and distribution pattern before individual grahas are analyzed.

Categories Evaluated:
1. Sāṅkhya Yogas (Pattern of Distribution - 7 yogas)
2. General Scope Yogas (Sun-Moon Quadrant Geometry - 3 yogas)
3. Mahābhāgya Yoga (Supreme Fortune Synergies - Male & Female configurations)
4. Śubha & Aśubha Solitary House Yogas (1st house occupants & flanking - 4 yogas)
5. 3-Tier Kemadruma Yoga & Cancellation (Lunar Isolation & Rescue - 2 yogas)
6. Solar Flanking Yogas (Veśi, Vośi, Ubhayācarī - 6 variations)
7. Dual-Lagna Raja Yoga (Ubhayalagna Synchrony - 1 yoga)
"""

from typing import List, Dict, Any, Set, Tuple
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_lagna_sign, get_planets_data, get_sign_of_planet, get_house_of_planet,
    NATURAL_BENEFICS, NATURAL_MALEFICS, ZODIAC_SIGNS, SIGN_LORDS
)

CLASSICAL_7_GRAHAS: List[str] = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"
]

ODD_SIGNS: Set[str] = {"Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"}
EVEN_SIGNS: Set[str] = {"Taurus", "Cancer", "Virgo", "Scorpio", "Capricorn", "Pisces"}


def detect_sankhya_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Evaluates the 7 Sāṅkhya Yogas based on the number of unique zodiac signs
    occupied by the classical 7 planets (Sun through Saturn).
    Scripture: BPHS Ch. 35 (Nabhasa Yogas).
    """
    detected: List[YogaInstance] = []
    occupied_signs: Set[str] = set()
    participating_grahas: List[str] = []

    for p in CLASSICAL_7_GRAHAS:
        sign = get_sign_of_planet(chart, p)
        if sign and sign in ZODIAC_SIGNS:
            occupied_signs.add(sign)
            participating_grahas.append(p)

    num_signs = len(occupied_signs)
    if num_signs == 0:
        return detected

    sankhya_definitions = {
        1: {
            "id": "sankhya_gola_yoga",
            "name": "Gola Yoga (Singular Focus)",
            "archetype": "Extremely concentrated, intense, narrow life focus. All energy is channeled into a single existential sphere.",
            "manifestations": [
                "Unwavering single-minded intensity or potential dogmatism.",
                "All major karmic lessons and resources converge into one singular department of life.",
                "Tremendous potential for extreme specialization or obsessive determination."
            ]
        },
        2: {
            "id": "sankhya_yuga_yoga",
            "name": "Yuga Yoga (Dualistic Tension)",
            "archetype": "Life pivots around strong dualities, intense polarization, and heavy interdependence on key partners or rivals.",
            "manifestations": [
                "Continuous push-and-pull between two primary areas of life or core relationships.",
                "Reliance on alliances, contracts, or strong counterparties to make progress.",
                "Tendency to experience life in black-and-white or high-contrast terms."
            ]
        },
        3: {
            "id": "sankhya_shula_yoga",
            "name": "Śūla Yoga (Trident Resolve)",
            "archetype": "Piercing ambition, austere courage, sharp and aggressive resolve. Endures hardship to conquer goals.",
            "manifestations": [
                "Sharp, incisive willpower and readiness to overcome formidable obstacles.",
                "Can display an austere, uncompromising, or battle-ready disposition.",
                "High tolerance for adversity and rigorous physical or mental endurance."
            ]
        },
        4: {
            "id": "sankhya_kedara_yoga",
            "name": "Kedāra Yoga (Agricultural Patience)",
            "archetype": "Steadfast, grounded, hardworking, and patient. Builds enduring tangible assets like fertile fields.",
            "manifestations": [
                "Constructive, methodical builder mindset with long-term stamina.",
                "Pragmatic approach to resources, real estate, and tangible security.",
                "High dependability and resilience against fleeting worldly turbulence."
            ]
        },
        5: {
            "id": "sankhya_pasa_yoga",
            "name": "Pāśa Yoga (Ties of Duty)",
            "archetype": "Strong bonds to family, duty, and community. Skilled in worldly negotiations, administration, and social webs.",
            "manifestations": [
                "Entangled in extensive familial, professional, or social obligations.",
                "Resourceful administrative ability, diplomatic skill, and social networking.",
                "Progress is achieved through navigating obligations and serving key networks."
            ]
        },
        6: {
            "id": "sankhya_dama_yoga",
            "name": "Dāma Yoga (Generous Benefactor)",
            "archetype": "Broad-minded, generous, helpful to many, endowed with versatile talents and public respect.",
            "manifestations": [
                "Generous and philanthropic outlook, naturally inclined to support and protect others.",
                "Multifaceted worldly skills and ability to connect diverse groups of people.",
                "Honored in society for fairness, benevolence, and balanced judgment."
            ]
        },
        7: {
            "id": "sankhya_veena_yoga",
            "name": "Vīṇā Yoga (Harmonious Versatility)",
            "archetype": "Balanced, artistic, cultured, and multifaceted. Life unfolds with melodic grace and diverse capabilities.",
            "manifestations": [
                "Love of music, literature, aesthetics, and cultural refinement.",
                "Widespread intellectual curiosity and ability to adapt effortlessly to multiple disciplines.",
                "Harmonious distribution of planetary energy across the entire horoscope."
            ]
        }
    }

    if num_signs in sankhya_definitions:
        defn = sankhya_definitions[num_signs]
        detected.append(YogaInstance(
            id=defn["id"],
            name=defn["name"],
            category=YogaCategory.CONTEXTUAL,
            status=YogaStatus.PURE,
            plausibility_score=90.0,
            participating_planets=participating_grahas,
            participating_houses=sorted(list({get_house_of_planet(chart, p) for p in participating_grahas if get_house_of_planet(chart, p) > 0})),
            scripture_ref="BPHS Ch. 35 (Nabhasa Sāṅkhya Yogas)",
            archetype=defn["archetype"],
            manifestation_effects=defn["manifestations"],
            positive_factors=[f"Classical 7 grahas distributed cleanly across exactly {num_signs} unique signs ({', '.join(sorted(occupied_signs))})."],
            breakers=[]
        ))

    return detected


def detect_general_scope_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Evaluates General Scope Yogas based on the Sun-Moon quadrant geometry.
    Measures the distance from Sun to Moon:
    - Kendra (1, 4, 7, 10 from Sun): High Visibility Scope
    - Panaphara (2, 5, 8, 11 from Sun): Middle-Phase Resource Scope
    - Apoklima (3, 6, 9, 12 from Sun): Introspective & Contemplative Scope
    Scripture: BPHS Ch. 38, Phaladeepika Ch. 6.
    """
    detected: List[YogaInstance] = []
    sun_house = get_house_of_planet(chart, "Sun")
    moon_house = get_house_of_planet(chart, "Moon")

    if sun_house <= 0 or moon_house <= 0:
        return detected

    rel_house = ((moon_house - sun_house) % 12) + 1

    if rel_house in (1, 4, 7, 10):
        detected.append(YogaInstance(
            id="kendra_scope_yoga",
            name="Kendra Scope Yoga (High Visibility)",
            category=YogaCategory.CONTEXTUAL,
            status=YogaStatus.PURE,
            plausibility_score=85.0,
            participating_planets=["Sun", "Moon"],
            participating_houses=[sun_house, moon_house],
            scripture_ref="BPHS Ch. 38.1-3, Phaladeepika Ch. 6.14",
            archetype="Moon occupies a Kendra from Sun. High visibility, prominent self-expression, and dynamic public engagement.",
            manifestation_effects=[
                "Strong external presence; private emotional needs (Moon) are directly projected into outer expression (Sun).",
                "High public visibility and dramatic, high-contrast personality shifts.",
                "Natural confidence in taking center stage and leading initiatives."
            ],
            positive_factors=[f"Moon is in house {rel_house} (Kendra) from the Sun."],
            breakers=[]
        ))
    elif rel_house in (2, 5, 8, 11):
        detected.append(YogaInstance(
            id="panaphara_scope_yoga",
            name="Panaphara Scope Yoga (Steady Growth)",
            category=YogaCategory.CONTEXTUAL,
            status=YogaStatus.PURE,
            plausibility_score=80.0,
            participating_planets=["Sun", "Moon"],
            participating_houses=[sun_house, moon_house],
            scripture_ref="BPHS Ch. 38.1-3, Phaladeepika Ch. 6.15",
            archetype="Moon occupies a Panaphara (Succedent) house from Sun. Resource-focused, deliberate, steady mid-life development.",
            manifestation_effects=[
                "Pragmatic approach to emotional fulfillment through material security and gradual cultivation.",
                "Peak life accomplishments and steady resources materialize during the mature middle phase of life.",
                "Patience, persistence, and steady resource consolidation."
            ],
            positive_factors=[f"Moon is in house {rel_house} (Panaphara) from the Sun."],
            breakers=[]
        ))
    else:  # 3, 6, 9, 12
        detected.append(YogaInstance(
            id="apoklima_scope_yoga",
            name="Apoklima Scope Yoga (Introspective Depth)",
            category=YogaCategory.CONTEXTUAL,
            status=YogaStatus.PURE,
            plausibility_score=80.0,
            participating_planets=["Sun", "Moon"],
            participating_houses=[sun_house, moon_house],
            scripture_ref="BPHS Ch. 38.1-3, Phaladeepika Ch. 6.16",
            archetype="Moon occupies an Apoklima (Cadent) house from Sun. Subdued public posturing with profound introspective depth.",
            manifestation_effects=[
                "Prefers behind-the-scenes mastery, advisory roles, research, or spiritual contemplation over loud fanfare.",
                "Rich, complex inner emotional world that is not immediately visible to superficial observers.",
                "High capacity for philosophical detachment and independent mental self-sufficiency."
            ],
            positive_factors=[f"Moon is in house {rel_house} (Apoklima) from the Sun."],
            breakers=[]
        ))

    return detected


def detect_mahabhagya_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Evaluates Mahābhāgya Yoga (Supreme Fortune Synergy).
    Conditions:
    - Male Native: Day birth + Lagna in Odd Sign + Sun in Odd Sign + Moon in Odd Sign.
    - Female Native: Night birth + Lagna in Even Sign + Sun in Even Sign + Moon in Even Sign.
    Scripture: BPHS Ch. 37.40-42, Phaladeepika Ch. 6.17-18.
    """
    detected: List[YogaInstance] = []
    lagna_sign = get_lagna_sign(chart)
    sun_sign = get_sign_of_planet(chart, "Sun")
    moon_sign = get_sign_of_planet(chart, "Moon")

    if not lagna_sign or not sun_sign or not moon_sign:
        return detected

    # Day birth: Sun in houses 7-12 (above horizon) or chart flag
    sun_house = get_house_of_planet(chart, "Sun")
    is_day_birth = chart.get("is_day_birth")
    if is_day_birth is None:
        is_day_birth = (sun_house in (7, 8, 9, 10, 11, 12)) if sun_house > 0 else True

    gender = str(chart.get("gender") or chart.get("meta", {}).get("gender", "")).strip().lower()

    # Check Male Configuration
    male_match = (
        is_day_birth and
        lagna_sign in ODD_SIGNS and
        sun_sign in ODD_SIGNS and
        moon_sign in ODD_SIGNS
    )

    # Check Female Configuration
    female_match = (
        (not is_day_birth) and
        lagna_sign in EVEN_SIGNS and
        sun_sign in EVEN_SIGNS and
        moon_sign in EVEN_SIGNS
    )

    if male_match and gender != "female":
        detected.append(YogaInstance(
            id="mahabhagya_male_yoga",
            name="Mahābhāgya Yoga (Supreme Fortune - Male Configuration)",
            category=YogaCategory.CONTEXTUAL,
            status=YogaStatus.PURE,
            plausibility_score=95.0,
            participating_planets=["Sun", "Moon"],
            participating_houses=[get_house_of_planet(chart, "Sun"), get_house_of_planet(chart, "Moon"), 1],
            scripture_ref="BPHS Ch. 37.40-41, Phaladeepika Ch. 6.17",
            archetype="Supreme Fortune through perfect solar-masculine congruence: Day birth with Lagna, Sun, and Moon all in active Odd signs.",
            manifestation_effects=[
                "Effortless public authority, natural dignity, and command over large groups.",
                "Strong generosity, high reputation, and widespread societal recognition.",
                "Smooth manifestation of goals with enduring wealth and protection against disgrace."
            ],
            positive_factors=[
                "Day birth confirms solar vitality.",
                f"Lagna ({lagna_sign}), Sun ({sun_sign}), and Moon ({moon_sign}) all occupy active masculine Odd signs."
            ],
            breakers=[]
        ))

    if female_match and gender != "male":
        detected.append(YogaInstance(
            id="mahabhagya_female_yoga",
            name="Mahābhāgya Yoga (Supreme Fortune - Female Configuration)",
            category=YogaCategory.CONTEXTUAL,
            status=YogaStatus.PURE,
            plausibility_score=95.0,
            participating_planets=["Sun", "Moon"],
            participating_houses=[get_house_of_planet(chart, "Sun"), get_house_of_planet(chart, "Moon"), 1],
            scripture_ref="BPHS Ch. 37.41-42, Phaladeepika Ch. 6.18",
            archetype="Supreme Fortune through perfect lunar-feminine congruence: Night birth with Lagna, Sun, and Moon all in receptive Even signs.",
            manifestation_effects=[
                "Deep poise, magnetic grace, and natural harmony within family and community.",
                "Generous, noble conduct with profound intuitive discernment.",
                "Long-lasting prosperity, domestic contentment, and high social respect."
            ],
            positive_factors=[
                "Night birth confirms lunar resonance.",
                f"Lagna ({lagna_sign}), Sun ({sun_sign}), and Moon ({moon_sign}) all occupy receptive feminine Even signs."
            ],
            breakers=[]
        ))

    return detected


def detect_solitary_first_house_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Evaluates Solitary 1st House Occupancy and Lagna Flanking Yogas.
    - Solitary Mars in 1st: Aśubha Tanu (Extreme physical grit, warrior constitution)
    - Solitary Saturn in 1st: Aśubha Tanu (Stoic discipline, early burdens fostering lifelong resilience)
    - Solitary Benefic in 1st: Śubha Tanu / Chāmarā (Natural personal grace, charisma, protection)
    - Śubhakartari of 1st House: Benefics flanking 2nd and 12th from Lagna
    - Pāpakartari of 1st House: Malefics flanking 2nd and 12th from Lagna
    Scripture: BPHS Ch. 34 & 37.
    """
    detected: List[YogaInstance] = []
    planets_data = get_planets_data(chart)
    planet_houses = {p: get_house_of_planet(chart, p) for p in planets_data}

    h1_planets = [p for p in planets_data if planet_houses.get(p) == 1]
    h2_planets = [p for p in planets_data if planet_houses.get(p) == 2]
    h12_planets = [p for p in planets_data if planet_houses.get(p) == 12]

    # 1. Solitary Mars in 1st
    if h1_planets == ["Mars"]:
        detected.append(YogaInstance(
            id="solitary_mars_tanu_yoga",
            name="Solitary Mars in 1st House (Aśubha Fortitude)",
            category=YogaCategory.CONTEXTUAL,
            status=YogaStatus.STAINED,
            plausibility_score=85.0,
            participating_planets=["Mars"],
            participating_houses=[1],
            scripture_ref="BPHS Ch. 12 & 34",
            archetype="Mars stands alone in the 1st House, imparting formidable physical grit, sharp courage, and fierce independence.",
            manifestation_effects=[
                "Extreme physical resilience, athletic capacity, and warrior-like constitution.",
                "Fierce independence, intolerance for condescension, and quick temper.",
                "Challenges gentility and delicate diplomacy in close partnerships."
            ],
            positive_factors=["Unyielding courage and physical stamina."],
            breakers=[YogaBreakerDetail(
                factor="Solitary Malefic in Ascendant",
                culprit_planet="Mars",
                description="Mars alone in 1st Bhava increases combative friction and headstrong impulsiveness.",
                penalty=15.0
            )]
        ))

    # 2. Solitary Saturn in 1st
    elif h1_planets == ["Saturn"]:
        detected.append(YogaInstance(
            id="solitary_saturn_tanu_yoga",
            name="Solitary Saturn in 1st House (Stoic Resilience)",
            category=YogaCategory.CONTEXTUAL,
            status=YogaStatus.STAINED,
            plausibility_score=85.0,
            participating_planets=["Saturn"],
            participating_houses=[1],
            scripture_ref="BPHS Ch. 12 & 34",
            archetype="Saturn stands alone in the 1st House, forging a stoic, disciplined, and sober personality through early self-reliance.",
            manifestation_effects=[
                "Deep patience, mature gravity from an early age, and realistic life expectations.",
                "Lifelong perseverance and ability to endure prolonged solitary toil.",
                "Tendency toward melancholy, heavy self-criticism, or initial physical hesitation."
            ],
            positive_factors=["Enduring discipline and grounded realism."],
            breakers=[YogaBreakerDetail(
                factor="Solitary Malefic in Ascendant",
                culprit_planet="Saturn",
                description="Saturn alone in 1st Bhava creates solemn hesitation and heavy emotional self-containment.",
                penalty=15.0
            )]
        ))

    # 3. Solitary Natural Benefic in 1st
    elif len(h1_planets) == 1 and h1_planets[0] in NATURAL_BENEFICS:
        ben = h1_planets[0]
        detected.append(YogaInstance(
            id=f"solitary_{ben.lower()}_tanu_yoga",
            name=f"Solitary {ben} in 1st House (Śubha Tanu)",
            category=YogaCategory.CONTEXTUAL,
            status=YogaStatus.PURE,
            plausibility_score=90.0,
            participating_planets=[ben],
            participating_houses=[1],
            scripture_ref="BPHS Ch. 12 & 37 (Chāmarā & Śubha Lagna)",
            archetype=f"A solitary natural benefic ({ben}) blesses the Ascendant, radiating charm, benevolence, and natural social protection.",
            manifestation_effects=[
                "Pleasing personal demeanor, gracious communication, and natural charisma.",
                "Inherent moral compass, social generosity, and ease in winning goodwill.",
                "Strong protection against severe bodily harm and chronic disgrace."
            ],
            positive_factors=[f"{ben} occupying 1st house without disruptive co-occupants."],
            breakers=[]
        ))

    # 4. Lagna Flanking (Kartari)
    if h2_planets and h12_planets:
        h2_benefics = [p for p in h2_planets if p in NATURAL_BENEFICS]
        h12_benefics = [p for p in h12_planets if p in NATURAL_BENEFICS]
        h2_malefics = [p for p in h2_planets if p in NATURAL_MALEFICS]
        h12_malefics = [p for p in h12_planets if p in NATURAL_MALEFICS]

        # Pure Śubhakartari of Lagna
        if h2_benefics and h12_benefics and not h2_malefics and not h12_malefics:
            detected.append(YogaInstance(
                id="shubhakartari_lagna_yoga",
                name="Śubhakartari Yoga of the 1st House",
                category=YogaCategory.CONTEXTUAL,
                status=YogaStatus.PURE,
                plausibility_score=90.0,
                participating_planets=h2_benefics + h12_benefics,
                participating_houses=[12, 1, 2],
                scripture_ref="BPHS Ch. 34.1-2, Phaladeepika Ch. 6.2",
                archetype="The Ascendant is safely held between benefics in both 2nd and 12th houses, nurturing the body and self-esteem.",
                manifestation_effects=[
                    "High life vitality, smooth physical health, and warm social reception.",
                    "Personal endeavors are well-supported financially (2nd) and spiritually/mentally (12th).",
                    "Strong psychological equilibrium and immunity to petty external slander."
                ],
                positive_factors=[f"Benefics in 12th ({h12_benefics}) and 2nd ({h2_benefics}) flank the Ascendant."],
                breakers=[]
            ))

        # Pure Pāpakartari of Lagna
        elif h2_malefics and h12_malefics and not h2_benefics and not h12_benefics:
            detected.append(YogaInstance(
                id="papakartari_lagna_yoga",
                name="Pāpakartari Yoga of the 1st House",
                category=YogaCategory.CONTEXTUAL,
                status=YogaStatus.STAINED,
                plausibility_score=85.0,
                participating_planets=h2_malefics + h12_malefics,
                participating_houses=[12, 1, 2],
                scripture_ref="BPHS Ch. 34.3-4, Phaladeepika Ch. 6.3",
                archetype="The Ascendant is hemmed between malefics in both 2nd and 12th houses, creating persistent pressure on the self.",
                manifestation_effects=[
                    "Feeling boxed in by circumstances, recurrent physical strain, or heightened anxiety.",
                    "Demands continuous expenditure of willpower and vigilance to maintain peace.",
                    "Fosters immense grit and defensive resourcefulness over time."
                ],
                positive_factors=["Builds extreme resilience and self-protective cunning."],
                breakers=[YogaBreakerDetail(
                    factor="Malefics Hemming 1st House",
                    culprit_planet=", ".join(h2_malefics + h12_malefics),
                    description="Malefics in 2nd and 12th houses create chronic friction and psychological pressure.",
                    penalty=25.0
                )]
            ))

    return detected


def detect_kemadruma_yoga(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Evaluates 3-Tier Kemadruma Yoga and its Cancellation (Kemadruma Bhaṅga).
    - Tier 1 (Trigger): No planets (excluding Sun, Rahu, Ketu) in 2nd or 12th from Moon.
    - Tier 2 (Core Check): Moon is not in a Kendra (1, 4, 7, 10) from Lagna.
    - Tier 3 (Complete Isolation): No classical planets in Kendras (1, 4, 7, 10) from Moon.
    Scripture: BPHS Ch. 37.11-16, Phaladeepika Ch. 6.6-8.
    """
    detected: List[YogaInstance] = []
    planets_data = get_planets_data(chart)
    planet_houses = {p: get_house_of_planet(chart, p) for p in planets_data}

    moon_house = planet_houses.get("Moon", 0)
    if moon_house <= 0:
        return detected

    # Tier 1: Flanking planets from Moon (excluding Sun, Rahu, Ketu, Moon)
    h2_moon = (moon_house % 12) + 1
    h12_moon = ((moon_house - 2) % 12) + 1

    flankers = [
        p for p in planets_data
        if planet_houses.get(p) in (h2_moon, h12_moon) and p not in ("Sun", "Rahu", "Ketu", "Moon")
    ]

    # If flankers exist, Kemadruma cannot form at all
    if len(flankers) > 0:
        return detected

    # Tier 2: Moon occupying a Kendra from Lagna
    moon_in_lagna_kendra = moon_house in (1, 4, 7, 10)

    # Tier 3: Classical planets occupying Kendras from Moon
    moon_kendras = [((moon_house + k - 1) % 12) + 1 for k in (0, 3, 6, 9)]
    planets_in_moon_kendras = [
        p for p in CLASSICAL_7_GRAHAS
        if p != "Moon" and planet_houses.get(p) in moon_kendras
    ]

    # Full Kemadruma (All 3 tiers fulfilled)
    if not moon_in_lagna_kendra and len(planets_in_moon_kendras) == 0:
        detected.append(YogaInstance(
            id="kemadruma_yoga",
            name="Kemadruma Yoga (Lunar Isolation)",
            category=YogaCategory.CONTEXTUAL,
            status=YogaStatus.STAINED,
            plausibility_score=85.0,
            participating_planets=["Moon"],
            participating_houses=[moon_house],
            scripture_ref="BPHS Ch. 37.11-13, Phaladeepika Ch. 6.6",
            archetype="The Moon stands completely isolated without planetary flankers or supportive Kendra pillars, fostering deep subjective loneliness.",
            manifestation_effects=[
                "Pervasive feeling of emotional isolation or walking a solitary path.",
                "Subconscious anxiety and occasional emotional self-doubt or estrangement from kin.",
                "Supreme potential for spiritual self-reliance, non-attachment, and ascetic mastery."
            ],
            positive_factors=["Catalyzes deep introspection and unshakeable inner independence."],
            breakers=[YogaBreakerDetail(
                factor="Complete Lunar Isolation",
                culprit_planet="Moon",
                description="Moon lacks flanking planets (2nd/12th) and has no classical planets in Kendras from Lagna or itself.",
                penalty=30.0
            )]
        ))
    else:
        # Kemadruma Bhaṅga (Rescued Lunar Isolation)
        rescuing_factors = []
        rescuing_planets = []
        if moon_in_lagna_kendra:
            rescuing_factors.append(f"Moon occupies a powerful Kendra (House {moon_house}) from Lagna, anchoring the personality in public life.")
        if planets_in_moon_kendras:
            rescuing_planets.extend(planets_in_moon_kendras)
            rescuing_factors.append(f"Classical planets ({', '.join(planets_in_moon_kendras)}) occupy Kendras from Moon, providing emotional pillars.")

        detected.append(YogaInstance(
            id="kemadruma_bhanga_yoga",
            name="Kemadruma Bhaṅga Yoga (Rescued Lunar Isolation)",
            category=YogaCategory.CONTEXTUAL,
            status=YogaStatus.RESCUED,
            plausibility_score=85.0,
            participating_planets=["Moon"] + rescuing_planets,
            participating_houses=sorted(list({moon_house} | {planet_houses.get(p, 0) for p in rescuing_planets if planet_houses.get(p, 0) > 0})),
            scripture_ref="BPHS Ch. 37.14-16, Phaladeepika Ch. 6.7-8",
            archetype="Initial lunar vulnerability and feeling of alienation are completely rescued through active worldly responsibility or supportive planetary pillars.",
            manifestation_effects=[
                "Early sense of emotional solitude transforms into extraordinary self-reliance and worldly authority.",
                "Overcomes initial internal hesitation to build enduring respect and public position.",
                "Deep psychological empathy forged through conquered loneliness."
            ],
            positive_factors=rescuing_factors,
            breakers=[]
        ))

    return detected


def detect_solar_flanking_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Evaluates Solar Flanking Yogas (Veśi, Vośi, Ubhayācarī).
    Formed by planets in 2nd and 12th from Sun (excluding Moon, Rahu, Ketu).
    Scripture: BPHS Ch. 37.1-10, Phaladeepika Ch. 6.9-13.
    """
    detected: List[YogaInstance] = []
    planets_data = get_planets_data(chart)
    planet_houses = {p: get_house_of_planet(chart, p) for p in planets_data}

    sun_house = planet_houses.get("Sun", 0)
    if sun_house <= 0:
        return detected

    h2_sun = (sun_house % 12) + 1
    h12_sun = ((sun_house - 2) % 12) + 1

    p_in_2 = [
        p for p in planets_data
        if planet_houses.get(p) == h2_sun and p not in ("Moon", "Rahu", "Ketu", "Sun")
    ]
    p_in_12 = [
        p for p in planets_data
        if planet_houses.get(p) == h12_sun and p not in ("Moon", "Rahu", "Ketu", "Sun")
    ]

    # Helper to classify nature
    def classify_flavor(planets: List[str]) -> Tuple[str, str, YogaStatus]:
        bens = [p for p in planets if p in NATURAL_BENEFICS]
        mals = [p for p in planets if p in NATURAL_MALEFICS]
        if bens and not mals:
            return "Śubha-", "Pure benefics bestow ethical nobility, eloquence, and smooth prosperity.", YogaStatus.PURE
        elif mals and not bens:
            return "Pāpa-", "Malefics impart formidable cunning, sharp ambition, and hard-edged grit.", YogaStatus.STAINED
        else:
            return "Miśra-", "Mixed planets create dynamic versatility and competitive resourcefulness.", YogaStatus.PURE

    # 1. Ubhayācarī Yoga (Both 2nd and 12th occupied)
    if p_in_2 and p_in_12:
        prefix, note, status = classify_flavor(p_in_2 + p_in_12)
        detected.append(YogaInstance(
            id="ubhayacari_yoga",
            name=f"{prefix}Ubhayācarī Yoga (Solar Flanking Symmetry)",
            category=YogaCategory.CONTEXTUAL,
            status=status,
            plausibility_score=90.0,
            participating_planets=["Sun"] + p_in_2 + p_in_12,
            participating_houses=[h12_sun, sun_house, h2_sun],
            scripture_ref="BPHS Ch. 37.7-10, Phaladeepika Ch. 6.13",
            archetype=f"Planets flank the Sun on both sides (2nd and 12th), granting well-rounded executive leadership and poise. {note}",
            manifestation_effects=[
                "Broad societal vision, commanding executive poise, and strong worldly standing.",
                "Balanced integration of resources/accumulation (2nd) and strategic release/foresight (12th).",
                "High stamina and capacity to manage diverse responsibilities simultaneously."
            ],
            positive_factors=[f"Planets in 2nd ({p_in_2}) and 12th ({p_in_12}) flank the Sun."],
            breakers=[]
        ))

    # 2. Veśi Yoga (Only 2nd from Sun occupied)
    elif p_in_2 and not p_in_12:
        prefix, note, status = classify_flavor(p_in_2)
        detected.append(YogaInstance(
            id="vesi_yoga",
            name=f"{prefix}Veśi Yoga (Solar Materialization)",
            category=YogaCategory.CONTEXTUAL,
            status=status,
            plausibility_score=85.0,
            participating_planets=["Sun"] + p_in_2,
            participating_houses=[sun_house, h2_sun],
            scripture_ref="BPHS Ch. 37.1-3, Phaladeepika Ch. 6.9-10",
            archetype=f"Planets in 2nd from Sun channel solar authority into tangible manifestation, eloquence, and wealth. {note}",
            manifestation_effects=[
                "Articulate speech, tangible financial accumulation, and skillful worldly execution.",
                "Generous demeanor, truthfulness, and strong memory.",
                "Skill in converting royal or executive opportunities into durable assets."
            ],
            positive_factors=[f"Planets in 2nd from Sun: {', '.join(p_in_2)}."],
            breakers=[]
        ))

    # 3. Vośi Yoga (Only 12th from Sun occupied)
    elif p_in_12 and not p_in_2:
        prefix, note, status = classify_flavor(p_in_12)
        detected.append(YogaInstance(
            id="vosi_yoga",
            name=f"{prefix}Vośi Yoga (Solar Vision & Charity)",
            category=YogaCategory.CONTEXTUAL,
            status=status,
            plausibility_score=85.0,
            participating_planets=["Sun"] + p_in_12,
            participating_houses=[h12_sun, sun_house],
            scripture_ref="BPHS Ch. 37.4-6, Phaladeepika Ch. 6.11-12",
            archetype=f"Planets in 12th from Sun bestow philosophical vision, charitable release, and detachment. {note}",
            manifestation_effects=[
                "Philosophical intellect, charitable impulses, and deep contemplative foresight.",
                "Prefers working behind the scenes or in expansive, cross-cultural environments.",
                "Generous expenditure on noble causes or ambitious long-term visions."
            ],
            positive_factors=[f"Planets in 12th from Sun: {', '.join(p_in_12)}."],
            breakers=[]
        ))

    return detected


def detect_dual_lagna_raja_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Evaluates Dual-Lagna Raja Yoga (Ubhayalagna Synchrony).
    Validates classical Kendra-Koṇa lord combinations evaluated simultaneously
    from both Janma Lagna (external life) and Candra Lagna (mental/experiential life).
    Scripture: BPHS Ch. 34 & 37.
    """
    detected: List[YogaInstance] = []
    lagna_sign = get_lagna_sign(chart)
    moon_sign = get_sign_of_planet(chart, "Moon")

    if not lagna_sign or not moon_sign or lagna_sign not in ZODIAC_SIGNS or moon_sign not in ZODIAC_SIGNS:
        return detected

    planets_data = get_planets_data(chart)

    # 1. Calculate house rulers from Lagna
    l_idx = ZODIAC_SIGNS.index(lagna_sign)
    lagna_rulers: Dict[int, str] = {
        h: SIGN_LORDS[ZODIAC_SIGNS[(l_idx + h - 1) % 12]] for h in range(1, 13)
    }

    # 2. Calculate house rulers from Moon (Candra Lagna)
    m_idx = ZODIAC_SIGNS.index(moon_sign)
    candra_rulers: Dict[int, str] = {
        h: SIGN_LORDS[ZODIAC_SIGNS[(m_idx + h - 1) % 12]] for h in range(1, 13)
    }

    # Kendra (1, 4, 7, 10) and Koṇa (1, 5, 9) pairs
    # Significant Kendra-Kona pairs: (9, 10), (1, 5), (1, 9), (4, 9), (5, 10)
    KEY_PAIRS: List[Tuple[int, int]] = [(9, 10), (4, 9), (5, 10), (1, 9), (1, 5)]

    for k_house, kn_house in KEY_PAIRS:
        # Check Janma Lagna
        lord_k_lagna = lagna_rulers[k_house]
        lord_kn_lagna = lagna_rulers[kn_house]

        # Check Candra Lagna
        lord_k_candra = candra_rulers[k_house]
        lord_kn_candra = candra_rulers[kn_house]

        # Check if the same pair of planets rules Kendra/Koṇa in both frameworks
        pair_lagna = {lord_k_lagna, lord_kn_lagna}
        pair_candra = {lord_k_candra, lord_kn_candra}

        if len(pair_lagna) == 2 and pair_lagna == pair_candra:
            p1, p2 = list(pair_lagna)
            # Check if they are connected (conjunct in same sign)
            sign1 = get_sign_of_planet(chart, p1)
            sign2 = get_sign_of_planet(chart, p2)

            if sign1 and sign2 and sign1 == sign2:
                detected.append(YogaInstance(
                    id=f"ubhayalagna_raja_yoga_{p1.lower()}_{p2.lower()}",
                    name=f"Ubhayalagna Raja Yoga ({p1} + {p2})",
                    category=YogaCategory.CONTEXTUAL,
                    status=YogaStatus.PURE,
                    plausibility_score=95.0,
                    participating_planets=[p1, p2],
                    participating_houses=[get_house_of_planet(chart, p1)],
                    scripture_ref="BPHS Ch. 34 (Raja Yoga Phala) & Ch. 37",
                    archetype=f"Supreme Dual-Lagna Sovereign Synergy: {p1} and {p2} form a potent Kendra-Koṇa Raja Yoga simultaneously from both Janma Lagna and Candra Lagna.",
                    manifestation_effects=[
                        "External achievement and internal emotional fulfillment are in perfect harmonic lockstep.",
                        "What the native accomplishes in the outer world brings genuine, profound satisfaction to the soul.",
                        "Extraordinary authority, high public recognition, and unshakeable inner peace."
                    ],
                    positive_factors=[
                        f"{p1} and {p2} are conjunct in {sign1}.",
                        f"Rules Kendra/Koṇa houses simultaneously from Lagna ({lagna_sign}) and Moon ({moon_sign})."
                    ],
                    breakers=[]
                ))

    return detected


def detect_contextual_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Master orchestrator for all ~25 Contextual Setup Yogas:
    1. Sāṅkhya Yogas (Pattern of Distribution - 7 yogas)
    2. General Scope Yogas (Sun-Moon Quadrant Geometry - 3 yogas)
    3. Mahābhāgya Yoga (Supreme Fortune Synergies - Male & Female configurations)
    4. Śubha & Aśubha Solitary House Yogas (1st house occupants & flanking - 4 yogas)
    5. 3-Tier Kemadruma Yoga & Cancellation (Lunar Isolation & Rescue - 2 yogas)
    6. Solar Flanking Yogas (Veśi, Vośi, Ubhayācarī - 6 variations)
    7. Dual-Lagna Raja Yoga (Ubhayalagna Synchrony - 1 yoga)
    """
    all_contextual: List[YogaInstance] = []

    # 1. Sāṅkhya Yogas
    all_contextual.extend(detect_sankhya_yogas(chart))

    # 2. General Scope Yogas
    all_contextual.extend(detect_general_scope_yogas(chart))

    # 3. Mahābhāgya Yoga
    all_contextual.extend(detect_mahabhagya_yogas(chart))

    # 4. Solitary 1st House & Kartari
    all_contextual.extend(detect_solitary_first_house_yogas(chart))

    # 5. Kemadruma & Bhaṅga
    all_contextual.extend(detect_kemadruma_yoga(chart))

    # 6. Solar Flanking Yogas
    all_contextual.extend(detect_solar_flanking_yogas(chart))

    # 7. Dual-Lagna Raja Yoga
    all_contextual.extend(detect_dual_lagna_raja_yogas(chart))

    return all_contextual
