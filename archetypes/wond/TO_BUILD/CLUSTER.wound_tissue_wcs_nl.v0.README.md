# C-1: CLUSTER.wound_tissue_wcs_nl.v0 — TE BOUWEN

**Inspanning:** ½ dag  
**Type:** Nieuw cluster-archetype

## Beschrijving
WCS-kleurclassificatie als herbruikbaar cluster. Plug-in in het Specific Details-slot
van CLUSTER.exam_wound.

## Elementen
| Element | Type | Waarden |
|---------|------|---------|
| Primaire kleur | DV_CODED_TEXT | Zwart (necrose) / Geel (fibrine/slough) / Rood (granulerend) |
| Secundaire kleur | DV_CODED_TEXT | Idem (optioneel, bij mengvorm) |
| % rood weefsel | DV_PROPORTION | 0-100% |
| % geel weefsel | DV_PROPORTION | 0-100% |
| % zwart weefsel | DV_PROPORTION | 0-100% |

## SNOMED-CT bindings (C-7)
- Rood: 371091000 (granulation tissue)
- Geel: 371092007 (slough)
- Zwart: 6867005 (gangrene / necrosis)
