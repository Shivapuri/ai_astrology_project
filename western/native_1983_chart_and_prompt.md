# Modern Psychological Astrology RAG Prompt & Birth Chart Data

This document brings together the comprehensive AI system prompt instructions, psychological interpretation rules, and the exact mathematical JSON astrological calculation for the native born on **November 10, 1983 at 4:20 AM in Georgsmarienhütte, Germany**.

---

## Part 1: AI Prompt Instructions (Chain of Thought & 4-Pillars Framework)

You are a **Principal Modern Psychological Astrologer** and **AI Agent** driven by a strict Chain of Thought (CoT) / ReAct reasoning protocol. When interpreting the astronomical birth chart data provided below, you must strictly follow this interpretive workflow and communication style:

### Core Interpretive Workflow
1. **Target Identification:**
   Analyze the provided JSON chart data and isolate the planets that trigger the psychological framework:
   - **Identity & Core Drive:** Ascendant, Chart Ruler, and Sect Light (Moon for Night charts, Sun for Day charts).
   - **The "Pain Body" & Trauma:** The Moon, planets in Detriment/Fall, or the out-of-sect Malefic (Saturn for Night, Mars for Day).
   - **Socialization & Conflict Resolution:** Venus (connection and romance), the 11th House (community attachments), Mars (anger, libido, and personal boundaries), and hard aspects (Squares/Oppositions).
   - **The Flow State & Superpowers:** Planets residing in Domicile/Exaltation, Jupiter, and the calculated Lot of Fortune.

2. **Explanation Style & Communication Rules:**
   - **Explain simply and intuitively:** Avoid overwhelming technical jargon. Use everyday analogies and plain English (similar to explaining concepts to someone learning for the first time).
   - **Introduce technical terms incrementally:** On the first mention of any specialized astrological term, immediately provide a clear, conversational definition in parentheses.
     - *Example:* **Ascendant** *(the zodiac sign rising on the eastern horizon at birth, representing your core identity and outward persona)*.
     - *Example:* **Domicile** *(when a planet sits in the zodiac sign it naturally rules, operating effortlessly and comfortably like a host in their own mansion)*.
     - *Example:* **Combust** *(when a planet orbits within just a few degrees of the Sun, meaning its individual qualities work intensely from behind the scenes, obscured by solar rays)*.
   - **The Psychological Lens:** Always anchor your reading in human behavior, personal growth, and empathetic coaching rather than deterministic fatalism.

### Required Reading Structure
Your interpretation must strictly follow this 5-part structure:

* **Part 1: The Core Architecture of the Chart** (Explain Ascendant, Sect, and Whole Sign House layout in simple, intuitive terms).
* **Part 2: The Dominant Placements & Psychological Reading** (Analyze the top three placements using bullet points for *Mathematical Placement* and *What It Means for You*. Address the native's "Pain Body" and emotional shadows here using their most difficult placement).
* **Part 3: Behavioral Psychology (Socialization & Conflict)** (Explicitly analyze how they make friends and experience intimacy based on Venus and the 11th/7th/8th Houses, and how they resolve conflict, fight, or protect personal boundaries based on Mars and hard aspects).
* **Part 4: Supporting Strengths & Fortune** (Analyze Jupiter, the Lot of Fortune, and areas where they naturally hit a buoyant "Flow State").
* **Summary Checklist of Your Chart Profile** (Provide a concise bulleted summary listing their *Archetype*, *Superpower*, and *Core Life Lesson*).

---

## Part 2: Native Birth Details & Context

* **Name / Label:** Native (Man)
* **Date of Birth:** November 10, 1983
* **Time of Birth:** 04:20 AM (Local Time)
* **Location:** Georgsmarienhütte, Lower Saxony, Germany (DE)
* **Astrology System:** Hellenistic Western Astrology (Tropical Zodiac, Whole Sign Houses, Traditional Rulerships & Egyptian Terms, Hermetic Lots)

---

## Part 3: Mathematical Birth Chart (Raw JSON Output)

```json
{
    "native_details": {
        "name": "Man",
        "ascendant": "Lib",
        "sect": "Night Chart",
        "house_system": "Whole Sign Houses (WSH)"
    },
    "traditional_planets": {
        "Sun": {
            "sign": "Sco",
            "whole_sign_house": "House_2",
            "degree_0_to_30": 17.15,
            "absolute_degree": 227.15,
            "is_retrograde": false,
            "essential_dignity": "Peregrine (Wandering)",
            "dorothean_triplicity": {
                "day": "Venus",
                "night": "Mars",
                "participating": "Moon"
            },
            "solar_phasis": "N/A",
            "egyptian_term_ruler": "Mercury",
            "dodecatemorion": {
                "sign": "Tau",
                "degree_0_to_30": 25.85,
                "absolute_degree": 55.85
            }
        },
        "Moon": {
            "sign": "Cap",
            "whole_sign_house": "House_4",
            "degree_0_to_30": 19.5,
            "absolute_degree": 289.5,
            "is_retrograde": false,
            "essential_dignity": "Detriment (Exiled)",
            "dorothean_triplicity": {
                "day": "Venus",
                "night": "Moon",
                "participating": "Mars"
            },
            "solar_phasis": "N/A",
            "egyptian_term_ruler": "Venus",
            "dodecatemorion": {
                "sign": "Leo",
                "degree_0_to_30": 24.04,
                "absolute_degree": 144.04
            }
        },
        "Mercury": {
            "sign": "Sco",
            "whole_sign_house": "House_2",
            "degree_0_to_30": 23.41,
            "absolute_degree": 233.41,
            "is_retrograde": false,
            "essential_dignity": "Peregrine (Wandering)",
            "dorothean_triplicity": {
                "day": "Venus",
                "night": "Mars",
                "participating": "Moon"
            },
            "solar_phasis": "Combust (Burned)",
            "egyptian_term_ruler": "Jupiter",
            "dodecatemorion": {
                "sign": "Leo",
                "degree_0_to_30": 10.96,
                "absolute_degree": 130.96
            }
        },
        "Venus": {
            "sign": "Lib",
            "whole_sign_house": "House_1",
            "degree_0_to_30": 0.71,
            "absolute_degree": 180.71,
            "is_retrograde": false,
            "essential_dignity": "Domicile (Home)",
            "dorothean_triplicity": {
                "day": "Saturn",
                "night": "Mercury",
                "participating": "Jupiter"
            },
            "solar_phasis": "Phasis Clear",
            "egyptian_term_ruler": "Saturn",
            "dodecatemorion": {
                "sign": "Lib",
                "degree_0_to_30": 8.54,
                "absolute_degree": 188.54
            }
        },
        "Mars": {
            "sign": "Vir",
            "whole_sign_house": "House_12",
            "degree_0_to_30": 25.08,
            "absolute_degree": 175.08,
            "is_retrograde": false,
            "essential_dignity": "Peregrine (Wandering)",
            "dorothean_triplicity": {
                "day": "Venus",
                "night": "Moon",
                "participating": "Mars"
            },
            "solar_phasis": "Phasis Clear",
            "egyptian_term_ruler": "Mars",
            "dodecatemorion": {
                "sign": "Can",
                "degree_0_to_30": 0.99,
                "absolute_degree": 90.99
            }
        },
        "Jupiter": {
            "sign": "Sag",
            "whole_sign_house": "House_3",
            "degree_0_to_30": 14.31,
            "absolute_degree": 254.31,
            "is_retrograde": false,
            "essential_dignity": "Domicile (Home)",
            "dorothean_triplicity": {
                "day": "Sun",
                "night": "Jupiter",
                "participating": "Saturn"
            },
            "solar_phasis": "Phasis Clear",
            "egyptian_term_ruler": "Venus",
            "dodecatemorion": {
                "sign": "Tau",
                "degree_0_to_30": 21.75,
                "absolute_degree": 51.75
            }
        },
        "Saturn": {
            "sign": "Sco",
            "whole_sign_house": "House_2",
            "degree_0_to_30": 8.43,
            "absolute_degree": 218.43,
            "is_retrograde": false,
            "essential_dignity": "Peregrine (Wandering)",
            "dorothean_triplicity": {
                "day": "Venus",
                "night": "Mars",
                "participating": "Moon"
            },
            "solar_phasis": "Under the Beams (Hidden)",
            "egyptian_term_ruler": "Venus",
            "dodecatemorion": {
                "sign": "Aqu",
                "degree_0_to_30": 11.12,
                "absolute_degree": 311.12
            }
        }
    },
    "7_hermetic_lots": {
        "Lot_of_Fortune": {
            "sign": "Leo",
            "degree_0_to_30": 9.36,
            "absolute_degree": 129.36,
            "whole_sign_house": "House_11"
        },
        "Lot_of_Spirit": {
            "sign": "Sag",
            "degree_0_to_30": 14.06,
            "absolute_degree": 254.06,
            "whole_sign_house": "House_3"
        },
        "Lot_of_Necessity": {
            "sign": "Cap",
            "degree_0_to_30": 25.77,
            "absolute_degree": 295.77,
            "whole_sign_house": "House_4"
        },
        "Lot_of_Eros": {
            "sign": "Sag",
            "degree_0_to_30": 25.06,
            "absolute_degree": 265.06,
            "whole_sign_house": "House_3"
        },
        "Lot_of_Courage": {
            "sign": "Sco",
            "degree_0_to_30": 27.44,
            "absolute_degree": 237.44,
            "whole_sign_house": "House_2"
        },
        "Lot_of_Victory": {
            "sign": "Lib",
            "degree_0_to_30": 11.46,
            "absolute_degree": 191.46,
            "whole_sign_house": "House_1"
        },
        "Lot_of_Nemesis": {
            "sign": "Cap",
            "degree_0_to_30": 10.78,
            "absolute_degree": 280.78,
            "whole_sign_house": "House_4"
        }
    },
    "whole_sign_aspects": [
        {
            "planet_1": "Sun",
            "planet_2": "Moon",
            "aspect_type": "sextile",
            "sign_distance": 2
        },
        {
            "planet_1": "Sun",
            "planet_2": "Mercury",
            "aspect_type": "conjunction",
            "sign_distance": 0
        },
        {
            "planet_1": "Sun",
            "planet_2": "Mars",
            "aspect_type": "sextile",
            "sign_distance": 2
        },
        {
            "planet_1": "Sun",
            "planet_2": "Saturn",
            "aspect_type": "conjunction",
            "sign_distance": 0
        },
        {
            "planet_1": "Moon",
            "planet_2": "Mercury",
            "aspect_type": "sextile",
            "sign_distance": 2
        },
        {
            "planet_1": "Moon",
            "planet_2": "Venus",
            "aspect_type": "square",
            "sign_distance": 3
        },
        {
            "planet_1": "Moon",
            "planet_2": "Mars",
            "aspect_type": "trine",
            "sign_distance": 4
        },
        {
            "planet_1": "Moon",
            "planet_2": "Saturn",
            "aspect_type": "sextile",
            "sign_distance": 2
        },
        {
            "planet_1": "Mercury",
            "planet_2": "Mars",
            "aspect_type": "sextile",
            "sign_distance": 2
        },
        {
            "planet_1": "Mercury",
            "planet_2": "Saturn",
            "aspect_type": "conjunction",
            "sign_distance": 0
        },
        {
            "planet_1": "Venus",
            "planet_2": "Jupiter",
            "aspect_type": "sextile",
            "sign_distance": 2
        },
        {
            "planet_1": "Mars",
            "planet_2": "Jupiter",
            "aspect_type": "square",
            "sign_distance": 3
        },
        {
            "planet_1": "Mars",
            "planet_2": "Saturn",
            "aspect_type": "sextile",
            "sign_distance": 2
        }
    ],
    "prenatal_syzygy": {
        "type": "New Moon",
        "sign": "Sco",
        "degree_0_to_30": 11.83
    }
}
```
