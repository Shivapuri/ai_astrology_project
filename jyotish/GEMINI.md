# Jyotish Engine AI Guardrails (MANDATORY)

If you are an AI modifying `.py` files in this directory, you **MUST** adhere to the following:

1. **Read the Twin Markdown File:** Every major `.py` file (like `relationships.py`) and every subfolder (like `avasthas/`) has corresponding `.md` documentation. You must read it before modifying the code.
2. **Separation of Concerns:** The calculation of a planet's base status (Friendships, Dignities, Aspects) is done in `relationships.py`. Do NOT calculate friendships or dignities directly inside specific UI scripts or Avastha scripts. Call the functions in `relationships.py`.
3. **Zero Breakage Policy:** This mathematical engine is heavily tested. Ensure you do not change the return types of core functions.
