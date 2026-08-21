import argparse
import sys
import webbrowser
import os

from jyotish.generate_jyotish import generate_kala_chart
import generate_html_chart

def main():
    parser = argparse.ArgumentParser(description="Astra - Ernst Wilhelm Kala Chart Generator")
    parser.add_argument("--name", type=str, default="User", help="Name of the person")
    parser.add_argument("--year", type=int, required=True, help="Birth year (e.g. 1983)")
    parser.add_argument("--month", type=int, required=True, help="Birth month (1-12)")
    parser.add_argument("--day", type=int, required=True, help="Birth day (1-31)")
    parser.add_argument("--hour", type=int, required=True, help="Birth hour (0-23)")
    parser.add_argument("--minute", type=int, required=True, help="Birth minute (0-59)")
    parser.add_argument("--lat", type=float, required=True, help="Latitude (e.g. 52.2036)")
    parser.add_argument("--lon", type=float, required=True, help="Longitude (e.g. 8.0442)")
    parser.add_argument("--tz", type=float, required=True, help="Timezone offset from UTC (e.g. 1.0 for CET)")

    args = parser.parse_args()

    # Step 1: Calculate the astronomy data (Ernst Wilhelm method)
    print("Calculating Tropical Rasis and Equatorial Nakshatras...")
    json_path = "vedic_context.json"
    generate_kala_chart(
        name=args.name,
        year=args.year,
        month=args.month,
        day=args.day,
        hour=args.hour,
        minute=args.minute,
        latitude=args.lat,
        longitude=args.lon,
        timezone_offset=args.tz,
        output_filepath=json_path
    )

    # Step 2: Render the beautiful SVG HTML design
    print("Rendering SVG Chart UI...")
    planets = generate_html_chart.parse_astra_json(json_path)
    south_svg = generate_html_chart.generate_south_indian(planets)
    north_svg = generate_html_chart.generate_north_indian(planets)
    
    html_path = "index.html"
    generate_html_chart.create_html(south_svg, north_svg, json_path, html_path)

    # Step 3: Automatically open in the browser
    file_url = f"file://{os.path.abspath(html_path)}"
    print(f"Done! Opening chart in browser: {file_url}")
    webbrowser.open(file_url)

if __name__ == "__main__":
    main()
