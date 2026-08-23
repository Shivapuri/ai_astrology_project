# AI Agent Instructions for Astra Knowledge Base (`/knowledge_base/`)

## Purpose
This directory serves as the core repository for all astrological reference texts, mythological backgrounds, and technical planetary data used within the Astra software. The content here is designed to be directly referenced by the UI (e.g., when a user clicks on a planet or sign to view its details) or parsed into a structured database (JSON/SQL) for the application's backend.

## Strict Content Standards
- **Ernst Wilhelm's "Kala" Methodology ONLY:** All reference material must strictly adhere to the teachings of Ernst Wilhelm (*Graha Sutras*, *Vault of the Heavens*, etc.) and the classical Sanskrit texts he relies on (primarily *Brihat Parashara Hora Shastra*).
- **No Syncretism:** Do not mix in Western astrological concepts, modern psychological astrology, or generalized Vedic interpretations that contradict the primary sources. 
- **Verification Mandate:** Before adding or modifying any entry in this folder, AI agents MUST cross-reference the facts against the PDFs and text databases in the `/source-material/` directory.

## Critical Technical Guardrails (Do Not Deviate)
Based on explicit teachings in *Vault of the Heavens* and BPHS, AI agents must enforce the following logic when writing or parsing data:
1. **House Systems:** Ernst Wilhelm explicitly rejects the Sri Pati (Porphyry) house system due to distortion. Always state that the **Equal House system** (30 degrees from Lagna) is the preferred method for mathematical Bhava impact, built upon the immutable foundation of the **Rasi Chakra**.
2. **Rasi Gunas and Castes:** NEVER use generic modern mappings (e.g., assuming all Earth signs are Vaishyas). You must use the specific psychological motivations mapped by Ernst Wilhelm:
   - Taurus: Rajasic Sudra
   - Gemini: Rajasic Vaishya
   - Virgo: Tamasic Sudra
   - Libra: Rajasic Vaishya
   - Aquarius: Tamasic Vaishya
3. **Kalapurusha Anatomy:** The physiological body parts of the 12 houses map exactly to the natural zodiac (Aries=Head to Pisces=Feet) as corroborated by *Brihat Jataka* Ch 5. Never alter this mapping based on the rising sign.
4. **Rasi Body Sizes:** Strictly follow the Sanskrit definitions in BPHS Chapter 4: Aries is *Large/Prominent* (Bṛhadgātra); Taurus is *Long* (Dīrgha); Cancer is *Bulky/Massive* (Sthaulya tanu); Sagittarius is *Medium/Even* (Samagātro).
5. **Multiple House Karakas (Significators):** Ensure all permanent Karakas from BPHS Chapter 32 are listed. Do not truncate them. (e.g., The 10th house MUST list Sun, Mercury, Jupiter, and Saturn. The 4th house MUST list Moon and Mercury).

## Formatting Guidelines
- **Parseable Markdown:** Keep the markdown formatting clean, structured, and consistent. Use standardized headings (`##`), bulleted lists (`*`), and tables (`| | |`) so that scripts can easily parse this text into JSON or HTML for the frontend.
- **Granular Categories:** When describing an astrological entity, break down the information into clear sections:
  - Etymology & Metaphysics
  - Vishnu Avatara (including Para Atma vs Jiva distinctions)
  - Presiding Deities
  - Astrological Profile (Element, Humour/Dosha, Guna, Caste, Gender)
  - Remedial Propitiation (Image, Garment, Food/Grain, Hymn)

## Usage in Application
When tasked with displaying knowledge base data in the Astra UI:
1. Ensure the text is formatted cleanly for the user.
2. If building an interactive component (e.g., a modal or sidebar), parse these markdown files into a structured data format (like JSON) first, rather than hardcoding the text into the UI components.
