from kerykeion import AstrologicalSubject
import json

def generate_ai_json():
    # 1. Enter the birth data here (Name, Year, Month, Day, Hour, Minute, City, Country Code)
    # Note: Kerykeion automatically fetches the coordinates and timezone for the city!
    subject = AstrologicalSubject("Steve", 1990, 7, 15, 10, 30, "London", "GB")

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
            "ascendant": subject.first_house.sign
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
    filename = "chart_context.json"
    with open(filename, "w") as outfile:
        json.dump(ai_payload, outfile, indent=4)

    print(f"✅ Success! Chart data saved to {filename}")

if __name__ == "__main__":
    generate_ai_json()

