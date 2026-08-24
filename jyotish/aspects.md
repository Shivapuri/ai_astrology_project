# Astrological Aspects (Drishti)

This document explains the mathematical rules and astrological logic for how aspects (Drishtis) are calculated in the Astra engine. The accompanying Python module is `aspects.py`.

## Overview
In Jyotish (Vedic Astrology), *Drishti* literally means "glance" or "sight." It is how planets and signs influence each other across the zodiac. Ernst Wilhelm's methodology, strictly based on Sage Parashara's teachings, separates aspects into two completely distinct categories: **Rasi Drishti** (Sign Aspects) and **Graha Drishti** (Planetary Aspects).

---

## 1. Rasi Drishti (Sign-to-Sign Aspects)

### The Simple Explanation
Imagine the zodiac signs are rooms in a house. Some rooms have windows that look directly into other rooms. If a planet is sitting in one room, it can clearly see (and be seen by) anyone in the rooms connected by windows. 
- **Binary:** The window is either open or closed. You either aspect the sign 100%, or 0%. There is no halfway.
- **Mutual:** If you can see them, they can see you.

### The Technical Rules
The 12 signs are divided into three modalities: Moveable (Cardinal), Fixed, and Dual (Mutable). 

1. **Moveable Signs** (Aries, Cancer, Libra, Capricorn) aspect all **Fixed Signs**, *except* the one immediately adjacent to them.
   * *Example:* Aries (Moveable) aspects Leo, Scorpio, and Aquarius. It does *not* aspect Taurus because Taurus is right next door.
2. **Fixed Signs** (Taurus, Leo, Scorpio, Aquarius) aspect all **Moveable Signs**, *except* the one immediately adjacent to them.
   * *Example:* Taurus (Fixed) aspects Cancer, Libra, and Capricorn. It does *not* aspect Aries because Aries is right next door.
3. **Dual Signs** (Gemini, Virgo, Sagittarius, Pisces) aspect **all other Dual Signs**.

### How it is Used
Rasi Drishtis form the structural bedrock of the chart. They are used to detect *Yogas* (planetary combinations), determine long-term permanent influences, and calculate sign-based timing periods (like Jaimini Dashas).

---

## 2. Graha Drishti (Planetary Longitude Aspects)

### The Simple Explanation
If Rasi Drishti is like rooms with windows, Graha Drishti is like a person shining a flashlight. The flashlight is brightest exactly where it is pointed, but the light gently fades the further away you get from the center of the beam. 
- **Continuous (Fractional):** The strength of the aspect is measured on a scale from 0 to 60 *Virupas* (points). 60 is a full, blinding aspect; 0 is no aspect at all.
- **Not Mutual:** Just because the Sun is shining its light on the Moon, does *not* mean the Moon is shining its light back on the Sun.
- **Degrees Matter:** It is calculated based on the exact mathematical degrees of the planets, not just the signs they occupy.

### The Technical Rules
By default, every planet "looks" directly across the sky (180 degrees) with full strength (60 Virupas). As you move away from 180 degrees, the strength of the glance fades mathematically. 
*Note: In this strict system, the shadow nodes Rahu and Ketu do **not** cast Graha Drishti.*

**Special Planetary Glances:**
Three planets have "special" glances that are added on top of the base calculation:
1. **Mars (Kuja):** As the warrior, Mars is highly protective of its inner territory (4th house / ~90°) and highly alert to external threats (8th house / ~210°). It gets a massive strength boost at these angles.
2. **Jupiter (Guru):** As the wise counselor, Jupiter looks upon the houses of future creativity (5th / ~120°) and higher purpose (9th / ~240°) with supreme grace. It gets a strength boost here.
3. **Saturn (Shani):** As the stern worker, Saturn keeps a watchful eye on its immediate efforts (3rd / ~60°) and its heavy burdens/career (10th / ~270°). It gets a strength boost at these angles.

### How it is Used
Graha Drishti reveals the psychological and qualitative influence planets have on one another. It is used heavily in *Shadbala* (the 6-fold strength calculation) and for timing events using planetary periods (like Vimshottari Dasha).
