"""
jyotish/baseline_tables.py
Static Reference Catalogs & Sanskrit Tables for Astra Stage 1.

Contains immutable constants, planetary listings, zodiac/nakshatra sequences,
combustion boundaries, D60 Shastiamsa deities, and Chandra Kriyādi classifications.
"""

from typing import List, Tuple, Dict, Set, Any

PLANETS_ORDER: List[str] = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
ALL_BODIES: List[str] = PLANETS_ORDER + ["Lagna", "MC"]
TARA_GRAHAS: List[str] = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

ZODIAC_SIGNS: List[str] = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_LORDS: Dict[str, str] = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

NAKSHATRAS: List[str] = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

NITYA_YOGAS: List[str] = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Sobhana", "Atiganda",
    "Sukarma", "Dhriti", "Sula", "Ganda", "Vriddhi", "Dhruva",
    "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan",
    "Parigha", "Siva", "Siddha", "Sadhya", "Subha", "Sukla",
    "Brahma", "Indra", "Vaidhriti"
]

VIMSHOTTARI_SEQUENCE: List[str] = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
VIMSHOTTARI_YEARS: Dict[str, int] = {'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7, 'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17}

PLANET_ABBREVIATIONS: Dict[str, str] = {
    "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
    "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke",
    "Lagna": "Lg", "MC": "MC"
}

COMBUSTION_ORBS: Dict[str, float] = {
    "Moon": 12.0,
    "Mars": 17.0,
    "Jupiter": 11.0,
    "Saturn": 15.0,
    "Venus": 10.0,       # 8.0° if retrograde
    "Mercury": 14.0      # 12.0° if retrograde
}

VARGAS_LIST: List[str] = [
    "D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12",
    "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"
]

# Fixed Natural Friendships (Naisargika Sambandha) based on Moolatrikona rules per BPHS Ch. 15
NAISARGIKA_SAMBANDHA: Dict[str, Dict[str, List[str]]] = {
    "Sun": {"Friends": ["Moon", "Mars", "Jupiter"], "Neutrals": ["Mercury"], "Enemies": ["Venus", "Saturn"]},
    "Moon": {"Friends": ["Sun", "Mercury"], "Neutrals": ["Mars", "Jupiter", "Venus", "Saturn"], "Enemies": []},
    "Mars": {"Friends": ["Sun", "Moon", "Jupiter"], "Neutrals": ["Venus", "Saturn"], "Enemies": ["Mercury"]},
    "Mercury": {"Friends": ["Sun", "Venus"], "Neutrals": ["Mars", "Jupiter", "Saturn"], "Enemies": ["Moon"]},
    "Jupiter": {"Friends": ["Sun", "Moon", "Mars"], "Neutrals": ["Saturn"], "Enemies": ["Mercury", "Venus"]},
    "Venus": {"Friends": ["Mercury", "Saturn"], "Neutrals": ["Mars", "Jupiter"], "Enemies": ["Sun", "Moon"]},
    "Saturn": {"Friends": ["Mercury", "Venus"], "Neutrals": ["Jupiter"], "Enemies": ["Sun", "Moon", "Mars"]}
}

# Specific fixed dignities (Exaltation, Moolatrikona, Own Sign)
FIXED_DIGNITIES: Dict[str, Dict[str, Any]] = {
    "Sun": {"Exalted": "Aries", "Debilitated": "Libra", "Moolatrikona": "Leo", "Own": ["Leo"]},
    "Moon": {"Exalted": "Taurus", "Debilitated": "Scorpio", "Moolatrikona": "Taurus", "Own": ["Cancer"]},
    "Mars": {"Exalted": "Capricorn", "Debilitated": "Cancer", "Moolatrikona": "Aries", "Own": ["Aries", "Scorpio"]},
    "Mercury": {"Exalted": "Virgo", "Debilitated": "Pisces", "Moolatrikona": "Virgo", "Own": ["Gemini", "Virgo"]},
    "Jupiter": {"Exalted": "Cancer", "Debilitated": "Capricorn", "Moolatrikona": "Sagittarius", "Own": ["Sagittarius", "Pisces"]},
    "Venus": {"Exalted": "Pisces", "Debilitated": "Virgo", "Moolatrikona": "Libra", "Own": ["Taurus", "Libra"]},
    "Saturn": {"Exalted": "Libra", "Debilitated": "Aries", "Moolatrikona": "Aquarius", "Own": ["Capricorn", "Aquarius"]},
    # Kala standard rules for Nodes
    "Rahu": {"Exalted": "Taurus", "Debilitated": "Scorpio", "Moolatrikona": "Gemini", "Own": ["Aquarius"]},
    "Ketu": {"Exalted": "Scorpio", "Debilitated": "Taurus", "Moolatrikona": "Sagittarius", "Own": ["Scorpio"]}
}

EXALTATION_SIGNS: Dict[str, str] = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
    "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra"
}

DEBILITATION_SIGNS: Dict[str, str] = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
    "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries"
}

NATURAL_BENEFICS: Set[str] = {"Jupiter", "Venus", "Moon", "Mercury"}
NATURAL_MALEFICS: Set[str] = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}

UPACAYA_HOUSES: Set[int] = {3, 6, 10, 11}
KENDRA_HOUSES: Set[int] = {1, 4, 7, 10}
TRIKONA_HOUSES: Set[int] = {1, 5, 9}
DUHSTHANA_HOUSES: Set[int] = {6, 8, 12}

# 60 Shastiamsa (D60) Deities per BPHS Ch. 6 / Phaladeepika Ch. 3
SHASTIAMSA_DEITIES: List[str] = [
    "Ghora", "Rakshasa", "Deva", "Kubera", "Yaksha", "Kinnara", "Bhrashta", "Kulaghna",
    "Garala", "Vahni", "Maya", "Purishaka", "Apampati", "Marutvan", "Kala", "Sarpa",
    "Amrita", "Indu", "Mridu", "Komala", "Heramba", "Brahma", "Vishnu", "Maheshwara",
    "Deva", "Ardra", "Kalinasa", "Kshiteeswara", "Kamalakara", "Gulika", "Mrityu", "Kala",
    "Davagni", "Ghora", "Yama", "Kantaka", "Suda", "Amrita", "Poornachandra", "Vishadagdha",
    "Kulanasa", "Vamshakshaya", "Utpata", "Kala", "Saumya", "Komalata", "Sheetala", "Karaladamshtra",
    "Candramukhi", "Praveena", "Kalapavaka", "Dandayudha", "Nirmala", "Subhada", "Kroora", "Atisheeta",
    "Amrita", "Payodhi", "Bhramana", "Chandrarekha"
]

# 24 Malefic Shastiamsa indices in odd signs (1-indexed per classical texts)
SHASTIAMSA_MALEFIC_ODD: Set[int] = {
    1, 2, 8, 9, 10, 11, 12, 15, 16, 30, 31, 32, 33, 34, 35, 39, 40, 42, 43, 44, 48, 51, 52, 59
}

# =============================================================================
# CANDRA KRIYĀDI: 60 KRIYĀS, 12 AVASTHĀS, 36 VELĀS (Phaladeepika Ch. 4.12–20)
# Format: (Number, Sanskrit Name, English Translation, IsBenefic)
# =============================================================================
CHANDRA_KRIYAS_DATA: List[Tuple[int, str, str, bool]] = [
    (1, "Sthanadbhrashta", "Fallen from position / displaced", False),
    (2, "Tapasvi", "Penance / ascetic contemplation", True),
    (3, "Parayuvatirata", "Lust for another's partner", False),
    (4, "Dyutakrit", "Addicted to gambling", False),
    (5, "Hastimukhyarudha", "Mounted on a royal elephant", True),
    (6, "Simhasanastha", "Seated on a sovereign throne", True),
    (7, "Narapati", "Sovereign king / ruler of men", True),
    (8, "Ariha", "Destroyer of enemies", True),
    (9, "Dandaneta", "Army commander / administrator", True),
    (10, "Guni", "Endowed with high virtues", True),
    (11, "Nishprana", "Lifeless / devoid of energy", False),
    (12, "Chinnamurdha", "Severed head / extreme danger", False),
    (13, "Kshatakaracharana", "Injured hands and feet", False),
    (14, "Bandhanastha", "Imprisoned / confined in bonds", False),
    (15, "Vinashta", "Ruined / annihilated", False),
    (16, "Raja", "Regal authority / king", True),
    (17, "Vedanadhite", "Engaged in sacred scriptural study", True),
    (18, "Svapiti", "Slumbering / lethargic", False),
    (19, "Sucharita", "Noble and virtuous conduct", True),
    (20, "Dharmakarta", "Performer of righteous deeds", True),
    (21, "Sadvamshya", "Born of distinguished lineage", True),
    (22, "Nidhisangata", "Discoverer of treasure / wealth", True),
    (23, "Shrutakula", "Learned in shastras and noble family", True),
    (24, "Vyakhyapara", "Skilled commentator / expounder", True),
    (25, "Shatruha", "Slayer of opposing forces", True),
    (26, "Rogi", "Afflicted with bodily illness", False),
    (27, "Shatrujita", "Vanquished by adversaries", False),
    (28, "Svadeshachalita", "Forced departure from homeland", False),
    (29, "Bhritya", "Subjugated to servitude", False),
    (30, "Vinashtarthaka", "Deprived of all resources", False),
    (31, "Asthani", "Member of the royal court", True),
    (32, "Sumantraka", "Wise counselor / minister", True),
    (33, "Paramahibharta", "Lord of extensive lands", True),
    (34, "Sabharya", "United with faithful spouse", True),
    (35, "Gajatrasta", "Terror-stricken by wild elephant", False),
    (36, "Samyugabhitiman", "Panicked on the battlefield", False),
    (37, "Atibhaya", "Overwhelmed with intense dread", False),
    (38, "Lina", "Concealed / living in hiding", False),
    (39, "Annadata", "Generous benefactor of sustenance", True),
    (40, "Agniga", "Entering fire / consumed by flame", False),
    (41, "Kshudbadhasahita", "Suffering pangs of starvation", False),
    (42, "Annamatti", "Enjoying nourishing feast", True),
    (43, "Vicharan", "Restlessly wandering aimlessly", False),
    (44, "Mamsashana", "Consuming flesh / coarse living", False),
    (45, "Astrakshata", "Wounded by cutting weapons", False),
    (46, "Sodvaha", "Celebration of matrimonial union", True),
    (47, "Dhritakanduka", "Joyfully playing with ball / sport", True),
    (48, "Dyutavihari", "Distracted by games of chance", False),
    (49, "Nripa", "Monarch / royal sovereign", True),
    (50, "Duhkhita", "Overcome by melancholy and grief", False),
    (51, "Shayastha", "Bedridden with prolonged debility", False),
    (52, "Ripusevita", "Honored and attended by former foes", True),
    (53, "Sasuhrit", "Surrounded by devoted companions", True),
    (54, "Yogi", "Accomplished yogic practitioner", True),
    (55, "Bharyanvita", "Blessed with harmonious spouse", True),
    (56, "Mishtahi", "Savoring delicate confections", True),
    (57, "Payah Piban", "Drinking sanctified milk / nourished", True),
    (58, "Sukritakrit", "Author of meritorious deeds", True),
    (59, "Svastha", "Established in inner health and self", True),
    (60, "Sukham Aste", "Abiding in supreme bliss and ease", True)
]

CHANDRA_AVASTHAS_DATA: List[Tuple[int, str, str, bool]] = [
    (1, "Pravasa", "Exile / absence from home", False),
    (2, "Mahitanripahita", "Favored by honored sovereign", True),
    (3, "Dasata", "Bondage / servitude", False),
    (4, "Pranahani", "Loss of vitality / mortal danger", False),
    (5, "Bhupalatva", "Attainment of regal status", True),
    (6, "Svavamshochitaguna", "Virtues reflecting noble lineage", True),
    (7, "Roga", "Affliction with disease", False),
    (8, "Asthanavattvam", "Presiding in royal assembly", True),
    (9, "Bhiti", "State of fear and anxiety", False),
    (10, "Kshudbadhitatva", "Tormented by hunger", False),
    (11, "Yuvatiparinaya", "Union with young maiden / joy", True),
    (12, "Mishtashitva", "Partaking in delicious feast", True)
]

CHANDRA_VELAS_DATA: List[Tuple[int, str, str, bool]] = [
    (1, "Murdhamaya", "Headache / cranial disorder", False),
    (2, "Muditata", "Cheerfulness / delight", True),
    (3, "Yajanam", "Sacred ritual / sacrifice", True),
    (4, "Sukhastha", "Firmly rooted in comfort", True),
    (5, "Netramaya", "Ophthalmic disorder / eye pain", False),
    (6, "Sukhidata", "Giver / receiver of happiness", True),
    (7, "Vanitavihara", "Pleasure excursions with partner", True),
    (8, "Ugrajvara", "Burning virulent fever", False),
    (9, "Kanakabhushanam", "Adorned with gold ornaments", True),
    (10, "Ashrumoksha", "Shedding sorrowful tears", False),
    (11, "Kshvelanam", "Ingestion of poison / venom", False),
    (12, "Nidhuvana", "Amorous intimacy / love-making", True),
    (13, "Jatharasya Roga", "Severe gastrointestinal disease", False),
    (14, "Krida Jale", "Delightful sport in water", True),
    (15, "Hasana", "Mirthful laughter and gaiety", True),
    (16, "Chitravilekhana", "Painting and fine artistic creation", True),
    (17, "Kroda", "Seething fury / wrath", False),
    (18, "Nrittakarana", "Graceful performance of dance", True),
    (19, "Ghritabhukti", "Consuming food enriched with ghee", True),
    (20, "Nidra", "Restful / rejuvenating sleep", True),
    (21, "Danakriya", "Noble acts of spiritual charity", True),
    (22, "Dashanaruk", "Acute dental affliction", False),
    (23, "Kalaha", "Quarrel and domestic discord", False),
    (24, "Prayana", "Embarking on travel / departure", True),
    (25, "Unmattata", "Frenzy / mental derangement", False),
    (26, "Salilaplavana", "Submersion / peril from water", False),
    (27, "Virodha", "Bitter opposition and enmity", False),
    (28, "Svochhasnana", "Purifying bath at will", True),
    (29, "Kshudbhayam", "Apprehension of famine / hunger", False),
    (30, "Shastralabha", "Acquiring weapons / noble disciplines", True),
    (31, "Svaira Goshthi", "Unhindered philosophical conclave", True),
    (32, "Yodhana", "Violent conflict in battle", False),
    (33, "Punyakarma", "Undertaking holy enterprises", True),
    (34, "Papachara", "Adhering to sinful practices", False),
    (35, "Krurakarma", "Perpetration of ruthless deeds", False),
    (36, "Praharsha", "Exultation and supreme rejoicing", True)
]
