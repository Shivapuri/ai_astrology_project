/**
 * Astra Astrological Synthesis Report Widget (report_widget.js)
 * 
 * Provides an interactive Master Ingredients Desk for astrological synthesis:
 * 1. Polarity Core (Ascendant Nakshatra ⟷ Moon Nakshatra with Panchadha Maitri & Tattvas)
 * 2. Canonical 4-Step Nakshatra Dominance & 7-Temperament Distribution
 * 3. Operational Axis (Rising Rashi ⟷ Rising Navamsha Pada with Vargottama check)
 * 4. Macro Environmental Tallies (Elements, Gunas, Rising Mode, Ayurvedic Doshas)
 * 5. Planetary Prominence & Dignity Leaderboard (Highlighting #1 Chart Commander)
 * 6. Synthesis Desk (Aggregated ingredients checklist)
 * 
 * Strictly adheres to Astra's Pergamon warm parchment theme and >= 12px font floor.
 */

/**
 * 7 Nakshatra Balance Types Metadata & Psychological Dossiers
 * Derived from classical Jyotish (Light on Life, Brihat Jataka) & Vic DiCara's expositions.
 */
const NAKSHATRA_TEMPERAMENT_DOSSIER = {
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
};

if (typeof window !== 'undefined') {
    window.NAKSHATRA_TEMPERAMENT_DOSSIER = NAKSHATRA_TEMPERAMENT_DOSSIER;
}

/**
 * Helper to identify which natal planets or Lagna occupy a given star.
 */
function getOccupantsForStar(starName, chartData) {
    const occupants = [];
    const data = chartData || window.currentChartData;
    if (!data || !starName) return occupants;

    const cleanStar = starName.trim().toLowerCase();
    const grahas = data.nakshatras ? (data.nakshatras.grahas || {}) : {};

    const checkOrder = ["Lagna", "Moon", "Sun", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
    checkOrder.forEach(ent => {
        const info = grahas[ent];
        if (info && info.nakshatra && info.nakshatra.trim().toLowerCase() === cleanStar) {
            occupants.push(`${ent}${info.pada ? ` (Pada ${info.pada})` : ''}`);
        }
    });

    return occupants;
}

/**
 * Builds the interactive Two-Tier Temperament Dossier HTML for a chosen category group.
 * Tier 1: Group Macro Archetype (Sanskrit, essence, macro psychology, dynamic thermodynamic state).
 * Tier 2: Star-by-Star Micro Dossier with constituent star cards, deity, coordinates, and natal occupancy.
 */
function renderTemperamentDrawerHtml(group, tbItem, chartData) {
    const dossier = NAKSHATRA_TEMPERAMENT_DOSSIER[group] || {};
    const label = dossier.label || tbItem?.display_name || group;
    const sanskrit = dossier.sanskrit || tbItem?.sanskrit || '';
    const pct = (tbItem && typeof tbItem.percentage === 'number') ? tbItem.percentage : 14.3;
    const pts = (tbItem && typeof tbItem.points === 'number') ? tbItem.points : 0;
    const dev = (tbItem && typeof tbItem.deviation_pct === 'number') ? tbItem.deviation_pct : 0;

    // Status evaluation based on classical synthesis criteria
    let status = 'Balanced';
    let badgeBg = '#f1f5f9';
    let badgeColor = '#334155';
    let badgeBorder = '#cbd5e1';
    let badgeIcon = '●';

    if (pct > 16.0) {
        status = 'Surplus';
        badgeBg = '#dcfce7';
        badgeColor = '#166534';
        badgeBorder = '#86efac';
        badgeIcon = '▲';
    } else if (pct < 10.0) {
        status = 'Deficit';
        badgeBg = '#fee2e2';
        badgeColor = '#991b1b';
        badgeBorder = '#fca5a5';
        badgeIcon = '▼';
    }

    // Dynamic Thermodynamic state based on native's percentage
    let thermHtml = '';
    const therm = dossier.thermodynamics || {};
    if (pct > 16.0) {
        thermHtml = `
            <div style="margin-top:10px; padding:10px 12px; background:#f0fdf4; border:1px solid #86efac; border-radius:6px;">
                <div style="font-size:12px; font-weight:700; color:#15803d; margin-bottom:3px; display:flex; align-items:center; gap:5px;">
                    <span>▲</span> Surplus Expression (> 16.0%):
                </div>
                <div style="font-size:12px; color:#14532d; line-height:1.45;">
                    ${therm.surplus || 'Abundance of energy manifesting through strong stamina but risking dogmatism.'}
                </div>
            </div>
        `;
    } else if (pct < 10.0) {
        thermHtml = `
            <div style="margin-top:10px; padding:10px 12px; background:#fef2f2; border:1px solid #fca5a5; border-radius:6px;">
                <div style="font-size:12px; font-weight:700; color:#b91c1c; margin-bottom:3px; display:flex; align-items:center; gap:5px;">
                    <span>▼</span> Deficit Expression (< 10.0%):
                </div>
                <div style="font-size:12px; color:#7f1d1d; line-height:1.45;">
                    ${therm.deficit || 'Deficit of energy requiring conscious cultivation of member star qualities.'}
                </div>
            </div>
        `;
    } else {
        thermHtml = `
            <div style="margin-top:10px; padding:10px 12px; background:#f7fee7; border:1px solid #bef264; border-radius:6px;">
                <div style="font-size:12px; font-weight:700; color:#4d7c0f; margin-bottom:3px; display:flex; align-items:center; gap:5px;">
                    <span>●</span> Equilibrium Expression (10.0% – 16.0%):
                </div>
                <div style="font-size:12px; color:#365314; line-height:1.45;">
                    ${therm.balanced || 'Steady, reliable balance maintaining natural flexibility.'}
                </div>
            </div>
        `;
    }

    // Tier 2: Star-by-Star Micro Cards
    const starsList = dossier.nakshatras || [];
    const starsDetail = dossier.stars_detail || {};
    let starCardsHtml = '';

    starsList.forEach(star => {
        const sInfo = starsDetail[star] || {};
        const occupants = getOccupantsForStar(star, chartData);
        const isOccupied = occupants.length > 0;

        let occupancyBadge = '';
        let cardBorder = '1px solid #e2e8f0';
        let cardBg = '#ffffff';
        let cardShadow = '0 1px 3px rgba(0,0,0,0.04)';

        if (isOccupied) {
            occupancyBadge = `
                <span style="font-size:11px; font-weight:700; padding:2px 8px; border-radius:12px; background:#eff6ff; color:#1d4ed8; border:1.5px solid #bfdbfe; display:inline-flex; align-items:center; gap:4px; box-shadow:0 1px 2px rgba(37,99,235,0.1);">
                    ★ Occupied: ${occupants.join(', ')}
                </span>
            `;
            cardBorder = '1.5px solid #93c5fd';
            cardBg = '#f8fafc';
            cardShadow = '0 2px 8px rgba(37,99,235,0.08)';
        }

        const positivesList = (sInfo.positives || []).map(p => `<li>${p}</li>`).join('');
        const negativesList = (sInfo.negatives || []).map(n => `<li>${n}</li>`).join('');

        starCardsHtml += `
            <div style="background:${cardBg}; border:${cardBorder}; border-radius:8px; padding:12px; box-shadow:${cardShadow}; display:flex; flex-direction:column; gap:8px;">
                <!-- Star Card Top Header -->
                <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:6px; border-bottom:1px solid #e2e8f0; padding-bottom:6px;">
                    <div>
                        <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
                            <span style="font-family:Georgia, serif; font-size:15px; font-weight:800; color:#0f172a;">
                                ${star}
                            </span>
                            <span style="font-size:12px; font-weight:600; color:#475569;">
                                — <em>${sInfo.title || ''}</em>
                            </span>
                        </div>
                        <div style="font-size:11.5px; color:#64748b; margin-top:2px;">
                            <strong>Span:</strong> ${sInfo.span || '--'} • <strong>Deity &amp; Symbol:</strong> ${sInfo.deity_symbol || '--'}
                        </div>
                    </div>
                    ${occupancyBadge}
                </div>

                <!-- Two-Column Positives / Negatives Sub-Grid -->
                <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; margin-top:4px;">
                    <!-- Positive Qualities -->
                    <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:5px; padding:8px 10px;">
                        <div style="font-size:12px; font-weight:700; color:#15803d; margin-bottom:4px; display:flex; align-items:center; gap:5px;">
                            <span>✨</span> (+) Integrated / Favorable
                        </div>
                        <ul style="margin:0; padding-left:16px; font-size:12px; color:#14532d; line-height:1.4; display:flex; flex-direction:column; gap:3px;">
                            ${positivesList}
                        </ul>
                    </div>

                    <!-- Negative Qualities -->
                    <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:5px; padding:8px 10px;">
                        <div style="font-size:12px; font-weight:700; color:#b91c1c; margin-bottom:4px; display:flex; align-items:center; gap:5px;">
                            <span>⚠️</span> (-) Shadow / When Afflicted
                        </div>
                        <ul style="margin:0; padding-left:16px; font-size:12px; color:#7f1d1d; line-height:1.4; display:flex; flex-direction:column; gap:3px;">
                            ${negativesList}
                        </ul>
                    </div>
                </div>
            </div>
        `;
    });

    return `
        <!-- Tier 1: Group Macro Archetype -->
        <div style="border-bottom:1.5px solid #e2e8f0; padding-bottom:12px;">
            <!-- Top Drawer Bar -->
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px;">
                <div>
                    <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                        <span style="font-family:Georgia, serif; font-size:16px; font-weight:800; color:#0f172a;">
                            ${label} (${sanskrit}) Class
                        </span>
                        <span style="font-size:11.5px; font-weight:700; padding:2px 8px; border-radius:12px; background:${badgeBg}; color:${badgeColor}; border:1px solid ${badgeBorder};">
                            ${badgeIcon} ${status} (${pct}%)
                        </span>
                    </div>
                    <div style="font-size:12px; color:#334155; margin-top:3px; font-style:italic;">
                        "${dossier.essence || ''}"
                    </div>
                </div>
                <div style="display:flex; align-items:center; gap:10px;">
                    <div style="text-align:right;">
                        <span style="font-size:13.5px; font-weight:700; color:#1e293b;">${pts} pts</span>
                        <div style="font-size:11px; color:#64748b;">${dev >= 0 ? '+' : ''}${dev}% vs baseline (14.3%)</div>
                    </div>
                    <button type="button" onclick="selectTemperamentDossier('${group}')" style="background:transparent; border:none; color:#94a3b8; cursor:pointer; font-size:15px; padding:2px 6px; line-height:1; border-radius:4px;" title="Close Dossier">✕</button>
                </div>
            </div>

            <!-- Macro Psychology Analysis -->
            <div style="margin-top:8px; font-size:12.5px; color:#334155; line-height:1.5; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:8px 12px;">
                <strong style="color:#0f172a;">Core Psychological Drive:</strong> ${dossier.macro_psychology || ''}
            </div>

            <!-- Thermodynamic Balance State -->
            ${thermHtml}
        </div>

        <!-- Tier 2: Star-by-Star Micro Dossier -->
        <div style="margin-top:14px;">
            <div style="font-family:Georgia, serif; font-size:14px; font-weight:700; color:#1e293b; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;">
                <span>✨ Constituent Stars in this Group (${starsList.length})</span>
                <span style="font-size:11.5px; font-weight:600; color:#64748b;">Micro Dossier &amp; Natal Occupancy</span>
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(320px, 1fr)); gap:12px;">
                ${starCardsHtml}
            </div>
        </div>
    `;
}

/**
 * Highlights the currently active temperament card and row in the UI.
 */
function updateTemperamentSelectionUI(container, activeGroup) {
    if (!container) return;

    // Ribbon cards
    container.querySelectorAll('.temperament-ribbon-card').forEach(card => {
        if (card.dataset.group === activeGroup) {
            card.style.outline = '2px solid #0f172a';
            card.style.outlineOffset = '1px';
            card.style.transform = 'scale(1.04)';
            card.style.boxShadow = '0 3px 8px rgba(0,0,0,0.15)';
            card.style.zIndex = '3';
        } else {
            card.style.outline = 'none';
            card.style.transform = 'none';
            card.style.boxShadow = 'none';
            card.style.zIndex = '1';
        }
    });

    // Deviation rows
    container.querySelectorAll('.temperament-deviation-row').forEach(row => {
        if (row.dataset.group === activeGroup) {
            row.style.background = '#f1f5f9';
            row.style.borderLeft = '3px solid #2563eb';
        } else {
            row.style.background = 'transparent';
            row.style.borderLeft = '3px solid transparent';
        }
    });
}

/**
 * Toggles or switches the interactive Temperament Dossier summary drawer.
 */
function selectTemperamentDossier(group, triggeringEl) {
    if (!group) return;

    let el = triggeringEl;
    if (!el && typeof window !== 'undefined' && window.event && window.event.target) {
        el = window.event.target;
    }

    const root = el ? el.closest('.temperament-distribution-container') : null;
    const containers = root ? [root] : document.querySelectorAll('.temperament-distribution-container');

    containers.forEach(cnt => {
        const drawer = cnt.querySelector('.temperament-dossier-drawer');
        if (!drawer) return;

        const currentGroup = drawer.dataset.activeGroup;
        const isCollapsed = drawer.style.display === 'none' || drawer.dataset.collapsed === 'true';

        // Clicking the currently active group toggles collapse
        if (currentGroup === group && !isCollapsed) {
            drawer.style.display = 'none';
            drawer.dataset.collapsed = 'true';
            updateTemperamentSelectionUI(cnt, null);
            return;
        }

        drawer.style.display = 'block';
        drawer.dataset.collapsed = 'false';
        drawer.dataset.activeGroup = group;

        const tb = cnt._temperamentBreakdown || (window.currentChartData?.report?.nakshatra_dominance?.temperament_breakdown) || [];
        const tbItem = tb.find(item => item.group === group) || {
            group: group,
            display_name: NAKSHATRA_TEMPERAMENT_DOSSIER[group]?.label || group,
            sanskrit: NAKSHATRA_TEMPERAMENT_DOSSIER[group]?.sanskrit || '',
            percentage: 14.3,
            points: 0,
            deviation_pct: 0
        };

        const chartData = cnt._chartData || window.currentChartData;
        drawer.innerHTML = renderTemperamentDrawerHtml(group, tbItem, chartData);
        updateTemperamentSelectionUI(cnt, group);

        if (el && typeof drawer.scrollIntoView === 'function') {
            drawer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    });
}

if (typeof window !== 'undefined') {
    window.selectTemperamentDossier = selectTemperamentDossier;
}

function switchReportTab(btn, tabId) {
    const widget = btn.closest('.widget-synthesis-report') || document.getElementById('widgetMaximizeModal');
    if (!widget) return;

    // Update buttons
    widget.querySelectorAll('.report-pill-btn').forEach(b => {
        b.classList.remove('active');
        b.style.background = 'transparent';
        b.style.color = '#6b5a4b';
    });
    btn.classList.add('active');
    btn.style.background = '#fffdfa';
    btn.style.color = '#4a3325';

    // Update panes
    widget.querySelectorAll('.report-tab-pane').forEach(p => {
        p.style.display = 'none';
        p.classList.remove('active');
    });
    const targetPane = widget.querySelector(`.tab-${tabId}`);
    if (targetPane) {
        targetPane.style.display = 'flex';
        targetPane.classList.add('active');
    }

    if (tabId === 'synthesis') {
        const selectPlanet = widget.querySelector('.select-synthesis-planet') || widget.querySelector('#select-synthesis-planet');
        if (selectPlanet && selectPlanet.value && window.currentChartData) {
            renderSynthesisTriptych(widget, selectPlanet.value, window.currentChartData);
        }
    }
}

function updateReportWidget(cell, chartData) {
    const currentData = chartData || window.currentChartData;
    if (!currentData) return;

    const report = currentData.report;
    if (!report) {
        const body = cell.querySelector('.report-body');
        if (body) {
            body.innerHTML = '<div style="padding:20px; text-align:center; color:#888; font-size:13.5px;">Calculating report ingredients...</div>';
        }
        return;
    }

    const polarity = report.polarity_core || {};
    const nakDominance = report.nakshatra_dominance || {};
    const operationalAxis = report.operational_axis || {};
    const envTally = report.environmental_tally || {};
    const planetRank = report.planetary_rankings || {};
    const synthesis = report.synthesis_ingredients || {};

    // 0. Update Toolbar Dominant Badge
    const domBadge = cell.querySelector('.report-dominant-badge');
    if (domBadge && nakDominance.dominant_nakshatra) {
        const dNak = nakDominance.dominant_nakshatra.nakshatra;
        const dPct = nakDominance.dominant_nakshatra.dominance_pct;
        const dTemp = nakDominance.dominant_temperament ? nakDominance.dominant_temperament.label.split(' ')[0] : '';
        domBadge.textContent = `★ Dominant: ${dNak} (${dPct}%) • ${dTemp}`;
    }

    // ==========================================
    // TAB 1: POLARITY CORE & STARS
    // ==========================================

    // 1.1 Polarity Relationship Banner
    const polBanner = cell.querySelector('.polarity-banner-container');
    if (polBanner && polarity.relationship) {
        const rel = polarity.relationship;
        let badgeColor = '#15803d';
        let badgeBg = '#f0fdf4';
        let borderColor = '#86efac';

        if (rel.friction_score > 65) {
            badgeColor = '#b91c1c';
            badgeBg = '#fef2f2';
            borderColor = '#fca5a5';
        } else if (rel.friction_score > 35) {
            badgeColor = '#b45309';
            badgeBg = '#fffbeb';
            borderColor = '#fde68a';
        }

        polBanner.innerHTML = `
            <div style="background:${badgeBg}; border:1.5px solid ${borderColor}; border-radius:6px; padding:10px 14px;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="font-size:15px; font-weight:700; color:#1e293b;">⚡ Polarity Core: ${rel.state}</span>
                        <span style="font-size:12px; font-weight:700; padding:2px 8px; border-radius:12px; background:${badgeColor}; color:#ffffff;">Friction: ${rel.friction_score}/100</span>
                    </div>
                    <div style="font-size:12.5px; font-weight:600; color:#475569;">
                        Rulers: <strong>${rel.ruler_asc}</strong> vs <strong>${rel.ruler_moon}</strong> (${rel.panchadha_maitri}) • Elements: <strong>${rel.elements}</strong> (${rel.tattva_status})
                    </div>
                </div>
                <div style="font-size:13px; color:#334155; margin-top:6px; line-height:1.45;">
                    ${rel.summary} <em>(${rel.tattva_note})</em>
                </div>
            </div>
        `;
    }

    // 1.2 Ascendant Nakshatra Card (Ahamkara / Action)
    const ascWrapper = cell.querySelector('.asc-nak-card-wrapper');
    if (ascWrapper && polarity.ascendant_nakshatra) {
        const a = polarity.ascendant_nakshatra;
        const lore = a.lore || {};
        ascWrapper.innerHTML = `
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-left:4px solid #2563eb; border-radius:6px; padding:12px; display:flex; flex-direction:column; gap:8px; height:100%;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div style="font-size:12px; font-weight:700; text-transform:uppercase; color:#2563eb; letter-spacing:0.5px;">🚩 Ascendant Star (Ahaṃkāra / Bodily Action)</div>
                        <div style="font-size:16px; font-weight:800; color:#0f172a; margin-top:2px;">${a.name} <span style="font-size:13px; font-weight:600; color:#64748b;">(Pada ${a.pada} in ${a.sign})</span></div>
                    </div>
                    <span style="font-size:12px; font-weight:700; padding:2px 8px; border-radius:4px; background:#eff6ff; color:#1d4ed8; border:1px solid #bfdbfe;">${a.group} Class</span>
                </div>
                <div style="font-size:12.5px; color:#475569; background:#f8fafc; border-radius:4px; padding:6px 8px;">
                    <div><strong>Star:</strong> ${lore.astronomical_star || '--'} • <strong>Span:</strong> ${lore.zodiacal_span || '--'}</div>
                    <div style="margin-top:2px;"><strong>Deity:</strong> ${lore.presiding_deity || '--'}</div>
                    <div style="margin-top:2px;"><strong>Symbol:</strong> ${lore.symbol_etymology || '--'}</div>
                    <div style="margin-top:2px;"><strong>Lord/Sublord:</strong> ${a.ruler} / ${a.sub_lord}</div>
                </div>
                <div style="font-size:13px; color:#1e293b; line-height:1.45; margin-top:2px;">
                    <strong>Core Action Drive:</strong> ${lore.core_psychology || '--'}
                </div>
                <div style="font-size:12.5px; color:#475569; margin-top:auto; padding-top:6px; border-top:1px dashed #e2e8f0;">
                    <strong>Real-World Spheres:</strong> ${lore.real_world_manifestations || '--'}
                </div>
            </div>
        `;
    }

    // 1.3 Moon Nakshatra Card (Manas / Perception)
    const moonWrapper = cell.querySelector('.moon-nak-card-wrapper');
    if (moonWrapper && polarity.moon_nakshatra) {
        const m = polarity.moon_nakshatra;
        const lore = m.lore || {};
        moonWrapper.innerHTML = `
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-left:4px solid #7c3aed; border-radius:6px; padding:12px; display:flex; flex-direction:column; gap:8px; height:100%;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div style="font-size:12px; font-weight:700; text-transform:uppercase; color:#7c3aed; letter-spacing:0.5px;">🌙 Moon Star (Manas / Sensory Mind &amp; Feeling)</div>
                        <div style="font-size:16px; font-weight:800; color:#0f172a; margin-top:2px;">${m.name} <span style="font-size:13px; font-weight:600; color:#64748b;">(Pada ${m.pada} in ${m.sign})</span></div>
                    </div>
                    <span style="font-size:12px; font-weight:700; padding:2px 8px; border-radius:4px; background:#f5f3ff; color:#6d28d9; border:1px solid #ddd6fe;">${m.group} Class</span>
                </div>
                <div style="font-size:12.5px; color:#475569; background:#f8fafc; border-radius:4px; padding:6px 8px;">
                    <div><strong>Star:</strong> ${lore.astronomical_star || '--'} • <strong>Span:</strong> ${lore.zodiacal_span || '--'}</div>
                    <div style="margin-top:2px;"><strong>Deity:</strong> ${lore.presiding_deity || '--'}</div>
                    <div style="margin-top:2px;"><strong>Symbol:</strong> ${lore.symbol_etymology || '--'}</div>
                    <div style="margin-top:2px;"><strong>Lord/Sublord:</strong> ${m.ruler} / ${m.sub_lord}</div>
                </div>
                <div style="font-size:13px; color:#1e293b; line-height:1.45; margin-top:2px;">
                    <strong>Varāhamihira Moon Reading:</strong> <em>"${lore.varahamihira_moon || '--'}"</em>
                </div>
                <div style="font-size:13px; color:#1e293b; line-height:1.45; margin-top:2px;">
                    <strong>Core Emotional Nature:</strong> ${lore.core_psychology || '--'}
                </div>
                <div style="font-size:12.5px; color:#475569; margin-top:auto; padding-top:6px; border-top:1px dashed #e2e8f0;">
                    <strong>Real-World Spheres:</strong> ${lore.real_world_manifestations || '--'}
                </div>
            </div>
        `;
    }

    // 1.4 Nakshatra Dominance Leaderboard (Prominence-Scaled Occupancy)
    const domContainer = cell.querySelector('.nakshatra-dominance-container');
    if (domContainer && nakDominance.leaderboard) {
        let rowsHtml = '';
        nakDominance.leaderboard.forEach(item => {
            const occBadges = item.occupants.map(o => {
                const promTag = (o.prominence && o.prominence !== 1.0) ? ` <span style="font-weight:600; color:#64748b; font-size:11px;">(P:${o.prominence})</span>` : '';
                return `<span style="font-weight:700; background:#e2e8f0; color:#1e293b; padding:1px 6px; border-radius:3px; font-size:12px;">${o.entity} ${o.weight}pt${promTag}</span>`;
            }).join(' ');
            
            rowsHtml += `
                <div style="margin-bottom:8px; padding-bottom:8px; border-bottom:1px solid #f1f5f9;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
                        <div style="display:flex; align-items:center; gap:6px;">
                            <strong style="font-size:13.5px; color:#0f172a;">#${item.rank} ${item.nakshatra}</strong>
                            <span style="font-size:12px; padding:1px 6px; border-radius:3px; background:#f1f5f9; color:#475569;">${item.group}</span>
                            <div style="display:inline-flex; gap:4px; margin-left:4px;">${occBadges}</div>
                        </div>
                        <div style="font-size:13px; font-weight:700; color:#1e293b;">
                            ${item.total_points} pts <span style="font-size:12px; font-weight:600; color:#64748b;">(${item.dominance_pct}%)</span>
                        </div>
                    </div>
                    <div style="width:100%; height:8px; background:#e2e8f0; border-radius:4px; overflow:hidden;">
                        <div style="height:100%; width:${Math.min(100, item.dominance_pct)}%; background:#3b82f6; border-radius:4px;"></div>
                    </div>
                </div>
            `;
        });

        domContainer.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-size:14px; font-weight:700; color:#1e293b;">📊 Nakshatra Dominance Leaderboard</span>
                <span style="font-size:12px; color:#64748b;">Prominence-Scaled Occupancy: Moon=8×P • Lagna=4pt • Sun=2×P • Grahas=1×P</span>
            </div>
            ${rowsHtml}
        `;
    }

    // 1.5 Balance of Nakṣatra Types (Vic DiCara Style Bi-Directional Chart)
    const tempContainer = cell.querySelector('.temperament-distribution-container');
    if (tempContainer && nakDominance.temperament_breakdown) {
        const tb = nakDominance.temperament_breakdown;
        tempContainer._temperamentBreakdown = tb;
        tempContainer._chartData = currentData;

        // 1. Top Proportional Ribbon
        let ribbonCardsHtml = '';
        const maxPct = Math.max(...tb.map(t => t.percentage), 14.3);

        tb.forEach(t => {
            const isDominant = (t.percentage === maxPct && t.percentage > 18.0);
            const isSevereDeficit = (t.percentage <= 2.0);
            
            // Highlight dominant (taller & vivid green) and deficit (pale coral)
            let cardBg = t.percentage > 14.3 ? '#86efac' : '#fecaca';
            let cardText = t.percentage > 14.3 ? '#14532d' : '#7f1d1d';
            let minH = isDominant ? '48px' : '38px';
            let border = isDominant ? '2px solid #16a34a' : '1px solid rgba(0,0,0,0.08)';

            if (isSevereDeficit) {
                cardBg = '#fee2e2';
                cardText = '#991b1b';
            }

            const dossier = NAKSHATRA_TEMPERAMENT_DOSSIER[t.group] || {};
            const starsList = (dossier.nakshatras || []).join(', ');
            const firstPos = (dossier.positives && dossier.positives[0]) || '';
            const firstNeg = (dossier.negatives && dossier.negatives[0]) || '';
            const sanskritLabel = dossier.sanskrit || t.sanskrit || '';

            // Clean title string and rich HTML tooltip
            const rawTitleText = `${t.display_name} (${sanskritLabel}) • Stars: ${starsList}\n\n(+) ${firstPos}\n(-) ${firstNeg}`;
            const richTooltipHtml = `<div style="font-family:Georgia, serif; font-size:13.5px; font-weight:700; color:#f8fafc; border-bottom:1px solid rgba(255,255,255,0.2); padding-bottom:4px; margin-bottom:6px;">${t.display_name} (${sanskritLabel}) Class</div><div style="font-size:12px; color:#cbd5e1; margin-bottom:4px;"><strong style="color:#ffffff;">Member Stars:</strong> ${starsList}</div><div style="font-size:12px; color:#94a3b8; margin-bottom:6px; font-style:italic;">"${dossier.essence || ''}"</div><div style="font-size:12px; color:#86efac; margin-bottom:4px; line-height:1.35;"><strong>(+) Integrated:</strong> ${firstPos}</div><div style="font-size:12px; color:#fca5a5; line-height:1.35;"><strong>(-) Shadow:</strong> ${firstNeg}</div>`;

            ribbonCardsHtml += `
                <div class="temperament-ribbon-card tooltip-target"
                     data-group="${t.group}"
                     data-tooltip="${richTooltipHtml.replace(/"/g, '&quot;')}"
                     title="${rawTitleText.replace(/"/g, '&quot;')}"
                     onclick="selectTemperamentDossier('${t.group}')"
                     style="flex: ${Math.max(t.percentage, 7)}; min-height:${minH}; background:${cardBg}; color:${cardText}; border:${border}; border-radius:6px; padding:4px 6px; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; cursor:pointer; transition:all 0.2s ease; user-select:none;">
                    <span style="font-size:11.5px; font-weight:700; white-space:nowrap;">${t.display_name}</span>
                    <span style="font-size:11px; font-weight:600; opacity:0.9;">${t.percentage}%</span>
                </div>
            `;
        });

        // 2. Bottom Bi-Directional Deviation Rows
        // Center is 14.3% baseline (50% position).
        // Category label is centered above the bar (matching Vic DiCara's chart).
        const MAX_RANGE = 25.0; // +/- 25% deviation covers extreme charts
        const MAX_BAR_WIDTH_PCT = 36; // Leaves 14% breathing room for outer percentage labels

        let deviationRowsHtml = '';
        tb.forEach(t => {
            const dev = t.deviation_pct; // e.g. +12.7% or -13.3%
            const isRight = dev >= 0;
            const absDev = Math.abs(dev);
            
            // Calculate proportional bar width with safe bounds
            let barWidthPct = Math.min(MAX_BAR_WIDTH_PCT, (absDev / MAX_RANGE) * MAX_BAR_WIDTH_PCT);
            if (absDev > 0.1 && barWidthPct < 2.0) {
                barWidthPct = 2.0; // Minimum visible bar indicator
            }

            const barColor = isRight ? '#4ade80' : '#f87171'; // Green for surplus, Salmon/Coral for deficit
            const valueColor = isRight ? '#16a34a' : '#dc2626';

            const dossier = NAKSHATRA_TEMPERAMENT_DOSSIER[t.group] || {};
            const starsList = (dossier.nakshatras || []).join(', ');
            const firstPos = (dossier.positives && dossier.positives[0]) || '';
            const firstNeg = (dossier.negatives && dossier.negatives[0]) || '';
            const sanskritLabel = dossier.sanskrit || t.sanskrit || '';

            const rawTitleText = `${t.display_name} (${sanskritLabel}) • Stars: ${starsList}\n\n(+) ${firstPos}\n(-) ${firstNeg}`;
            const richTooltipHtml = `<div style="font-family:Georgia, serif; font-size:13.5px; font-weight:700; color:#f8fafc; border-bottom:1px solid rgba(255,255,255,0.2); padding-bottom:4px; margin-bottom:6px;">${t.display_name} (${sanskritLabel}) Class</div><div style="font-size:12px; color:#cbd5e1; margin-bottom:4px;"><strong style="color:#ffffff;">Member Stars:</strong> ${starsList}</div><div style="font-size:12px; color:#94a3b8; margin-bottom:6px; font-style:italic;">"${dossier.essence || ''}"</div><div style="font-size:12px; color:#86efac; margin-bottom:4px; line-height:1.35;"><strong>(+) Integrated:</strong> ${firstPos}</div><div style="font-size:12px; color:#fca5a5; line-height:1.35;"><strong>(-) Shadow:</strong> ${firstNeg}</div>`;

            deviationRowsHtml += `
                <div class="temperament-deviation-row tooltip-target"
                     data-group="${t.group}"
                     data-tooltip="${richTooltipHtml.replace(/"/g, '&quot;')}"
                     title="${rawTitleText.replace(/"/g, '&quot;')}"
                     onclick="selectTemperamentDossier('${t.group}')"
                     style="position:relative; margin-bottom:8px; cursor:pointer; padding:2px 4px; border-radius:4px; border-left:3px solid transparent; transition:all 0.2s ease;">
                    <!-- Centered Category Label above the bar (matches reference chart) -->
                    <div style="text-align:center; line-height:1.2; margin-bottom:2px;">
                        <span style="font-size:12px; font-weight:700; color:#1e293b; font-family:Georgia, serif; background:rgba(255,255,255,0.9); padding:0 6px; border-radius:3px;">
                            ${t.display_name}
                        </span>
                    </div>

                    <!-- Horizontal Bar & Percentage Row -->
                    <div style="position:relative; height:16px; display:flex; align-items:center;">
                        <!-- Left Deficit Bar (extends left from 50% baseline) -->
                        ${!isRight ? `
                            <div style="position:absolute; right:50%; width:${barWidthPct}%; height:13px; background:${barColor}; border-radius:7px 0 0 7px; box-shadow:0 1px 2px rgba(0,0,0,0.06);"></div>
                            <span style="position:absolute; right:calc(50% + ${barWidthPct}% + 6px); font-size:11px; font-weight:700; color:${valueColor}; white-space:nowrap;">${t.percentage}%</span>
                        ` : ''}

                        <!-- Right Surplus Bar (extends right from 50% baseline) -->
                        ${isRight ? `
                            <div style="position:absolute; left:50%; width:${barWidthPct}%; height:13px; background:${barColor}; border-radius:0 7px 7px 0; box-shadow:0 1px 2px rgba(0,0,0,0.06);"></div>
                            <span style="position:absolute; left:calc(50% + ${barWidthPct}% + 6px); font-size:11px; font-weight:700; color:${valueColor}; white-space:nowrap;">${t.percentage}%</span>
                        ` : ''}
                    </div>
                </div>
            `;
        });

        tempContainer.innerHTML = `
            <div style="font-size:15px; font-weight:700; color:#1e293b; margin-bottom:10px; font-family:Georgia, serif; display:flex; justify-content:space-between; align-items:center;">
                <span>Balance of Nakṣatra Types</span>
                <span style="font-size:11.5px; font-weight:600; color:#64748b; font-family:sans-serif;">Baseline: 14.3% per type</span>
            </div>

            <!-- Top Proportional Ribbon -->
            <div style="display:flex; gap:4px; align-items:flex-end; margin-bottom:14px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:6px;">
                ${ribbonCardsHtml}
            </div>

            <!-- Bottom Bi-Directional Deviation Graph -->
            <div style="position:relative; background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:14px 10px; overflow:hidden;">
                <!-- Vertical Background Grid Lines -->
                <div style="position:absolute; top:0; bottom:0; left:14%; width:1px; background:#f1f5f9;"></div>
                <div style="position:absolute; top:0; bottom:0; left:26%; width:1px; background:#f1f5f9;"></div>
                <div style="position:absolute; top:0; bottom:0; left:38%; width:1px; background:#f1f5f9;"></div>
                <div style="position:absolute; top:0; bottom:0; left:50%; width:2px; background:#1e293b; z-index:1;"></div> <!-- Black Center Baseline -->
                <div style="position:absolute; top:0; bottom:0; left:62%; width:1px; background:#f1f5f9;"></div>
                <div style="position:absolute; top:0; bottom:0; left:74%; width:1px; background:#f1f5f9;"></div>
                <div style="position:absolute; top:0; bottom:0; left:86%; width:1px; background:#f1f5f9;"></div>

                <!-- Subtle Background Tints -->
                <div style="position:absolute; top:0; bottom:0; left:0; width:50%; background:rgba(239, 68, 68, 0.02); pointer-events:none;"></div>
                <div style="position:absolute; top:0; bottom:0; left:50%; width:50%; background:rgba(34, 197, 94, 0.02); pointer-events:none;"></div>

                <!-- Rows -->
                <div style="position:relative; z-index:2;">
                    ${deviationRowsHtml}
                </div>
            </div>

            <!-- Interactive Temperament Dossier Drawer -->
            <div class="temperament-dossier-drawer" style="margin-top: 12px; transition: all 0.3s ease; background: #fffdfa; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px;"></div>
        `;

        // Load dossier for the native's Dominant Temperament by default
        const dominantGroup = (nakDominance.dominant_temperament && nakDominance.dominant_temperament.group)
            ? nakDominance.dominant_temperament.group
            : (tb[0]?.group || 'Chara');
        const drawer = tempContainer.querySelector('.temperament-dossier-drawer');
        if (drawer) {
            drawer.style.display = 'block';
            drawer.dataset.collapsed = 'false';
            drawer.dataset.activeGroup = dominantGroup;
            const domTbItem = tb.find(item => item.group === dominantGroup) || tb[0];
            drawer.innerHTML = renderTemperamentDrawerHtml(dominantGroup, domTbItem, currentData);
            updateTemperamentSelectionUI(tempContainer, dominantGroup);
        }
    }

    // 1.6 All Occupied Nakshatras Table
    const tableContainer = cell.querySelector('.all-nakshatras-table-container');
    if (tableContainer) {
        const nakGrahas = currentData.nakshatras ? currentData.nakshatras.grahas || {} : {};
        const d1Grahas = currentData.vargas && currentData.vargas.D1 ? currentData.vargas.D1.grahas || {} : {};
        const d1Lagna = currentData.vargas && currentData.vargas.D1 ? currentData.vargas.D1.lagna || {} : {};

        const nakGroupMap = {};
        if (nakDominance.leaderboard) {
            nakDominance.leaderboard.forEach(item => {
                nakGroupMap[item.nakshatra] = item.group;
            });
        }

        const entitiesList = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
        let trHtml = '';

        entitiesList.forEach(ent => {
            const nInfo = nakGrahas[ent] || {};
            const nakName = nInfo.nakshatra || '--';
            const grp = nakGroupMap[nakName] || '--';
            const sign = ent === "Lagna" ? (d1Lagna.sign || '--') : (d1Grahas[ent]?.sign || '--');
            const deg = ent === "Lagna" ? (d1Lagna.degree_0_to_30?.toFixed(2) || '--') : (d1Grahas[ent]?.degree_0_to_30?.toFixed(2) || '--');

            trHtml += `
                <tr style="border-bottom:1px solid #f1f5f9; font-size:13px;">
                    <td style="padding:6px 8px; font-weight:700; color:#1e293b;">${ent}</td>
                    <td style="padding:6px 8px; color:#475569;">${sign} ${deg}°</td>
                    <td style="padding:6px 8px; font-weight:600; color:#0f172a;">${nakName}</td>
                    <td style="padding:6px 8px; color:#475569;">Pada ${nInfo.pada || '--'}</td>
                    <td style="padding:6px 8px; color:#475569;">${nInfo.nakshatra_lord || '--'} / ${nInfo.sub_lord || '--'}</td>
                    <td style="padding:6px 8px;"><span style="font-size:12px; font-weight:600; padding:1px 6px; border-radius:3px; background:#f1f5f9; color:#475569;">${grp}</span></td>
                </tr>
            `;
        });

        tableContainer.innerHTML = `
            <div style="font-size:14px; font-weight:700; color:#1e293b; margin-bottom:8px;">✨ Planetary Nakshatras &amp; Overlords</div>
            <table style="width:100%; border-collapse:collapse; text-align:left;">
                <thead>
                    <tr style="background:#f8fafc; border-bottom:1.5px solid #cbd5e1; font-size:12px; color:#475569; text-transform:uppercase;">
                        <th style="padding:6px 8px;">Body</th>
                        <th style="padding:6px 8px;">Rāśi Position</th>
                        <th style="padding:6px 8px;">Nakshatra</th>
                        <th style="padding:6px 8px;">Pada</th>
                        <th style="padding:6px 8px;">Lord / Sublord</th>
                        <th style="padding:6px 8px;">Temperament</th>
                    </tr>
                </thead>
                <tbody>${trHtml}</tbody>
            </table>
        `;
    }

    // ==========================================
    // TAB 2: ELEMENTS & OPERATIONAL AXIS
    // ==========================================
    const axisContainer = cell.querySelector('.operational-axis-container');
    if (axisContainer && operationalAxis.rashi_lagna) {
        const r = operationalAxis.rashi_lagna;
        const n = operationalAxis.navamsha_lagna;
        const vBadge = operationalAxis.is_vargottama 
            ? `<div style="background:#f0fdf4; border:1px solid #86efac; border-radius:4px; padding:6px 10px; margin-top:8px; font-size:13px; font-weight:700; color:#15803d;">🌟 VARGOTTAMA LAGNA DETECTED: +30% Vitality, Inner Consistency &amp; Resilience</div>` 
            : '';

        axisContainer.innerHTML = `
            <div style="font-size:14px; font-weight:700; color:#1e293b; margin-bottom:8px;">🌲 Operational Axis: Rāśi Tree vs. Navāṁśa Fruit</div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:10px;">
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:12px; font-weight:700; color:#2563eb; text-transform:uppercase;">D1 Rising Rāśi (The Outer Tree)</div>
                    <div style="font-size:15px; font-weight:700; color:#0f172a; margin-top:2px;">${r.sign} (Lord: ${r.lord})</div>
                    <div style="font-size:12.5px; color:#475569; margin-top:4px;">${r.element} Element • ${r.guna} • ${r.rising_mode}</div>
                    <div style="font-size:13px; color:#334155; margin-top:6px; line-height:1.4;">${r.interpretation}</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:12px; font-weight:700; color:#7c3aed; text-transform:uppercase;">D9 Rising Navāṁśa (The Inner Fruit)</div>
                    <div style="font-size:15px; font-weight:700; color:#0f172a; margin-top:2px;">${n.sign} (Lord: ${n.lord})</div>
                    <div style="font-size:12.5px; color:#475569; margin-top:4px;">${n.element} Element • ${n.guna} • Lord D1 Dignity: ${n.lord_d1_dignity}</div>
                    <div style="font-size:13px; color:#334155; margin-top:6px; line-height:1.4;">${n.interpretation}</div>
                </div>
            </div>
            ${vBadge}
        `;
    }

    // 2.2 Balance of Environmental Harmonics (Bi-Directional Graphic with Mode Switcher)
    const envDistContainer = cell.querySelector('.environmental-distribution-container');
    if (envDistContainer && envTally) {
        if (!envDistContainer.dataset.envMode) {
            envDistContainer.dataset.envMode = 'elements';
        }

        const renderEnvDistribution = (mode) => {
            envDistContainer.dataset.envMode = mode;
            let title = 'Balance of Four Elements (Tattvas)';
            let baselineLabel = 'Equilibrium Baseline: 25.0% (1/4th)';
            let baselinePct = 25.0;
            let items = [];

            if (mode === 'elements') {
                title = '🔥 Balance of Four Elements (Tattvas)';
                baselineLabel = 'Equilibrium Baseline: 25.0% (1/4th)';
                baselinePct = 25.0;
                items = envTally.elements?.breakdown || [];
            } else if (mode === 'gunas') {
                title = '🌀 Balance of Three Guṇas (Modalities)';
                baselineLabel = 'Equilibrium Baseline: 33.3% (1/3rd)';
                baselinePct = 33.3;
                items = envTally.gunas?.breakdown || [];
            } else if (mode === 'doshas') {
                title = '🍵 Balance of Ayurvedic Doshas (Prakṛti)';
                baselineLabel = 'Equilibrium Baseline: 33.3% (1/3rd)';
                baselinePct = 33.3;
                items = envTally.ayurvedic_doshas?.breakdown || [];
            }

            if (!items || items.length === 0) return;

            // 1. Top Proportional Ribbon
            let ribbonCardsHtml = '';
            const maxPct = Math.max(...items.map(t => t.percentage), baselinePct);

            items.forEach(t => {
                const isDominant = (t.percentage === maxPct && t.percentage > baselinePct);
                const isSevereDeficit = (t.percentage <= 5.0);

                let cardBg = t.percentage > baselinePct ? '#86efac' : '#fecaca';
                let cardText = t.percentage > baselinePct ? '#14532d' : '#7f1d1d';
                let minH = isDominant ? '48px' : '38px';
                let border = isDominant ? '2px solid #16a34a' : '1px solid rgba(0,0,0,0.08)';

                if (isSevereDeficit) {
                    cardBg = '#fee2e2';
                    cardText = '#991b1b';
                }

                ribbonCardsHtml += `
                    <div style="flex: ${Math.max(t.percentage, 8)}; min-height:${minH}; background:${cardBg}; color:${cardText}; border:${border}; border-radius:6px; padding:4px 6px; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; transition:all 0.2s ease;">
                        <span style="font-size:11.5px; font-weight:700; white-space:nowrap;">${t.icon || ''} ${t.display_name}</span>
                        <span style="font-size:11px; font-weight:600; opacity:0.9;">${t.percentage}% <span style="font-size:10px; opacity:0.8;">(${t.points} pt)</span></span>
                    </div>
                `;
            });

            // 2. Bottom Bi-Directional Deviation Rows
            const MAX_RANGE = 35.0; // +/- 35% covers extreme shifts
            const MAX_BAR_WIDTH_PCT = 36; // Leaves 14% breathing room for labels

            let deviationRowsHtml = '';
            items.forEach(t => {
                const dev = t.deviation_pct; // e.g. +45.0% or -25.0%
                const isRight = dev >= 0;
                const absDev = Math.abs(dev);

                let barWidthPct = Math.min(MAX_BAR_WIDTH_PCT, (absDev / MAX_RANGE) * MAX_BAR_WIDTH_PCT);
                if (absDev > 0.1 && barWidthPct < 2.0) {
                    barWidthPct = 2.0;
                }

                const barColor = isRight ? '#4ade80' : '#f87171'; // Green for surplus, Salmon for deficit
                const valueColor = isRight ? '#16a34a' : '#dc2626';
                const signPrefix = dev > 0 ? '+' : '';
                const d1Info = (t.d1_count !== undefined) ? ` • D1: ${t.d1_count}` : '';

                deviationRowsHtml += `
                    <div style="position:relative; margin-bottom:10px;">
                        <!-- Centered Category Label above the bar -->
                        <div style="text-align:center; line-height:1.2; margin-bottom:2px;">
                            <span style="font-size:12px; font-weight:700; color:#1e293b; font-family:Georgia, serif; background:rgba(255,255,255,0.95); padding:1px 8px; border-radius:3px; border:1px solid #f1f5f9; box-shadow:0 1px 2px rgba(0,0,0,0.03);">
                                ${t.icon || ''} ${t.display_name} <span style="font-size:11px; color:#64748b; font-weight:500;">(${t.sanskrit || ''})</span>
                            </span>
                        </div>

                        <!-- Horizontal Bar & Percentage Row -->
                        <div style="position:relative; height:18px; display:flex; align-items:center;">
                            <!-- Left Deficit Bar -->
                            ${!isRight ? `
                                <div style="position:absolute; right:50%; width:${barWidthPct}%; height:14px; background:${barColor}; border-radius:7px 0 0 7px; box-shadow:0 1px 2px rgba(0,0,0,0.06);"></div>
                                <span style="position:absolute; right:calc(50% + ${barWidthPct}% + 6px); font-size:11px; font-weight:700; color:${valueColor}; white-space:nowrap;">
                                    ${t.percentage}% <span style="font-size:10px; font-weight:600; opacity:0.85;">(${signPrefix}${dev}% | ${t.points} pt${d1Info})</span>
                                </span>
                            ` : ''}

                            <!-- Right Surplus Bar -->
                            ${isRight ? `
                                <div style="position:absolute; left:50%; width:${barWidthPct}%; height:14px; background:${barColor}; border-radius:0 7px 7px 0; box-shadow:0 1px 2px rgba(0,0,0,0.06);"></div>
                                <span style="position:absolute; left:calc(50% + ${barWidthPct}% + 6px); font-size:11px; font-weight:700; color:${valueColor}; white-space:nowrap;">
                                    ${t.percentage}% <span style="font-size:10px; font-weight:600; opacity:0.85;">(${signPrefix}${dev}% | ${t.points} pt${d1Info})</span>
                                </span>
                            ` : ''}
                        </div>
                    </div>
                `;
            });

            // Pills active styles
            const activeElemStyle = mode === 'elements' ? 'background:#ffffff; color:#1e293b; font-weight:700; box-shadow:0 1px 2px rgba(0,0,0,0.08);' : 'background:transparent; color:#64748b; font-weight:600;';
            const activeGunaStyle = mode === 'gunas' ? 'background:#ffffff; color:#1e293b; font-weight:700; box-shadow:0 1px 2px rgba(0,0,0,0.08);' : 'background:transparent; color:#64748b; font-weight:600;';
            const activeDoshaStyle = mode === 'doshas' ? 'background:#ffffff; color:#1e293b; font-weight:700; box-shadow:0 1px 2px rgba(0,0,0,0.08);' : 'background:transparent; color:#64748b; font-weight:600;';

            envDistContainer.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:10px;">
                    <div>
                        <div style="font-size:15px; font-weight:700; color:#1e293b; font-family:Georgia, serif;">${title}</div>
                        <div style="font-size:11.5px; font-weight:600; color:#64748b; font-family:sans-serif; margin-top:1px;">
                            ${baselineLabel} • Ṣaḍvarga (20-pt Harmonic Matrix)
                        </div>
                    </div>

                    <!-- Mode Switcher Pills -->
                    <div class="env-mode-pills" style="display:inline-flex; background:#f1f5f9; border:1px solid #e2e8f0; border-radius:6px; padding:2px; gap:2px;">
                        <button type="button" class="btn-env-mode-elem" style="border:none; border-radius:4px; padding:3px 9px; font-size:11.5px; cursor:pointer; ${activeElemStyle}">🔥 Elements</button>
                        <button type="button" class="btn-env-mode-guna" style="border:none; border-radius:4px; padding:3px 9px; font-size:11.5px; cursor:pointer; ${activeGunaStyle}">🌀 Guṇas</button>
                        <button type="button" class="btn-env-mode-dosha" style="border:none; border-radius:4px; padding:3px 9px; font-size:11.5px; cursor:pointer; ${activeDoshaStyle}">🍵 Doshas</button>
                    </div>
                </div>

                <!-- Top Proportional Ribbon -->
                <div style="display:flex; gap:4px; align-items:flex-end; margin-bottom:14px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:6px;">
                    ${ribbonCardsHtml}
                </div>

                <!-- Bottom Bi-Directional Deviation Graph -->
                <div style="position:relative; background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:14px 10px; overflow:hidden;">
                    <!-- Vertical Background Grid Lines -->
                    <div style="position:absolute; top:0; bottom:0; left:14%; width:1px; background:#f1f5f9;"></div>
                    <div style="position:absolute; top:0; bottom:0; left:26%; width:1px; background:#f1f5f9;"></div>
                    <div style="position:absolute; top:0; bottom:0; left:38%; width:1px; background:#f1f5f9;"></div>
                    <div style="position:absolute; top:0; bottom:0; left:50%; width:2px; background:#1e293b; z-index:1;"></div> <!-- Black Center Baseline -->
                    <div style="position:absolute; top:0; bottom:0; left:62%; width:1px; background:#f1f5f9;"></div>
                    <div style="position:absolute; top:0; bottom:0; left:74%; width:1px; background:#f1f5f9;"></div>
                    <div style="position:absolute; top:0; bottom:0; left:86%; width:1px; background:#f1f5f9;"></div>

                    <!-- Subtle Background Tints -->
                    <div style="position:absolute; top:0; bottom:0; left:0; width:50%; background:rgba(239, 68, 68, 0.02); pointer-events:none;"></div>
                    <div style="position:absolute; top:0; bottom:0; left:50%; width:50%; background:rgba(34, 197, 94, 0.02); pointer-events:none;"></div>

                    <!-- Rows -->
                    <div style="position:relative; z-index:2;">
                        ${deviationRowsHtml}
                    </div>
                </div>
            `;

            // Attach click listeners to pills
            const btnElem = envDistContainer.querySelector('.btn-env-mode-elem');
            const btnGuna = envDistContainer.querySelector('.btn-env-mode-guna');
            const btnDosha = envDistContainer.querySelector('.btn-env-mode-dosha');

            if (btnElem) btnElem.onclick = (e) => { e.stopPropagation(); renderEnvDistribution('elements'); };
            if (btnGuna) btnGuna.onclick = (e) => { e.stopPropagation(); renderEnvDistribution('gunas'); };
            if (btnDosha) btnDosha.onclick = (e) => { e.stopPropagation(); renderEnvDistribution('doshas'); };
        };

        // Initial render using stored or default mode
        renderEnvDistribution(envDistContainer.dataset.envMode || 'elements');
    }

    const envContainer = cell.querySelector('.environmental-tallies-container');
    if (envContainer && envTally.elements) {
        const e = envTally.elements;
        const g = envTally.gunas;
        const d = envTally.ayurvedic_doshas;

        envContainer.innerHTML = `
            <div style="font-size:14px; font-weight:700; color:#1e293b; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                <span>🌿 Macro Environmental Tally (Ṣaḍvarga Weighted)</span>
                <span style="font-size:11.5px; font-weight:600; color:#64748b;">D1:6 • D9:5 • D3:4 • D2:2 • D12:2 • D30:1</span>
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:10px;">
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:13px; font-weight:700; color:#0f172a; margin-bottom:4px;">🔥 Five Great Elements (Tattvas)</div>
                    <div style="font-size:12.5px; color:#475569;">
                        <div>Fire: <strong>${e.percentages.Fire}%</strong> <span style="font-size:11.5px; color:#64748b;">(${e.points.Fire} pt | D1: ${e.counts.Fire})</span></div>
                        <div>Earth: <strong>${e.percentages.Earth}%</strong> <span style="font-size:11.5px; color:#64748b;">(${e.points.Earth} pt | D1: ${e.counts.Earth})</span></div>
                        <div>Air: <strong>${e.percentages.Air}%</strong> <span style="font-size:11.5px; color:#64748b;">(${e.points.Air} pt | D1: ${e.counts.Air})</span></div>
                        <div>Water: <strong>${e.percentages.Water}%</strong> <span style="font-size:11.5px; color:#64748b;">(${e.points.Water} pt | D1: ${e.counts.Water})</span></div>
                    </div>
                    <div style="font-size:13px; font-weight:700; color:#b91c1c; margin-top:6px;">Dominant Tattva: ${e.dominant}</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:13px; font-weight:700; color:#0f172a; margin-bottom:4px;">🌀 Three Guṇas (Modality)</div>
                    <div style="font-size:12.5px; color:#475569;">
                        <div>Rajas (Movable): <strong>${g.percentages['Rajas (Movable)']}%</strong> <span style="font-size:11.5px; color:#64748b;">(${g.points['Rajas (Movable)']} pt)</span></div>
                        <div>Tamas (Fixed): <strong>${g.percentages['Tamas (Fixed)']}%</strong> <span style="font-size:11.5px; color:#64748b;">(${g.points['Tamas (Fixed)']} pt)</span></div>
                        <div>Sattva (Dual): <strong>${g.percentages['Sattva (Dual)']}%</strong> <span style="font-size:11.5px; color:#64748b;">(${g.points['Sattva (Dual)']} pt)</span></div>
                    </div>
                    <div style="font-size:13px; font-weight:700; color:#0d9488; margin-top:6px;">Dominant Guṇa: ${g.dominant}</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:13px; font-weight:700; color:#0f172a; margin-bottom:4px;">🍵 Ayurvedic Constitution (Prakṛti)</div>
                    <div style="font-size:12.5px; color:#475569;">
                        <div>Vāta (Air): <strong>${d.percentages.Vata}%</strong> <span style="font-size:11.5px; color:#64748b;">(${d.points.Vata} pt)</span></div>
                        <div>Pitta (Fire): <strong>${d.percentages.Pitta}%</strong> <span style="font-size:11.5px; color:#64748b;">(${d.points.Pitta} pt)</span></div>
                        <div>Kapha (Earth/Water): <strong>${d.percentages.Kapha}%</strong> <span style="font-size:11.5px; color:#64748b;">(${d.points.Kapha} pt)</span></div>
                    </div>
                    <div style="font-size:13px; font-weight:700; color:#2563eb; margin-top:6px;">Prakṛti Baseline: ${d.dominant}</div>
                </div>
            </div>
        `;
    }

    // ==========================================
    // TAB 3: PLANETARY PROMINENCE & DIGNITY
    // ==========================================
    const cmdSpotlight = cell.querySelector('.commander-spotlight-container');
    const formatAvastha = val => (val && typeof val === 'object') ? (val.state || val.name || '--') : (val || '--');

    if (cmdSpotlight && planetRank.chart_commander) {
        const c = planetRank.chart_commander;
        const dMood = formatAvastha(c.dignity_mood);
        const mat = formatAvastha(c.maturity);

        cmdSpotlight.innerHTML = `
            <div style="background:#fffbeb; border:1.5px solid #fde68a; border-radius:6px; padding:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-size:12px; font-weight:700; color:#92400e; text-transform:uppercase;">👑 #1 Chart Commander (Highest Stage Volume)</div>
                        <div style="font-size:16px; font-weight:800; color:#78350f; margin-top:2px;">${c.planet} in House ${c.house} (${c.sign})</div>
                    </div>
                    <span style="font-size:13px; font-weight:700; padding:2px 8px; border-radius:4px; background:#fef3c7; color:#92400e; border:1px solid #fcd34d;">Score: ${c.prominence_score}</span>
                </div>
                <div style="font-size:13px; color:#451a03; margin-top:6px; line-height:1.45;">
                    Commands the chart via <strong>${c.shadbala_rupas} Rupas</strong> (${c.shadbala_ratio}x required Shadbala) with access bonuses: <em>${c.opportunity_reasons.join(', ') || 'Angular strength'}</em>. Dignity Mood: <strong>${dMood}</strong> (${mat} maturity, Vimshopaka: ${c.vimshopak_score}/20).
                </div>
            </div>
        `;
    }

    const promTable = cell.querySelector('.prominence-table-container');
    if (promTable && planetRank.leaderboard) {
        let pTrHtml = '';
        planetRank.leaderboard.forEach(p => {
            const pMood = formatAvastha(p.dignity_mood);
            pTrHtml += `
                <tr style="border-bottom:1px solid #f1f5f9; font-size:13px;">
                    <td style="padding:6px 8px; font-weight:700; color:#1e293b;">#${p.rank} ${p.planet}</td>
                    <td style="padding:6px 8px; color:#475569;">House ${p.house} (${p.sign})</td>
                    <td style="padding:6px 8px; font-weight:700; color:#0f172a;">${p.prominence_score}</td>
                    <td style="padding:6px 8px; color:#475569;">${p.shadbala_rupas} (${p.shadbala_ratio}x)</td>
                    <td style="padding:6px 8px; color:#0284c7; font-size:12px;">${p.opportunity_reasons.join(', ') || '--'}</td>
                    <td style="padding:6px 8px; font-weight:600; color:#334155;">${pMood}</td>
                    <td style="padding:6px 8px; color:#475569;">${p.vimshopak_score}</td>
                    <td style="padding:6px 8px;"><span style="font-size:12px; font-weight:700; padding:1px 6px; border-radius:3px; background:${p.net_scale_score >= 0 ? '#f0fdf4' : '#fef2f2'}; color:${p.net_scale_score >= 0 ? '#15803d' : '#b91c1c'};">${p.net_scale_score}%</span></td>
                </tr>
            `;
        });

        promTable.innerHTML = `
            <div style="font-size:14px; font-weight:700; color:#1e293b; margin-bottom:8px;">📊 Planetary Prominence vs. Dignity Leaderboard</div>
            <table style="width:100%; border-collapse:collapse; text-align:left;">
                <thead>
                    <tr style="background:#f8fafc; border-bottom:1.5px solid #cbd5e1; font-size:12px; color:#475569; text-transform:uppercase;">
                        <th style="padding:6px 8px;">Rank / Graha</th>
                        <th style="padding:6px 8px;">Placement</th>
                        <th style="padding:6px 8px;">Prominence Score</th>
                        <th style="padding:6px 8px;">Shadbala (SBR)</th>
                        <th style="padding:6px 8px;">Opportunity Center</th>
                        <th style="padding:6px 8px;">Dignity Mood</th>
                        <th style="padding:6px 8px;">Vimshopaka</th>
                        <th style="padding:6px 8px;">Net Scale</th>
                    </tr>
                </thead>
                <tbody>${pTrHtml}</tbody>
            </table>
        `;
    }

    // ==========================================
    // TAB 4: SYNTHESIS DESK
    // ==========================================
    const synDesk = cell.querySelector('.synthesis-desk-container');
    if (synDesk && synthesis.action_mode) {
        synDesk.innerHTML = `
            <div style="font-size:14px; font-weight:700; color:#1e293b; margin-bottom:10px;">🧪 Synthesis Desk: The Master Astrological Recipe</div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:10px;">
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:12px; font-weight:700; color:#64748b; text-transform:uppercase;">1. Bodily Action Vehicle</div>
                    <div style="font-size:15px; font-weight:700; color:#0f172a; margin-top:2px;">${synthesis.action_mode} (${synthesis.action_group})</div>
                    <div style="font-size:12.5px; color:#475569; margin-top:4px;">How you project energy and initiate outer worldly action.</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:12px; font-weight:700; color:#64748b; text-transform:uppercase;">2. Emotional Mind Filter</div>
                    <div style="font-size:15px; font-weight:700; color:#0f172a; margin-top:2px;">${synthesis.perception_mode} (${synthesis.perception_group})</div>
                    <div style="font-size:12.5px; color:#475569; margin-top:4px;">How you perceive, feel, and digest life events internally.</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:12px; font-weight:700; color:#64748b; text-transform:uppercase;">3. Core Polarity Friction</div>
                    <div style="font-size:15px; font-weight:700; color:#0f172a; margin-top:2px;">${synthesis.polarity_state} (${synthesis.polarity_friction}/100)</div>
                    <div style="font-size:12.5px; color:#475569; margin-top:4px;">Baseline harmony or creative conflict between action and feeling.</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:12px; font-weight:700; color:#64748b; text-transform:uppercase;">4. Primary Driving Temperament</div>
                    <div style="font-size:15px; font-weight:700; color:#0f172a; margin-top:2px;">${synthesis.dominant_temperament} (${synthesis.dominant_nakshatra})</div>
                    <div style="font-size:12.5px; color:#475569; margin-top:4px;">The strongest underlying behavioral current in your birth chart.</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:12px; font-weight:700; color:#64748b; text-transform:uppercase;">5. Environmental Field</div>
                    <div style="font-size:15px; font-weight:700; color:#0f172a; margin-top:2px;">${synthesis.dominant_element} • ${synthesis.dominant_guna}</div>
                    <div style="font-size:12.5px; color:#475569; margin-top:4px;">Prakṛti Dosha: <strong>${synthesis.dominant_dosha}</strong> • Vargottama: ${synthesis.is_vargottama ? 'Yes (+30%)' : 'No'}</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:12px; font-weight:700; color:#64748b; text-transform:uppercase;">6. Dominant Chart Commander</div>
                    <div style="font-size:15px; font-weight:700; color:#0f172a; margin-top:2px;">${synthesis.chart_commander} (Score: ${synthesis.commander_prominence})</div>
                    <div style="font-size:12.5px; color:#475569; margin-top:4px;">Commands the loudest voice and stage presence across all life areas.</div>
                </div>
            </div>
            <div style="margin-top:14px; padding:12px; background:#fffdf5; border:1px solid #fef3c7; border-radius:6px;">
                <div style="font-size:13.5px; font-weight:700; color:#78350f; margin-bottom:4px;">✨ Astrologer Synthesis Synthesis Blueprint:</div>
                <div style="font-size:13px; color:#451a03; line-height:1.5;">
                    The native acts upon the world through the <strong>${synthesis.action_mode}</strong> archetype (${synthesis.action_group}), while emotionally experiencing reality through <strong>${synthesis.perception_mode}</strong> (${synthesis.perception_group}). With a polarity index of <strong>${synthesis.polarity_friction}/100</strong>, life manifests through <em>${synthesis.polarity_state}</em>. When navigating crises, the chart draws supreme authority from <strong>${synthesis.chart_commander}</strong>, operating within an environment grounded in <strong>${synthesis.dominant_element}</strong> and <strong>${synthesis.dominant_guna}</strong>.
                </div>
            </div>
        `;
    }

    // Initialize 3-Way Synthesis Cockpit for Tab 4
    initSynthesisCockpit(cell, currentData);
}

let _cachedFlowchartsData = null;
let _mermaidLoadingPromise = null;

function initMermaidLibrary() {
    if (typeof mermaid === 'undefined') return false;
    if (!window._astraMermaidInitialized) {
        try {
            mermaid.initialize({
                startOnLoad: false,
                theme: 'base',
                securityLevel: 'loose',
                themeVariables: {
                    primaryColor: '#ffffff',
                    primaryTextColor: '#0f172a',
                    primaryBorderColor: '#cbd5e1',
                    lineColor: '#64748b',
                    secondaryColor: '#f8fafc',
                    tertiaryColor: '#ffffff'
                },
                flowchart: {
                    htmlLabels: true,
                    curve: 'basis',
                    nodeSpacing: 35,
                    rankSpacing: 40
                }
            });
            window._astraMermaidInitialized = true;
        } catch (e) {
            console.error("Error initializing Mermaid.js:", e);
        }
    }
    return true;
}

function ensureMermaidReady() {
    if (typeof mermaid !== 'undefined') {
        initMermaidLibrary();
        return Promise.resolve(window.mermaid);
    }
    if (_mermaidLoadingPromise) return _mermaidLoadingPromise;

    _mermaidLoadingPromise = new Promise((resolve) => {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js';
        script.onload = () => {
            initMermaidLibrary();
            resolve(window.mermaid);
        };
        script.onerror = () => {
            console.error("Failed to load Mermaid CDN");
            resolve(null);
        };
        document.head.appendChild(script);
    });
    return _mermaidLoadingPromise;
}

async function getSignificationsFlowcharts(chartData) {
    if (_cachedFlowchartsData) return _cachedFlowchartsData;
    if (chartData && chartData.report && chartData.report.flowcharts && chartData.report.flowcharts.planets) {
        _cachedFlowchartsData = chartData.report.flowcharts;
        return _cachedFlowchartsData;
    }
    try {
        const resp = await fetch('/static/data/significations_flowcharts.json');
        if (resp.ok) {
            _cachedFlowchartsData = await resp.json();
            return _cachedFlowchartsData;
        }
    } catch (err) {
        console.warn("Could not fetch /static/data/significations_flowcharts.json:", err);
    }
    return { planets: {}, signs: {}, houses: {} };
}

// ============================================================================
// Fixed HTML/CSS Pillar Cards + Native SVG Connector Overlay Engine (Tab 4)
// ============================================================================

let _cachedSignificationsData = null;
async function getSignificationsData(chartData) {
    if (_cachedSignificationsData) return _cachedSignificationsData;
    if (chartData && chartData.report && chartData.report.significations_data && chartData.report.significations_data.planets) {
        _cachedSignificationsData = chartData.report.significations_data;
        return _cachedSignificationsData;
    }
    try {
        const resp = await fetch('/static/data/significations_data.json');
        if (resp.ok) {
            _cachedSignificationsData = await resp.json();
            return _cachedSignificationsData;
        }
    } catch (err) {
        console.warn("Could not fetch /static/data/significations_data.json:", err);
    }
    return { planets: {}, signs: {}, houses: {} };
}

// Backward-compatibility Mermaid helpers for legacy tests
function stripOuterSubgraph(mermaidText) {
    if (!mermaidText) return '';
    const lines = mermaidText.split('\n');
    const cleaned = lines.filter(l => l.trim() && !l.trim().startsWith('flowchart'));
    if (!cleaned.length) return '';
    if (cleaned[0].trim().startsWith('subgraph')) {
        let depth = 0;
        let endIdx = null;
        for (let i = 0; i < cleaned.length; i++) {
            const s = cleaned[i].trim();
            if (s.startsWith('subgraph')) depth++;
            else if (s === 'end') {
                depth--;
                if (depth === 0) { endIdx = i; break; }
            }
        }
        if (endIdx === cleaned.length - 1) return cleaned.slice(1, endIdx).join('\n');
    }
    return cleaned.join('\n');
}

function prefixMermaidBlock(mermaidText, prefix) {
    if (!mermaidText) return { code: '', edges: 0 };
    const processedLines = [];
    let edgeCount = 0;
    const lines = mermaidText.split('\n');
    for (let i = 0; i < lines.length; i++) {
        const trimmed = lines[i].trim();
        if (!trimmed || trimmed.startsWith('%%') || trimmed.startsWith('flowchart') || trimmed.startsWith('direction')) continue;
        const pad = '        ';
        if (trimmed.startsWith('subgraph')) {
            const match = trimmed.match(/^subgraph\s+([a-zA-Z0-9_]+)(.*)/);
            if (match) processedLines.push(`${pad}subgraph ${prefix}${match[1]}${match[2]}`);
            else processedLines.push(pad + trimmed);
            continue;
        }
        if (trimmed === 'end') { processedLines.push(`${pad}end`); continue; }
        if (trimmed.includes('[') && trimmed.endsWith(']')) {
            const idx = trimmed.indexOf('[');
            processedLines.push(`${pad}${prefix}${trimmed.substring(0, idx).trim()}${trimmed.substring(idx)}`);
            continue;
        }
        const edgeMatches = trimmed.match(/(?:-->|-\.->|---|==>)/g);
        if (edgeMatches) edgeCount += edgeMatches.length;
        const parts = trimmed.split(/(\|[^\n|]*\|)/);
        const newParts = [];
        for (let j = 0; j < parts.length; j++) {
            const part = parts[j];
            if (part.startsWith('|') && part.endsWith('|')) newParts.push(part);
            else newParts.push(part.replace(/\b([a-zA-Z0-9_]+)\b/g, (m, id) => `${prefix}${id}`));
        }
        processedLines.push(pad + newParts.join(''));
    }
    return { code: processedLines.join('\n'), edges: edgeCount };
}

function extractFlowchartNodes(mermaidText, prefix, groupName) {
    if (!mermaidText) return [];
    const nodes = [];
    const lines = mermaidText.split('\n');
    for (let i = 0; i < lines.length; i++) {
        const trimmed = lines[i].trim();
        if (!trimmed || trimmed.startsWith('subgraph') || trimmed.startsWith('%%') || trimmed.startsWith('flowchart') || trimmed === 'end' || trimmed.startsWith('direction')) continue;
        if (trimmed.includes('[') && trimmed.endsWith(']')) {
            const idx = trimmed.indexOf('[');
            const rawId = trimmed.substring(0, idx).trim();
            let content = trimmed.substring(idx + 1, trimmed.length - 1);
            if (content.startsWith('"') && content.endsWith('"')) content = content.substring(1, content.length - 1);
            const bMatch = content.match(/<b>(.*?)<\/b>/);
            const title = bMatch ? bMatch[1].replace(/<br\s*\/?>/gi, ' ').trim() : rawId;
            const subMatch = content.match(/<span class=['"]sub['"]>(.*?)<\/span>/);
            const sub = subMatch ? subMatch[1].trim() : '';
            let cleanLabel = sub ? `${title} (${sub})` : title;
            cleanLabel = cleanLabel.replace(/<[^>]+>/g, '').trim();
            const cleanTitle = title.replace(/<[^>]+>/g, '').trim();
            nodes.push({ id: `${prefix}${rawId}`, rawId: rawId, title: cleanTitle, sub: sub, label: cleanLabel, group: groupName });
        }
    }
    return nodes;
}

function buildUnifiedMermaidCode(pData, sData, hData, planetName, signName, houseNum, links) {
    const pRaw = stripOuterSubgraph(pData.mermaid || '');
    const sRaw = stripOuterSubgraph(sData.mermaid || '');
    const hRaw = stripOuterSubgraph(hData.mermaid || '');
    const pBlock = prefixMermaidBlock(pRaw, 'P_');
    const sBlock = prefixMermaidBlock(sRaw, 'S_');
    const hBlock = prefixMermaidBlock(hRaw, 'H_');
    const pSym = pData.symbol || '🪐';
    const sSym = sData.symbol || '♈';
    const pTitle = pData.title ? `${pSym} ${pData.title}` : `${pSym} Planet: ${planetName}`;
    const sTitle = sData.title ? `${sSym} ${sData.title}` : `${sSym} Sign: ${signName}`;
    const hTitle = hData.title ? `🏛️ House ${houseNum} (${hData.formula || hData.sanskrit || ''})` : `🏛️ House ${houseNum}`;

    let code = `flowchart LR\n`;
    code += `    subgraph ColPlanet ["${pTitle}"]\n        direction TB\n${pBlock.code}\n    end\n`;
    code += `    subgraph ColSign ["${sTitle}"]\n        direction TB\n${sBlock.code}\n    end\n`;
    code += `    subgraph ColHouse ["${hTitle}"]\n        direction TB\n${hBlock.code}\n    end\n`;
    code += `\n    ColPlanet ~~~ ColSign\n    ColSign ~~~ ColHouse\n`;

    const baseEdgeCount = pBlock.edges + sBlock.edges + hBlock.edges + 2;
    if (links && links.length > 0) {
        code += `\n    %% User Cross-Connections\n`;
        links.forEach((link) => {
            if (link.type === 'dissonance') {
                code += `    ${link.from} -.->|<span style="color:#b91c1c;font-weight:bold;">Clashes</span>| ${link.to}\n`;
            } else {
                code += `    ${link.from} ==>|<span style="color:#15803d;font-weight:bold;">Resonates</span>| ${link.to}\n`;
            }
        });
        code += `\n`;
        links.forEach((link, idx) => {
            const edgeIndex = baseEdgeCount + idx;
            if (link.type === 'dissonance') {
                code += `    linkStyle ${edgeIndex} stroke:#dc2626,stroke-width:2.5px,stroke-dasharray: 5 5;\n`;
            } else {
                code += `    linkStyle ${edgeIndex} stroke:#16a34a,stroke-width:3px;\n`;
            }
        });
    }
    return code;
}

// ----------------------------------------------------------------------------
// Local Storage Persistence for Synthesis Links
// ----------------------------------------------------------------------------

function getSynthesisPlanetLinks(nativeId, planetName) {
    const key = `astra_synth_links_${nativeId}_${planetName}`;
    try {
        const val = localStorage.getItem(key);
        if (val) {
            const parsed = JSON.parse(val);
            if (Array.isArray(parsed)) return parsed;
        }
    } catch (e) {
        console.warn("Could not read synthesis links from localStorage:", e);
    }
    return [];
}

function saveSynthesisPlanetLinks(nativeId, planetName, links) {
    const key = `astra_synth_links_${nativeId}_${planetName}`;
    try {
        localStorage.setItem(key, JSON.stringify(links));
    } catch (e) {
        console.error("Could not write synthesis links to localStorage:", e);
    }
}

// ----------------------------------------------------------------------------
// Native SVG Connector Overlay: Bézier Curve Math & Path Rendering
// ----------------------------------------------------------------------------

function redrawAllConnections(cockpitContainer, links) {
    if (!cockpitContainer) return;
    const stageWrapper = cockpitContainer.querySelector('#synth-stage-wrapper') || cockpitContainer.querySelector('.synth-stage-wrapper');
    const pathsGroup = cockpitContainer.querySelector('#synth-paths-group');
    if (!stageWrapper || !pathsGroup) return;

    pathsGroup.innerHTML = '';
    if (!links || links.length === 0) return;

    const stageRect = stageWrapper.getBoundingClientRect();
    if (stageRect.width === 0 || stageRect.height === 0) return;

    links.forEach(link => {
        const fromEl = stageWrapper.querySelector(`.synth-node-box[data-node-id="${link.from}"]`);
        const toEl = stageWrapper.querySelector(`.synth-node-box[data-node-id="${link.to}"]`);
        if (!fromEl || !toEl) return;

        const r1 = fromEl.getBoundingClientRect();
        const r2 = toEl.getBoundingClientRect();

        let x1, y1, x2, y2, d;
        const isDissonance = link.type === 'dissonance';
        const strokeColor = isDissonance ? '#dc2626' : '#16a34a';
        const markerUrl = isDissonance ? 'url(#arrow-red)' : 'url(#arrow-green)';

        // If in approximately the same card column, loop outward to the right
        if (Math.abs(r1.left - r2.left) < 30) {
            x1 = r1.right - stageRect.left;
            y1 = r1.top + r1.height / 2 - stageRect.top;
            x2 = r2.right - stageRect.left;
            y2 = r2.top + r2.height / 2 - stageRect.top;
            const loopX = Math.max(x1, x2) + 36;
            d = `M ${x1} ${y1} C ${loopX} ${y1}, ${loopX} ${y2}, ${x2} ${y2}`;
        } else if (r1.left < r2.left) {
            // Source is to the left: dock right edge of source to left edge of target
            x1 = r1.right - stageRect.left;
            y1 = r1.top + r1.height / 2 - stageRect.top;
            x2 = r2.left - stageRect.left;
            y2 = r2.top + r2.height / 2 - stageRect.top;
            const dx = Math.max(35, (x2 - x1) * 0.45);
            d = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;
        } else {
            // Source is to the right: dock left edge of source to right edge of target
            x1 = r1.left - stageRect.left;
            y1 = r1.top + r1.height / 2 - stageRect.top;
            x2 = r2.right - stageRect.left;
            y2 = r2.top + r2.height / 2 - stageRect.top;
            const dx = Math.max(35, (x1 - x2) * 0.45);
            d = `M ${x1} ${y1} C ${x1 - dx} ${y1}, ${x2 + dx} ${y2}, ${x2} ${y2}`;
        }

        const pathEl = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        pathEl.setAttribute('d', d);
        pathEl.setAttribute('fill', 'none');
        pathEl.setAttribute('stroke', strokeColor);
        pathEl.setAttribute('stroke-width', '2.5');
        if (isDissonance) {
            pathEl.setAttribute('stroke-dasharray', '6 4');
        }
        pathEl.setAttribute('marker-end', markerUrl);
        pathEl.setAttribute('data-from', link.from);
        pathEl.setAttribute('data-to', link.to);
        pathsGroup.appendChild(pathEl);
    });
}

function renderConnectionsChips(cockpitContainer, links, onRemove) {
    const listEl = cockpitContainer.querySelector('#cockpit-connections-list') || cockpitContainer.querySelector('.cockpit-connections-list');
    if (!listEl) return;

    if (!links || links.length === 0) {
        listEl.innerHTML = `<span class="no-links-msg" style="font-size: 11.5px; color: #94a3b8; font-style: italic;">No cross-symbol links created yet. Click any two boxes across the cards to link them.</span>`;
        return;
    }

    let html = '';
    links.forEach((l, idx) => {
        const isDis = l.type === 'dissonance';
        const icon = isDis ? '⚡' : '🔗';
        const typeLabel = isDis ? 'Clashes' : 'Resonates';
        html += `
            <div class="synth-conn-chip ${l.type}" data-idx="${idx}">
                <span>${icon} <strong>${l.fromLabel || l.from}</strong> ⟷ <strong>${l.toLabel || l.to}</strong> (${typeLabel})</span>
                <button type="button" class="btn-del-conn" data-idx="${idx}" title="Remove link">×</button>
            </div>
        `;
    });
    listEl.innerHTML = html;

    listEl.querySelectorAll('.btn-del-conn').forEach(btn => {
        btn.onclick = (e) => {
            e.stopPropagation();
            const idx = parseInt(btn.getAttribute('data-idx'), 10);
            if (!isNaN(idx) && onRemove) {
                onRemove(idx);
            }
        };
    });
}

// ----------------------------------------------------------------------------
// Card Rendering Engine: Multi-Pillar HTML Architecture
// ----------------------------------------------------------------------------

function renderPillarCard(targetCol, cardData, entityType, displayTitle, symbol) {
    if (!targetCol || !cardData) return;

    const sym = symbol || cardData.symbol || (entityType === 'house' ? '🏛️' : (entityType === 'planet' ? '🪐' : '♈'));
    const title = displayTitle || cardData.title || cardData.name || '';
    const formula = cardData.formula || (cardData.sanskrit ? `${cardData.sanskrit}` : '');

    let html = `
        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span class="synth-card-symbol">${sym}</span>
                <div>
                    <div class="synth-card-title">${title}</div>
                    ${cardData.sanskrit ? `<div style="font-size: 11px; color: #64748b; font-style: italic;">${cardData.sanskrit}</div>` : ''}
                </div>
            </div>
            ${formula ? `<span class="synth-card-formula" title="${formula}">${formula}</span>` : ''}
        </div>
        <div class="synth-pillars-container">
    `;

    const pillars = cardData.pillars || [];
    pillars.forEach(pillar => {
        html += `
            <div class="synth-pillar-col">
                <div class="synth-pillar-title" title="${pillar.name}">${pillar.name}</div>
                <div style="display: flex; flex-direction: column; gap: 6px;">
        `;
        (pillar.items || []).forEach(item => {
            html += `
                <div class="synth-node-box" data-node-id="${item.id}" data-node-title="${item.title}" data-node-sub="${item.sub || ''}" data-node-group="${displayTitle || cardData.name || entityType}">
                    <div class="synth-node-title">${item.title}</div>
                    ${item.sub ? `<div class="synth-node-sub">${item.sub}</div>` : ''}
                </div>
            `;
        });
        html += `
                </div>
            </div>
        `;
    });

    html += `</div>`;

    if (cardData.anatomy) {
        html += `
            <div class="synth-anatomy-footer">
                <span>🏛️</span>
                <span><strong>Kalapurusha Anatomy:</strong> ${cardData.anatomy}</span>
            </div>
        `;
    }

    targetCol.innerHTML = html;
}

// ----------------------------------------------------------------------------
// Interactive Selection & Action Bar Engine
// ----------------------------------------------------------------------------

function setupSelectionEngine(cockpitContainer, nativeId, planetName, currentData, triggerAutoSaveNotes) {
    const stageWrapper = cockpitContainer.querySelector('#synth-stage-wrapper') || cockpitContainer.querySelector('.synth-stage-wrapper');
    const actionBar = cockpitContainer.querySelector('#synth-action-bar');
    const selLabel = cockpitContainer.querySelector('#synth-selection-label');
    const btnRes = cockpitContainer.querySelector('#btn-action-res');
    const btnDis = cockpitContainer.querySelector('#btn-action-dis');
    const btnCancel = cockpitContainer.querySelector('#btn-action-cancel');
    const txtResonance = cockpitContainer.querySelector('#txt-resonance') || cockpitContainer.querySelector('.txt-resonance');
    const txtDissonance = cockpitContainer.querySelector('#txt-dissonance') || cockpitContainer.querySelector('.txt-dissonance');

    if (!stageWrapper) return;

    cockpitContainer._selectedBoxes = cockpitContainer._selectedBoxes || [];

    const updateVisuals = () => {
        const allBoxes = stageWrapper.querySelectorAll('.synth-node-box');
        allBoxes.forEach(b => {
            b.classList.remove('selected-first', 'selected-second');
        });

        const selected = cockpitContainer._selectedBoxes;
        if (selected[0] && selected[0].el) {
            selected[0].el.classList.add('selected-first');
        }
        if (selected[1] && selected[1].el) {
            selected[1].el.classList.add('selected-second');
        }

        if (actionBar && selLabel) {
            if (selected.length === 2) {
                selLabel.textContent = `${selected[0].group}: ${selected[0].title} ⟷ ${selected[1].group}: ${selected[1].title}`;
                actionBar.style.display = 'flex';
            } else {
                actionBar.style.display = 'none';
            }
        }
    };

    const attachBoxClicks = () => {
        const boxes = stageWrapper.querySelectorAll('.synth-node-box');
        boxes.forEach(box => {
            box.onclick = (e) => {
                e.stopPropagation();
                const id = box.getAttribute('data-node-id');
                const title = box.getAttribute('data-node-title');
                const sub = box.getAttribute('data-node-sub');
                const group = box.getAttribute('data-node-group');

                const existingIdx = cockpitContainer._selectedBoxes.findIndex(b => b.id === id);
                if (existingIdx >= 0) {
                    cockpitContainer._selectedBoxes.splice(existingIdx, 1);
                } else {
                    if (cockpitContainer._selectedBoxes.length >= 2) {
                        cockpitContainer._selectedBoxes = [{ id, title, sub, group, el: box }];
                    } else {
                        cockpitContainer._selectedBoxes.push({ id, title, sub, group, el: box });
                    }
                }
                updateVisuals();
            };
        });
    };

    const onRemoveLink = (idx) => {
        let links = getSynthesisPlanetLinks(nativeId, planetName);
        links.splice(idx, 1);
        saveSynthesisPlanetLinks(nativeId, planetName, links);
        renderConnectionsChips(cockpitContainer, links, onRemoveLink);
        redrawAllConnections(cockpitContainer, links);
    };

    const commitLink = (type) => {
        const selected = cockpitContainer._selectedBoxes;
        if (selected.length < 2) return;

        const b1 = selected[0];
        const b2 = selected[1];
        const fromLabel = `${b1.group}: ${b1.title}`;
        const toLabel = `${b2.group}: ${b2.title}`;

        let links = getSynthesisPlanetLinks(nativeId, planetName);
        const existingIdx = links.findIndex(l => (l.from === b1.id && l.to === b2.id) || (l.from === b2.id && l.to === b1.id));
        if (existingIdx >= 0) {
            links[existingIdx].type = type;
            links[existingIdx].fromLabel = fromLabel;
            links[existingIdx].toLabel = toLabel;
        } else {
            links.push({
                from: b1.id,
                to: b2.id,
                fromLabel: fromLabel,
                toLabel: toLabel,
                type: type
            });
        }
        saveSynthesisPlanetLinks(nativeId, planetName, links);

        // Append bullet note to scratchpad
        if (type === 'resonance' && txtResonance) {
            const bullet = `• ${fromLabel} resonates with ${toLabel}`;
            if (!txtResonance.value.includes(b1.title) || !txtResonance.value.includes(b2.title)) {
                txtResonance.value = txtResonance.value ? `${txtResonance.value.trim()}\n${bullet}: ` : `${bullet}: `;
                if (triggerAutoSaveNotes) triggerAutoSaveNotes();
            }
        } else if (type === 'dissonance' && txtDissonance) {
            const bullet = `• ${fromLabel} clashes with ${toLabel}`;
            if (!txtDissonance.value.includes(b1.title) || !txtDissonance.value.includes(b2.title)) {
                txtDissonance.value = txtDissonance.value ? `${txtDissonance.value.trim()}\n${bullet}: ` : `${bullet}: `;
                if (triggerAutoSaveNotes) triggerAutoSaveNotes();
            }
        }

        cockpitContainer._selectedBoxes = [];
        updateVisuals();
        renderConnectionsChips(cockpitContainer, links, onRemoveLink);
        redrawAllConnections(cockpitContainer, links);
    };

    if (btnRes) {
        btnRes.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            commitLink('resonance');
        };
    }
    if (btnDis) {
        btnDis.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            commitLink('dissonance');
        };
    }
    if (btnCancel) {
        btnCancel.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            cockpitContainer._selectedBoxes = [];
            updateVisuals();
        };
    }

    const btnClear = cockpitContainer.querySelector('#btn-clear-connections') || cockpitContainer.querySelector('.btn-clear-connections');
    if (btnClear) {
        btnClear.onclick = (e) => {
            e.preventDefault();
            saveSynthesisPlanetLinks(nativeId, planetName, []);
            cockpitContainer._selectedBoxes = [];
            updateVisuals();
            renderConnectionsChips(cockpitContainer, [], onRemoveLink);
            redrawAllConnections(cockpitContainer, []);
        };
    }

    attachBoxClicks();
    updateVisuals();

    // Initial chips & SVG path render
    const currentLinks = getSynthesisPlanetLinks(nativeId, planetName);
    renderConnectionsChips(cockpitContainer, currentLinks, onRemoveLink);

    setTimeout(() => {
        redrawAllConnections(cockpitContainer, currentLinks);
    }, 60);

    // Setup ResizeObserver for zero-jitter docking on resize
    if (!cockpitContainer._synthResizeObserver && window.ResizeObserver) {
        cockpitContainer._synthResizeObserver = new ResizeObserver(() => {
            const l = getSynthesisPlanetLinks(nativeId, planetName);
            redrawAllConnections(cockpitContainer, l);
        });
        cockpitContainer._synthResizeObserver.observe(stageWrapper);
    }
}

// ----------------------------------------------------------------------------
// Cockpit Lifecycle Orchestration
// ----------------------------------------------------------------------------

function initSynthesisCockpit(cell, chartData) {
    const cockpitContainer = cell.querySelector('.synthesis-cockpit-container');
    if (!cockpitContainer) return;

    const selectPlanet = cell.querySelector('.select-synthesis-planet') || cell.querySelector('#select-synthesis-planet');
    if (!selectPlanet) return;

    const currentData = chartData || window.currentChartData;
    if (!currentData || !currentData.report) return;

    const report = currentData.report;
    const planetRank = report.planetary_rankings || {};
    const leaderboard = planetRank.leaderboard || [];

    const classicalPlanets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'];
    const availableLeaderboard = leaderboard.filter(p => classicalPlanets.includes(p.planet));

    // Determine initial selected planet: Commander if classical, else first available, else Sun
    let commanderPlanet = (planetRank.chart_commander && planetRank.chart_commander.planet) || '';
    if (!classicalPlanets.includes(commanderPlanet)) {
        commanderPlanet = availableLeaderboard.length > 0 ? availableLeaderboard[0].planet : 'Sun';
    }

    const currentVal = selectPlanet.value;
    const initialPlanet = (currentVal && classicalPlanets.includes(currentVal)) ? currentVal : commanderPlanet;

    // Populate Focus Graha dropdown
    let optionsHtml = '';
    availableLeaderboard.forEach(p => {
        const isSelected = p.planet === initialPlanet ? 'selected' : '';
        const isCmdr = (planetRank.chart_commander && planetRank.chart_commander.planet === p.planet) ? ' 👑' : '';
        optionsHtml += `<option value="${p.planet}" ${isSelected}>#${p.rank} ${p.planet}${isCmdr} in ${p.sign} (House ${p.house}) — ${p.nakshatra}</option>`;
    });
    selectPlanet.innerHTML = optionsHtml;
    selectPlanet.value = initialPlanet;

    // Populate ambient context strip
    const ambientText = cockpitContainer.querySelector('.context-ambient-text');
    if (ambientText) {
        const polCore = report.polarity_core || {};
        const ascNak = polCore.ascendant_nakshatra || {};
        const moonNak = polCore.moon_nakshatra || {};
        ambientText.innerHTML = `<strong>${ascNak.name || '--'}</strong> Lagna (${ascNak.group || '--'}) <span style="margin:0 4px; color:#b45309;">⟷</span> <strong>${moonNak.name || '--'}</strong> Moon (${moonNak.group || '--'})`;
    }

    // Change event on Focus Graha dropdown
    selectPlanet.onchange = () => {
        cockpitContainer._selectedBoxes = [];
        renderSynthesisCockpit(cell, selectPlanet.value, currentData);
    };

    // Render initial synthesis cockpit
    renderSynthesisCockpit(cell, initialPlanet, currentData);
}

async function renderSynthesisCockpit(cell, planetName, chartData) {
    if (typeof cell === 'string') {
        chartData = planetName || window.currentChartData;
        planetName = cell;
        cell = document.querySelector('.widget-synthesis-report') || document;
    }
    const cockpitContainer = cell.querySelector('.synthesis-cockpit-container');
    if (!cockpitContainer) return;

    const currentData = chartData || window.currentChartData;
    if (!currentData || !currentData.report) return;

    const report = currentData.report;
    const leaderboard = (report.planetary_rankings && report.planetary_rankings.leaderboard) || [];
    const pEntry = leaderboard.find(p => p.planet === planetName) || {
        planet: planetName,
        sign: 'Aries',
        house: 1,
        nakshatra: '--',
        nakshatra_lord: '--'
    };

    const S = pEntry.sign || 'Aries';
    const H = String(pEntry.house || 1);
    const N = pEntry.nakshatra || '--';
    const NL = pEntry.nakshatra_lord || '--';

    // 1. Placement Flavor Context Strip
    const focusText = cockpitContainer.querySelector('.context-focus-text');
    if (focusText) {
        focusText.innerHTML = `<strong>${planetName}</strong> in <strong>${S}</strong> (House ${H}) • <em>${N}</em> (Lord: ${NL})`;
    }

    // 2. Setup Scratchpad Notes Persistence
    const nativeId = (currentData.subject_info && currentData.subject_info.name)
        ? currentData.subject_info.name.replace(/[^a-zA-Z0-9_-]/g, '_')
        : (currentData.id || 'default_chart');
    const noteKey = `astra_synth_${nativeId}_${planetName}`;
    const txtResonance = cockpitContainer.querySelector('.txt-resonance') || cockpitContainer.querySelector('#txt-resonance');
    const txtDissonance = cockpitContainer.querySelector('.txt-dissonance') || cockpitContainer.querySelector('#txt-dissonance');
    const txtSynthesis = cockpitContainer.querySelector('.txt-synthesis') || cockpitContainer.querySelector('#txt-synthesis');
    const btnSave = cockpitContainer.querySelector('.btn-save-synthesis');
    const saveStatus = cockpitContainer.querySelector('.synth-save-status');

    const saveNotes = () => {
        const payload = {
            resonance: txtResonance ? txtResonance.value : '',
            dissonance: txtDissonance ? txtDissonance.value : '',
            synthesis: txtSynthesis ? txtSynthesis.value : '',
            updatedAt: new Date().toISOString()
        };
        try {
            localStorage.setItem(noteKey, JSON.stringify(payload));
            if (saveStatus) {
                saveStatus.textContent = 'Saved to local cache ✓';
                saveStatus.style.opacity = '1';
                setTimeout(() => { if (saveStatus) saveStatus.style.opacity = '0'; }, 2000);
            }
        } catch (e) {
            console.error("Error writing to localStorage:", e);
        }
    };

    if (btnSave) {
        btnSave.onclick = (e) => {
            e.preventDefault();
            saveNotes();
        };
    }

    let debounceTimer = null;
    const triggerAutoSave = () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(saveNotes, 600);
    };

    if (txtResonance) txtResonance.oninput = triggerAutoSave;
    if (txtDissonance) txtDissonance.oninput = triggerAutoSave;
    if (txtSynthesis) txtSynthesis.oninput = triggerAutoSave;

    try {
        const rawNote = localStorage.getItem(noteKey);
        if (rawNote) {
            const parsed = JSON.parse(rawNote);
            if (txtResonance) txtResonance.value = parsed.resonance || '';
            if (txtDissonance) txtDissonance.value = parsed.dissonance || '';
            if (txtSynthesis) txtSynthesis.value = parsed.synthesis || '';
        } else {
            if (txtResonance) txtResonance.value = '';
            if (txtDissonance) txtDissonance.value = '';
            if (txtSynthesis) txtSynthesis.value = '';
        }
    } catch (e) {
        console.warn("Could not read notes from localStorage:", e);
    }

    // 3. Load Significations Data
    const data = await getSignificationsData(currentData);
    const pData = (data.planets && data.planets[planetName]) || {};
    const sData = (data.signs && data.signs[S]) || {};
    const hData = (data.houses && data.houses[H]) || {};

    // 4. Render Fixed HTML/CSS Pillar Cards
    const cardColPlanet = cockpitContainer.querySelector('#card-col-planet');
    const cardColSign = cockpitContainer.querySelector('#card-col-sign');
    const cardColHouse = cockpitContainer.querySelector('#card-col-house');

    if (cardColPlanet) {
        renderPillarCard(cardColPlanet, pData, 'planet', pData.title || `Planet: ${planetName}`, pData.symbol || '🪐');
    }
    if (cardColSign) {
        renderPillarCard(cardColSign, sData, 'sign', sData.title || `Sign: ${S}`, sData.symbol || '♈');
    }
    if (cardColHouse) {
        renderPillarCard(cardColHouse, hData, 'house', hData.title || `House ${H}`, '🏛️');
    }

    // 5. Setup Interactive Selection & SVG Overlay Engine
    setupSelectionEngine(cockpitContainer, nativeId, planetName, currentData, triggerAutoSave);
}

// Backward-compatibility alias
async function renderSynthesisTriptych(cell, planetName, chartData) {
    return renderSynthesisCockpit(cell, planetName, chartData);
}

function openFloatingReport() {
    if (typeof closeKalaMenu === 'function') closeKalaMenu();
    const modal = document.getElementById('widgetMaximizeModal');
    const card = document.getElementById('widgetMaximizeCard');
    const titleEl = document.getElementById('widgetMaximizeModalTitle');
    const container = document.getElementById('widgetMaximizeContainer');
    if (!modal || !titleEl || !container || !window.currentChartData) return;

    if (typeof resetFloatingWindowPosition === 'function') resetFloatingWindowPosition();
    if (card) {
        const w = Math.min(1380, window.innerWidth - 40);
        const h = Math.min(840, window.innerHeight - 60);
        card.style.width = w + 'px';
        card.style.height = h + 'px';
        card.style.left = Math.max(20, Math.round((window.innerWidth - w) / 2)) + 'px';
        card.style.top = Math.max(30, Math.round((window.innerHeight - h) / 2)) + 'px';
    }

    const subjectName = (window.currentChartData.subject_info && window.currentChartData.subject_info.name) 
        ? window.currentChartData.subject_info.name 
        : 'Chart';
    titleEl.textContent = subjectName + " — Astrological Synthesis Report";

    const tmpl = document.getElementById('tmpl-report');
    if (tmpl) {
        container.innerHTML = '';
        container.appendChild(tmpl.content.cloneNode(true));
        updateReportWidget(container, window.currentChartData);
    }

    modal.style.display = 'block';
    modal.classList.add('active');
}

// Pluggable Widget Registration
if (typeof window !== 'undefined' && window.widgetRegistry) {
    window.widgetRegistry.register('report', {
        id: 'report',
        title: 'Astrological Synthesis Report',
        icon: '📜',
        category: 'Diagnostics',
        templateId: 'tmpl-report',
        isScrollable: true,
        render: function(container, chartData, options) {
            const tmpl = document.getElementById('tmpl-report');
            if (tmpl) {
                container.innerHTML = '';
                container.appendChild(tmpl.content.cloneNode(true));
                updateReportWidget(container, chartData);
            }
        },
        onUpdate: function(cell, chartData) {
            updateReportWidget(cell, chartData);
        }
    });

    window.openFloatingReport = openFloatingReport;
    window.updateReportWidget = updateReportWidget;
    window.switchReportTab = switchReportTab;
    window.selectTemperamentDossier = selectTemperamentDossier;
    window.NAKSHATRA_TEMPERAMENT_DOSSIER = NAKSHATRA_TEMPERAMENT_DOSSIER;
    window.initSynthesisCockpit = initSynthesisCockpit;
    window.renderSynthesisTriptych = renderSynthesisTriptych;
    window.renderSynthesisCockpit = renderSynthesisCockpit;
    window.getSignificationsFlowcharts = getSignificationsFlowcharts;
    window.getSignificationsData = getSignificationsData;
    window.buildUnifiedMermaidCode = buildUnifiedMermaidCode;
    window.getSynthesisPlanetLinks = getSynthesisPlanetLinks;
    window.saveSynthesisPlanetLinks = saveSynthesisPlanetLinks;
    window.redrawAllConnections = redrawAllConnections;
}

