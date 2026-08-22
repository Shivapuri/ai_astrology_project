# Avasthas Implementation: Outstanding Tasks

This document outlines the remaining Avasthas to be implemented in the Astra calculation engine, along with the exact source materials and citations where the rules and descriptions can be found.

## Task 1: Deeptadi Avasthas (Moods)
* **Goal:** Implement the 9 moods (Deepta/Radiant, Swastha/Confident, Mudita/Happy, Shanta/Peaceful, etc.) which detail the psychological attitude of the planet.
* **Sanskrit Citation (BPHS Chapter 45, Verse 7):**
  > दीप्तः स्वस्थः प्रमुदितः शान्तो दीनोऽथ दुःखितः ।
  > विकलश्च खलः कोऽपीत्यवस्था नवधाऽपराः ॥ ७॥
* **Exact Description Source:** 
  * Read **Chapter 7** in *Vault of the Heavens* (`/Users/hajnaljanos/PycharmProjects/astra/source-material/Vault of the Heavens_Ernst Wilhelm.pdf`).
  * The Sanskrit logic is further detailed in BPHS Chapter 45 (available in `/Users/hajnaljanos/PycharmProjects/astra/source-material/sanskrit_texts/BPHS_Ch41-45.txt`).
* **Implementation steps:**
  * Create `jyotish/avasthas/deepti.py`.
  * Hook it into `generate_jyotish.py`.
  * Add the data column to `index.html`.
  * Update `documentations/avasthas.md` with the rules.

## Task 2: Lajjitadi Avasthas (House Relationships)
* **Goal:** Implement the 6 states indicating how planets behave in specific houses while aspected by/conjunct specific friends/enemies (Proud, Starved, Ashamed, Thirsty, Delighted, Agitated).
* **Sanskrit Citation (BPHS Chapter 45, Verses 21-22):**
  > लज्जितो गर्वितश्चैव क्षुधितस्तृषितस्तथा ।
  > मुदितः क्षोभितश्चेति ग्रहावस्थाः प्रकीर्तिताः ॥ २१॥
  > पुत्रर्क्षे राहुकेत्वर्खे रविसौरिकुजैर्युतः ।
  > प्रेक्षितो वा खगः कश्चिल्लज्जितावस्थ इष्यते ॥ २२॥
* **Exact Description Source:**
  * Read **Chapter 24** in *Vault of the Heavens* (`/Users/hajnaljanos/PycharmProjects/astra/source-material/Vault of the Heavens_Ernst Wilhelm.pdf`).
* **Implementation steps:**
  * Create `jyotish/avasthas/lajjita.py`.
  * Hook it into `generate_jyotish.py`.
  * Add the data column to `index.html`.
  * Update `documentations/avasthas.md`.

## Task 3: Shayanadi Avasthas (Mental Seizures / Activity States)
* **Goal:** Implement the 12 activity states (Laying down, Sitting, etc.) utilizing a complex algorithm combining the planet's Nakshatra, Ascendant, and time elements.
* **Sanskrit Citation (BPHS Chapter 45, Verses 33-35):**
  > शयनासननेत्रपाणिप्रकाशगमनानि च ।
  > आगमः सदसि ख्यातिः कौतुकं निद्रया सह ॥ ३३॥
  > अवस्थाः कथिता विप्र भोजनेन समन्विताः ।
  > ...
* **Exact Description Source:**
  * Read **Chapter 25** in *Vault of the Heavens* (`/Users/hajnaljanos/PycharmProjects/astra/source-material/Vault of the Heavens_Ernst Wilhelm.pdf`).
* **Implementation steps:**
  * Create `jyotish/avasthas/shayana.py`.
  * Hook it into `generate_jyotish.py`.
  * Add the data column to `index.html`.
  * Update `documentations/avasthas.md`.
