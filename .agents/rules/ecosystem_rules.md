# openEHR Ecosysteem Governance Regels (Antigravity AI)

Dit document bevat de ononderhandelbare regels voor AI-assistenten die opereren in het Sensire openEHR ecosysteem (`OpenEHRDemo`, `Sensii`, `SensireSpecieleBeslisOndersteuning`).

## Regel 1: Rol en Verantwoordelijkheid van deze Repository (`OpenEHRDemo`)
- `OpenEHRDemo` is de **Single Source of Truth (SSOT)** voor alle openEHR archetypes, templates (ADLT), gecompileerde OPT 1.4 XML bestanden, en terminologietabellen.
- Dit project is afhankelijk van de inhoud van de twee zuster-repositories:
  1. `~/Sensii` (58 wijkverpleegkundige formulieren, Omaha contract, SFP beslismotor)
  2. `~/SensireSpecieleBeslisOndersteuning` (164 zorgpaden, `v*_flow.json` + `ReAble/`)
- Als er in die bronnen iets wijzigt, is het de taak van dit project om de openEHR modellen opnieuw te controleren, te genereren en te compileren.

## Regel 2: Schrijf Nooit Direct in Consumenten-UI
- Wijzig nooit rechtstreeks applicatie-code in `Sensii` of `SensireSpecieleBeslisOndersteuning` vanuit deze repository, behalve het exporteren van gevalideerde JSON-contracten naar hun respectievelijke `contract/` mappen via `scripts/sync_ecosystem.py` of `scripts/export_sensii_contract.py`.

## Regel 3: Terminologiebeleid
- Alle Nederlandse concepten en vertalingen moeten de formele 5-staps cascade volgen ([`TERMINOLOGIE_CASCADE.md`](file:///home/vlieger/OpenEHRDemo/TERMINOLOGIE_CASCADE.md)):
  1. Nictiz ZIBs ➔ 2. SNOMED CT NL ➔ 3. openEHR CKM ➔ 4. V&VN / Omaha NL ➔ 5. Zorgpad Fallback.

## Regel 4: Geen Pseudo-Code of Ongeteste OPTs
- Elk openEHR template moet worden gecompileerd via Nedap Archie Java (`compiler/src/main/java/nl/sensire/openehr/OPTGenerator.java`) en door de Python OPT 1.4 XML postprocessor (`compiler/full_opt14_lxml.py`) worden gevalideerd voor EHRbase conformiteit.
