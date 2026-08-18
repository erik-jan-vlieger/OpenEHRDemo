# Handoff Instructie voor Antigravity CLI in ~/SensireSpecieleBeslisOndersteuning

> **Doel**: Instructies voor het implementeren van **Fase 2 (Passieve openEHR Inspectie Badge)** in de WebViewer van Speciële Beslisondersteuning.

---

## 1. Belangrijkste Uitgangspunt: Nul Verstoring voor Redacteurs

- `SensireSpecieleBeslisOndersteuning` wordt actief gebruikt door redacteurs en wijkverpleegkundigen om continu zorgpaden aan te passen.
- **Geen verplichte openEHR velden, geen verplichte Omaha invoer, geen validatieblokkades in de editor.**
- De implementatie betreft **uitsluitend een passieve informatieve badge** in de WebViewer (`5.WebViewer`).

---

## 2. In te richten Functionaliteit (Fase 2)

1. **Locatie Data-Contract**:
   👉 [`/home/vlieger/SensireSpecieleBeslisOndersteuning/contract/carepaths_openehr_contract.json`](file:///home/vlieger/SensireSpecieleBeslisOndersteuning/contract/carepaths_openehr_contract.json)
2. **In de WebViewer Header / Detailpagina**:
   - Voeg een subtiele, niet-storende badge toe: `[ 🧬 openEHR Ready ]`.
   - Als de gebruiker op de badge klikt, verschijnt een kleine modal/popover met:
     - **Template ID**: bijv. `openEHR-EHR-COMPOSITION.sensire_w5_diabetische_voet_triage_o.0.0`
     - **ReAble Status**: `Ja (met Educatie & Regietrede)` / `Standaard`
     - **Gekoppelde Archetypes**: Lijst van archetypes (`problem_diagnosis`, `care_plan_request`, `health_education`)
     - **AQL Voorbeeld Query**: Kant-en-klare snippet om dit zorgpad in EHRbase op te vragen.
     - **Download/Inspect Link**: Naar het OPT 1.4 XML bestand.

---

## 3. Kant-en-Klare Startprompt voor de Antigravity CLI in deze repo

Kopieer en plak onderstaande tekst in de Antigravity CLI wanneer je `~/SensireSpecieleBeslisOndersteuning` opent:

```text
Lees /home/vlieger/SensireSpecieleBeslisOndersteuning/contract/carepaths_openehr_contract.json en /home/vlieger/OpenEHRDemo/docs/HANDOFF_TO_SPECIELE_BESLISONDERSTEUNING.md.
Implementeer Fase 2 (Passieve openEHR Inspectie Badge) in 5.WebViewer:
1. Toon bij elk zorgpad een niet-storende [ 🧬 openEHR Ready ] badge.
2. Laat bij een klik een modal openen met het template-ID, de archetypes en het AQL-voorbeeld uit het contract.
Let op: Verander niets aan de redactie- of invoerflow van de zorgpaden; het is puur een passieve weergave op basis van het JSON-contract.
```
