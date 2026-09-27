#!/usr/bin/env python3
"""
symbol_and_font_inspector.py
============================
A precision utility to:
1. Scan and filter all emojis, planetary glyphs, color circles, and symbols in the app.
2. Programmatically detect which font renders each symbol (via Chromium CDP or macOS CoreText).
3. Provide reusable filtering functions to strip or replace symbols in text.
"""

import os
import sys
import json
import argparse
import unicodedata
from collections import defaultdict

# Pre-defined domain sets for astrological & UI classification
PLANETARY_GLYPHS = {
    '☉': 'Sun',
    '☽': 'Moon',
    '☿': 'Mercury',
    '♀': 'Venus',
    '♂': 'Mars',
    '♃': 'Jupiter',
    '♄': 'Saturn',
    '☊': 'Rahu (North Node)',
    '☋': 'Ketu (South Node)',
    '♅': 'Uranus',
    '♆': 'Neptune',
    '♇': 'Pluto',
    '⚳': 'Ceres',
    '⚴': 'Pallas',
    '⚵': 'Juno',
    '⚶': 'Vesta',
    '⚷': 'Chiron'
}

ZODIAC_SYMBOLS = {
    '♈': 'Aries',
    '♉': 'Taurus',
    '♊': 'Gemini',
    '♋': 'Cancer',
    '♌': 'Leo',
    '♍': 'Virgo',
    '♎': 'Libra',
    '♏': 'Scorpio',
    '♐': 'Sagittarius',
    '♑': 'Capricorn',
    '♒': 'Aquarius',
    '♓': 'Pisces'
}

COLOR_INDICATORS = {
    '🟢': 'Green Circle',
    '🔴': 'Red Circle',
    '🟡': 'Yellow Circle',
    '🟠': 'Orange Circle',
    '🔵': 'Blue Circle',
    '🟣': 'Purple Circle',
    '⚫': 'Black Circle',
    '⚪': 'White Circle',
    '🟤': 'Brown Circle',
    '🟩': 'Green Square',
    '🟥': 'Red Square',
    '🟨': 'Yellow Square',
    '🟧': 'Orange Square',
    '🟦': 'Blue Square',
    '🟪': 'Purple Square',
    '⬛': 'Black Square',
    '⬜': 'White Square',
}

def classify_symbol(char: str) -> str:
    """Classifies a character into a human-readable astrological/UI category."""
    if char in PLANETARY_GLYPHS:
        return 'Planetary Glyph'
    if char in ZODIAC_SYMBOLS:
        return 'Zodiac Sign'
    if char in COLOR_INDICATORS:
        return 'Color Indicator'
    
    cp = ord(char)
    # Standard emoji blocks (Faces, People, Objects, Activities, Symbols)
    if (0x1F300 <= cp <= 0x1F9FF) or (0x1FA00 <= cp <= 0x1FAFF) or (0x1F600 <= cp <= 0x1F64F):
        return 'Emoji'
    
    # Dingbats & Miscellaneous Symbols
    if 0x2700 <= cp <= 0x27BF:
        return 'Dingbat / Checkmark'
    if 0x2600 <= cp <= 0x26FF:
        return 'Misc Symbol'
    if 0x25A0 <= cp <= 0x25FF:
        return 'Geometric Shape'
    if 0x2190 <= cp <= 0x21FF:
        return 'Arrow'
    
    cat = unicodedata.category(char)
    if cat == 'So':
        return 'Other Symbol'
    return 'Special Character'

def is_target_symbol(char: str) -> bool:
    """Returns True if the character is an emoji, planetary symbol, color dot, or UI symbol."""
    if char in PLANETARY_GLYPHS or char in ZODIAC_SYMBOLS or char in COLOR_INDICATORS:
        return True
    
    cp = ord(char)
    cat = unicodedata.category(char)
    
    # Exclude standard ASCII and Latin punctuation/alphanumeric
    if cp < 0x80:
        return False
    if cp in (0x00B0, 0x00A9, 0x00AE, 0x2018, 0x2019, 0x201C, 0x201D, 0x2013, 0x2014, 0x2026, 0x2022):
        # Degree sign, copyright, curly quotes, dashes, bullet
        return False
        
    # Emojis & Pictographs
    if 0x1F300 <= cp <= 0x1FAFF:
        return True
    # Miscellaneous symbols, Dingbats
    if 0x2600 <= cp <= 0x27BF:
        return True
    # Category 'So' (Symbol, other)
    if cat == 'So':
        return True
        
    return False

# ==============================================================================
# Filtering & Cleaning Utilities (Can be imported into any module)
# ==============================================================================

def strip_emojis(text: str) -> str:
    """Removes all emojis and color indicator circles from text."""
    return ''.join(c for c in text if classify_symbol(c) not in ('Emoji', 'Color Indicator'))

def strip_planetary_symbols(text: str) -> str:
    """Removes all planetary and zodiac glyphs from text."""
    return ''.join(c for c in text if c not in PLANETARY_GLYPHS and c not in ZODIAC_SYMBOLS)

def strip_all_symbols(text: str) -> str:
    """Removes all emojis, planetary glyphs, color circles, and UI dingbats from text."""
    return ''.join(c for c in text if not is_target_symbol(c))

def replace_symbols_with_labels(text: str) -> str:
    """Replaces emojis and astrological glyphs with plain readable labels (e.g. ☉ -> [Sun])."""
    result = []
    for c in text:
        if c in PLANETARY_GLYPHS:
            result.append(f'[{PLANETARY_GLYPHS[c]}]')
        elif c in ZODIAC_SYMBOLS:
            result.append(f'[{ZODIAC_SYMBOLS[c]}]')
        elif c in COLOR_INDICATORS:
            result.append(f'[{COLOR_INDICATORS[c]}]')
        elif is_target_symbol(c):
            name = unicodedata.name(c, 'SYMBOL').title()
            result.append(f'[{name}]')
        else:
            result.append(c)
    return ''.join(result)

# ==============================================================================
# Programmatic Font Resolution
# ==============================================================================

def resolve_font_coretext(char_str: str) -> str:
    """
    Programmatically asks the macOS CoreText typography engine which font
    it selects as fallback to render this specific character.
    """
    import ctypes
    from ctypes import c_void_p, c_char_p, Structure
    
    try:
        ct = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreText.framework/CoreText')
        cf = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
        
        cf.CFStringCreateWithCString.argtypes = [c_void_p, c_char_p, ctypes.c_uint32]
        cf.CFStringCreateWithCString.restype = c_void_p
        cf.CFStringGetLength.argtypes = [c_void_p]
        cf.CFStringGetLength.restype = ctypes.c_long
        cf.CFStringGetCString.argtypes = [c_void_p, c_char_p, ctypes.c_long, ctypes.c_uint32]
        cf.CFStringGetCString.restype = ctypes.c_bool
        cf.CFRelease.argtypes = [c_void_p]

        class CFRange(Structure):
            _fields_ = [('location', ctypes.c_long), ('length', ctypes.c_long)]

        ct.CTFontCreateWithName.argtypes = [c_void_p, ctypes.c_double, c_void_p]
        ct.CTFontCreateWithName.restype = c_void_p
        ct.CTFontCreateForString.argtypes = [c_void_p, c_void_p, CFRange]
        ct.CTFontCreateForString.restype = c_void_p
        ct.CTFontCopyFamilyName.argtypes = [c_void_p]
        ct.CTFontCopyFamilyName.restype = c_void_p

        kCFStringEncodingUTF8 = 0x08000100
        cf_str = cf.CFStringCreateWithCString(None, char_str.encode('utf-8'), kCFStringEncodingUTF8)
        length = cf.CFStringGetLength(cf_str)
        
        base_font = ct.CTFontCreateWithName(None, 14.0, None)
        matched_font = ct.CTFontCreateForString(base_font, cf_str, CFRange(0, length))
        cf_family = ct.CTFontCopyFamilyName(matched_font)
        
        buf = ctypes.create_string_buffer(256)
        cf.CFStringGetCString(cf_family, buf, 256, kCFStringEncodingUTF8)
        font_name = buf.value.decode('utf-8')
        
        cf.CFRelease(cf_str)
        cf.CFRelease(base_font)
        cf.CFRelease(matched_font)
        cf.CFRelease(cf_family)
        return font_name
    except Exception as e:
        return f'Unknown (Error: {e})'

async def resolve_fonts_browser_async(symbols: list, font_family: str = None) -> dict:
    """
    Programmatically asks Chromium (via Playwright & Chrome DevTools Protocol)
    which platform font is used to render each symbol under the app's CSS font stack.
    """
    from playwright.async_api import async_playwright
    
    if font_family is None:
        font_family = "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif"
        
    results = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Build HTML page
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body {{ font-family: {font_family}; font-size: 24px; }}
          </style>
        </head>
        <body>
        """
        for idx, sym in enumerate(symbols):
            html += f'<div id="node_{idx}">{sym}</div>\n'
        html += "</body></html>"
        
        await page.set_content(html)
        
        # Use Chrome DevTools Protocol (CDP) to inspect actual rendered platform font
        cdp = await page.context.new_cdp_session(page)
        await cdp.send('DOM.enable')
        await cdp.send('CSS.enable')
        doc = await cdp.send('DOM.getDocument')
        
        for idx, sym in enumerate(symbols):
            try:
                node = await cdp.send('DOM.querySelector', {'nodeId': doc['root']['nodeId'], 'selector': f'#node_{idx}'})
                node_id = node['nodeId']
                fonts_info = await cdp.send('CSS.getPlatformFontsForNode', {'nodeId': node_id})
                fonts = fonts_info.get('fonts', [])
                font_names = [f['familyName'] for f in fonts]
                results[sym] = font_names[0] if font_names else 'Default Fallback'
            except Exception:
                results[sym] = 'Unknown'
                
        await browser.close()
    return results

def resolve_fonts_browser(symbols: list, font_family: str = None) -> dict:
    """Synchronous wrapper for resolve_fonts_browser_async."""
    import asyncio
    return asyncio.run(resolve_fonts_browser_async(symbols, font_family))

# ==============================================================================
# Codebase Scanner
# ==============================================================================

def scan_codebase(root_dir: str = '.'):
    """Scans all source code in the repository and finds all target symbols."""
    exts = ('.py', '.js', '.html', '.css', '.json')
    ignore_dirs = {'.git', 'venv', '__pycache__', 'node_modules', '.gemini', 'cache', '.pytest_cache'}
    
    symbol_records = defaultdict(lambda: {'count': 0, 'files': defaultdict(int)})
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Exclude ignored folders
        dirnames[:] = [
            d for d in dirnames 
            if d not in ignore_dirs and not any(p in os.path.join(dirpath, d) for p in ['/source-material/sanskrit_texts', '/codebase_export'])
        ]
        
        for fname in filenames:
            if fname.endswith(exts) and not fname.startswith('codebase_export'):
                filepath = os.path.join(dirpath, fname)
                relpath = os.path.relpath(filepath, root_dir)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        for lno, line in enumerate(f, 1):
                            for char in line:
                                if is_target_symbol(char):
                                    symbol_records[char]['count'] += 1
                                    symbol_records[char]['files'][relpath] += 1
                except Exception:
                    pass
                    
    return symbol_records

# ==============================================================================
# CLI Entrypoint
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Astra Symbol & Font Inspector")
    parser.add_argument('--scan', action='store_true', help="Scan the Astra codebase for symbols and emojis")
    parser.add_argument('--detect-fonts', action='store_true', help="Programmatically detect which font renders each symbol")
    parser.add_argument('--engine', choices=['browser', 'os', 'both'], default='both', help="Font detection engine (Chromium CDP, macOS CoreText, or both)")
    parser.add_argument('--filter-text', type=str, help="Filter out emojis and symbols from a given text string")
    parser.add_argument('--replace-text', type=str, help="Replace symbols with text labels in a given string")
    parser.add_argument('--json', action='store_true', help="Output results in JSON format")
    args = parser.parse_args()

    if args.filter_text:
        print("Original:", args.filter_text)
        print("Cleaned (No emojis/symbols):", strip_all_symbols(args.filter_text))
        return

    if args.replace_text:
        print("Original:", args.replace_text)
        print("Replaced:", replace_symbols_with_labels(args.replace_text))
        return

    # Default action: Scan and report
    print("=" * 80)
    print("ASTRA SYMBOL, EMOJI & FONT DETECTOR")
    print("=" * 80)
    print("Scanning codebase...")
    symbols = scan_codebase('.')
    print(f"Discovered {len(symbols)} unique symbols across the codebase.\n")

    # Font detection
    browser_fonts = {}
    os_fonts = {}
    
    unique_chars = list(symbols.keys())
    
    if args.detect_fonts or True:
        if args.engine in ('os', 'both') and sys.platform == 'darwin':
            print("Querying macOS CoreText font engine...")
            for ch in unique_chars:
                os_fonts[ch] = resolve_font_coretext(ch)
                
        if args.engine in ('browser', 'both'):
            print("Querying Chromium Browser font engine (Playwright CDP)...")
            try:
                browser_fonts = resolve_fonts_browser(unique_chars)
            except Exception as e:
                print(f"Warning: Browser font detection failed: {e}")

    # Build report data
    report_rows = []
    for ch, data in sorted(symbols.items(), key=lambda x: x[1]['count'], reverse=True):
        cat = classify_symbol(ch)
        cp = f"U+{ord(ch):04X}"
        name = unicodedata.name(ch, 'UNKNOWN')
        b_font = browser_fonts.get(ch, 'N/A')
        o_font = os_fonts.get(ch, 'N/A')
        
        top_files = sorted(data['files'].items(), key=lambda x: x[1], reverse=True)[:3]
        file_summary = ", ".join([f"{f} ({c}x)" for f, c in top_files])
        
        report_rows.append({
            'symbol': ch,
            'codepoint': cp,
            'name': name,
            'category': cat,
            'count': data['count'],
            'browser_font': b_font,
            'os_font': o_font,
            'locations': file_summary
        })

    if args.json:
        print(json.dumps(report_rows, indent=2))
        return

    # Display grouped by Category
    categories = ['Planetary Glyph', 'Zodiac Sign', 'Color Indicator', 'Emoji', 'Misc Symbol', 'Dingbat / Checkmark', 'Geometric Shape', 'Arrow', 'Other Symbol']
    
    for cat in categories:
        items = [r for r in report_rows if r['category'] == cat]
        if not items:
            continue
        print(f"\n### {cat.upper()}S ({len(items)} items)")
        print(f"{'Sym':<4} {'Codepoint':<9} {'Count':<7} {'Browser Font (Chromium)':<26} {'macOS Font (CoreText)':<24} {'Description'}")
        print("-" * 110)
        for r in items:
            print(f"{r['symbol']:<4} {r['codepoint']:<9} {r['count']:<7} {r['browser_font']:<26} {r['os_font']:<24} {r['name']}")

if __name__ == '__main__':
    main()
