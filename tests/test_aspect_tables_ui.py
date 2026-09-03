"""
Test that the three Aspect grid tables actually render data rows in the browser.

This is a regression test — a previous cleanup accidentally deleted the HTML
templates and JS rendering logic, leaving empty yellow boxes.  We catch that
by asserting that the tables have at least 7 data rows (one per classical
planet) plus the +/- total rows.
"""

import pytest
from playwright.sync_api import sync_playwright


FLASK_URL = "http://127.0.0.1:5001"
import urllib.request
CHART_ID = "angelina-jolie"

def is_server_running(url=FLASK_URL):
    try:
        urllib.request.urlopen(url)
        return True
    except:
        return False

@pytest.fixture(scope="module", autouse=True)
def check_server():
    if not is_server_running():
        pytest.skip("Flask server is not running on port 5001")

@pytest.fixture(scope="module")
def page():
    """Launch a headless browser, load Angelina Jolie's chart, and yield the page."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page()
        pg.goto(FLASK_URL)
        pg.wait_for_timeout(1500)

        # Load Angelina Jolie
        pg.evaluate(f"loadChart('{CHART_ID}')")
        pg.wait_for_timeout(2000)

        yield pg
        browser.close()


def _count_rows(page, table_id: str) -> int:
    """Return the number of <tr> elements inside a table's <tbody>."""
    return page.evaluate(
        f"""(() => {{
            const t = document.getElementById('{table_id}');
            if (!t) return 0;
            const tbody = t.querySelector('tbody');
            return tbody ? tbody.querySelectorAll('tr').length : 0;
        }})()"""
    )


def _count_header_cols(page, table_id: str) -> int:
    """Return the number of <th> elements in the thead row."""
    return page.evaluate(
        f"""(() => {{
            const t = document.getElementById('{table_id}');
            if (!t) return 0;
            const thead = t.querySelector('thead');
            return thead ? thead.querySelectorAll('th').length : 0;
        }})()"""
    )


class TestAspectTableRendering:
    """Ensure the three Kala-style aspect matrix tables render non-empty data."""

    @pytest.mark.parametrize("table_id,expected_min_rows", [
        ("kalaAspectsPlanetsTable", 11),        # 9 planets + 2 totals
        ("kalaAspectsBhavaChalitaTable", 9),     # 7 planets + 2 totals
        ("kalaAspectsEqualHousesTable", 9),       # 7 planets + 2 totals
    ])
    def test_table_has_data_rows(self, page, table_id, expected_min_rows):
        """Each table must have enough rows for all planets plus +/- totals."""
        rows = _count_rows(page, table_id)
        assert rows >= expected_min_rows, (
            f"Table #{table_id} has only {rows} rows, expected >= {expected_min_rows}. "
            f"The table is probably not rendering data."
        )

    @pytest.mark.parametrize("table_id,expected_cols", [
        ("kalaAspectsPlanetsTable", 10),          # blank + 9 planets
        ("kalaAspectsBhavaChalitaTable", 13),     # blank + 12 houses
        ("kalaAspectsEqualHousesTable", 13),       # blank + 12 houses
    ])
    def test_table_has_header_columns(self, page, table_id, expected_cols):
        """Each table must have the right number of column headers."""
        cols = _count_header_cols(page, table_id)
        assert cols == expected_cols, (
            f"Table #{table_id} has {cols} header columns, expected {expected_cols}."
        )

    def test_planets_table_has_nonzero_values(self, page):
        """The planets table must contain at least one cell with a numeric value > 0."""
        has_value = page.evaluate(
            """(() => {
                const t = document.getElementById('kalaAspectsPlanetsTable');
                if (!t) return false;
                const cells = t.querySelectorAll('tbody td');
                for (const c of cells) {
                    const v = parseInt(c.textContent);
                    if (!isNaN(v) && v > 0) return true;
                }
                return false;
            })()"""
        )
        assert has_value, "Planets table has no non-zero numeric values — data is not loading."

    def test_plus_minus_totals_present(self, page):
        """The planets table must have rows labelled '+' and '-'."""
        labels = page.evaluate(
            """(() => {
                const t = document.getElementById('kalaAspectsPlanetsTable');
                if (!t) return [];
                const rows = t.querySelectorAll('tbody tr');
                const lastTwo = Array.from(rows).slice(-2);
                return lastTwo.map(r => r.querySelector('td strong')?.textContent || '');
            })()"""
        )
        assert '+' in labels, "Missing '+' totals row in planets table."
        assert '-' in labels, "Missing '-' totals row in planets table."
