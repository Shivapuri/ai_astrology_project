from kerykeion import AstrologicalSubject, NatalAspects
import json

def generate_ai_json(
    name: str = "User",
    year: int = 1983,
    month: int = 11,
    day: int = 10,
    hour: int = 4,
    minute: int = 20,
    city: str = "Georgsmarienhütte",
    country_code: str = "DE",
    output_filename: str = "chart_context.json"
):
    # 1. Create the Subject
    subject = AstrologicalSubject(name, year, month, day, hour, minute, city, country_code)
    
    # 2. Calculate Aspects using NatalAspects
    natal_aspects = NatalAspects(subject)

    planet_keys = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
    house_keys = [
        "first_house", "second_house", "third_house", "fourth_house", "fifth_house", "sixth_house",
        "seventh_house", "eighth_house", "ninth_house", "tenth_house", "eleventh_house", "twelfth_house"
    ]

    # 3. Build the Improved AI Payload
    ai_payload = {
        "native_details": {
            "name": subject.name,
            "sun_sign": subject.sun.sign,
            "moon_sign": subject.moon.sign,
            "ascendant": subject.first_house.sign,
            "birth_time": f"{hour:02d}:{minute:02d}",
            "location": f"{city}, {country_code}",
            # If Sun is above horizon (Houses 7-12), Day chart. Below (1-6), Night chart.
            "sect": "Day Chart" if getattr(subject, "sun").house in [
                "Seventh_House", "Eighth_House", "Ninth_House", "Tenth_House", "Eleventh_House", "Twelfth_House"
            ] else "Night Chart"
        },
        "planets": {
            getattr(subject, p).name: {
                "sign": getattr(subject, p).sign,
                "house": getattr(subject, p).house,
                "degree_0_to_30": round(getattr(subject, p).position, 2), # 0-30 degree within sign
                "absolute_degree": round(getattr(subject, p).abs_pos, 2),  # 0-360 zodiac degree
                "is_retrograde": getattr(subject, p).retrograde
            } for p in planet_keys
        },
        "houses": {
            getattr(subject, h).name: {
                "sign": getattr(subject, h).sign,
                "degree_0_to_30": round(getattr(subject, h).position, 2)
            } for h in house_keys
        },
        # Major aspects calculated by Kerykeion
        "aspects": [
            {
                "planet_1": aspect.p1_name,
                "planet_2": aspect.p2_name,
                "aspect_type": aspect.aspect,
                "orb": round(aspect.orbit, 2)
            } for aspect in natal_aspects.relevant_aspects
        ]
    }

    # 4. Save to JSON
    with open(output_filename, "w") as outfile:
        json.dump(ai_payload, outfile, indent=4)

    print(f"✅ Success! Improved chart data saved to {output_filename}")

if __name__ == "__main__":
    generate_ai_json()
