"""
jyotish/yogas/bhava_yogas.py
The 24 Bhava Yogas — 12 Auspicious (Śubha) and 12 Converse (Aśubha) House Yogas.
Scripture: Phaladeepika Ch. 6, Verses 44–70.
"""

from typing import List, Dict, Any
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_house_rulers, get_planets_data,
    get_lagna_sign, get_aspect_score, _first_ruler,
    audit_combustion, audit_shadbala_muscle, audit_neecha_bhanga,
    resolve_yoga_score_and_status,
    OWN_SIGNS, EXALTATION_SIGNS, DEBILITATION_SIGNS,
    ASPECT_PALPABLE_THRESHOLD
)

KENDRA_TRIKONA_HOUSES = (1, 4, 5, 7, 9, 10)
TRIKONA_HOUSES = (1, 5, 9)
DUSTHANA_HOUSES = (6, 8, 12)
BENEFICS = ("Jupiter", "Venus", "Mercury")
MALEFICS = ("Saturn", "Mars", "Rahu", "Ketu", "Sun")

# The 24 Bhava definitions from Phaladeepika 6.44-70
# Note on Houses 6, 8, 12 Inversion Paradox (Phaladeepika 6.50, 6.52, 6.56 vs 6.63, 6.65, 6.69):
# - For Houses 1-5, 7, 9-11: Lord in Kendra/Trikona is Auspicious; Lord in Dusthana (6,8,12) is Converse (STAINED/RESCUED).
# - For Houses 8 & 12: Lord in Kendra/Trikona forms Asura (6.52) / Musala (6.56) (Converse/Challenging — STAINED/RESCUED, never PURE!),
#   whereas Lord in Dusthana (6,8,12) forms Sarala (6.65) / Vimala (6.69) (Auspicious Reversal — deduplicated with viparita.py).
BHAVA_YOGA_CONFIGS = {
    1: {
        "good": {
            "id": "camara_yoga",
            "name": "Cāmara Yoga (Royal Fly-Whisk)",
            "archetype": "Personal Eminence: 1st House Lord fortified in Kendra/Trikoṇa in dignity, conferring royal stature and vitality.",
            "effects": ["Commands high social stature, magnificent health, long life, and spotless personal integrity."]
        },
        "bad": {
            "id": "ava_yoga",
            "name": "Ava Yoga (Obscurity)",
            "archetype": "Physical Frailty & Obscurity: 1st House Lord trapped in a Dusthana, requiring continuous effort to gain recognition.",
            "effects": ["Feelings of being unappreciated or overlooked; occasional health vulnerabilities requiring active discipline."]
        }
    },
    2: {
        "good": {
            "id": "dhenu_yoga",
            "name": "Dhenu Yoga (The Milch Cow)",
            "archetype": "Abundant Nourishment: 2nd House Lord fortified in dignity in Kendra/Trikoṇa, yielding sweet speech and continuous wealth.",
            "effects": ["Abundant financial assets, eloquent speech, high education, and joyful family life."]
        },
        "bad": {
            "id": "nihsva_yoga",
            "name": "Niḥsva Yoga (Depleted Treasury)",
            "archetype": "Depleted Treasury: 2nd House Lord trapped in a Dusthana, creating financial fluctuations and harsh speech.",
            "effects": ["Financial instability, unexpected domestic expenditures, or challenges in accumulating liquid wealth."]
        }
    },
    3: {
        "good": {
            "id": "shaurya_yoga",
            "name": "Śaurya Yoga (The Hero)",
            "archetype": "Valorous Initiative: 3rd House Lord fortified in Kendra/Trikoṇa, granting brave leadership and supportive siblings.",
            "effects": ["Supreme courage, decisive manual skill, loyal younger siblings, and success in athletic or entrepreneurial ventures."]
        },
        "bad": {
            "id": "mrti_yoga",
            "name": "Mṛti Yoga (Broken Initiatives)",
            "archetype": "Faltering Courage: 3rd House Lord trapped in a Dusthana, leading to sibling friction and hesitated actions.",
            "effects": ["Hesitation in executing initiatives, lack of sibling harmony, or unrewarded physical labor."]
        }
    },
    4: {
        "good": {
            "id": "jaladhi_yoga",
            "name": "Jaladhi Yoga (The Ocean Estate)",
            "archetype": "Vast Domestic Peace: 4th House Lord fortified in Kendra/Trikoṇa, granting palatial estates, vehicles, and maternal joy.",
            "effects": ["Commands fine properties, luxury vehicles, profound emotional contentment, and deep filial affection."]
        },
        "bad": {
            "id": "kuhu_yoga",
            "name": "Kuhu Yoga (The Dark Moon Home)",
            "archetype": "Emotional Solitude: 4th House Lord trapped in a Dusthana, producing domestic disruption and vehicle troubles.",
            "effects": ["Restless home life, challenges with mother or ancestral estates, and frequent domestic relocations."]
        }
    },
    5: {
        "good": {
            "id": "chatra_yoga",
            "name": "Chatra Yoga (The Royal Canopy)",
            "archetype": "Sovereign Intellect: 5th House Lord fortified in Kendra/Trikoṇa, granting brilliant scholarship and noble progeny.",
            "effects": ["Brilliant creative intellect, profound advisory wisdom, loving children, and royal favor."]
        },
        "bad": {
            "id": "pamara_yoga",
            "name": "Pāmara Yoga (The Indiscriminate)",
            "archetype": "Dissipated Discernment: 5th House Lord trapped in a Dusthana, obscuring intellectual discrimination.",
            "effects": ["Challenges in educational pursuits, misunderstandings with children, or restless mental focus."]
        }
    },
    6: {
        "good": {
            "id": "astra_yoga",
            "name": "Astra Yoga (The Weapon)",
            "archetype": "Overcoming Adversaries: 6th House Lord fortified in an Upachaya/Kendra, providing a decisive weapon against rivals.",
            "effects": ["Subdues legal opponents, masters debt management, and displays athletic or surgical resilience."]
        }
    },
    7: {
        "good": {
            "id": "kama_yoga",
            "name": "Kāma Yoga (The Beloved)",
            "archetype": "Harmonious Alliance: 7th House Lord fortified in Kendra/Trikoṇa, bestowing a devoted, virtuous spouse.",
            "effects": ["Joyous marital partnership, virtuous and beautiful companion, and thriving commercial alliances."]
        },
        "bad": {
            "id": "shatru_yoga",
            "name": "Śatru Yoga (Marital Friction)",
            "archetype": "Allied Friction: 7th House Lord trapped in a Dusthana, causing marital separation or business disputes.",
            "effects": ["Strained marital communication, unexpected legal or commercial disputes with partners."]
        }
    },
    8: {
        "converse_kendra": {
            "id": "asura_yoga",
            "name": "Asura Yoga (The Titanic Ambition)",
            "archetype": "Fierce Volatile Ambition (Converse 8th Bhava Yoga): 8th House Lord occupies a Kendra/Trikoṇa, injecting crisis-driven intensity and volatile ambition into central life pillars.",
            "effects": ["Intense competitive drive, volatile transformations, and friction when pursuing unilateral agendas (Phaladeepika 6.52)."]
        }
    },
    9: {
        "good": {
            "id": "bhagya_yoga",
            "name": "Bhāgya Yoga (Divine Grace)",
            "archetype": "The Fortunate Heir: 9th House Lord fortified in Kendra/Trikoṇa, bestowing righteous paternal legacy and spiritual luck.",
            "effects": ["Effortless good fortune, deep philosophical piety, righteous mentorship, and philanthropic renown."]
        },
        "bad": {
            "id": "nirbhagya_yoga",
            "name": "Nirbhāgya Yoga (Lost Heritage)",
            "archetype": "Estranged Legacy: 9th House Lord trapped in a Dusthana, creating distance from paternal heritage.",
            "effects": ["Skepticism toward orthodox beliefs, distance from paternal legacy, and having to forge luck through self-reliance."]
        }
    },
    10: {
        "good": {
            "id": "khyati_yoga",
            "name": "Khyāti Yoga (World Renown)",
            "archetype": "Eminent Vocation: 10th House Lord fortified in Kendra/Trikoṇa, bestowing celebrated civic accomplishment.",
            "effects": ["Praised by state and corporate heads; lasting civic impact, spotless leadership, and career eminence."]
        },
        "bad": {
            "id": "duskriti_yoga",
            "name": "Duṣkṛti Yoga (Disgraced Vocation)",
            "archetype": "Frustrated Career: 10th House Lord trapped in a Dusthana, causing vocational setbacks and unappreciated work.",
            "effects": ["Career volatility, bureaucratic obstacles, and feeling trapped in unfulfilling professional obligations."]
        }
    },
    11: {
        "good": {
            "id": "parijata_yoga",
            "name": "Pārijāta Yoga (The Wish-Fulfilling Tree)",
            "archetype": "Continuous Inflow: 11th House Lord fortified in Kendra/Trikoṇa, fulfilling desires through vast social networks.",
            "effects": ["Inexhaustible sources of income, supportive elder siblings, influential friends, and effortless fulfillment of hopes."]
        },
        "bad": {
            "id": "daridra_h11_yoga",
            "name": "Daridra Yoga (11th House Stagnation)",
            "archetype": "Stagnant Inflow: 11th House Lord trapped in a Dusthana, delaying financial returns on social and commercial labor.",
            "effects": ["Delays in monetization, unsupportive social circles, and intermittent financial bottlenecks."]
        }
    },
    12: {
        "converse_kendra": {
            "id": "musala_yoga",
            "name": "Musala Yoga (Converse 12th Bhava Dissipation)",
            "archetype": "Worldly Detachment & Hard-Won Wealth (Converse 12th Bhava Yoga): 12th House Lord occupies a Kendra/Trikoṇa, introducing expenditure pressure and material restlessness.",
            "effects": ["Wealth acquired through heavy effort, high overhead expenses, and periodic detachment from worldly routines (Phaladeepika 6.56)."]
        }
    }
}


def detect_bhava_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Scans chart for the Bhava Auspicious (Śubha) and Converse (Aśubha) Yogas."""
    detected: List[YogaInstance] = []
    lagna_sign = get_lagna_sign(chart)
    planets_data = get_planets_data(chart)
    house_rulers = get_house_rulers(chart)

    if not lagna_sign or not planets_data:
        return detected

    planet_houses = {p: get_house_of_planet(chart, p) for p in planets_data}
    trikona_lords = {
        _first_ruler(house_rulers, th)
        for th in TRIKONA_HOUSES
        if _first_ruler(house_rulers, th)
    }

    for h_num in range(1, 13):
        lord = _first_ruler(house_rulers, h_num)
        if not lord or lord not in planets_data:
            continue

        lord_h = planet_houses.get(lord, 0)
        if lord_h <= 0:
            continue

        lord_sign = get_sign_of_planet(chart, lord)
        is_exalted = (lord_sign == EXALTATION_SIGNS.get(lord))
        is_own = (lord_sign in OWN_SIGNS.get(lord, []))
        is_debilitated = (lord_sign == DEBILITATION_SIGNS.get(lord))
        is_in_kt = lord_h in KENDRA_TRIKONA_HOUSES
        houses_involved = [h_num] if h_num == lord_h else [h_num, lord_h]

        config = BHAVA_YOGA_CONFIGS.get(h_num, {})

        # 1. Evaluate Auspicious (Śubha) Bhava Yoga (Houses 1-7, 9-11)
        good_cfg = config.get("good")
        if good_cfg:
            if (is_exalted or is_own or is_in_kt) and not is_debilitated and lord_h not in DUSTHANA_HOUSES:
                base_score = 82.0
                if is_exalted or is_own:
                    base_score += 8.0

                breakers: List[YogaBreakerDetail] = []
                breakers.extend(audit_combustion([lord], chart))
                sb_breakers, sb_positives = audit_shadbala_muscle([lord], chart)
                breakers.extend(sb_breakers)

                # For H6 (Astra Yoga), require own/exalted dignity or Trikona co-rulership for PURE
                if h_num == 6 and not (is_exalted or is_own or lord in trikona_lords):
                    breakers.append(YogaBreakerDetail(
                        factor="6th House Martial Friction",
                        culprit_planet=lord,
                        description=f"6th Lord ({lord}) in Kendra/Trikona without own/exalted dignity brings competitive struggle alongside resilience.",
                        penalty=15.0
                    ))

                score, status = resolve_yoga_score_and_status(base_score, breakers)
                score = max(30.0, score)

                detected.append(YogaInstance(
                    id=good_cfg["id"],
                    name=good_cfg["name"],
                    category=YogaCategory.BHAVA,
                    status=status,
                    plausibility_score=round(score, 1),
                    participating_planets=[lord],
                    participating_houses=houses_involved,
                    scripture_ref=f"Phaladeepika 6.{43 + h_num}",
                    archetype=good_cfg["archetype"],
                    manifestation_effects=good_cfg["effects"],
                    positive_factors=[
                        f"Lord of H{h_num} ({lord}) occupies {'exalted' if is_exalted else 'own sign' if is_own else 'supportive Kendra/Trikoṇa'} House {lord_h} ({lord_sign})."
                    ] + sb_positives,
                    breakers=breakers
                ))

        # 2. Evaluate Converse 8th & 12th Kendra/Trikona Yogas: Asura (6.52) & Musala (6.56)
        # Affliction Status Invariant: Asura & Musala are Converse Bhava Yogas (STAINED or RESCUED, never PURE!)
        converse_kendra_cfg = config.get("converse_kendra")
        if converse_kendra_cfg and h_num in (8, 12):
            if (is_exalted or is_own or is_in_kt) and lord_h not in DUSTHANA_HOUSES:
                is_mitigated = (is_exalted or is_own or lord in trikona_lords)
                positive_factors: List[str] = []
                breakers = [
                    YogaBreakerDetail(
                        factor=f"Dusthana H{h_num} Leakage into Kendra/Trikoṇa",
                        culprit_planet=lord,
                        description=f"Lord of Dusthana H{h_num} ({lord}) occupies House {lord_h} ({lord_sign}), injecting H{h_num} volatility or expenditure into angular/trinal pillars.",
                        penalty=15.0 if is_mitigated else 25.0
                    )
                ]
                if is_mitigated:
                    status = YogaStatus.RESCUED
                    score = 72.0
                    positive_factors.append(
                        f"Mitigated (Bhaṅga): {lord} is fortified by {'exaltation' if is_exalted else 'own sign' if is_own else 'Trikoṇa co-rulership'}, channeling H{h_num} intensity constructively."
                    )
                else:
                    status = YogaStatus.STAINED
                    score = 65.0

                detected.append(YogaInstance(
                    id=converse_kendra_cfg["id"],
                    name=converse_kendra_cfg["name"],
                    category=YogaCategory.BHAVA,
                    status=status,
                    plausibility_score=round(score, 1),
                    participating_planets=[lord],
                    participating_houses=houses_involved,
                    scripture_ref=f"Phaladeepika 6.{44 + h_num}",
                    archetype=converse_kendra_cfg["archetype"],
                    manifestation_effects=converse_kendra_cfg["effects"],
                    positive_factors=positive_factors,
                    breakers=breakers
                ))

        # 3. Evaluate Converse (Aśubha) Dusthana Bhava Yogas (for houses 1-5, 7, 9-11)
        # Condition: Lord of house sits in a Dusthana (6, 8, 12)
        bad_cfg = config.get("bad")
        if bad_cfg and h_num not in (6, 8, 12):
            if lord_h in DUSTHANA_HOUSES:
                benefic_aspects = [
                    bp for bp in BENEFICS
                    if bp != lord and get_aspect_score(chart, bp, lord) >= ASPECT_PALPABLE_THRESHOLD
                ]
                is_nb_rescued = False
                if is_debilitated:
                    is_nb_rescued, _, _ = audit_neecha_bhanga(lord, chart)

                is_mitigated = bool(is_exalted or is_own or is_nb_rescued or benefic_aspects)
                positive_factors = []
                if is_exalted or is_own:
                    positive_factors.append(
                        f"Mitigated (Bhaṅga): {lord} occupies {'exalted' if is_exalted else 'own'} sign ({lord_sign}) in House {lord_h}."
                    )
                if is_nb_rescued:
                    positive_factors.append(
                        f"Mitigated (Nīcabhaṅga): {lord}'s debilitation in House {lord_h} is cancelled."
                    )
                if benefic_aspects:
                    positive_factors.append(
                        f"Mitigated (Śubha Dṛṣṭi): {lord} receives palpable benefic aspect from {', '.join(benefic_aspects)}."
                    )

                score = 55.0 if is_mitigated else 65.0
                status = YogaStatus.RESCUED if is_mitigated else YogaStatus.STAINED

                breakers = [
                    YogaBreakerDetail(
                        factor="Dusthana Placement",
                        culprit_planet=lord,
                        description=f"Lord of H{h_num} ({lord}) sits in Dusthana House {lord_h}, creating friction and delays.",
                        penalty=15.0 if is_mitigated else 25.0
                    )
                ]
                detected.append(YogaInstance(
                    id=bad_cfg["id"],
                    name=bad_cfg["name"],
                    category=YogaCategory.BHAVA,
                    status=status,
                    plausibility_score=round(score, 1),
                    participating_planets=[lord],
                    participating_houses=houses_involved,
                    scripture_ref=f"Phaladeepika 6.{57 + h_num}",
                    archetype=bad_cfg["archetype"],
                    manifestation_effects=bad_cfg["effects"],
                    positive_factors=positive_factors,
                    breakers=breakers
                ))

    return detected
