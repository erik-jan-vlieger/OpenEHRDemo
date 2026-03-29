# C-3c: EVALUATION.sims_classification_nl.v0 — TE BOUWEN

**Inspanning:** ½ dag  
**Type:** Nieuw EVALUATION-archetype (klinisch oordeel)

## Beschrijving
Sims-risicoclassificatie voor preventieve podotherapeutische zorg.

## Elementen
| Element | Type | Waarden/Toelichting |
|---------|------|---------------------|
| Sims-categorie | DV_ORDINAL | 0=geen risico / 1=verhoogd / 2=hoog / 3=zeer hoog |
| PS-verlies (neuropathie) | DV_BOOLEAN | Beschermd gevoel afwezig |
| PAV-tekenen | DV_BOOLEAN | Perifeer arterieel vaatlijden |
| Ulcus in voorgeschiedenis | DV_BOOLEAN | |
| Amputatie in voorgeschiedenis | DV_BOOLEAN | |
| Zorgfrequentie advies | DV_TEXT | Afgeleid van categorie |

## GDL2-regel
Monofilament-score ≤5 + PAV = Sims ≥ 2 automatisch voorstellen.
