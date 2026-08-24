# Jyotish Engine: Shad Bala (Six-Fold Strength)

This module calculates Shad Bala, the exact quantification of a planet's inherent strength. 

---

## 1. Simple Description (For the Layperson)
Think of **Shad Bala** like measuring the raw "horsepower" of a planet's engine. It tells us exactly how much pure energy or force a planet has to do its job. 

However, it's very important to understand that Shad Bala **only** measures raw power (quantity). It does *not* tell us whether the planet will use that power for good or for bad (quality). As Ernst Wilhelm explains, it measures how much weight the planet can carry, but other calculations (like Ishta/Kashta Phala) tell us whether it is carrying gold or lead.

Shad Bala is calculated by adding up points (called *Virupas*) from six different sources:
1. **Sthana Bala (Positional Strength):** How strong is it based on the exact zodiac sign and degree it's sitting in?
2. **Dig Bala (Directional Strength):** Is the planet in its favorite part of the sky? (e.g., the Sun is strongest at high noon).
3. **Kala Bala (Time Strength):** How strong is the planet based on the time of day, day of the week, and phase of the Moon?
4. **Cheshta Bala (Motional Strength):** Is the planet moving fast or slow? Is it retrograde (closest to Earth)?
5. **Naisargika Bala (Natural Strength):** The permanent, natural brightness of the planet (the Sun is always naturally the strongest, Saturn the weakest).
6. **Drik Bala (Aspectual Strength):** How much energy is it gaining or losing from other planets looking at it?

---

## 2. Technical AI Description (Logic Constraints)
If you are modifying `shadbala.py`, strictly observe these mathematical rules.
The final Shad Bala is the sum of 6 components, measured in *Virupas* (60 Virupas = 1 Rupa). 

### Phase 1: Naisargika Bala (Natural Strength)
This is a fixed constant for each planet regardless of the chart:
- Sun: 60.0 Virupas
- Moon: 51.4 Virupas
- Venus: 42.8 Virupas
- Jupiter: 34.3 Virupas
- Mercury: 25.7 Virupas
- Mars: 17.1 Virupas
- Saturn: 8.6 Virupas

### Phase 2: Dig Bala (Directional Strength)
Each planet gets 60 Virupas at its optimal House Cusp and 0 Virupas at the exact opposite cusp (linearly interpolating in between based on degrees):
- Sun & Mars: Strongest at 10th House Cusp (Nabhoga/MC). Weakest at 4th.
- Moon & Venus: Strongest at 4th House Cusp (Patala/IC). Weakest at 10th.
- Jupiter & Mercury: Strongest at 1st House Cusp (Vilagna/Lagna). Weakest at 7th.
- Saturn: Strongest at 7th House Cusp (Badhu/Descendant). Weakest at 1st.

### Phase 3: Sthana Bala - Component 1: Uccha Bala (Exaltation Strength)
Uccha Bala measures the strength a planet derives from being close to its deep exaltation point. 
- Maximum strength (60 Virupas) is achieved at the exact degree of Deep Exaltation.
- Minimum strength (0 Virupas) is achieved at the exact degree of Deep Debilitation.
- For every 3 degrees a planet moves away from deep debilitation toward deep exaltation, it gains 1 Virupa (because 180 degrees / 60 Virupas = 3 degrees per Virupa).

The exact Deep Exaltation points are:
- Sun: 10° Aries (Absolute longitude: 10.0°)
- Moon: 3° Taurus (Absolute longitude: 33.0°)
- Mars: 28° Capricorn (Absolute longitude: 298.0°)
- Mercury: 15° Virgo (Absolute longitude: 165.0°)
- Jupiter: 5° Cancer (Absolute longitude: 95.0°)
- Venus: 27° Pisces (Absolute longitude: 357.0°)
- Saturn: 20° Libra (Absolute longitude: 200.0°)

### Phase 3: Sthana Bala - Component 2: Ojayugmarasyamsa Bala (Odd/Even Strength)
Venus and Moon naturally thrive in Even (female) signs and Even Navamsas. They gain 15 Virupas in an Even Rasi and an additional 15 Virupas in an Even Navamsa. The other planets (Sun, Mars, Jupiter, Mercury, Saturn) gain 15 Virupas in an Odd (male) Rasi and an additional 15 Virupas in an Odd Navamsa. Maximum possible points: 30 Virupas.

### Phase 3: Sthana Bala - Component 3: Kendra Bala (Angular Strength)
Planets are strongest when angular (in the 1st, 4th, 7th, or 10th houses from the Ascendant).
- Kendra (Angle: 1, 4, 7, 10): 60 Virupas
- Panapara (Succedent: 2, 5, 8, 11): 30 Virupas
- Apoklima (Cadent: 3, 6, 9, 12): 15 Virupas

### Phase 3: Sthana Bala - Component 4: Drekkana Bala (Decanate Strength)
Depending on the gender of the planet, it thrives in different 10-degree segments of a sign.
- Male planets (Sun, Mars, Jupiter): Gain 15 Virupas in the 1st Drekkana (0-10°)
- Female planets (Moon, Venus): Gain 15 Virupas in the 2nd Drekkana (10-20°)
- Neuter planets (Mercury, Saturn): Gain 15 Virupas in the 3rd Drekkana (20-30°)

### Phase 3: Sthana Bala - Component 5: Saptavarga Bala (Seven-fold Divisional Strength)
Planets are evaluated not just in the main birth chart (D1), but across 7 different divisional charts (Hora, Drekkana, Saptamsa, Navamsa, Dvadasamsa, and Trimsamsa). In each of these 7 charts, the planet is awarded Virupas based on its dignity:
- Moolatrikona: 45 Virupas
- Own Sign: 30 Virupas
- Great Friend's Sign: 20 Virupas
- Friend's Sign: 15 Virupas
- Neutral's Sign: 10 Virupas
- Enemy's Sign: 4 Virupas
- Great Enemy's Sign: 2 Virupas
*(These dignity points are derived directly from the planet's compound relationship with the sign's ruling planet).*

---

## 3. Scriptural Foundation (Sanskrit Quotes)
The rules in this file are directly grounded in the ancient texts retrieved from the project's scripture database.

### What is Shadbala?
> "Shad Bala is a sophisticated method for determining the inherent strength of a planet. Inherent strength is purely a measurement of raw strength; it is completely different from auspicious strength... Shad Bala simply measures the amount of weight a planet can carry, whether it is carrying lead or gold other factors determine."
> *— Ernst Wilhelm, Vault of the Heavens*

### Dig Bala (Directional Strength) Rule
> अथ ग्रहाणां दिग्बलम् । विलग्नपातालबधूनभोगा बुधामरेज्यौ भृगुसूनुचन्द्रौ । मन्दो धरासूनुदिवाकरौ चेत् क्रमेण ते दिग्बलशालिनः स्युः ॥ ३५॥
> *atha grahANAM digbalam | vilagnapAtAlabadhUnabhogA budhAmarejyau bhR^igusUnuchandrau | mando dharAsUnudivAkarau chet krameNa te digbalashAlinaH syuH || 35||*
> **Translation of astronomical mapping:** Vilagna (Ascendant - 1st) for Budha (Mercury) and Amarejya (Jupiter). Patala (Nadir - 4th) for Bhrigusunu (Venus) and Chandra (Moon). Badhu (Descendant - 7th) for Manda (Saturn). Nabhoga (Midheaven - 10th) for Dharasunu (Mars) and Divakara (Sun).
> *— Jataka Parijata Chapter 4:35*

### Sthana Bala (Uccha Bala / Exaltation) Rule
> मेषो वृषो मृगः कन्या कर्को मीनस्तथा तुला । सूर्यादीनां क्रमादेते कथिता उच्चराशयः ॥ ४९॥
> *meSho vR^iSho mR^igaH kanyA karko mInastathA tulA | sUryAdInAM kramAdete kathitA uchcharAshayaH || 49||*
> **Translation:** Aries, Taurus, Capricorn, Virgo, Cancer, Pisces, and Libra are the exaltation signs for the Sun and the other planets respectively.
> 
> भागा दश त्रयोऽष्टाश्व्यस्तिथ्योऽक्षा भमिता नखाः । उच्चात् सप्तमभं नीचं तैरेवांशैः प्रकीर्तितम् ॥ ५०॥
> *bhAgA dasha trayo.aShTAshvyastithyo.akShA bhamitA nakhAH | uchchAt saptamabhaM nIchaM tairevAMshaiH prakIrtitam || 50||*
> **Translation of degrees:** 10 (Sun), 3 (Moon), 28 (Mars), 15 (Mercury), 5 (Jupiter), 27 (Venus), and 20 (Saturn) are the deep exaltation degrees. The 7th sign from the exaltation is debilitation at the exact same degrees.
> *— Brihat Parashara Hora Shastra Chapter 3:49-50*

### Ojayugmarasyamsa, Kendra, and Drekkana Rules
> "Venus and the Moon gain 15 virupas in an even rasi and 15 virupas in an even navamsa, the other planets gain this odd rasis and navamsas. A planet in an angle (Kendra) gains 60 virupas, in a panapara 30, and in apoklimas 15. Male planets gain 15 virupas in the first drekkana of a rasi, female planets gain 15 in the second drekkana of a rasi, and neuter planets gain 15 in the third drekkana."
> *— Ernst Wilhelm, Vault of the Heavens (Translating classical Parashari principles)*

### Saptavarga Bala (7-Divisional Strength) Rules
> एवं होरादृकाणाद्रिभागांकद्वादशांशजम्।ह् । त्रिंशांशजं तदैक्यञ्च सप्तवर्गसमुद्।ह्भवम्।ह् ॥ ४॥
> *evaM horAdR^ikANAdribhAgAMkadvAdashAMshajam.h | triMshAMshajaM tadaikya~ncha saptavargasamud.hbhavam.h || 4||*
> **Translation:** Thus, the strength derived from Hora (D2), Drekkana (D3), Saptamsa (D7), Navamsa (D9), Dvadasamsa (D12), and Trimsamsa (D30), when combined [with Rasi/D1], gives the Saptavarga strength.
> 
> भागीकृत्य त्रिभिर्भक्तं लब्धमुच्चबलं भवेत्।ह् । स्वत्रिकोणस्वगेहाधिमित्रमित्रसमारिषु ॥ २॥
> अधिशत्रुगृहे चापि स्थितानां क्रमशो बलम्।ह् । भूताब्धयः खाग्निनखास्तिथ्यो दश युगाः कराः ॥ ३॥
> *bhAgIkR^itya tribhirbhaktaM labdhamuchchabalaM bhavet.h | svatrikoNasvagehAdhimitramitrasamAriShu || 2||
> adhishatrugR^ihe chApi sthitAnAM kramasho balam.h | bhUtAbdhayaH khAgninakhAstithyo dasha yugAH karAH || 3||*
> **Translation of Point Values:** In Moolatrikona, Own Sign, Great Friend, Friend, Neutral, Enemy, and Great Enemy's signs respectively, the strength is 45, 30, 20, 15, 10, 4, and 2 Virupas.
> *— Brihat Parashara Hora Shastra Chapter 28:2-4*

### Phase 4: Kala Bala - Time Strength (Part 1)
Kala Bala measures how strong a planet is based on the astronomical time of day, phase of the Moon, and portion of the day/night.

#### 1. Nathonnatha Bala (Day/Night Strength)
Measures the Sun's distance from the Nadir (IC). At Midday (when Sun is at MC), the Sun, Jupiter, and Venus gain a maximum of 60 Virupas. At Midnight (when Sun is at IC), the Moon, Mars, and Saturn gain a maximum of 60 Virupas. Mercury gets 60 Virupas at all times.

#### 2. Paksha Bala (Moon Phase Strength)
Measures the Moon's distance from the Sun. Benefics (Moon, Mercury, Jupiter, Venus) gain 60 Virupas at Full Moon (180° away from Sun) and 0 at New Moon (0° from Sun). Malefics (Sun, Mars, Saturn) are inverted, gaining 60 at New Moon.

#### 3. Tribhaga Bala (Third-Portion Strength)
Divides the Day (when Sun is above horizon) and Night into three equal portions.
- **Day:** 1st third belongs to Mercury. 2nd third belongs to Sun. 3rd third belongs to Saturn.
- **Night:** 1st third belongs to Moon. 2nd third belongs to Venus. 3rd third belongs to Mars.
- Jupiter gets 60 Virupas at all times.

---

### Kala Bala Rules (Nathonnatha, Paksha, Tribhaga)
> चक्राद्।ह् विशोध्य तद्।ह्भागास्त्रिभिर्भक्ताश्च दिग्।ह्बलम्।ह् । इष्टाधटि निशीथात्तन्नतं त्रिंशच्च्युतं नतम्।ह् ॥ ८॥
> चन्द्रभौमशनीनां च नतं द्विघ्नं कलादिकम्।ह् । षष्टिशुद्धं तदन्येषां सदा रूपं बुधस्य हि ॥ ९॥
> अथ पक्षबलं वक्ष्ये सूर्ये चन्द्राद्।ह् विशोध्य च । षड्।ह्भाधिके विशोध्यार्काद्।ह् भागीकृत्त्य त्रिभिर्भजेत्।ह् ॥ १०॥
> पक्षजं बलमिन्दुज्ञशुक्रेज्यानां तु षष्टितः । विशोध्य तब्दलं ज्ञेनं पापानां पक्षसंभवम्।ह् ॥ ११॥
> दिनत्र्यंशेषु सौम्यार्कशनीनां निट्।ह्त्रिभागके । चन्द्रशुक्रकुजानां च बलं पूर्णं सदा गुरोः ॥ १२॥
> *dinatryaMsheShu saumyArkashanInAM niT.htribhAgake | chandrashukrakujAnAM cha balaM pUrNaM sadA guroH || 12||*
> **Translation:** For the three parts of the Day, the strength belongs to Mercury (saumya), Sun (arka), and Saturn (shani). For the three parts of the Night, the strength belongs to Moon (chandra), Venus (shukra), and Mars (kuja). Jupiter's (guru) strength is always full (60). Paksha strength evaluates the distance between Sun and Moon; Benefics (Moon, Mercury, Venus, Jupiter) get full strength at full moon, while Malefics get the remainder from 60.
> *— Brihat Parashara Hora Shastra Chapter 28:8-12*

#### 4. Ayana Bala (Equatorial Declination Strength)
Measures the planet's Kranti (Declination) from the celestial equator. Sun, Mars, Jupiter, and Venus gain strength when they have Northern declination (up to 60 Virupas at +24°). Moon and Saturn gain strength when they have Southern declination (up to 60 Virupas at -24°). Mercury operates at maximum strength (60 Virupas) at both extreme poles and drops to 30 Virupas precisely at the equator.
*(Note: Yuddha Bala [Planetary War] and Calendar Lords [Year, Month, Day, Hour] are advanced extensions of Kala Bala remaining to be integrated into the total Shadbala loop).*

### Ayana Bala Rules (Declination)
> पञ्चाब्धयः सुराः सूर्याः खण्डकांशाः क्रमादमी । सायनग्रहदोराशितुल्यखण्डयुतिश्च स ॥ १५॥
> भागादिकहतादेष्यात्।ह् त्रिंशल्लब्धयुता लवाः । स्वमृणं तुलमेषादौ शनीन्द्वोश्च त्रिराशिषु ॥ १६॥
> *pa~nchAbdhayaH surAH sUryAH khaNDakAMshAH kramAdamI | sAyanagrahadorAshitulyakhaNDayutishcha sa || 15||
> bhAgAdikahatAdeShyAt.h triMshallabdhayutA lavAH | svamR^iNaM tulameShAdau shanIndvoshcha trirAshiShu || 16||*
> **Translation:** Using the Tropical (Sayana) planet's longitude, calculate the Kranti (Declination). Add or subtract (svamRinaM) the values. The strength of Saturn and Moon (shanIndvoshcha) works in reverse (Southern Declination is favored).
> *— Brihat Parashara Hora Shastra Chapter 28:15-16*

### Phase 5: Cheshta Bala - Motional Strength
Cheshta Bala measures a planet's strength based on its speed, retrograde motion, and proximity to Earth. A planet gains max strength (60 Virupas) when it is retrograde and closest to Earth, and 0 when it is far away behind the Sun.

#### The Sun and Moon Exception
Because the luminaries (Sun and Moon) do not undergo retrograde motion, their Cheshta Bala is inherited directly from their time strengths:
- **Sun's Cheshta Bala** is exactly equal to its **Ayana Bala**.
- **Moon's Cheshta Bala** is exactly equal to its **Paksha Bala**.

### Cheshta Bala Rules
> यद्रवेरायनं वीर्यं चेष्टाख्यं तावदेव हि । विधोः पक्षबलं यावत्।ह् तावच्चेष्टाबलं स्मृतम्।ह् ॥ १८॥
> *yadraverAyanaM vIryaM cheShTAkhyaM tAvadeva hi | vidhoH paxabalaM yAvat.h tAvachcheShTAbalaM smR^itam.h || 18||*
> **Translation:** Whatever the Ayana strength of Ravi (Sun), that same is its Cheshta. Whatever the Paksha strength of Vidhu (Moon), that same is its Cheshta strength.
> *— Brihat Parashara Hora Shastra Chapter 28:18*

#### Cheshta Bala for the 5 Star Planets
For Mars, Mercury, Jupiter, Venus, and Saturn, Cheshta Bala is calculated mathematically using the **Cheshta Kendra** (Motional Anomaly).
The Cheshta Kendra measures the planet's angular distance from its *Seeghrocca* (Apex of Fast Motion).
- **Superior Planets (Mars, Jupiter, Saturn):** The Seeghrocca is the Sun.
- **Inferior Planets (Mercury, Venus):** The Seeghrocca is their true Heliocentric Longitude.
When the Cheshta Kendra reaches 180° (closest to Earth, fully retrograde), the planet gets 60 Virupas. When the Kendra is 0° (furthest from Earth, behind the Sun), it gets 0 Virupas.

### Cheshta Kendra Rule
> चेष्टाकेन्द्राच्च तद्रश्मिं साधयेदुच्चरश्मिवत्।ह् । चेष्टाकेन्द्रं कुजादीनां पूर्वमुक्तं मया द्विज ॥ ३॥
> *cheShTAkendrAchcha tadrashmiM sAdhayeduchcharashmivat.h | cheShTAkendraM kujAdInAM pUrvamuktaM mayA dvija || 3||*
> **Translation:** From the Cheshta Kendra, determine its rays (strength) exactly like Exaltation (Uccha) strength [divide the angle by 3]. I have previously explained the Cheshta Kendra of Mars and the others, O Brahmin.
> *— Brihat Parashara Hora Shastra Chapter 29:3*

---

### Phase 6: Drik Bala - Aspectual Strength
Drik Bala evaluates the strength a planet receives from the aspects (Drishti) of other planets. 
- Aspects from Benefics (Jupiter, Mercury, Venus, Moon) increase strength.
- Aspects from Malefics (Sun, Mars, Saturn) decrease strength.

Only a quarter (1/4) of a malefic's aspect is deducted, and only a quarter (1/4) of a benefic's aspect is added, **except** for Mercury and Jupiter, whose full aspect values are added.

The aspect value is a mathematically precise piecewise function that awards 60 Virupas at direct opposition (180°), 30 Virupas at a trine (120°), and scales geometrically across the zodiac.

### Drik Bala (Drishti Sphuta) Rules
> दृश्याद्।ह् विशोध्य द्रष्टारं षड्राशिभ्योऽधिकान्तरम्।ह् । दिगभ्यः संशोध्य तद्।ह्भागा द्विभक्ता दृक्।ह् स्फुटा भवेत्।ह् ॥ ६॥
> पञ्चाधिके विना राशिं भागाद्विघ्नाश्च दृक्।ह् स्फुटा । वेदाधिके त्यजेद्।ह् भूताद्।ह् भागा दृष्टिः त्रिभाधिके ॥ ७॥
> विशोध्यार्णवतो द्वाभ्यां लब्धं त्रिंशद्।ह्युतं च दृक्।ह् । द्व्यधिके तु विना राशिं भागास्तिथियुतास्तथा ॥ ८॥
> *dR^ishyAd.h vishodhya draShTAraM ShaDrAshibhyo.adhikAntaram.h | digabhyaH saMshodhya tad.hbhAgA dvibhaktA dR^ik.h sphuTA bhavet.h || 6||
> pa~nchAdhike vinA rAshiM bhAgAdvighnAshcha dR^ik.h sphuTA | vedAdhike tyajed.h bhUtAd.h bhAgA dR^iShTiH tribhAdhike || 7||
> vishodhyArNavato dvAbhyAM labdhaM triMshad.hyutaM cha dR^ik.h | dvyadhike tu vinA rAshiM bhAgAstithiyutAstathA || 8||*
> **Translation:** Subtract the aspecting planet from the aspected planet. If the difference is > 6 signs (180°), subtract from 10 signs and divide by 2. If > 5 signs, ignore the sign and double the degrees. If > 4 signs, subtract from 5 signs... [this continues to form the exact piecewise function].
> *— Brihat Parashara Hora Shastra Chapter 27:6-8*

### Phase 7: Ishta and Kashta Phalas (Auspicious / Inauspicious Effects)
Beyond standard strength (Bala), the exact measure of a planet's tendency to give good (Ishta) or evil (Kashta) results during its Dasa (planetary period) is calculated mathematically.
- **Ishta Phala** is the geometric mean of the planet's Positional Exaltation strength (Uccha Bala) and its Motional Anomaly strength (Cheshta Bala).
- **Kashta Phala** is the geometric mean of the *lack* of these two strengths (the difference from 60).

**Formula:**
- Ishta Phala = $\sqrt{\text{Uccha Bala} \times \text{Cheshta Bala}}$
- Kashta Phala = $\sqrt{(60 - \text{Uccha Bala}) \times (60 - \text{Cheshta Bala})}$

### Ishta / Kashta Rules
> कथ्याम्यथा भावानां खेटानां च पदं द्विज । अथ चेष्टमनिष्टं च ग्रहानां कथयाम्यहम्।ह् । यद्।ह्वशाच्च प्रयच्छन्ति शुभाऽशुभदशाफलम्।ह् ॥ १॥
> स्वनीचोनो ग्रह शोध्यः षड्।ह्भाधिक्ये भमण्डलात्।ह् । सैको राशिर्भवेदुच्चरश्मिर्द्विघ्नांशसंयुतः ॥ २॥
> चेष्टाकेन्द्राच्च तद्रश्मिं साधयेदुच्चरश्मिवत्।ह् । चेष्टाकेन्द्रं कुजादीनां पूर्वमुक्तं मया द्विज ॥ ३॥
> *kathyAmyathA bhAvAnAM kheTAnAM cha padaM dvija | atha cheShTamaniShTaM cha grahAnAM kathayAmyaham.h | yad.hvashAchcha prayachChanti shubhA.ashubhadashAphalam.h || 1||*
> *svanIchono graha shodhyaH ShaD.hbhAdhikye bhamaNDalAt.h | saiko rAshirbhaveduchcharashmirdvighnAMshasaMyutaH || 2||*
> *cheShTAkendrAchcha tadrashmiM sAdhayeduchcharashmivat.h | cheShTAkendraM kujAdInAM pUrvamuktaM mayA dvija || 3||*
> **Translation:** Now I shall tell the strength of Bhavas and Grahas, O Brahmin. I shall explain the Ishta (auspicious) and Anishta / Kashta (inauspicious) state of planets, by which they yield good and bad effects in their Dasas. Subtract the planet's longitude from its debilitation point... this yields the Uccha Rashmi (exaltation rays). From the Cheshta Kendra, determine its rays (strength) exactly like Exaltation.
> *— Brihat Parashara Hora Shastra Chapter 29:1-3*
