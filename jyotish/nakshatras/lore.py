"""
Astra Nakshatra Lore & Classification Interface
Loads the comprehensive 27-Nakshatra database and provides normalized lookups
for classical groups, devatas, symbols, and psychological profiles.
"""

import os
import json
from typing import Dict, Any, Optional

try:
    from jyotish.nakshatras.nakshatra_data import NAKSHATRA_DATABASE
except ImportError:
    _CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    _DB_PATH = os.path.join(_CURRENT_DIR, "nakshatra_database.json")
    with open(_DB_PATH, "r", encoding="utf-8") as f:
        NAKSHATRA_DATABASE: Dict[str, Dict[str, Any]] = json.load(f)

# Normalized alias map for robust lookup
_ALIAS_MAP: Dict[str, str] = {}
for canonical_key, data in NAKSHATRA_DATABASE.items():
    _ALIAS_MAP[canonical_key.lower()] = canonical_key
    for alias in data.get("aliases", []):
        _ALIAS_MAP[alias.lower()] = canonical_key

NAKSHATRA_GROUP_METADATA: Dict[str, Dict[str, str]] = {
    "Tikshna": {
        "sanskrit": "Tīkṣṇa / Dāruṇa",
        "label": "Bitter, Sharp & Dreadful",
        "nature": "Cathartic disruption, penetrating strategy, relentless truth-seeking",
        "color": "#991b1b",
        "bg": "#fef2f2"
    },
    "Ugra": {
        "sanskrit": "Ugra / Krūra",
        "label": "Fierce, Severe & Strong",
        "nature": "Formidable ambition, boundary defense, rigorous discipline",
        "color": "#c2410c",
        "bg": "#fff7ed"
    },
    "Dhruva": {
        "sanskrit": "Dhruva / Sthira",
        "label": "Fixed, Permanent & Enduring",
        "nature": "Lasting foundations, institutional legacy, patient stability",
        "color": "#15803d",
        "bg": "#f0fdf4"
    },
    "Mridu": {
        "sanskrit": "Mṛdu",
        "label": "Soft, Mild & Tender",
        "nature": "Aesthetic refinement, cooperative harmony, deep empathy",
        "color": "#0d9488",
        "bg": "#f0fdfa"
    },
    "Laghu": {
        "sanskrit": "Kṣipra / Laghu",
        "label": "Light, Swift & Quick",
        "nature": "Agility, rapid healing, technical dexterity, effortless realization",
        "color": "#2563eb",
        "bg": "#eff6ff"
    },
    "Chara": {
        "sanskrit": "Cara / Cala",
        "label": "Movable, Dynamic & Mobile",
        "nature": "Locomotion, rhythm, trade, independent individuation",
        "color": "#7c3aed",
        "bg": "#f5f3ff"
    },
    "Mishra": {
        "sanskrit": "Miśra / Sādhāraṇa",
        "label": "Mixed (Sharp & Soft)",
        "nature": "Universal catalysis, one-pointed focus coupled with devotion",
        "color": "#b45309",
        "bg": "#fffbeb"
    }
}

NAKSHATRA_TEMPERAMENT_DOSSIER: Dict[str, Dict[str, Any]] = {
    "Dhruva": {
        "label": "Enduring",
        "sanskrit": "Dhruva / Sthira",
        "nakshatras": ["Rohini", "Uttara Phalguni", "Uttara Ashadha", "Uttara Bhadrapada"],
        "essence": "Permanence, lasting legacy, generational security, calm gravitas, consolidation of victory.",
        "macro_psychology": "Refuses to build on shifting sands. Dhruva asterisms represent the consolidation, protection, and harvesting of long-term ventures. Where initial action stars charge forward into battle, Dhruva stars build the fortress, legislate the treaties, and preserve generational continuity.",
        "thermodynamics": {
            "surplus": "Unshakable perseverance and stamina; but risks stubborn dogmatism, cold aloofness, fear of spontaneity, and staying in decayed structures long after they should have been dismantled.",
            "balanced": "Steady, reliable endurance. Builds enduring value while maintaining sufficient flexibility to navigate life transitions peacefully.",
            "deficit": "Inability to sustain long-term momentum; brilliant starts that get abandoned midway; chronic impatience with slow growth cycles; difficulty creating lasting institutions."
        },
        "positives": [
            "Builds enduring monuments, institutions, and relationships that withstand time",
            "Rock-solid emotional stability; imperturbable to external praise or blame",
            "Profound intellectual gravitas, meditative depth, and executive patience",
            "Consolidation of victory; making peace with rivals to sustain long-term prosperity"
        ],
        "negatives": [
            "Stubborn conservatism and severe resistance to necessary change or evolution",
            "Cold dismissal of transient human needs or mundane emotional expressions",
            "Aloof withdrawal, melancholic depression, or neglecting immediate duties",
            "Smug complacency and moral entitlement within comfortable routines"
        ],
        "stars_detail": {
            "Rohini": {
                "title": "The Fertile Manifestor & Artistic Ascendant",
                "span": "10° 00' – 23° 20' Taurus",
                "deity_symbol": "Brahmā (Creator) | Ox-drawn cart overflowing with produce",
                "positives": [
                    "Extraordinary ability to materialize ideas into lush physical and artistic reality",
                    "Smooth climbing power that eludes obstacles gracefully rather than through conflict",
                    "Warm charisma, sweet speech, and generous maternal nurturance",
                    "Deep dedication to creating beauty, wealth, and family legacies that endure"
                ],
                "negatives": [
                    "Possessive attachment and treating romantic partners or status as personal property",
                    "Hyper-critical fault-finding driven by an obsessive eye for imperfection",
                    "Complacent indulgence in sensory luxury, laziness, and vanity",
                    "Emotional manipulation using tears or guilt to bind others"
                ]
            },
            "Uttara Phalguni": {
                "title": "The Honorable Ally & Institutional Patron",
                "span": "26° 40' Leo – 10° 00' Virgo",
                "deity_symbol": "Aryaman (Chivalry & Patronage) | Back legs of a bed / formal cot",
                "positives": [
                    "Uncompromising integrity in honoring vows, covenants, and formal contracts",
                    "Noble patronage; uses wealth, prestige, and learning to uplift dependents",
                    "Transforms passionate romantic spark into permanent, prosperous marriage",
                    "Diplomatic skill in creating peaceful, lawful community alliances"
                ],
                "negatives": [
                    "Elitist snobbery and evaluating others strictly through superficial etiquette",
                    "Fear of social disruption; staying trapped in decayed partnerships to avoid scandal",
                    "Moral hypocrisy; demanding absolute loyalty while excusing own lapses",
                    "Entitled expectation of lifelong gratitude and deference from beneficiaries"
                ]
            },
            "Uttara Ashadha": {
                "title": "The Victorious Builder & Sovereign Conciliator",
                "span": "26° 40' Sagittarius – 10° 00' Capricorn",
                "deity_symbol": "The Ten Vishvadevas (Universal Truth & Skill) | Standing Elephant Body",
                "positives": [
                    "Consolidates victory by reconciling former enemies into durable coalitions",
                    "Imperturbable poise; unruffled by superficial praise or hostile criticism",
                    "Grounded in universal, objective ethical laws that inspire wide trust",
                    "Exceptional executive stamina for managing extensive multi-year programs"
                ],
                "negatives": [
                    "Unyielding obstinacy; clinging to flawed enterprises out of sheer pride",
                    "Burden martyrdom; taking on overwhelming administrative loads alone",
                    "Disorganized proliferation; starting multiple projects and abandoning them midway",
                    "Cold emotional distance that treats intimate relationships like corporate negotiations"
                ]
            },
            "Uttara Bhadrapada": {
                "title": "The Contemplative Anchor & Master of Gravitas",
                "span": "03° 20' – 16° 40' Pisces",
                "deity_symbol": "Ahirbudhnya (Cosmic Deep Abyss) | Back legs of the funeral cot",
                "positives": [
                    "Supreme spiritual gravitas; anchored in the eternal truth that outlives destruction",
                    "Transcendent composure; absorbs personal crises and loss without shattering",
                    "Selfless, quiet philanthropy; acting as a secret protector to the vulnerable",
                    "Profound intellectual depth in esoteric philosophy, research, and mathematics"
                ],
                "negatives": [
                    "Existential gloom, melancholia, and viewing worldly life as utterly futile",
                    "Ascetic paralysis; completely neglecting physical, relational, and financial duties",
                    "Chilling inaccessibility that leaves intimate partners feeling isolated",
                    "Passive-aggressive inertia; stonewalling issues with stubborn silence"
                ]
            }
        }
    },
    "Chara": {
        "label": "Mobile",
        "sanskrit": "Cara / Cala",
        "nakshatras": ["Punarvasu", "Swati", "Shravana", "Dhanishtha", "Shatabhisha"],
        "essence": "Locomotion, rhythm, trade, information flow, dynamic adaptability, independent flight.",
        "macro_psychology": "Drives dynamic locomotion, conversational flow, commercial trade, and rhythmic adaptability. Governs the circulation of ideas, physical grace, and the capacity to shift gears quickly. Refuses stagnation, choosing cyclical renewal or independent flight over inert comfort.",
        "thermodynamics": {
            "surplus": "High environmental adaptability and rapid networking; but risks chronic restlessness, superficial novelty-seeking, difficulty with permanent roots, and abandoning stability out of fear of boredom.",
            "balanced": "Fluid adaptability, rhythmic timing, and communicative eloquence. Moves gracefully between changing domains while sustaining personal integrity and core commitments.",
            "deficit": "Rigid inertia; difficulty adjusting to changing environments or shifting travel plans; conversational stiffness and resistance to adopting fresh perspectives."
        },
        "positives": [
            "High environmental adaptability and mental agility",
            "Exceptional skill in communication, networking, and circulating ideas",
            "Natural rhythm, timing, physical coordination, and social charisma",
            "Regenerative cycles; talent for reviving exhausted enterprises"
        ],
        "negatives": [
            "Chronic restlessness and difficulty sustaining long-term routines",
            "Superficial novelty-seeking; abandoning stability out of fear of boredom",
            "Rootless isolation or counter-cultural rebellion that alienates allies",
            "Tendency toward gossip or using verbal fluency to evade accountability"
        ],
        "stars_detail": {
            "Punarvasu": {
                "title": "The Restorative Renewer & Cyclical Voyager",
                "span": "20° 00' Gemini – 03° 20' Cancer",
                "deity_symbol": "Aditi (Cosmic Mother of Boundless Space) | Quiver of returning arrows",
                "positives": [
                    "Talent for reviving exhausted resources and bringing fresh life into stagnant enterprises",
                    "Cyclical wisdom; ventures forth and returns with renewed insight and forgiving generosity",
                    "Contentment with simple needs, imaginative poetic breadth, and philosophical optimism",
                    "Natural capacity to grant second chances and rehabilitate flawed situations"
                ],
                "negatives": [
                    "Chronic restlessness and inability to tolerate stable, routine contentment",
                    "Abandoning solid achievements prematurely in search of a clean slate",
                    "Lack of tenacity for tedious administrative grinds once the initial freshness fades",
                    "Fickle convictions that waver whenever boredom threatens"
                ]
            },
            "Swati": {
                "title": "The Autonomous Pioneer & Flexible Strategist",
                "span": "06° 40' Libra – 20° 00' Libra",
                "deity_symbol": "Vāyu (Wind God of Prāṇa) | Young sprout bending in the wind / Sword",
                "positives": [
                    "Extraordinary adaptability; survives hostile circumstances by bending without breaking",
                    "Independent self-reliance; thrives outside the herd on autonomous commercial tracks",
                    "Refined diplomatic finesse and commercial acumen in negotiating mutual advantage",
                    "Quiet intellectual incubation and artistic appreciation under Saraswatī's grace"
                ],
                "negatives": [
                    "Erratic, shifting loyalties that alienate long-term friends and allies",
                    "Rootless isolation and stubborn counter-cultural defiance taken to extremes",
                    "Selfish evasion of domestic, familial, or contractual obligations",
                    "Chilling emotional detachment and manipulative commercial opportunism"
                ]
            },
            "Shravana": {
                "title": "The Discerning Listener & Strategic Strider",
                "span": "10° 00' Capricorn – 23° 20' Capricorn",
                "deity_symbol": "Viṣṇu (The Cosmic Strider & Preserver) | Three footprints / The ear",
                "positives": [
                    "Exceptional oral learning and accurate retention of sacred and technical lineages",
                    "Deliberate, strategic spatial coordination and purposeful long-range pacing",
                    "Eloquent rhetorical skill, pedagogical clarity, and high social respect",
                    "Reverent devotion to preserving authentic wisdom for future generations"
                ],
                "negatives": [
                    "Obsession with petty gossip, rumor circulation, and unverified hearsay",
                    "Using verbal dexterity and sophistry to dodge personal accountability",
                    "Hyper-sensitive pride that takes offense at innocent remarks",
                    "Manipulating audiences through half-truths and selective listening"
                ]
            },
            "Dhanishtha": {
                "title": "The Cadenced Conductor & Splendid Manifestor",
                "span": "23° 20' Capricorn – 06° 40' Aquarius",
                "deity_symbol": "The Eight Vasus (Elemental Gods of Abundance) | Musical drum (mṛdaṅga) / Flute",
                "positives": [
                    "Mastery of rhythm, timing, and cadence; brings structural symmetry out of chaos",
                    "Supreme ability to translate latent artistic gifts into concrete wealth and recognition",
                    "Inspiring group leadership, civic generosity, and high martial or athletic bravery",
                    "Dynamic social mobility; easily connects diverse people to achieve prosperity"
                ],
                "negatives": [
                    "Overweening material ambition that burns out personal intimacy and warmth",
                    "Ruthless disregard for emotional subtleties when driving organizational agendas",
                    "Grasping possessiveness toward status symbols, titles, and public deference",
                    "Quarrelsome, abrasive temper when collective rhythms are disrupted"
                ]
            },
            "Shatabhisha": {
                "title": "The Subterranean Healer & Counter-Cultural Seer",
                "span": "06° 40' Aquarius – 20° 00' Aquarius",
                "deity_symbol": "Varuṇa (Lord of Cosmic Waters & Law) | Circle of 100 stars / Empty circle",
                "positives": [
                    "Deep diagnostic genius in unconventional medicine, chemotherapy, and complex illnesses",
                    "Fearless counter-cultural insight; exposes institutional hypocrisies without flinching",
                    "Protective containment; maintains sovereign boundaries against toxic influences",
                    "Unwavering commitment to universal cosmic laws above petty social conventions"
                ],
                "negatives": [
                    "Alienating cynicism, chronic suspicion, and defensive emotional secrecy",
                    "Paralyzing isolation; building impenetrable psychological walls around oneself",
                    "Stonewalling loved ones through stubborn, icy silence and aloofness",
                    "Vindictive holding of ancient grudges under a banner of righteous justice"
                ]
            }
        }
    },
    "Laghu": {
        "label": "Quick",
        "sanskrit": "Kṣipra / Laghu",
        "nakshatras": ["Ashwini", "Pushya", "Hasta"],
        "essence": "Light touch, fine manual dexterity, rapid manifestation, emergency relief, effortless grace.",
        "macro_psychology": "Operates with a dexterous flying touch, swift crisis intervention, and friction-free manifestation. Refuses heavy, sluggish entanglements; accomplishes objectives quickly through technical agility, generosity, and nimble coordination.",
        "thermodynamics": {
            "surplus": "Effortless, frictionless manifestation and high craftsmanship; but risks 'haste makes waste,' impatience with slow development, micro-managing control, and frantic speech.",
            "balanced": "Nimble problem-solving, dexterous execution, and generous guidance. Balances lightning comprehension with steady patience for completion.",
            "deficit": "Sluggish execution; feeling easily overwhelmed by sudden emergencies; lacking manual agility or rapid technical grasp; taking tedious detours for simple tasks."
        },
        "positives": [
            "Effortless realization of virtuous objectives without delay or friction",
            "High technical dexterity, fine craftsmanship, and artistic finesse",
            "Rapid healing, instant comprehension, and crisis troubleshooting",
            "Generous mentoring, ethical wisdom, and nourishing paternal care"
        ],
        "negatives": [
            "Haste makes waste; impatience leading to sloppy execution or racing speech",
            "Grasping urge to over-control environments and micro-manage others",
            "Pliable ethics; resorting to dishonorable shortcuts or trickery under pressure",
            "Intolerance for necessary, repetitive, long-term grinding routines"
        ],
        "stars_detail": {
            "Ashwini": {
                "title": "The Miraculous Healer & Untethered Pioneer",
                "span": "00° 00' Aries – 13° 20' Aries",
                "deity_symbol": "The Aśvinī Kumāras (Celestial Twin Physicians) | Horse's head / Galloping steed",
                "positives": [
                    "Miraculous speed in crisis troubleshooting, trauma recovery, and medical intervention",
                    "Untethered enthusiasm for pioneering ventures and initiating daring breakthroughs",
                    "Keen reflexes, natural physical agility, and an infectious, youthful vitality",
                    "Generous instinct to bring instantaneous relief to suffering people and animals"
                ],
                "negatives": [
                    "Hasty, half-baked decisions ('haste makes waste') leading to chronic missteps",
                    "Extreme restlessness; abandons projects the moment the initial novelty wanes",
                    "Racing speech, frantic agitation, and inability to listen patiently to others",
                    "Reckless thrill-seeking and dangerous speeding without regard for consequences"
                ]
            },
            "Pushya": {
                "title": "The Auspicious Nourisher & Paternal Preceptor",
                "span": "03° 20' Cancer – 16° 40' Cancer",
                "deity_symbol": "Bṛhaspati (Guru of the Gods & Lord of Sacred Speech) | Cow's milk udder / Blossom",
                "positives": [
                    "Purest frictionless quickness; virtuous objectives materialize smoothly without obstacles",
                    "Boundless paternal mentorship, moral integrity, and unconditional nourishment",
                    "Calm emotional stability that provides shelter and spiritual grounding for communities",
                    "Deep reverence for sacred tradition, righteous conduct (Dharma), and high scholarship"
                ],
                "negatives": [
                    "Smug complacency and moral entitlement within comfortable orthodox routines",
                    "Dogmatic self-righteousness; judging those who choose unconventional spiritual paths",
                    "Over-protective, smothering control disguised as benevolent paternal guidance",
                    "Sluggish physical resistance to necessary modernization and energetic reform"
                ]
            },
            "Hasta": {
                "title": "The Dexterous Artisan & Sovereign Manipulator",
                "span": "10° 00' Virgo – 23° 20' Virgo",
                "deity_symbol": "Savitṛ (The Solar Awakener & Instigator) | The open hand / Grasping fist",
                "positives": [
                    "Exceptional manual and technical dexterity, fine craftsmanship, and surgical precision",
                    "Alert, dexterous intelligence; transforms detailed plans into concrete reality",
                    "Resourceful problem-solver; masters intricate routines through industrious daily discipline",
                    "Playful wit, sleight-of-hand mastery, and cheerful adaptability under pressure"
                ],
                "negatives": [
                    "Grasping urge to hoard resources, micro-manage subordinates, and over-control environments",
                    "Pliable ethics; resorts to clever deception, trickery, or theft under financial stress",
                    "Severe anxiety and inner nervous tension when outcomes cannot be micromanaged",
                    "Mercenary opportunism; evaluating relationships strictly on utilitarian output"
                ]
            }
        }
    },
    "Mridu": {
        "label": "Sweet",
        "sanskrit": "Mṛdu",
        "nakshatras": ["Mrigashira", "Chitra", "Anuradha", "Revati"],
        "essence": "Cooperative compliance, aesthetic refinement, loving devotion (bhakti), intellect, gentle shelter.",
        "macro_psychology": "Embodies cooperative compliance, refined aesthetic vision, and devotion (bhakti). Unites beauty with intellect (buddhi); secures major victories through diplomatic gentleness, coalition building, and hospitality without creating enemies.",
        "thermodynamics": {
            "surplus": "Empathetic devotion, elegant design intelligence, and peaceful diplomacy; but risks weak personal boundaries, timidity, fear of confrontation, and romantic heartbreak.",
            "balanced": "Refined aesthetic judgment, cooperative harmony, and loyal affection. Navigates social dynamics with tact while firmly maintaining healthy boundaries.",
            "deficit": "Abrasive bluntness; difficulty fostering gentle intimacy; insensitivity to aesthetic nuances; alienating potential allies through unneeded confrontation."
        },
        "positives": [
            "Empathetic devotion, heartfelt loyalty, and gentle coalition building",
            "Refined aesthetic vision, architectural elegance, and keen design intelligence",
            "Cooperative diplomacy; achieves ambitious goals without creating enemies",
            "Nurturing hospitality, maternal care, and safe guidance for wayfarers"
        ],
        "negatives": [
            "Pliable weakness; lack of boundaries resulting in codependency and exploitation",
            "Timidity and chronic skittishness; avoiding necessary confrontations",
            "Vulnerability to deep romantic grief and emotional manipulation",
            "Superficial packaging; prioritizing outward beauty over inner substance"
        ],
        "stars_detail": {
            "Mrigashira": {
                "title": "The Gentle Inquirer & Aesthetic Forager",
                "span": "23° 20' Taurus – 06° 40' Gemini",
                "deity_symbol": "Soma (Moon God of Nectar & Fluctuating Mind) | The alert deer's head",
                "positives": [
                    "Insatiable, gentle curiosity; excels at research, investigation, and tracking clues",
                    "Sweet speech, delightful humor, and an enchanting, persuasive social presence",
                    "Deep aesthetic sensitivity to textures, fragrances, musical tones, and fine art",
                    "Harmonious diplomacy that soothes interpersonal tensions without conflict"
                ],
                "negatives": [
                    "Chronic skittishness and fickleness; constantly wandering without a stable anchor",
                    "Paranoid suspicion; sniffing imaginary dangers and misinterpreting benign motives",
                    "Superficial romantic flitting; easily infatuated and quickly disappointed",
                    "Timidity that flees from necessary confrontation, leaving issues unresolved"
                ]
            },
            "Chitra": {
                "title": "The Master Architect & Gem-Like Visionary",
                "span": "23° 20' Virgo – 06° 40' Libra",
                "deity_symbol": "Tvaṣṭṛ / Viśvakarmā (Divine Celestial Craftsman) | Multifaceted sparkling jewel",
                "positives": [
                    "Genius design intelligence, architectural balance, and acute structural symmetry",
                    "Razor-sharp, incisive intellect that cuts through confusion like a diamond",
                    "Ability to manifest extraordinary beauty, artistic elegance, and functional utility",
                    "Charismatic presence and persuasive public oratory in high-level debates"
                ],
                "negatives": [
                    "Obsession with superficial packaging, outward appearances, and hollow vanity",
                    "Hyper-critical aesthetic judgment that tears down partners' genuine efforts",
                    "Arrogant, self-absorbed persona hiding inner emotional emptiness",
                    "Transactional calculation disguised under charming, polished manners"
                ]
            },
            "Anuradha": {
                "title": "The Tender Peacemaker & Devotional Bridge",
                "span": "03° 20' Scorpio – 16° 40' Scorpio",
                "deity_symbol": "Mitra (The Divine Union-Maker & God of Friendship) | Lotus blossoming over mud / Archway",
                "positives": [
                    "Unconditional fidelity and devotion (bhakti); steadfast loyalty in difficult conditions",
                    "Blossoms with immaculate spiritual grace out of murky, traumatic emotional terrain",
                    "Charismatic capacity to build bridges between hostile camps and forge lasting peace",
                    "Cross-cultural curiosity and thriving in distant foreign lands through gentle respect"
                ],
                "negatives": [
                    "Vulnerability to codependency; becoming an emotional doormat for manipulative partners",
                    "Deep romantic grief and despair when unconditional affection is exploited",
                    "Passive-aggressive resentment born of unexpressed boundaries and unvoiced needs",
                    "Struggles with inner melancholy and feelings of being taken for granted"
                ]
            },
            "Revati": {
                "title": "The Generous Wayfarer & Sacred Shepherd",
                "span": "16° 40' Pisces – 30° 00' Pisces",
                "deity_symbol": "Pūṣan (Cosmic Nourisher & Shepherd of Wayfarers) | Pair of fish / Kettledrum",
                "positives": [
                    "Supreme empathy and boundless hospitality; provides safe sanctuary for all living beings",
                    "Guiding lost travelers through perilous life crises and safe karmic transitions",
                    "Effortless manifestation of prosperity through goodwill and clean ethical conduct",
                    "Deep intuitive, psychic attunement and protective shelter for vulnerable souls"
                ],
                "negatives": [
                    "Total dissolution of boundaries, leading to parasitic exploitation by toxic people",
                    "Chronic escapism and financial naivety; falling prey to fraudulent schemes",
                    "Rescuing and enabling dysfunctional behavior out of misguided compassion",
                    "Extreme emotional sensitivity that retreats into helpless, self-pitying seclusion"
                ]
            }
        }
    },
    "Ugra": {
        "label": "Strong",
        "sanskrit": "Ugra / Krūra",
        "nakshatras": ["Bharani", "Magha", "Purva Phalguni", "Purva Ashadha", "Purva Bhadrapada"],
        "essence": "Formidable willpower, breakthrough momentum, fierce boundary defense, discipline, royal backbone.",
        "macro_psychology": "Channels formidable willpower, boundary defense, moral rigor, and breakthrough power. Smashes administrative and societal stagnation; confronts adversity directly without flinching and protects dependents with royal fortitude.",
        "thermodynamics": {
            "surplus": "Unconquerable bravery, strict moral discipline, and commanding leadership; but risks belligerent aggression, volcanic anger, authoritarian bullying, and domestic combustion.",
            "balanced": "Resolute backbone, decisive courage, and righteous authority. Defends borders and initiates hard projects while respecting the delicate feelings of allies.",
            "deficit": "Lack of assertiveness; paralysis when confronting intimidation or bullies; reluctance to enforce ethical boundaries; crumbling under direct pressure."
        },
        "positives": [
            "Unconquerable bravery; willingness to smash through obstacles and fight for justice",
            "Strict self-regulation, moral discipline, and high endurance under hardship",
            "Regal presence and inspiring executive authority under pressure",
            "Passionate creative gestation and bold romantic commitment"
        ],
        "negatives": [
            "Belligerent aggressiveness, unnecessary litigation, and creating fierce rivals",
            "Hypocritical severity; imposing harsh standards while defending personal pride",
            "Volcanic temper, destructive rage, and incinerating valuable partnerships",
            "Bulldozing over subtle emotional feelings and consensus"
        ],
        "stars_detail": {
            "Bharani": {
                "title": "The Austere Gatekeeper & Weight-Bearer",
                "span": "13° 20' Aries – 26° 40' Aries",
                "deity_symbol": "Yama (King of Dharma & Cosmic Justice) | The vulva (womb of gestation)",
                "positives": [
                    "Supreme moral courage and willingness to shoulder crushing burdens without complaint",
                    "Deep understanding of the 'no pain, no gain' principle in spiritual and worldly mastery",
                    "Silent, patient incubation of monumental breakthroughs in the dark before birth",
                    "Fierce defense of justice, ethical boundaries, and vulnerable dependents"
                ],
                "negatives": [
                    "Puritanical severity; merciless and judgmental toward human frailties in others",
                    "Stubborn, immovable obstinacy when challenged; refusing all compromise",
                    "Volcanic outbursts of pent-up anger after months of rigid suppression",
                    "Severe guilt, self-punishing martyrdom, and emotional frigidity"
                ]
            },
            "Magha": {
                "title": "The Sovereign Patriarch & Regal Commander",
                "span": "00° 00' Leo – 13° 20' Leo",
                "deity_symbol": "The Pitṛs (Divine Ancestral Forefathers) | The royal throne room / Palanquin",
                "positives": [
                    "Regal presence, natural dignity, and inspiring command under severe stress",
                    "Reverent stewardship of ancestral legacy, historical honor, and institutional prestige",
                    "Magnanimous protection of subordinates and generous patronage to dependents",
                    "High executive backbone that cuts through administrative cowardice cleanly"
                ],
                "negatives": [
                    "Arrogant, condescending snobbery toward those deemed socially or culturally inferior",
                    "Obsessive need for deference, public flattery, and grand ceremonial titles",
                    "Authoritarian tyranny; punishing dissenters harshly to preserve personal prestige",
                    "Entitled complacency; resting on inherited family laurels without personal virtue"
                ]
            },
            "Purva Phalguni": {
                "title": "The Creative Gestator & Romantic Champion",
                "span": "13° 20' Leo – 26° 40' Leo",
                "deity_symbol": "Bhaga (Aditya of Shared Wealth & Marital Bliss) | Front legs of a love bed / Hammock",
                "positives": [
                    "Bold romantic courage; transforms tentative courtship into committed partnership",
                    "Vibrant creative gestation; pours passionate vitality into music, drama, and the arts",
                    "Generous warmth, festive hospitality, and an innate capacity to celebrate life",
                    "High social charisma that revitalizes weary communities through joyous gatherings"
                ],
                "negatives": [
                    "Reckless hedonism, vanity, and addiction to sensory indulgence and leisure",
                    "Lazy complacency; avoiding demanding responsibilities to lounge in comfort",
                    "Using affection and sexual intimacy as a weaponized bargaining chip in relationships",
                    "Melodramatic temper tantrums when denied the center stage or adoration"
                ]
            },
            "Purva Ashadha": {
                "title": "The Undefeated Crusader & Unstoppable Current",
                "span": "13° 20' Sagittarius – 26° 40' Sagittarius",
                "deity_symbol": "Āpaḥ (Deified Cosmic Waters) | Charging elephant tusk / Winnowing basket",
                "positives": [
                    "Invincible momentum (Aparājitā); cuts through structural barriers like an elephant",
                    "Unifying power of a swelling river; marshals disparate resources into an unstoppable coalition",
                    "Keen discernment that vigorously sifts valuable truth from worthless chaff",
                    "Unshakeable confidence that inspires followers to overcome seemingly impossible odds"
                ],
                "negatives": [
                    "Fanatical obstinacy; charging headlong into disastrous conflicts out of sheer hubris",
                    "Bulldozing over legitimate consensus, emotional needs, and wise counsel",
                    "Merciless, scorching pride that cannot admit tactical mistake or defeat",
                    "Starting destructive factional crusades over ideological trivialities"
                ]
            },
            "Purva Bhadrapada": {
                "title": "The Scorching Purifier & Mystic Ascetic",
                "span": "20° 00' Aquarius – 03° 20' Pisces",
                "deity_symbol": "Aja Ekapāda (The Cosmic One-Footed Fire Serpent) | Front legs of the funeral cot",
                "positives": [
                    "Piercing analytical intellect that incinerates false facades and religious hypocrisy",
                    "Uncompromising courage to confront mortality, tragedy, and existential shadow",
                    "Transmutes deep suffering into profound mystical detachment and transcendent vision",
                    "Radical reformer; purges corrupt institutional decay through fierce self-sacrifice"
                ],
                "negatives": [
                    "Caustic nihilism, misanthropy, and existential gloom that poisons domestic peace",
                    "Volcanic temper; burning down valuable relationships in flashes of rage",
                    "Morbid fascination with disaster, tragedy, and dark subterranean forces",
                    "Biting, sarcastic cruelty that wounds friends and alienates genuine well-wishers"
                ]
            }
        }
    },
    "Tikshna": {
        "label": "Bitter",
        "sanskrit": "Tīkṣṇa / Dāruṇa",
        "nakshatras": ["Ardra", "Ashlesha", "Jyeshtha", "Mula"],
        "essence": "Piercing inquiry, cathartic disruption, exposing decay, strategic defense, subterranean truth.",
        "macro_psychology": "Bores relentlessly downward into root causes, psychological depths, and corrupt decay. Operates through surgical precision, cathartic emotional storms, and strategic counter-attacks rather than blunt force. Strips away illusions to reveal bedrock reality.",
        "thermodynamics": {
            "surplus": "Uncompromising truth-seeking, acute diagnostic depth, and psychological mastery; but risks caustic cynicism, paranoid suspicion, manipulative intrigue, and burning down foundational security.",
            "balanced": "Keen psychological discernment, fearless diagnostic precision, and calm crisis management. Exposes decay without becoming consumed by bitterness.",
            "deficit": "Superficial credulity; easily blinded by polite facades; defenseless against psychological intrigue or workplace politics; struggling to endure necessary cathartic cleansings."
        },
        "positives": [
            "Uncompromising truth-seeking; bores to bedrock reality and strips away illusions",
            "Cathartic crisis management; sheds emotional tears to cleanse stagnant corruption",
            "Keen psychological acumen and strategic foresight in competitive arenas",
            "Diagnostic mastery over subtle poisons, esoteric lore, and radical treatments"
        ],
        "negatives": [
            "Caustic cynicism, bitter speech, and callous ingratitude toward benefactors",
            "Manipulative calculation, clinging possessiveness, and intrigue driven by envy",
            "Nihilistic burn-it-down rage when wounded; destroying foundational security",
            "Defensive paranoia and deep-seated fear of betrayal"
        ],
        "stars_detail": {
            "Ardra": {
                "title": "The Cathartic Storm & Illuminating Teardrop",
                "span": "06° 40' Gemini – 20° 00' Gemini",
                "deity_symbol": "Rudra (Roaring Storm God of Dissolution & Tears) | A single teardrop / Diamond",
                "positives": [
                    "Cathartic emotional purification; endures the storm to clear out accumulated filth",
                    "Radical diagnostic depth; handles hazardous poisons, chemotherapy, and crisis triage",
                    "Courage to strip away comforting illusions and stare directly at uncomfortable truths",
                    "Formidable mental resilience forged through surviving severe personal adversity"
                ],
                "negatives": [
                    "Caustic cynicism, bitter speech, and callous ingratitude toward benefactors",
                    "Chronic emotional turbulence and projecting unresolved grief onto innocent partners",
                    "Destructive temper that relishes tearing down structures purely out of malice",
                    "Paralyzing feelings of raw persecution, indignation, and victimization"
                ]
            },
            "Ashlesha": {
                "title": "The Subterranean Hypnotist & Fierce Guardian",
                "span": "16° 40' Cancer – 30° 00' Cancer",
                "deity_symbol": "The Nāgas (Divine Serpents of Subterranean Wisdom) | Coiled serpent embrace",
                "positives": [
                    "Profound psychological insight; instantly reads unvoiced motives and subtexts",
                    "Hypnotic verbal magnetism that disarms adversaries and commands collective attention",
                    "Fierce, unshakeable loyalty and willingness to carry massive burdens for inner circle",
                    "Deep mastery over esoteric sciences, toxicology, and subtle energetic currents"
                ],
                "negatives": [
                    "Suffocating emotional clinginess and treating intimate partners as possessions",
                    "Deep-seated paranoia, fear of betrayal, and venomous jealousy toward competitors",
                    "Cold, manipulative calculation; using secrets and vulnerabilities to control allies",
                    "Deceitful treachery when cornered, striking with lethal psychological poison"
                ]
            },
            "Jyeshtha": {
                "title": "The Vigilant Sovereign & Master Tactician",
                "span": "16° 40' Scorpio – 30° 00' Scorpio",
                "deity_symbol": "Indra (King of the Gods & Celestial Chieftain) | Round protective talisman / Umbrella",
                "positives": [
                    "Supreme crisis leadership; commands authority and defends institutions during sieges",
                    "Keen strategic defense; maneuvers opponents into exposing their own vulnerabilities",
                    "High executive grit that weathers severe political isolation without breaking",
                    "Stalwart guardian who shields dependents and organizations from hostile takeovers"
                ],
                "negatives": [
                    "Acute defensive paranoia, court intrigue, and obsessive fear of being dethroned",
                    "Two-faced hypocrisy; smiling publicly while scheming behind closed doors",
                    "Arrogant grandiosity that cannot tolerate rival talent or younger successors",
                    "Sudden catastrophic falls from power triggered by overextended political pride"
                ]
            },
            "Mula": {
                "title": "The Relentless Iconoclast & Bedrock Seeker",
                "span": "00° 00' Sagittarius – 13° 20' Sagittarius",
                "deity_symbol": "Nirṛti (Goddess of Dissolution & Calamity) | Tied bunch of roots / Elephant goad",
                "positives": [
                    "Relentless root-cause inquiry; bores through layers of superficiality to find bedrock truth",
                    "Uproots corrupt institutions, rotten ideological foundations, and outdated paradigms",
                    "Extraordinary resilience to rebuild life from absolute zero after severe disasters",
                    "Profound philosophical detachment and research acumen in esoteric science"
                ],
                "negatives": [
                    "Nihilistic burn-it-down rage; destroys valuable foundations in impulsive anger",
                    "Cruel iconoclasm; ruthlessly trampling on innocent people's tender feelings",
                    "Self-destructive defiance that brings ruin upon own family or enterprise",
                    "Bitter resentment toward existence, adopting a grim 'nothing matters' fatalism"
                ]
            }
        }
    },
    "Mishra": {
        "label": "Mixed",
        "sanskrit": "Miśra / Sādhāraṇa",
        "nakshatras": ["Krittika", "Vishakha"],
        "essence": "Universal catalyst (fire sacrifice), razor incisiveness, goal-directed coupling, focused momentum.",
        "macro_psychology": "The universal catalyst that combines sharp cutting discrimination with dedicated attachment. Necessary for igniting momentum in any enterprise; provides the fire sacrifice (Agni) and one-pointed coupling required to harvest ambitious goals.",
        "thermodynamics": {
            "surplus": "Incisive intellectual clarity, catalytic momentum, and intense dedication; but risks utilitarian opportunism, a scorching critical tongue, erratic detachment, and bitter rivalry.",
            "balanced": "Discriminating ambition, catalytic initiative, and loyal partnership. Ignites projects effectively while nurturing long-term relational harmony.",
            "deficit": "Lack of ignition energy; sluggish starts; difficulty focusing intently on targeted objectives; inability to cut away extraneous distractions."
        },
        "positives": [
            "Universal versatility; capable of igniting catalytic momentum in any endeavor",
            "One-pointed devotion (bhakti) and fierce determination to achieve targeted goals",
            "Razor-sharp discernment; dissects truth from irrelevant superficialities",
            "Strategic coupling; partners effectively with complementary talents"
        ],
        "negatives": [
            "Utilitarian opportunism; viewing allies as disposable means to an end",
            "Scorching tongue; burning domestic harmony with hyper-critical dissection",
            "Volatile inconsistency; erratic swings between intense heat and cool detachment",
            "Jealous rivalry; generating factional conflicts when goals are impeded"
        ],
        "stars_detail": {
            "Krittika": {
                "title": "The Sacred Flame & Discriminating Blade",
                "span": "26° 40' Aries – 10° 00' Taurus",
                "deity_symbol": "Agni (Sacred Fire God & Divine Consumer) | Razor blade / Flame / Axe",
                "positives": [
                    "Universal catalysis; kindles the initial spark, momentum, and digestive fire in any endeavor",
                    "Razor-sharp, incisive intellect that cleanly cuts extraneous fluff from pure truth",
                    "Courage to burn away toxins and impurities, restoring moral and physical health",
                    "Noble, maternal protection (the Pleiades foster mothers) behind a fiery exterior"
                ],
                "negatives": [
                    "Scorching critical tongue; burns domestic harmony with biting, unsparing remarks",
                    "Volatile inconsistency; erratic swings between burning passion and cold detachment",
                    "Impatient intolerance for human flaws, creating unnecessary enemies",
                    "Stubborn, fiery pride that incinerates valuable bridges when criticized"
                ]
            },
            "Vishakha": {
                "title": "The Triumphant Archer & Resolute Partner",
                "span": "20° 00' Libra – 03° 20' Scorpio",
                "deity_symbol": "Indrāgni (Indra + Agni: Sovereign Authority & Sacred Fire) | Triumphal arch / Potter's wheel",
                "positives": [
                    "One-pointed determination (bhakti); pursues targeted goals with tenaciously focused will",
                    "Strategic coupling; partners effectively with whoever possesses complementary resources",
                    "Triumphant harvesting; relentless work ethic that converts hard labor into definitive success",
                    "Transformative courage; crosses the threshold into intense emotional territory bravely"
                ],
                "negatives": [
                    "Utilitarian opportunism; viewing friends as disposable stepping stones to be discarded",
                    "Obsessive jealousy and bitter rivalry when peers achieve earlier recognition",
                    "Inability to enjoy accomplishments; immediately plunging into anxious new strivings",
                    "Divided loyalty and internal friction (the 'forked branch') that splits energy"
                ]
            }
        }
    }
}

ALL_NAKSHATRA_GROUPS = list(NAKSHATRA_GROUP_METADATA.keys())


def get_temperament_dossier(group: str) -> Dict[str, Any]:
    """Returns the temperament dossier for a given Nakshatra group class."""
    return NAKSHATRA_TEMPERAMENT_DOSSIER.get(group, {})



def normalize_nakshatra_name(name: str) -> str:
    """Normalizes any nakshatra string (case-insensitive, trims spaces)."""
    if not name:
        return "Ashwini"
    clean = name.strip().lower()
    return _ALIAS_MAP.get(clean, name.strip())


def get_nakshatra_lore(name: str) -> Dict[str, Any]:
    """
    Returns the complete psychological and astrological dossier for a Nakshatra.
    Falls back gracefully if an unknown name is provided.
    """
    norm = normalize_nakshatra_name(name)
    if norm in NAKSHATRA_DATABASE:
        return NAKSHATRA_DATABASE[norm]
    
    # Generic fallback
    return {
        "name": name,
        "aliases": [name],
        "group": "Mishra",
        "group_description": "General Asterism",
        "astronomical_star": "Vedic Constellation",
        "zodiacal_span": "--",
        "presiding_deity": "Universal Cosmic Intelligence",
        "symbol_etymology": "Asterism",
        "varahamihira_moon": "Endowed with vitality and purpose.",
        "core_psychology": "Expresses distinctive celestial nature and life momentum.",
        "real_world_manifestations": "Diverse creative, executive, and intellectual pursuits."
    }


def get_nakshatra_group(name: str) -> str:
    """Returns the group category (Tikshna, Ugra, Dhruva, Mridu, Laghu, Chara, Mishra)."""
    lore = get_nakshatra_lore(name)
    return lore.get("group", "Mishra")
