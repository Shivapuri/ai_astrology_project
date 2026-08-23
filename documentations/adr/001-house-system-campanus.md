# ADR 001: House System Choice (Campanus)

## Status
Accepted

## Context
Vedic astrology (Jyotish) typically uses Whole Sign houses or Sri Pati for Bhava Chalita charts. However, Ernst Wilhelm's Kala methodology diverges from this by using True 3D House Systems (such as Placidus or Campanus) mapped onto the Zodiac, arguing for a mathematically rigorous spatial division. 
During development, there was a discrepancy between test data generated from Jagannatha Hora (which defaulted to Placidus) and the visual output from the Kala software (which the user requires matching). 
Because of the high northern latitude (52°N) of test charts like "Shivpuri", Placidus caused intercepted signs (e.g., Cusp 8 and 9 both falling in Pisces, but Placidus having Cusp 8 in Aquarius and 9 in Pisces), creating visual mismatch with Kala's output.

## Decision
We will use the **Campanus** house system as the default for all Bhava Chalita and Cusp calculations.

## Justification
- Ernst Wilhelm strongly advocates for Campanus as the only astronomically and spatially correct 3D house system.
- The default in the Kala professional software is Campanus.
- Testing proved that using Campanus perfectly aligned our engine's cusp positions (and intercepted signs) with the exact visual layouts provided in screenshots from the Kala software.

## Trade-offs
- **Pros:** 100% authentic alignment with the Kala software methodology. Correctly handles high-latitude edge cases where intercepted signs drastically alter house bounds.
- **Cons:** Diverges from other standard Vedic software (like Jagannatha Hora or Parashara's Light) which may default to Placidus or Sri Pati, potentially causing initial confusion for users comparing outputs across different tools.

## Clarification on Ascendant Mechanics
To prevent any future confusion between Ernst Wilhelm's older writings (*Vault of the Heavens*) and his current *Kala* software calculations:
- **Whole Sign Layer (Bhavas):** The Ascendant is simply an actual point in space (e.g., $9^\circ 35'$ Leo). It does *not* define the middle or edge of the house. To find the house boundaries, the system goes backward to the start of the sign ($0^\circ$) and forward to the end of the sign ($30^\circ$), making the *entire sign* the house.
- **Campanus Cusp Layer:** This is a mathematically separate 3D layer. In this layer *only*, the exact Ascendant degree acts as the rigid **starting edge (cusp)** of the 1st slice, completely ignoring the 30-degree Zodiac sign boundaries. It is not the middle of the house.
