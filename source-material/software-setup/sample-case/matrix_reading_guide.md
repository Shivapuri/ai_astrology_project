# How to Read the Lajjitadi Avastha Tables

The mathematical tables inside Kala Software (specifically the Lajjitadi Avasthas, Shadbala, and Ishta/Cheshta tables) contain highly condensed, multi-layered calculations. Understanding the exact meaning of the values—and importantly, their colors—is crucial for replicating these math engines in Python.

## The Grid Layout
The tables function as a cross-reference matrix:
*   **Rows = The Giving Planet** (The planet exerting an influence, aspect, or avastha).
*   **Columns = The Receiving Planet** (The planet being modified by the row planet).

## Reading the Off-Diagonal Cells (e.g., Row Mars, Column Saturn)
These cells represent the *specific influence* one planet has on another.
They typically contain two numbers:

1.  **Top Number (The Modifier):** This is the raw influence score.
    *   **Green (`[G]`):** A positive modifier (Addition). Represents Delighted (Mudita) or Proud (Garvita) influences.
    *   **Red (`[R]`):** A negative modifier (Subtraction). Represents Starved (Kshudhita), Agitated (Kshobhita), Thirsty, or Ashamed influences.
    *   **Blue (`[B]`):** A neutral modifier (Zero effect). 
    *   *Mathematical Rule:* The absolute value is written, but the **color dictates the sign** (`+` for Green, `-` for Red, `0` for Blue).
2.  **Bottom Number (The Isolated Scenario):** This number represents what the Receiving Planet's final score *would* be if this specific modifier was the *only* one applied to its base score.
    *   *Formula:* `Base Score (of Column Planet) + This Specific Modifier`.

## Reading the Diagonal Cells (e.g., Row Saturn, Column Saturn)
The self-intersecting cells contain the overall calculation summaries for that specific planet. They typically contain three numbers:

1.  **Top Number (The Base Score):** Usually colored Green. This is the starting score for the planet (derived from Shadbala, Ishta, Cheshta, etc.) before any other planets interfere.
2.  **Middle Number (The Net Modifier):** Usually colored Black. This is the **sum total** of all positive and negative points received from every other planet in the chart.
3.  **Bottom Number (The Final Score):** Usually colored Red.
    *   *Formula:* `Base Score + Net Modifier = Final Score`.
    *   *(Note: In some specific tables, the positions of Base and Final may swap visually, but the mathematical relationship `A + B = C` is always maintained).*

## Extracting to CSV
When verifying your software against these baselines, the most robust way to extract this data into CSV format is to tag the numbers with their colors, so your Python tests can parse them dynamically:

*   `"29.1[R]"` -> Parsed as `-29.1`
*   `"35.1[G]"` -> Parsed as `+35.1`
*   `"14.9[B]"` -> Parsed as `0`

By adhering to this structure, you can precisely test if your Python backend correctly identifies Friends vs Enemies and applies the exact Lajjitadi addition/subtraction rules!
