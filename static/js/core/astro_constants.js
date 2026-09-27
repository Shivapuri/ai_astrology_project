/**
 * Astra Master Astrological Catalog (Single Source of Truth)
 * 
 * ALL planetary, zodiacal, divisional, and dignitary metadata is defined HERE.
 * Modifying a glyph, name, or token here instantly updates every widget across the app.
 * 
 * Complies with static/GEMINI.md:
 * - Monochrome Unicode Variation Selector 15 (\uFE0E) for all signs
 * - Canonical sanskrit terminology and color tokens
 */

const AstroCatalog = {
    // -------------------------------------------------------------------------
    // 1. ZODIAC SIGNS (1-indexed Aries through Pisces)
    // -------------------------------------------------------------------------
    signs: [
        { id: 1,  name: 'Aries',       abbr: 'Ar', glyph: '\u2648\uFE0E', lord: 'Mars',    element: 'Fire',  modality: 'Movable', polarity: 'Active',  udaya: 'Prishtodaya', anatomy: 'Head & Brain' },
        { id: 2,  name: 'Taurus',      abbr: 'Ta', glyph: '\u2649\uFE0E', lord: 'Venus',   element: 'Earth', modality: 'Fixed',   polarity: 'Passive', udaya: 'Prishtodaya', anatomy: 'Face & Throat' },
        { id: 3,  name: 'Gemini',      abbr: 'Ge', glyph: '\u264A\uFE0E', lord: 'Mercury', element: 'Air',   modality: 'Dual',    polarity: 'Active',  udaya: 'Shirshodaya', anatomy: 'Shoulders & Arms' },
        { id: 4,  name: 'Cancer',      abbr: 'Cn', glyph: '\u264B\uFE0E', lord: 'Moon',    element: 'Water', modality: 'Movable', polarity: 'Passive', udaya: 'Prishtodaya', anatomy: 'Chest & Stomach' },
        { id: 5,  name: 'Leo',         abbr: 'Le', glyph: '\u264C\uFE0E', lord: 'Sun',     element: 'Fire',  modality: 'Fixed',   polarity: 'Active',  udaya: 'Shirshodaya', anatomy: 'Heart & Spine' },
        { id: 6,  name: 'Virgo',       abbr: 'Vi', glyph: '\u264D\uFE0E', lord: 'Mercury', element: 'Earth', modality: 'Dual',    polarity: 'Passive', udaya: 'Shirshodaya', anatomy: 'Small Intestines' },
        { id: 7,  name: 'Libra',       abbr: 'Li', glyph: '\u264E\uFE0E', lord: 'Venus',   element: 'Air',   modality: 'Movable', polarity: 'Active',  udaya: 'Shirshodaya', anatomy: 'Kidneys & Lumbar' },
        { id: 8,  name: 'Scorpio',     abbr: 'Sc', glyph: '\u264F\uFE0E', lord: 'Mars',    element: 'Water', modality: 'Fixed',   polarity: 'Passive', udaya: 'Shirshodaya', anatomy: 'Pelvis & Excretory' },
        { id: 9,  name: 'Sagittarius', abbr: 'Sg', glyph: '\u2650\uFE0E', lord: 'Jupiter', element: 'Fire',  modality: 'Dual',    polarity: 'Active',  udaya: 'Prishtodaya', anatomy: 'Hips & Thighs' },
        { id: 10, name: 'Capricorn',   abbr: 'Cp', glyph: '\u2651\uFE0E', lord: 'Saturn',  element: 'Earth', modality: 'Movable', polarity: 'Passive', udaya: 'Prishtodaya', anatomy: 'Knees & Joints' },
        { id: 11, name: 'Aquarius',    abbr: 'Aq', glyph: '\u2652\uFE0E', lord: 'Saturn',  element: 'Air',   modality: 'Fixed',   polarity: 'Active',  udaya: 'Shirshodaya', anatomy: 'Calves & Ankles' },
        { id: 12, name: 'Pisces',      abbr: 'Pi', glyph: '\u2653\uFE0E', lord: 'Jupiter', element: 'Water', modality: 'Dual',    polarity: 'Passive', udaya: 'Ubhayodaya',  anatomy: 'Feet & Lymphatics' }
    ],

    // -------------------------------------------------------------------------
    // 2. PLANETS (Grahas) & Key Bodies
    // -------------------------------------------------------------------------
    planets: {
        'Sun':     { glyph: '☉\uFE0E', abbr: 'Su', sanskrit: 'Sūrya',   colorToken: 'var(--graha-sun)',     order: 1 },
        'Moon':    { glyph: '☽\uFE0E', abbr: 'Mo', sanskrit: 'Chandra', colorToken: 'var(--graha-moon)',    order: 2 },
        'Mars':    { glyph: '♂\uFE0E', abbr: 'Ma', sanskrit: 'Mangala', colorToken: 'var(--graha-mars)',    order: 3 },
        'Mercury': { glyph: '☿\uFE0E', abbr: 'Me', sanskrit: 'Budha',   colorToken: 'var(--graha-mercury)', order: 4 },
        'Jupiter': { glyph: '♃\uFE0E', abbr: 'Ju', sanskrit: 'Guru',    colorToken: 'var(--graha-jupiter)', order: 5 },
        'Venus':   { glyph: '♀\uFE0E', abbr: 'Ve', sanskrit: 'Śukra',   colorToken: 'var(--graha-venus)',   order: 6 },
        'Saturn':  { glyph: '♄\uFE0E', abbr: 'Sa', sanskrit: 'Śani',    colorToken: 'var(--graha-saturn)',  order: 7 },
        'Rahu':    { glyph: '☊\uFE0E', abbr: 'Ra', sanskrit: 'Rāhu',    colorToken: 'var(--graha-rahu)',    order: 8 },
        'Ketu':    { glyph: '☋\uFE0E', abbr: 'Ke', sanskrit: 'Ketu',    colorToken: 'var(--graha-ketu)',    order: 9 },
        'Lagna':   { glyph: 'Asc',     abbr: 'Asc', sanskrit: 'Lagna',  colorToken: 'var(--graha-lagna)',   order: 0 },
        // Outer planets & Asteroids for full catalog coverage
        'Uranus':  { glyph: '♅', abbr: 'Ur', sanskrit: 'Uranus',  colorToken: 'var(--text-heading)',  order: 10 },
        'Neptune': { glyph: '♆', abbr: 'Ne', sanskrit: 'Neptune', colorToken: 'var(--text-heading)',  order: 11 },
        'Pluto':   { glyph: '♇', abbr: 'Pl', sanskrit: 'Pluto',   colorToken: 'var(--text-heading)',  order: 12 },
        'Chiron':  { glyph: '⚷', abbr: 'Ch', sanskrit: 'Chiron',  colorToken: 'var(--text-heading)',  order: 13 },
        'Ceres':   { glyph: '⚳', abbr: 'Ce', sanskrit: 'Ceres',   colorToken: 'var(--text-heading)',  order: 14 },
        'Pallas':  { glyph: '⚴', abbr: 'Pa', sanskrit: 'Pallas',  colorToken: 'var(--text-heading)',  order: 15 },
        'Juno':    { glyph: '⚵', abbr: 'Ju', sanskrit: 'Juno',    colorToken: 'var(--text-heading)',  order: 16 },
        'Vesta':   { glyph: '⚶', abbr: 'Ve', sanskrit: 'Vesta',   colorToken: 'var(--text-heading)',  order: 17 }
    },

    // -------------------------------------------------------------------------
    // 3. ELEMENTS & MODALITIES METADATA
    // -------------------------------------------------------------------------
    elements: {
        'Fire':  { sanskrit: 'Agni',    varna: 'Kshatriya', dosha: 'Pitta', color: '#c0392b', bg: '#fdf2f0' },
        'Earth': { sanskrit: 'Prithvi', varna: 'Shudra',    dosha: 'Kapha', color: '#795548', bg: '#f5f0eb' },
        'Air':   { sanskrit: 'Vayu',    varna: 'Vaishya',   dosha: 'Vata',  color: '#1976d2', bg: '#f0f7fe' },
        'Water': { sanskrit: 'Jala',    varna: 'Brahmin',   dosha: 'Kapha', color: '#00897b', bg: '#eef8f7' }
    },

    modalities: {
        'Movable': { sanskrit: 'Chara',        label: 'Movable', color: '#b91c1c', bg: '#fee2e2' },
        'Fixed':   { sanskrit: 'Sthira',       label: 'Fixed',   color: '#1e40af', bg: '#dbeafe' },
        'Dual':    { sanskrit: 'Dwisvabhava',  label: 'Dual',    color: '#065f46', bg: '#d1fae5' }
    },

    // -------------------------------------------------------------------------
    // 4. FAST LOOKUP METHODS
    // -------------------------------------------------------------------------
    getSign(nameOrNum) {
        if (typeof nameOrNum === 'number') {
            return this.signs[(nameOrNum - 1 + 12) % 12];
        }
        if (!nameOrNum) return null;
        const str = String(nameOrNum).toLowerCase().trim();
        return this.signs.find(s => s.name.toLowerCase() === str || s.abbr.toLowerCase() === str) || null;
    },

    getPlanet(name) {
        if (!name) return { glyph: '', abbr: '', sanskrit: '', colorToken: 'var(--text-heading)' };
        if (this.planets[name]) return this.planets[name];
        const foundKey = Object.keys(this.planets).find(k => k.toLowerCase() === String(name).toLowerCase());
        if (foundKey) return this.planets[foundKey];
        return {
            glyph: name,
            abbr: String(name).substring(0, 2),
            sanskrit: name,
            colorToken: 'var(--text-heading)'
        };
    },

    getSignLord(signName) {
        const s = this.getSign(signName);
        return s ? s.lord : 'Unknown';
    },

    getSignsRuledBy(planetName) {
        if (!planetName) return [];
        const pNorm = String(planetName).toLowerCase().trim();
        const coRulers = {
            'rahu': ['Aquarius'],
            'ketu': ['Scorpio']
        };
        const standard = this.signs.filter(s => s.lord.toLowerCase() === pNorm).map(s => s.name);
        if (coRulers[pNorm]) {
            return Array.from(new Set([...standard, ...coRulers[pNorm]]));
        }
        return standard;
    },

    getAspectingSigns(signName) {
        // Jaimini Rashi Drishti: Movable aspects Fixed (except adjacent); Fixed aspects Movable (except adjacent); Dual aspects Dual.
        const rashiAspects = {
            'Aries':       ['Leo', 'Scorpio', 'Aquarius'],
            'Taurus':      ['Cancer', 'Libra', 'Capricorn'],
            'Gemini':      ['Virgo', 'Sagittarius', 'Pisces'],
            'Cancer':      ['Scorpio', 'Aquarius', 'Taurus'],
            'Leo':         ['Libra', 'Capricorn', 'Aries'],
            'Virgo':       ['Gemini', 'Sagittarius', 'Pisces'],
            'Libra':       ['Aquarius', 'Taurus', 'Leo'],
            'Scorpio':     ['Capricorn', 'Aries', 'Cancer'],
            'Sagittarius': ['Gemini', 'Virgo', 'Pisces'],
            'Capricorn':   ['Taurus', 'Leo', 'Scorpio'],
            'Aquarius':    ['Aries', 'Cancer', 'Libra'],
            'Pisces':      ['Gemini', 'Virgo', 'Sagittarius']
        };
        const s = this.getSign(signName);
        const resolvedName = s ? s.name : signName;
        return rashiAspects[resolvedName] || [];
    }
};

// Global export for browser & node / testing environments
if (typeof window !== 'undefined') {
    window.AstroCatalog = AstroCatalog;
}
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AstroCatalog };
}
