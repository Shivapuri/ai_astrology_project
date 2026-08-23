# AI Documentation: Avasthas Engine (MANDATORY)

If you are an AI modifying the Avasthas (Planetary States), observe these strict mathematical rules:

1. **NO Friendship Calculation Here:** Avastha scripts (`deepti.py`, `lajjita.py`, etc.) MUST NOT calculate friendships themselves. They receive pre-calculated dignity/friendship strings from the master loop in `generate_jyotish.py`.
2. **Read Specific Rules:** Read the matching `.md` file for an Avastha before editing its `.py` file. Each Avastha uses a wildly different base (e.g., Deeptadi uses Compound Friendship; Lajjitadi uses Natural Friendship).
