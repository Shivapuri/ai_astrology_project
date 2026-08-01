from kerykeion import AstrologicalSubject
import json
import sys

def generate_ai_json(
    name: str = "User",
    year: int = 1983,
    month: int = 11,
    day: int = 10,
    hour: int = 15,
    minute: int = 30,
    city: str = "Budapest",
    country_code: str = "HU",
    output_filename: str = "chart_context.json"
):
    # 1. Enter the birth data here (Name, Year, Month, Day, Hour, Minute, City, Country Code)
    # Kerykeion automatically fetches coordinates and time zone for the city.
    subject = AstrologicalSubject(name, year, month, day, hour, minute, city, country_code)

    planet_keys = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
    house_keys = [
        "first_house", "second_house", "third_house", "fourth_house", "fifth_house", "sixth_house",
        "seventh_house", "eighth_house", "ninth_house", "tenth_house", "eleventh_house", "twelfth_house"
    ]

    # 2. Extract clean data specifically for AI context
    ai_payload = {
        "native_details": {
            "name": subject.name,
            "sun_sign": subject.sun.sign,
            "moon_sign": subject.moon.sign,
            "ascendant": subject.first_house.sign,
            "birth_time": f"{hour:02d}:{minute:02d}",
            "location": f"{city}, {country_code}"
        },
        # Loop through planets and grab their sign, house, and exact degree
        "planets": {
            getattr(subject, p).name: {
                "sign": getattr(subject, p).sign,
                "house": getattr(subject, p).house,
                "degree": round(getattr(subject, p).abs_pos, 2)
            } for p in planet_keys
        },
        # Loop through all 12 houses and grab the sign on the cusp
        "houses": {
            getattr(subject, h).name: {
                "sign": getattr(subject, h).sign,
                "degree": round(getattr(subject, h).abs_pos, 2)
            } for h in house_keys
        }
    }

    # 3. Save it to a JSON file
    with open(output_filename, "w") as outfile:
        json.dump(ai_payload, outfile, indent=4)

    print(f"✅ Success! Chart data saved to {output_filename}")

if __name__ == "__main__":
    generate_ai_json()


