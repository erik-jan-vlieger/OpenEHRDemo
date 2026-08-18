# Handoff Instructie voor Antigravity CLI in ~/Sensii

> **Doel**: Dit document bevat de exacte instructies voor de Antigravity AI-assistent in de repository `~/Sensii` om de openEHR-integratie en visualisaties te implementeren op basis van het aangeleverde data-contract.

---

## 1. Context & Rolverdeling

1. `OpenEHRDemo` heeft het openEHR data-contract gegenereerd en klaargezet in:
   👉 [`/home/vlieger/Sensii/contract/sensii_openehr_contract.json`](file:///home/vlieger/Sensii/contract/sensii_openehr_contract.json)
2. **Sensii hoeft géén openEHR-compilers, Java of archetypes te bevatten.**
3. De taak van Sensii is uitsluitend: **het visualiseren en inspecteerbaar maken van dit contract in de bestaande UI**.

---

## 2. In te richten UI-functionaliteiten in Sensii

### A. De Doorloop (`viewer/templates/sensii_doorloop.html`)
In het Live Cliëntdossier (de rechterkolom):
1. Voeg een toggle toe in de top van de rail: `[ 👩‍⚕️ Klinisch Dossier ] | [ 🧬 openEHR Inspector ]`.
2. Wanneer `openEHR Inspector` actief is (of bij hover/click op een dossierkaart):
   - Toon de bijbehorende `archetype_id` (bijv. `openEHR-EHR-OBSERVATION.groningen_frailty_indicator_nl.v0`).
   - Toon de RM-klasse (`OBSERVATION`, `EVALUATION`, `ADMIN_ENTRY`).
   - Toon de bijbehorende AQL-query uit `sensii_openehr_contract.json`.
   - Toon een knop *"🔗 Speciëel Zorgpad"* als het Omaha-aandachtsgebied matcht met de `specialized_pathways_integration.triggers` (zoals Huid ➔ Diabetische Voet / Decubitus).

### B. De Meta-Visualisaties (`viewer/templates/sensii_visualisatie.html`)
1. **In Lens 1 (8 Fasen)**: Toon bij elke fase de corresponderende `template_id` (bijv. `sensire_sensii_h1_intake_triage_vag.v1`).
2. **In Lens 2 (Beslisbomen & Matrix)**: Toon in de formulierentabel de gemapte archetypes en RM-typen uit het contract.
3. **Nieuwe Lens: `🧬 openEHR Blueprint & Query Lab`**:
   - Geef een visueel overzicht van de 5 templates en 7 custom archetypes.
   - Bied een interactieve AQL-query viewer aan waar wijkverpleegkundigen en technici voorbeeld-queries kunnen inzien.

---

## 3. Kant-en-Klare Startprompt voor de Sensii Antigravity Sessie

Kopieer en plak de volgende prompt zodra je de Antigravity CLI opent in `~/Sensii`:

```text
Lees het bestand /home/vlieger/Sensii/contract/sensii_openehr_contract.json en /home/vlieger/OpenEHRDemo/docs/HANDOFF_TO_SENSII.md.
Implementeer op basis van dit contract de openEHR-visualisaties in Sensii:
1. Voeg een 'openEHR Inspector' toggle toe aan het Live Dossier in viewer/templates/sensii_doorloop.html.
2. Voeg een openEHR Blueprint & AQL view toe aan viewer/templates/sensii_visualisatie.html.
Let op: Gebruik puur de data uit het JSON-contract; definieer geen eigen openEHR-modellen in deze repo.
```
