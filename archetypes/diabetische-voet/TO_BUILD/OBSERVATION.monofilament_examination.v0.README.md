# C-3b: OBSERVATION.monofilament_examination.v0 — TE BOUWEN

**Inspanning:** 1 dag  
**Type:** Nieuw OBSERVATION-archetype (niet slechts cluster)

## Beschrijving
Semmes-Weinstein 10g monofilamenttest met plantaire locatiematrix en totaalscore.

## Elementen
| Element | Type | Toelichting |
|---------|------|-------------|
| Instrument | DV_TEXT | "10g Semmes-Weinstein monofilament" |
| Hallux links | DV_BOOLEAN | Waargenomen ja/nee |
| Hallux rechts | DV_BOOLEAN | |
| MTP-1 links | DV_BOOLEAN | 1e metatarsaalkop |
| MTP-1 rechts | DV_BOOLEAN | |
| MTP-3 links | DV_BOOLEAN | 3e metatarsaalkop |
| MTP-3 rechts | DV_BOOLEAN | |
| MTP-5 links | DV_BOOLEAN | 5e metatarsaalkop |
| MTP-5 rechts | DV_BOOLEAN | |
| Hiel links | DV_BOOLEAN | |
| Hiel rechts | DV_BOOLEAN | |
| Totaalscore | DV_COUNT | 0-10 (input voor Sims-berekening) |

## Output
Totaalscore ≤5/10 + PAV-tekenen → Sims-categorie ≥2 (via GDL2).
