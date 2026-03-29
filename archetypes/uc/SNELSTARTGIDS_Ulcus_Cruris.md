# Ulcus Cruris — Compleet Maken in OpenEHR

## Wat je al hebt

| Artefact | Status |
|----------|--------|
| Mermaid-protocol (Ulcus_Cruris.mermaid) | ✅ Klaar |
| GDL2 beslisregels (sensire_ulcus_cruris_v2_gdl2.json) | ✅ Klaar |
| ADL2: `OBSERVATION.ankle_brachial_pressure_index.v0` (C-4) | ✅ Klaar |
| ADL2: `CLUSTER.exam_stemmer_test.v0` (C-5) | ✅ Klaar |
| OET: `Ulcus_Cruris_Assessment_Sensire.v1` | 📎 Bijgevoegd |
| Example composition (JSON) | 📎 Bijgevoegd |

## Wat je nog moet doen — stap voor stap

### Stap 1: Internationale archetypes downloaden (30 min)

Download deze 12 archetypes uit https://ckm.openehr.org en sla ze op in één map:

| # | Archetype | Zoekterm in CKM |
|---|-----------|-----------------|
| 1 | `COMPOSITION.encounter.v1` | "encounter" |
| 2 | `EVALUATION.problem_diagnosis.v1` | "problem diagnosis" |
| 3 | `EVALUATION.clinical_synopsis.v1` | "clinical synopsis" |
| 4 | `EVALUATION.health_risk.v1` | "health risk" |
| 5 | `OBSERVATION.exam.v1` | "physical examination" |
| 6 | `OBSERVATION.blood_pressure.v2` | "blood pressure" |
| 7 | `CLUSTER.exam.v1` | "examination findings" |
| 8 | `CLUSTER.device.v1` | "medical device" |
| 9 | `CLUSTER.anatomical_location.v1` | "anatomical location" |
| 10 | `INSTRUCTION.therapeutic_item_order.v1` | "therapeutic item" |
| 11 | `INSTRUCTION.service_request.v1` | "service request" |
| 12 | `INSTRUCTION.care_plan.v0` | "care plan" |

**Tip:** Gebruik in CKM de "Bulk Export" functie → filter op bovenstaande namen → download als ZIP.

### Stap 2: Lokale archetypes importeren (15 min)

Importeer in de Archetype Designer (https://tools.openehr.org/designer):

1. De 12 internationale archetypes uit stap 1
2. `openEHR-EHR-OBSERVATION.ankle_brachial_pressure_index.v0.adl` (C-4)
3. `openEHR-EHR-CLUSTER.exam_stemmer_test.v0.adl` (C-5)

**Als import faalt:** Maak een nieuw archetype in de Designer met dezelfde RM-klasse en kopieer de elementen handmatig. De ADL2-bestanden dienen dan als specificatie.

### Stap 3: Template bouwen (45 min)

**Optie A — OET importeren:**
1. Importeer het bijgevoegde `Ulcus_Cruris_Assessment_Sensire.v1.oet` in de Archetype Designer
2. Controleer of alle archetype-referenties resolven
3. Fix eventuele ontbrekende referenties door de juiste archetypes toe te wijzen

**Optie B — Handmatig bouwen (als import faalt):**
1. Nieuw template → kies `COMPOSITION.encounter.v1` als root
2. Volg de structuur uit het OET-bestand sectie voor sectie (zie hieronder)
3. Per SECTION: sleep het juiste archetype erin vanuit je repository

**Template-structuur (wat je moet bouwen):**

```
COMPOSITION.encounter.v1 "Ulcus Cruris Assessment"
│
├── SECTION "Triage"
│   └── EVALUATION.problem_diagnosis.v1
│       → constraint name op: "Ulcus Cruris" / "Wond onderbeen"
│       → SNOMED: 420101004 |Venous ulcer of lower extremity|
│
├── SECTION "Oedeem-beoordeling"
│   ├── OBSERVATION.exam.v1 "Oedeem onderzoek"
│   │   └── CLUSTER.exam.v1 "Oedeem bevinding"
│   │       → voeg element toe: "Finding" = Aanwezig/Afwezig
│   │       → SNOMED: 267038008 |Edema|
│   └── CLUSTER.exam_stemmer_test.v0 [C-5]
│       → genest in het exam SLOT
│
├── SECTION "EAI-beoordeling"
│   ├── OBSERVATION.blood_pressure.v2 "Bloeddruk enkel (ABPI-bron)"
│   │   → constraint: alleen systolisch, label als ABPI-bron
│   │   → protocol: meetlocatie = enkel (a. dorsalis pedis / a. tibialis post.)
│   ├── OBSERVATION.blood_pressure.v2 "Bloeddruk arm (ABPI-bron)"
│   │   → constraint: alleen systolisch, label als ABPI-bron
│   │   → protocol: meetlocatie = a. brachialis
│   └── OBSERVATION.ankle_brachial_pressure_index.v0 [C-4]
│       → ratio + interpretatie + compressie-advies
│
├── SECTION "Vaatdiagnose"
│   └── EVALUATION.problem_diagnosis.v1
│       → constraint name op: Arterieel / Veneus / Gemengd
│       → SNOMED: 420101004, 238792006, of gemengd
│
├── SECTION "Compressietherapie"
│   ├── INSTRUCTION.therapeutic_item_order.v1
│   │   → item: UrgoK2 / UrgoK2 Lite / Geen
│   │   → SNOMED: 440681001 |Compression bandaging|
│   ├── ACTION.procedure.v1 "Zwachtelen"
│   │   → SNOMED: 440681001
│   └── CLUSTER.device.v1
│       → device name: UrgoK2 / UrgoK2 Lite
│       → enkelomvang (maat 1: 18-25 cm / maat 2: 25-32 cm)
│
├── SECTION "Verwijzingen"
│   └── INSTRUCTION.service_request.v1
│       → service name: Vaatchirurg / Huidtherapeut / Vakgroep Wond / HA
│       → reason + urgency (gekoppeld aan GDL2 outputs)
│
├── SECTION "Nazorg"
│   └── INSTRUCTION.care_plan.v0
│       → draagtijd, wisselfrequentie, evaluatiemoment
│
└── SECTION "Afsluiting"
    └── EVALUATION.clinical_synopsis.v1
        → uitkomst: steunkousen / voortzetten / geen kousen
```

### Stap 4: Template-constraints instellen (30 min)

Per sectie in de Designer:

**Verplichte velden (mandatory):**
- Problem/Diagnosis → name (1..1)
- ABPI → ratio (1..1)
- ABPI → interpretatie (1..1)
- Stemmer → resultaat (1..1)
- Therapeutic item order → item name (1..1)

**Weggeconstraineerde velden (0..0):**
- Blood_pressure: diastolisch, mean, alle overige → 0..0 (alleen systolisch nodig)
- Problem_diagnosis: alle optionele velden die niet relevant zijn

**Value set bindings:**
Gebruik de SNOMED-tabel uit de oorspronkelijke snelstartgids (C-7).

### Stap 5: OPT exporteren en uploaden (15 min)

1. In de Archetype Designer: **Export → Operational Template (OPT 1.4)**
2. Sla op als `Ulcus_Cruris_Assessment_Sensire.v1.opt`
3. Upload naar je EHRbase:
   ```bash
   curl -X POST \
     http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4 \
     -H "Content-Type: application/xml" \
     -d @Ulcus_Cruris_Assessment_Sensire.v1.opt
   ```
4. Controleer: `curl http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4`

### Stap 6: Example composition posten (15 min)

1. Gebruik het bijgevoegde `example_composition_ulcus_cruris.json`
2. Pas de `ehr_id` aan naar een bestaande EHR in je EHRbase
3. POST naar EHRbase:
   ```bash
   curl -X POST \
     http://localhost:8080/ehrbase/rest/openehr/v1/ehr/{ehr_id}/composition \
     -H "Content-Type: application/json" \
     -H "Prefer: return=representation" \
     -d @example_composition_ulcus_cruris.json
   ```
4. Controleer met een AQL-query:
   ```sql
   SELECT c/uid/value, 
          e/data[at0001]/events[at0002]/data[at0003]/items[at0007]/value 
   FROM EHR e 
   CONTAINS COMPOSITION c 
   CONTAINS OBSERVATION e[openEHR-EHR-OBSERVATION.ankle_brachial_pressure_index.v0]
   WHERE c/name/value = 'Ulcus Cruris Assessment'
   ```

### Stap 7: GDL2 koppelen (15 min)

Je hebt `sensire_ulcus_cruris_v2_gdl2.json` al klaar. Upload naar je CDS-engine:
- Als je **CDS Hooks** gebruikt: wrap de GDL2 als service
- Als je **Cambio CDS** gebruikt: importeer direct
- De `template_id` in de GDL2 data bindings (`Ulcus_Cruris_Assessment_Sensire.v1`) moet exact matchen met je OPT

---

## Totale tijdsinvestering

| Stap | Tijd |
|------|------|
| 1. CKM archetypes downloaden | 30 min |
| 2. Alles importeren in Designer | 15 min |
| 3. Template bouwen | 45 min |
| 4. Constraints + SNOMED | 30 min |
| 5. OPT export + upload | 15 min |
| 6. Example composition testen | 15 min |
| 7. GDL2 koppelen | 15 min |
| **Totaal** | **~2,5 uur** |

---

## Checklist: Ulcus Cruris compleet?

- [ ] 12 internationale archetypes gedownload
- [ ] C-4 (ABPI) en C-5 (Stemmer) geïmporteerd
- [ ] Template gebouwd met alle 8 secties
- [ ] Verplichte velden gemarkeerd
- [ ] SNOMED-bindings ingesteld
- [ ] OPT geëxporteerd en geüpload naar EHRbase
- [ ] Example composition succesvol gepost
- [ ] GDL2 gekoppeld aan template
- [ ] AQL-query retourneert verwachte data
