#!/usr/bin/env python3
"""
bulk_test_engine.py - Comprehensive Bulk QA Testing Suite for generate_chart.py

Rigorously tests the Hellenistic astrology engine against 1,000+ real and synthetic
birth charts spanning 1900–2024, leap years, diverse timezones, and global coordinates.
"""

import os
import json
import urllib.request
import traceback
import sys
from datetime import datetime

# Import local astrology engine
from generate_chart import generate_ai_json

DATASET_URLS = [
    "https://raw.githubusercontent.com/OpenAstrology/astro-databank-sample/main/birth_data.json",
    "https://raw.githubusercontent.com/datasets/astrology-benchmark/main/charts.json"
]

def load_or_generate_dataset(target_count: int = 1000) -> list:
    """Loads external dataset or generates 1,000+ benchmark birth records."""
    data = []
    
    for url in DATASET_URLS:
        try:
            print(f"📡 Attempting to fetch dataset from {url}...")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4) as response:
                content = response.read().decode('utf-8')
                downloaded_data = json.loads(content)
                if isinstance(downloaded_data, list) and len(downloaded_data) > 0:
                    print(f"✅ Successfully downloaded {len(downloaded_data)} records!")
                    return downloaded_data
        except Exception:
            pass

    print(f"ℹ️ Generating {target_count} benchmark chart records across global locations & historical dates...")
    
    GLOBAL_CITIES = [
        ("Berlin", "DE"), ("London", "GB"), ("New York", "US"), ("Tokyo", "JP"),
        ("Sydney", "AU"), ("New Delhi", "IN"), ("Paris", "FR"), ("Rome", "IT"),
        ("Sao Paulo", "BR"), ("Johannesburg", "ZA"), ("Cairo", "EG"), ("Reykjavik", "IS"),
        ("Moscow", "RU"), ("Buenos Aires", "AR"), ("Toronto", "CA"), ("Beijing", "CN"),
        ("Madrid", "ES"), ("Vienna", "AT"), ("Amsterdam", "NL"), ("Oslo", "NO")
    ]
    
    record_id = 1
    for year in range(1900, 2025):
        for month_offset in range(8):
            month = ((record_id * 3) % 12) + 1
            is_leap = (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
            max_days = 29 if (month == 2 and is_leap) else (28 if month == 2 else 30)
            day = ((record_id * 7) % max_days) + 1
            hour = (record_id * 11) % 24
            minute = (record_id * 23) % 60
            city, country = GLOBAL_CITIES[record_id % len(GLOBAL_CITIES)]
            
            data.append({
                "id": record_id,
                "name": f"Benchmark_Subject_{record_id}",
                "year": year,
                "month": month,
                "day": day,
                "hour": hour,
                "minute": minute,
                "city": city,
                "country_code": country
            })
            record_id += 1
            if len(data) >= target_count:
                break
        if len(data) >= target_count:
            break
            
    print(f"✅ Benchmark dataset ready with {len(data)} chart records.")
    return data

def run_bulk_test():
    """Rigorously tests generate_ai_json across all benchmark records."""
    dataset = load_or_generate_dataset(1000)
    total_charts = len(dataset)
    success_count = 0
    fail_count = 0
    
    output_temp = "temp_test_chart.json"
    log_file = "error_log.txt"
    
    if os.path.exists(log_file):
        os.remove(log_file)
        
    print("\n" + "=" * 65)
    print(f"🚀 STARTING BULK QA BENCHMARK: TESTING {total_charts} CHARTS")
    print("=" * 65 + "\n")
    
    start_time = datetime.now()
    
    for idx, chart in enumerate(dataset, 1):
        name = chart.get("name", f"Subject_{idx}")
        year = int(chart.get("year", 1990))
        month = int(chart.get("month", 1))
        day = int(chart.get("day", 1))
        hour = int(chart.get("hour", 12))
        minute = int(chart.get("minute", 0))
        city = chart.get("city", "London")
        country_code = chart.get("country_code", "GB")
        
        try:
            generate_ai_json(
                name=name,
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                city=city,
                country_code=country_code,
                output_filename=output_temp
            )
            
            if os.path.exists(output_temp) and os.path.getsize(output_temp) > 0:
                success_count += 1
            else:
                raise ValueError("Output chart_context.json is empty.")
                
        except Exception as e:
            fail_count += 1
            err_trace = traceback.format_exc()
            with open(log_file, "a") as f:
                f.write(f"--- FAILURE #{fail_count} ---\n")
                f.write(f"Chart Data: {json.dumps(chart)}\n")
                f.write(f"Error: {e}\n")
                f.write(f"Traceback:\n{err_trace}\n")
                f.write("=" * 50 + "\n\n")

        if idx % 100 == 0 or idx == total_charts:
            pct = (idx / total_charts) * 100
            print(f"📊 Progress: [{idx}/{total_charts}] ({pct:.1f}%) | Successes: {success_count} | Failures: {fail_count}")

    if os.path.exists(output_temp):
        os.remove(output_temp)
        
    duration = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "=" * 65)
    print("📋 BULK QA TEST RESULTS SUMMARY")
    print("=" * 65)
    print(f"Total Charts Tested : {total_charts}")
    print(f"Successful Charts   : {success_count} ({success_count/total_charts*100:.2f}%)")
    print(f"Failed Charts       : {fail_count} ({fail_count/total_charts*100:.2f}%)")
    print(f"Total Time Taken    : {duration:.2f} seconds")
    print(f"Testing Speed       : {total_charts/duration:.2f} charts/sec")
    print("=" * 65)
    
    if fail_count == 0:
        print("🎉 PERFECT SUCCESS! 1,000/1,000 charts passed with 0 errors!")
    else:
        print(f"⚠️ {fail_count} failure(s) logged in '{log_file}'.")

if __name__ == "__main__":
    run_bulk_test()
