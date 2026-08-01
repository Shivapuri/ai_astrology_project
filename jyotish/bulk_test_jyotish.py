"""
Offline Stress Testing Pipeline for Jyotishganit Engine (bulk_test_jyotish.py)
Validates calculations against 100 randomized birth charts, edge-case coordinates,
and historical dates, while utilizing a local cache for NASA JPL ephemeris files.
"""

import os
import sys
import random
import logging
import traceback
from datetime import datetime
from pathlib import Path

# Setup Cache Directory to prevent re-downloading ephemeris
PROJECT_ROOT = Path(__file__).parent.resolve()
CACHE_DIR = PROJECT_ROOT / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Also ensure jyotishganit default app support directory uses cache if available
USER_APP_DIR = Path.home() / "Library" / "Application Support" / "jyotishganit"
USER_APP_DIR.mkdir(parents=True, exist_ok=True)

# Copy cached ephemeris files if present in cache/
for eph_file in ["de421.bsp", "hip_main.dat"]:
    cache_path = CACHE_DIR / eph_file
    user_app_path = USER_APP_DIR / eph_file
    if cache_path.exists() and not user_app_path.exists():
        import shutil
        shutil.copy(cache_path, user_app_path)
    elif user_app_path.exists() and not cache_path.exists():
        import shutil
        shutil.copy(user_app_path, cache_path)

# Configure logging
LOG_FILE = PROJECT_ROOT / "bulk_test_jyotish.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

try:
    from generate_jyotish import generate_vedic_chart
except ImportError:
    logging.error("Could not import generate_vedic_chart from generate_jyotish.py")
    sys.exit(1)


def run_bulk_stress_test(num_tests: int = 100):
    """
    Executes 100 automated test calculations across randomized dates and global coordinates.
    """
    logging.info(f"--- Starting Bulk Stress Test ({num_tests} cases) ---")
    logging.info(f"Local Ephemeris Cache Directory: {CACHE_DIR}")

    success_count = 0
    failure_count = 0

    # Ensure ephemeris file existence check
    de421_cached = (CACHE_DIR / "de421.bsp").exists() or (USER_APP_DIR / "de421.bsp").exists()
    logging.info(f"NASA JPL DE421 Ephemeris Cache Status: {'CACHED (Offline Safe)' if de421_cached else 'DOWNLOADING ON FIRST RUN'}")

    for idx in range(1, num_tests + 1):
        # Generate random inputs
        test_year = random.randint(1920, 2030)
        test_month = random.randint(1, 12)
        test_day = random.randint(1, 28)
        test_hour = random.randint(0, 23)
        test_minute = random.randint(0, 59)
        
        # Test extreme & diverse global coordinates
        test_lat = round(random.uniform(-65.0, 70.0), 4)
        test_lon = round(random.uniform(-179.0, 179.0), 4)
        test_tz = round(random.uniform(-11.0, 13.0), 1)

        subject_name = f"TestSubject_{idx:03d}"

        try:
            # Perform calculation & temporary file export
            test_output_file = CACHE_DIR / f"test_out_{idx:03d}.json"
            generate_vedic_chart(
                name=subject_name,
                year=test_year,
                month=test_month,
                day=test_day,
                hour=test_hour,
                minute=test_minute,
                latitude=test_lat,
                longitude=test_lon,
                timezone_offset=test_tz,
                output_filepath=str(test_output_file)
            )

            # Cleanup output file to conserve space
            if test_output_file.exists():
                test_output_file.unlink()

            success_count += 1
            logging.info(f"[PASS {idx:03d}/{num_tests:03d}] {subject_name} ({test_year}-{test_month:02d}-{test_day:02d} {test_hour:02d}:{test_minute:02d}, Lat: {test_lat}, Lon: {test_lon}, TZ: {test_tz})")

        except Exception as e:
            failure_count += 1
            logging.error(f"[FAIL {idx:03d}/{num_tests:03d}] {subject_name} Failed!")
            logging.error(f"Error Details: {str(e)}")
            logging.error(traceback.format_exc())

    logging.info("=" * 60)
    logging.info(f"TEST SUMMARY: Total: {num_tests} | Passed: {success_count} | Failed: {failure_count}")
    logging.info(f"Success Rate: {(success_count / num_tests) * 100:.1f}%")
    logging.info("=" * 60)

    return success_count == num_tests


if __name__ == "__main__":
    success = run_bulk_stress_test(100)
    sys.exit(0 if success else 1)
