import json

def get_bphs_dignity(planet: str, sign: str, degree: float, compound_rel: str) -> str:
    """Returns the precise dignity according to BPHS degrees."""
    # Special exact degrees:
    # Sun: Ex 10 Ar, DB 10 Li, MT 0-20 Le, OH 20-30 Le
    # Moon: Ex 3 Ta, DB 3 Sc, MT 3-30 Ta, OH Ca
    # Mars: Ex 28 Cp, DB 28 Ca, MT 0-12 Ar, OH 12-30 Ar & Sc
    # Mercury: Ex 15 Vi, DB 15 Pi, MT 15-20 Vi, OH 20-30 Vi & Ge
    # Jupiter: Ex 5 Ca, DB 5 Cp, MT 0-10 Sg, OH 10-30 Sg & Pi
    # Venus: Ex 27 Pi, DB 27 Vi, MT 0-15 Li, OH 15-30 Li & Ta
    # Saturn: Ex 20 Li, DB 20 Ar, MT 0-20 Aq, OH 20-30 Aq & Cp
    # Note: For Vargas and general dignity, Exaltation is the WHOLE sign (except for Moon/Merc where MT/OH share the sign).
    # Wait, BPHS usually says if it's in Exaltation sign, it's exalted. But for Mercury, Virgo has 3: Ex, MT, OH.
    
    if planet == "Sun":
        if sign == "Aries": return "Exalted"
        if sign == "Libra": return "Debilitated"
        if sign == "Leo":
            if degree <= 20: return "Moolatrikona"
            else: return "Own Sign"
    elif planet == "Moon":
        if sign == "Taurus":
            if degree <= 3: return "Exalted"
            else: return "Moolatrikona"
        if sign == "Scorpio": return "Debilitated"
        if sign == "Cancer": return "Own Sign"
    elif planet == "Mars":
        if sign == "Capricorn": return "Exalted"
        if sign == "Cancer": return "Debilitated"
        if sign == "Aries":
            if degree <= 12: return "Moolatrikona"
            else: return "Own Sign"
        if sign == "Scorpio": return "Own Sign"
    elif planet == "Mercury":
        if sign == "Virgo":
            if degree <= 15: return "Exalted"
            elif degree <= 20: return "Moolatrikona"
            else: return "Own Sign"
        if sign == "Pisces": return "Debilitated"
        if sign == "Gemini": return "Own Sign"
    elif planet == "Jupiter":
        if sign == "Cancer": return "Exalted"
        if sign == "Capricorn": return "Debilitated"
        if sign == "Sagittarius":
            if degree <= 10: return "Moolatrikona"
            else: return "Own Sign"
        if sign == "Pisces": return "Own Sign"
    elif planet == "Venus":
        if sign == "Pisces": return "Exalted"
        if sign == "Virgo": return "Debilitated"
        if sign == "Libra":
            if degree <= 15: return "Moolatrikona"
            else: return "Own Sign"
        if sign == "Taurus": return "Own Sign"
    elif planet == "Saturn":
        if sign == "Libra": return "Exalted"
        if sign == "Aries": return "Debilitated"
        if sign == "Aquarius":
            if degree <= 20: return "Moolatrikona"
            else: return "Own Sign"
        if sign == "Capricorn": return "Own Sign"
    elif planet == "Rahu":
        if sign == "Taurus": return "Exalted"
        if sign == "Scorpio": return "Debilitated"
        if sign == "Gemini": return "Moolatrikona"
        if sign == "Aquarius": return "Own Sign"
    elif planet == "Ketu":
        if sign == "Scorpio": return "Exalted"
        if sign == "Taurus": return "Debilitated"
        if sign == "Sagittarius": return "Moolatrikona"
        if sign == "Scorpio": return "Own Sign"

    return f"{compound_rel}'s Sign"

