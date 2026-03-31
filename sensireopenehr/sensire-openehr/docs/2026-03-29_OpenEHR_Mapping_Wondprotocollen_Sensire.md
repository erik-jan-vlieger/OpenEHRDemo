# OpenEHR Mapping — Sensire Wondprotocollen

## 1. Analyse: Data-elementen per protocol

Uit de drie Mermaid-protocollen heb ik de volgende *registreerbare data-elementen* geëxtraheerd (dus niet de processtappen zelf, maar de informatie die vastgelegd moet worden).

### 1.1 Algemeen Wondprotocol

| Domein | Data-elementen |
|--------|----------------|
| **Wondidentificatie** | Type wond, locatie (anatomisch), lateraliteit, datum ontstaan, oncologisch ja/nee |
| **Wondinspectie** | Grootte (l×b×d in cm), kleur wondbed, geur, wondranden, wondomgeving, huidconditie, exsudaat (droog/vochtig/nat), oedeem |
| **TIME-analyse** | **T**: weefseltype + vitaliteit, afmeting; **I**: 5 infectietekenen (rubor, calor, tumor, dolor, functieverlies) + vocht + geur + koorts; **M**: exsudaatgraad, verbandverzadiging, wisselfrequentie; **E**: randkwaliteit, ondermijningen, eczeem, eelt |
| **WCS-kleur** | Zwart (necrose) / Geel (fibrine/slough) / Rood (granulerend) |
| **Pijnmanagement** | Pijnscore (ALTIS/VAS), type pijnstilling (systemisch/lokaal), medicatie, wachttijd |
| **Reiniging** | Reinigingsmethode, middel |
| **Debridement** | A-vitaal weefsel ja/nee, contra-indicatie (stolling, diepe structuren, maligniteit), type debridement |
| **Infectiebeleid** | Infectie ja/nee, ernst (DM: koorts >38°C, roodheid >2cm, pus, botcontact), beleid (lokaal/systemisch antibacterieel) |
| **Behandeling** | Exsudaatniveau → verbandkeuze, materiaal, wondomgeving verzorgd |
| **DM-laag** | Voetinspectie (huidkleur, temp, eelt, fissuren, standsafwijking, pulsaties, monofilament, nagels, schoeisel, oedeem), Charcot-vermoeden, plantaire wond, drukontlasting, voorlichting gegeven |
| **Verband** | Materiaal, methode, frequentie |
| **Rapportage** | Handeling + bevindingen, pijnscore (VAS), TIME-vastlegging, foto, behandelplan |
| **Escalatie** | Complexe wond (>2-3 weken stagnatie), verwijzing vakgroep |

### 1.2 Ulcus Cruris Protocol

| Domein | Data-elementen |
|--------|----------------|
| **Triage** | Nieuwe/bestaande cliënt, wond aan onderbeen/voet |
| **DM-screening** | Diabetes mellitus ja/nee |
| **Oedeem** | Oedeem ja/nee, Stemmer-test (positief/negatief → lymfoedeem vs veneus) |
| **EAI-beoordeling** | EAI-waarde, leeftijd EAI (<3 maanden), bron (specialist/HA), interpretatie (<0.6 / 0.6-1.3 / >1.3), diagnose (arterieel/veneus/gemengd) |
| **Compressie** | Type (UrgoK2 / UrgoK2 Lite), enkelomvang (maat 1: 18-25 cm, maat 2: 25-32 cm), zwachteltechniek |
| **Nazorg** | Draagtijd (max 7 dagen), wisselfrequentie, hergebruik (max 2×) |
| **Afsluiting** | Uitkomst: wond dicht + oedeemvrij → steunkousen; wond dicht + oedeem → voortzetten; trauma → geen kousen; geen veneus lijden → geen kousen |

### 1.3 Diabetische Voet Protocol

| Domein | Data-elementen |
|--------|----------------|
| **Anamnese** | Ontstaan + beloop, glucoseregulatie, claudicatio, mobiliteit, schoeisel, eerder ulcus/operatie, voettemperatuur, pijntype, visus, sociaal isolement |
| **Risicofactoren** | Slechte glucoseregulatie, perifeer vaatlijden, neuropathie, standsafwijkingen, eerdere amputatie, nierfalen, roken, verminderde visus, Charcot in VG |
| **Voetinspectie** | (Identiek aan DM-laag in AWP) Huidkleur, temperatuur, eelt, fissuren, standsafwijkingen, droge huid, pulsaties, monofilament-test, nagels, schoeisel, oedeem — beide voeten |
| **Charcot-screening** | Rode, warme, gezwollen voet zonder trauma → arts dezelfde dag |
| **Wond aanwezig** | Ja → door naar Algemeen Wondprotocol (met DM-laag); Nee → preventieve zorg |
| **Preventieve zorg** | Huid invetten, voeten wassen, niet blootsvoets, schoeisel, medisch pedicure, geen warmtebron, dagelijks inspectie |

---

## 2. Mapping naar OpenEHR Archetypes

### Legenda
- **🟢 A — Internationaal beschikbaar** (Published/Draft in openEHR International CKM)
- **🟡 B — Nationaal beschikbaar** (ZIBs-on-openEHR / Noorse CKM / Apperta UK)
- **🟠 C — Uit te breiden of nieuw te maken**

---

### 2.1 Kern-archetypes — Wondregistratie

| # | Data-domein | OpenEHR Archetype | Status |
|---|-------------|-------------------|--------|
| 1 | **Wonddiagnose & overzicht** | `EVALUATION.problem_diagnosis.v1` | 🟢 A — Published |
| 2 | **Wondtype-details** (extensie op probleem) | `CLUSTER.wound_assertion_details` | 🟢 A — Incubator (Heather Leslie, Skin & Wound project) |
| 3 | **Fysiek onderzoek (container)** | `OBSERVATION.exam.v1` | 🟢 A — Published |
| 4 | **Wondonderzoek** | `CLUSTER.exam_wound` | 🟢 A — Incubator (bevat grootte, wondbed, exsudaat, randen, ondermijningen) |
| 5 | **Anatomische locatie** | `CLUSTER.anatomical_location.v1` | 🟢 A — Published |
| 6 | **Foto/multimedia** | `CLUSTER.media_file.v1` | 🟢 A — Published |
| 7 | **Afmetingen wond** | `CLUSTER.physical_properties.v0` / dimensie-elementen in `CLUSTER.exam_wound` | 🟢 A — Draft |

### 2.2 TIME-framework & WCS

| # | Data-domein | OpenEHR Archetype | Status |
|---|-------------|-------------------|--------|
| 8 | **Tissue (weefseltype + vitaliteit)** | Onderdeel van `CLUSTER.exam_wound` (wondbed-kleur, weefseltype) | 🟢 A — Velden aanwezig; WCS-waardelijst (Zwart/Geel/Rood) als **lokale terminologie-binding** toevoegen |
| 9 | **Infection (infectietekenen)** | `CLUSTER.symptom_sign.v2` (per teken) + `EVALUATION.problem_diagnosis.v1` (infectiediagnose) | 🟢 A — Published |
| 10 | **Moisture (exsudaat)** | Onderdeel van `CLUSTER.exam_wound` (exsudaatgraad, type) | 🟢 A — Aanwezig |
| 11 | **Edge (wondranden)** | Onderdeel van `CLUSTER.exam_wound` (randkwaliteit) | 🟢 A — Aanwezig, maar **uitbreiden** met NL-specifieke waarden (verweekt wit, eelt, eczeem) |

**🟠 Actie C-1**: Ontwikkel een apart **`CLUSTER.wound_tissue_wcs_nl.v0`** — een lokaal cluster-archetype voor de WCS-kleurclassificatie. Dit cluster bevat: primaire kleur (Zwart/Geel/Rood), secundaire en tertiaire kleur bij mengvormen, en percentagevelden per weefselkleur in het wondbed. Plug dit in het 'Specific details'-slot van `CLUSTER.exam_wound`. Dit is architecturaal zuiverder dan alleen een template-constraint, omdat de WCS-classificatie een eigen beslismodel is dat verpleegkundige acties en verbandkeuze stuurt — het verdient een eigen herbruikbaar artefact.

### 2.3 Pijnmanagement

| # | Data-domein | OpenEHR Archetype | Status |
|---|-------------|-------------------|--------|
| 12 | **Pijnscore (VAS/ALTIS)** | `OBSERVATION.pain_scale.v0` of generiek `OBSERVATION.clinical_assessment_scale` | 🟡 B — Er zijn meerdere pijnschaal-archetypes in draft/incubator; de ZIB PijnScore mapt op een generiek observatie-archetype |
| 13 | **Pijnmedicatie** | `INSTRUCTION.medication_order.v4` + `ACTION.medication.v1` | 🟢 A — Published |

**🟠 Actie C-2**: Maak een **template-constraint** voor pijnmeting die zowel VAS (0-10) als ALTIS-score ondersteunt. Gebruik bij voorkeur het internationale `OBSERVATION.pain_scale` als dat gepubliceerd wordt, of anders een lokale specialisatie.

### 2.4 Procedures (Reiniging, Debridement, Verband)

| # | Data-domein | OpenEHR Archetype | Status |
|---|-------------|-------------------|--------|
| 14 | **Wondreiniging (actie)** | `ACTION.procedure.v1` (met gespecificeerde procedure-naam) | 🟢 A — Published |
| 15 | **Debridement (actie)** | `ACTION.procedure.v1` | 🟢 A — Published |
| 16 | **Debridement beslislogica** (contra-indicaties) | `EVALUATION.contraindication.v0` of vastleggen als clinical note | 🟢 A — Draft |
| 17 | **Verbandwisseling** | `ACTION.procedure.v1` + materiaal via `CLUSTER.device.v1` | 🟢 A — Published |
| 17b | **Verband-/zwachtelorder** | `INSTRUCTION.therapeutic_item_order.v1` | 🟢 A — Published; specifiek ontworpen voor niet-medicamenteuze therapeutische hulpmiddelen (verbanden, zwachtels, compressiesystemen). Ontologisch zuiverder dan `medication_order` voor deze items |
| 18 | **Zorgplan/wondplan** | `INSTRUCTION.care_plan.v0` of `EVALUATION.care_plan.v0` | 🟢 A — Draft |

### 2.5 Infectiebeleid

| # | Data-domein | OpenEHR Archetype | Status |
|---|-------------|-------------------|--------|
| 19 | **Infectiescreening** (5 klassieke tekenen) | `OBSERVATION.exam.v1` met nested `CLUSTER.exam_wound` (infectietekenen) | 🟢 A |
| 20 | **Koorts** | `OBSERVATION.body_temperature.v2` | 🟢 A — Published |
| 21 | **Lokaal antibacterieel beleid** | `INSTRUCTION.medication_order.v4` (zilver, jodium, honing) | 🟢 A |
| 22 | **Verwijzing arts** | `INSTRUCTION.service_request.v1` | 🟢 A — Published |

### 2.6 Diabetische Voet & DM-laag

| # | Data-domein | OpenEHR Archetype | Status |
|---|-------------|-------------------|--------|
| 23 | **DM-diagnose als context** | `EVALUATION.problem_diagnosis.v1` (DM als comorbiditeit) | 🟢 A |
| 24 | **Voetinspectie** | `OBSERVATION.exam.v1` + `CLUSTER.exam.v1` (gespecialiseerd voor voet) | 🟢 A — Generiek exam cluster beschikbaar |
| 25 | **Perifere pulsaties** | `CLUSTER.exam_peripheral_pulse` of element in voetexamen | 🟢 A — Draft beschikbaar |
| 26 | **Monofilament-test (sensibiliteit)** | | 🟠 C — Verdient een volwaardig **OBSERVATION**-archetype (niet slechts een CLUSTER), omdat de test een eigen protocol, events en plantaire locatiematrix heeft |
| 26b | **Wagner-classificatie (wondgradering)** | `OBSERVATION.diabetic_wound_wagner.v0` | 🟢 A — Incubator; gradeert DM-voetulcera (graad 0-5: van intacte huid tot uitgebreid gangreen) |
| 26c | **Sims-classificatie (risicoprofiel)** | | 🟠 C — **Nieuw archetype** nodig; Nederlands risico-classificatiemodel (categorie 0-3) gebaseerd op PS-verlies, PAV, ulcushistorie → bepaalt preventief zorgprofiel |
| 27 | **Charcot-screening** | `EVALUATION.health_risk.v1` (risicobeoordeling) | 🟢 A — Published |
| 28 | **Glucoseregulatie** | `OBSERVATION.laboratory_test_result.v1` (HbA1c) | 🟢 A — Published |
| 29 | **Claudicatio-anamnese** | `OBSERVATION.story.v1` + `CLUSTER.symptom_sign.v2` | 🟢 A — Published |
| 30 | **Risicofactoren DM voet** | `EVALUATION.health_risk.v1` | 🟢 A |
| 31 | **Drukontlasting** | `ACTION.procedure.v1` (type: hielen vrijleggen, dekenboog, vilt, gips/boot) | 🟢 A |
| 32 | **Voorlichting DM** | `ACTION.health_education.v1` | 🟢 A — Published |
| 33 | **Preventieve voetzorg** | `ACTION.health_education.v1` + `INSTRUCTION.care_plan.v0` | 🟢 A |
| 34 | **Schoeisel-beoordeling** | Geen specifiek archetype | 🟠 C — Vastleggen als element in voetexamen-cluster of care plan |

**🟠 Actie C-3**: Maak een **`CLUSTER.exam_diabetic_foot`** — specialisatie van `CLUSTER.exam.v1` voor diabetische voetinspectie. Bevat: huidkleur, temperatuur (bilateraal + asymmetrie), eelt/fissuren, standsafwijkingen, pulsaties (a. dorsalis pedis, a. tibialis posterior), nagelbeoordeling, schoeisel-beoordeling, Charcot-vermoeden. NB: de monofilament-test en Sims-classificatie worden als aparte archetypes gemodelleerd (zie C-3b en C-3c).

**🟠 Actie C-3b**: Maak een **`OBSERVATION.monofilament_examination.v0`** — een volwaardig OBSERVATION-archetype (geen cluster) voor de Semmes-Weinstein 10g monofilamenttest. Dit archetype bevat: gebruikte instrument (protocol), een matrix van plantaire testlocaties (hallux, metatarsaalkoppen, hiel) met per locatie een boolean resultaat (waargenomen: ja/nee), en een berekende totaalscore. Deze gestructureerde output levert de input voor automatische Sims-berekening via GDL2.

**🟠 Actie C-3c**: Maak een **`EVALUATION.sims_classification_nl.v0`** — een EVALUATION-archetype (klinisch oordeel, geen observatie) voor de Sims-risicoclassificatie. Bevat: ordinale uitslag (categorie 0, 1, 2, 3), plus boolean-velden voor de onderliggende risicofactoren (PS-verlies, PAV-tekenen, historie ulcus/amputatie). De Sims-score bepaalt direct de frequentie en aard van preventieve podotherapeutische zorg.

### 2.7 Ulcus Cruris — Specifieke elementen

| # | Data-domein | OpenEHR Archetype | Status |
|---|-------------|-------------------|--------|
| 35 | **Enkel-Arm Index (EAI/ABI)** | `OBSERVATION.ankle_brachial_index` | 🟡 B — Beschikbaar in Noorse CKM (Silje Ljosland Bakke); niet in internationale CKM |
| 36 | **Stemmer-test** | Geen bestaand archetype | 🟠 C — Nieuw element nodig |
| 37 | **Oedeem-beoordeling** | `CLUSTER.exam.v1` (bevinding: oedeem, ernst, locatie) + `CLUSTER.symptom_sign.v2` | 🟢 A |
| 38 | **Diagnose veneus/arterieel/gemengd** | `EVALUATION.problem_diagnosis.v1` (met specifieke codering) | 🟢 A |
| 39 | **Compressietherapie** | `ACTION.procedure.v1` (zwachtelen) + `CLUSTER.device.v1` (UrgoK2/Lite) | 🟢 A |
| 40 | **Enkelomvang (maatbepaling)** | `OBSERVATION.exam.v1` + omtrek-element | 🟢 A |
| 41 | **Steunkousen/afsluiting** | `INSTRUCTION.service_request.v1` (machtiging HA) + `EVALUATION.clinical_synopsis.v1` | 🟢 A |

**🟠 Actie C-4**: De EAI/ABPI vereist een **drielaags architecturaal model** om data-vervuiling van de vitale-parametertrendlijn te voorkomen:

- **Laag 1 — Fysieke metingen**: Leg de systolische druk aan de enkel (a. dorsalis pedis / a. tibialis posterior) en de arm (a. brachialis) vast in `OBSERVATION.blood_pressure.v2`, maar markeer deze metingen expliciet in het protocol-element (via terminologie-binding of DV_EHR_URI) als "uitsluitend ten behoeve van ABPI-berekening". Dit voorkomt dat downstream systemen, dashboards of CDS-algoritmen een lage enkeldruk door perifeer vaatlijden interpreteren als systemische cardiovasculaire hypotensie.
- **Laag 2 — Berekende ratio**: Neem het Noorse draft-archetype over als **`OBSERVATION.ankle_brachial_pressure_index.v0`** — bevat alleen het berekende quotiënt (bijv. 0.82) als numeriek data-element, met links naar de bronmetingen.
- **Laag 3 — Klinische evaluatie**: De interpretatie ("EAI < 0.6 = ernstig vaatlijden, compressie gecontra-indiceerd") hoort in een apart **`EVALUATION`-archetype** of in een 'Interpretation'-element binnen het observatie-archetype. Deze scheiding tussen rauwe meting en klinisch oordeel is essentieel voor betrouwbare beslissingsondersteuning.

**🟠 Actie C-5**: Maak een **`CLUSTER.exam_stemmer_test`** (of neem op als element in een oedeem-beoordelingscluster): Stemmer-test resultaat (positief/negatief), locatie (2e teen dorsaal), interpretatie (lymfoedeem / veneus oedeem).

---

## 3. Overzicht Templates

De drie protocollen vertalen zich naar **drie openEHR templates** (plus één gedeeld "wondregistratie" template):

### Template 1: `Wound_Assessment_Sensire.v1`
*Het Algemeen Wondprotocol — kern van alle wondzorg*

```
COMPOSITION.encounter.v1
├── SECTION "Wondidentificatie"
│   └── EVALUATION.problem_diagnosis.v1
│       ├── CLUSTER.wound_assertion_details
│       └── CLUSTER.anatomical_location.v1
├── SECTION "Wondinspectie (TIME)"
│   └── OBSERVATION.exam.v1
│       ├── CLUSTER.exam_wound (T, I, M, E)
│       ├── CLUSTER.wound_tissue_wcs_nl.v0 [NIEUW C-1] (kleur + %)
│       └── CLUSTER.media_file.v1 (foto)
├── SECTION "Pijnmanagement"
│   ├── OBSERVATION.pain_scale (VAS/ALTIS)
│   └── ACTION.medication.v1
├── SECTION "Reiniging & Debridement"
│   ├── ACTION.procedure.v1 (reiniging)
│   └── ACTION.procedure.v1 (debridement)
├── SECTION "Infectiebeleid"
│   ├── OBSERVATION.body_temperature.v2
│   └── INSTRUCTION.medication_order.v4
├── SECTION "Behandeling & Verband"
│   ├── INSTRUCTION.therapeutic_item_order.v1 (verbandorder)
│   ├── ACTION.procedure.v1 (verband aanleggen)
│   └── CLUSTER.device.v1 (materiaal)
├── SECTION "Escalatie"
│   ├── EVALUATION.clinical_synopsis.v1
│   └── INSTRUCTION.service_request.v1 (vakgroep)
└── SECTION "Rapportage"
    └── EVALUATION.clinical_synopsis.v1
```

### Template 2: `Diabetic_Foot_Assessment_Sensire.v1`
*Voetscreening en -inspectie DM-patiënt*

```
COMPOSITION.encounter.v1
├── SECTION "Anamnese"
│   └── OBSERVATION.story.v1
│       └── CLUSTER.symptom_sign.v2 (claudicatio, pijn, etc.)
├── SECTION "Risicofactoren"
│   └── EVALUATION.health_risk.v1
├── SECTION "Voetinspectie"
│   └── OBSERVATION.exam.v1
│       ├── CLUSTER.exam_diabetic_foot [NIEUW C-3]
│       │   ├── Huidkleur, temperatuur (bilateraal), eelt, fissuren
│       │   ├── Pulsaties (a. dorsalis pedis, a. tibialis post.)
│       │   ├── Standsafwijkingen, nagels, schoeisel
│       │   └── Charcot-vermoeden (ja/nee)
│       └── CLUSTER.anatomical_location.v1
├── SECTION "Monofilament-test"
│   └── OBSERVATION.monofilament_examination.v0 [NIEUW C-3b]
│       ├── Plantaire locatiematrix (per zone: ja/nee)
│       └── Totaalscore
├── SECTION "Wondgradering" (indien wond aanwezig)
│   └── OBSERVATION.diabetic_wound_wagner.v0 (graad 0-5)
├── SECTION "Risicoclassificatie"
│   └── EVALUATION.sims_classification_nl.v0 [NIEUW C-3c]
│       ├── Sims-categorie (0, 1, 2, 3)
│       └── Onderliggende factoren (PS-verlies, PAV, ulcushistorie)
├── SECTION "Charcot-alarm"
│   └── INSTRUCTION.service_request.v1 (arts dezelfde dag)
├── SECTION "Preventieve zorg"
│   └── ACTION.health_education.v1
└── SECTION "Verwijzing wondprotocol"
    └── (link naar Wound_Assessment template)
```

### Template 3: `Ulcus_Cruris_Assessment_Sensire.v1`
*Specifieke UC-diagnostiek en compressietherapie*

```
COMPOSITION.encounter.v1
├── SECTION "Triage"
│   └── EVALUATION.problem_diagnosis.v1 (UC-diagnose)
├── SECTION "DM-screening"
│   └── (link naar Diabetic_Foot_Assessment template)
├── SECTION "Oedeem-beoordeling"
│   ├── CLUSTER.exam.v1 (oedeem bevinding)
│   └── CLUSTER.exam_stemmer_test [NIEUW C-5]
├── SECTION "EAI-beoordeling (drielaags)"
│   ├── OBSERVATION.blood_pressure.v2 (enkel + arm, gelabeld als ABPI-bron)
│   ├── OBSERVATION.ankle_brachial_pressure_index.v0 [C-4] (berekende ratio)
│   └── EVALUATION (interpretatie: <0.6 / 0.6-1.3 / >1.3 → beleid)
├── SECTION "Vaatdiagnose"
│   └── EVALUATION.problem_diagnosis.v1 (arterieel/veneus/gemengd)
├── SECTION "Wondzorg"
│   └── (link naar Wound_Assessment template)
├── SECTION "Compressietherapie"
│   ├── INSTRUCTION.therapeutic_item_order.v1 (zwachtelorder)
│   ├── ACTION.procedure.v1 (zwachtelen)
│   ├── CLUSTER.device.v1 (UrgoK2 / UrgoK2 Lite)
│   └── Enkelomvang + maatbepaling
├── SECTION "Nazorg"
│   └── INSTRUCTION.care_plan.v0
└── SECTION "Afsluiting"
    └── EVALUATION.clinical_synopsis.v1
```

---

## 4. Concrete actielijst

### Stap 1: Internationale archetypes ophalen (🟢 A)
Download vanuit de internationale CKM (https://ckm.openehr.org):

| Archetype | Versie/Status | Opmerking |
|-----------|---------------|-----------|
| `EVALUATION.problem_diagnosis.v1` | Published | Kern voor wond- en comorbiditeitsdiagnoses |
| `OBSERVATION.exam.v1` | Published | Container voor alle onderzoeksbevindingen |
| `CLUSTER.exam.v1` | Published | Generiek onderzoekscluster |
| `CLUSTER.exam_wound` | Incubator | Wondspecifiek onderzoek (Heather Leslie) |
| `CLUSTER.wound_assertion_details` | Incubator | Extensie op problem_diagnosis voor wondtype |
| `CLUSTER.anatomical_location.v1` | Published | Wondlocatie |
| `CLUSTER.media_file.v1` | Published | Wondfoto's |
| `CLUSTER.symptom_sign.v2` | Published | Symptomen (infectie, claudicatio, pijn) |
| `CLUSTER.device.v1` | Published | Verbandmateriaal, zwachtelsysteem |
| `OBSERVATION.body_temperature.v2` | Published | Koorts bij infectie |
| `OBSERVATION.laboratory_test_result.v1` | Published | HbA1c en andere lab |
| `OBSERVATION.story.v1` | Published | Anamnese |
| `ACTION.procedure.v1` | Published | Reiniging, debridement, verband, zwachtelen |
| `ACTION.medication.v1` | Published | Pijnmedicatie |
| `ACTION.health_education.v1` | Published | DM-voorlichting, preventie |
| `INSTRUCTION.medication_order.v4` | Published | Pijn- en infectiemedicatie |
| `INSTRUCTION.service_request.v1` | Published | Verwijzingen (arts, vakgroep, vaatchirurg) |
| `INSTRUCTION.therapeutic_item_order.v1` | Published | Orders voor verbanden, zwachtels, compressiesystemen (niet-medicamenteuze therapeutische items) |
| `INSTRUCTION.care_plan.v0` | Draft | Wondplan, nazorgplan |
| `EVALUATION.health_risk.v1` | Published | DM-risicofactoren, Charcot-risico |
| `EVALUATION.clinical_synopsis.v1` | Published | Samenvatting bij rapportage/afsluiting |
| `EVALUATION.contraindication.v0` | Draft | Contra-indicaties debridement |
| `CLUSTER.physical_properties.v0` | Draft | Wondafmetingen (l×b×d) |
| `OBSERVATION.diabetic_wound_wagner.v0` | Incubator | Wagner-classificatie DM-voetulcera (graad 0-5) |
| `COMPOSITION.encounter.v1` | Published | Contactmoment als container |

**Totaal: ~25 bestaande internationale archetypes**

### Stap 2: Nationaal/regionaal beschikbare archetypes ophalen (🟡 B)

| Bron | Archetype | Actie |
|------|-----------|-------|
| **Noorse CKM** | `OBSERVATION.ankle_brachial_pressure_index` | Download, vertaal naar NL, gebruik als lokaal archetype |
| **ZIBs-on-openEHR** (github.com/openehr-nl) | Vertalingen van anatomical_location, problem_diagnosis, etc. | Gebruik de NL-vertalingen waar beschikbaar |
| **ZIB PijnScore** | Mapping via `OBSERVATION.pain_scale` of generiek observatie-archetype | Volg de ZIB-mapping van openEHR-NL werkgroep |

### Stap 3: Nieuwe of uitgebreide archetypes maken (🟠 C)

| ID | Wat | Type | Geschatte inspanning |
|----|-----|------|---------------------|
| **C-1** | `CLUSTER.wound_tissue_wcs_nl.v0` — WCS-kleurclassificatie als apart herbruikbaar cluster met primaire/secundaire kleur en percentagevelden | **Nieuw archetype** (ADL2) | ½ dag |
| **C-2** | Pijnschaal template-constraint (VAS 0-10 + ALTIS) | Template-constraint op bestaand archetype | ¼ dag |
| **C-3** | `CLUSTER.exam_diabetic_foot` — specialisatie van `CLUSTER.exam.v1` | **Nieuw archetype** (ADL2) met elementen: bilaterale temp, pulsaties, eelt, fissuren, standsafwijkingen, schoeisel, Charcot-vermoeden | 1 dag |
| **C-3b** | `OBSERVATION.monofilament_examination.v0` — volwaardig OBSERVATION-archetype voor de Semmes-Weinstein 10g test met plantaire locatiematrix en totaalscore | **Nieuw archetype** (ADL2) | 1 dag |
| **C-3c** | `EVALUATION.sims_classification_nl.v0` — Sims-risicoclassificatie (categorie 0-3) met onderliggende factoren (PS-verlies, PAV, ulcushistorie) | **Nieuw archetype** (ADL2) | ½ dag |
| **C-4** | ABI/EAI — drielaags model: (1) gelabelde bloeddrukmeting, (2) adoptie Noors ratio-archetype + NL-vertaling, (3) evaluatie-interpretatie | Lokale adoptie + template-configuratie | 1 dag |
| **C-5** | `CLUSTER.exam_stemmer_test` — simpel cluster: resultaat (pos/neg), locatie, interpretatie | **Nieuw archetype** (klein) | ¼ dag |
| **C-6** | NL-vertalingen voor alle gebruikte archetypes die nog geen NL-vertaling hebben | Vertaalwerk in CKM of lokaal | 2-3 dagen |
| **C-7** | SNOMED-CT bindings voor alle value sets. Concrete codes: **371087003** (diabetisch voetulcus), **420101004** (veneus ulcus cruris), **298007001** (vochtigheidsgraad wond), plus NHG-bindings voor WCS-kleuren, wondtypen, materialen, infectietekenen | Terminologie-binding in templates | 1-2 dagen |

### Stap 4: Templates bouwen

Gebruik de **Archetype Designer** (https://tools.openehr.org/designer) om de drie templates samen te stellen:

1. **`Wound_Assessment_Sensire.v1`** — Bouw als eerste; dit is de kern die door de andere twee wordt gebruikt. Bevat nu ook het WCS-cluster (C-1) en `therapeutic_item_order` voor verbandorders.
2. **`Diabetic_Foot_Assessment_Sensire.v1`** — Bevat C-3 (voetcluster), C-3b (monofilament OBSERVATION), C-3c (Sims EVALUATION), plus Wagner-gradering.
3. **`Ulcus_Cruris_Assessment_Sensire.v1`** — Bevat C-4 (ABPI drielaags), C-5 (Stemmer), `therapeutic_item_order` voor zwachtelorders.

Per template: constraint alle niet-gebruikte velden uit archetypes weg (0..0), maak verplichte velden mandatory, voeg value set bindings toe.

### Stap 5: Operational Templates (OPT) genereren en valideren

1. Exporteer elk template als **OPT 1.4** (voor EHRbase-compatibiliteit) of **OPT 2** (voor nieuwere platforms)
2. Upload naar je EHRbase-instantie
3. Valideer met testdata uit elk protocol-scenario
4. Genereer example compositions per template

### Stap 6: Beslislogica apart vastleggen

De flowchart-logica (beslisbomen) uit de Mermaid-diagrammen is *geen* data maar *procesbeschrijving*. Deze leg je vast in:

- **GDL2** (Guideline Definition Language) — voor klinische beslisregels
- Of **CDS Hooks / PlanDefinition (FHIR)** als je een hybride architectuur hebt

Voorbeelden van regels die je in GDL2 kunt vastleggen:
- "Als DM = ja → activeer DM-laag"
- "Als EAI < 0.6 → GEEN compressie + verwijs vaatchirurg"
- "Als EAI 0.6-0.8 → alleen lichte compressie (UrgoK2 Lite)"
- "Als Charcot-vermoeden = ja → alarm arts dezelfde dag"
- "Als wond > 2-3 weken zonder verbetering → escalatie vakgroep"
- "Monofilament-score ≤5/8 + PAV-tekenen → Sims-categorie ≥2 voorstellen"
- "INSTRUCTION.therapeutic_item_order (zwachtel) alleen toestaan als ABPI-ratio ≥ 0.6"

### Stap 7: FHIR-bridge — Terugmapping naar ZIB/FHIR voor landelijke uitwisseling

Als je EPD-omgeving verplicht is om data uit te wisselen conform MedMij-standaarden of het Landelijk Schakelpunt (die leunen op de "platte" ZIB's in HL7 FHIR-profielen), dan fungeert je rijke openEHR-databank als Single Source of Truth. In deze fase:

1. Gebruik declaratieve mapping tools (FHIR-Bridge, openFHIR-project) of transformatiescripts (XSLT, JSON-path mappings)
2. "Downscale" het longitudinale openEHR-dossier in real-time naar de vlakkere FHIR ZIB-profielen (zoals `nictiz.fhir.nl.r4.zib2020`)
3. Profiteer van de mapping-scripts die Nictiz openEHR-transitiewerkgroepen publiceren op GitHub (`openehr-nl/ZIBs-on-openEHR`, `Nictiz/HL7-mappings`)

---

## 5. Samenvatting effort-schatting

| Categorie | Items | Geschatte tijd |
|-----------|-------|----------------|
| 🟢 Internationale archetypes downloaden + configureren | ~25 archetypes | 1 dag |
| 🟡 Nationale archetypes ophalen (Noors ABI, ZIB-vertalingen) | 3-5 items | ½ dag |
| 🟠 Nieuwe archetypes bouwen (C-1 WCS, C-3 voetcluster, C-3b monofilament, C-3c Sims, C-5 Stemmer) | 5 archetypes | 3-4 dagen |
| 🟠 Template-constraints en value sets (C-2, C-4 ABPI drielaags, C-7 SNOMED) | 3 taken | 2-3 dagen |
| 🟠 NL-vertalingen (C-6) | ~15 archetypes | 2-3 dagen |
| Templates bouwen (3 templates) | 3 templates | 2-3 dagen |
| OPT generatie + validatie | 3 OPTs | 1 dag |
| GDL2 beslisregels | ~10 regels | 2-3 dagen |
| FHIR-bridge (ZIB-terugmapping) | Mapping configuratie | 2-3 dagen |
| **Totaal** | | **~16-22 werkdagen** |

---

## 6. Architectuuroverzicht

```
┌─────────────────────────────────────────────────────────┐
│                    EHRbase / openEHR CDR                 │
│                                                         │
│  ┌──────────────────┐ ┌──────────────┐ ┌─────────────┐  │
│  │ Wound_Assessment │ │ Diabetic_Foot│ │ Ulcus_Cruris│  │
│  │ Template (OPT)   │ │ Template     │ │ Template    │  │
│  └────────┬─────────┘ └──────┬───────┘ └──────┬──────┘  │
│           │                  │                │          │
│  ┌────────┴──────────────────┴────────────────┴───────┐  │
│  │         Gedeelde Archetype-bibliotheek              │  │
│  │                                                     │  │
│  │  🟢 25 Internationale archetypes (CKM)              │  │
│  │     incl. Wagner, therapeutic_item_order             │  │
│  │  🟡 ABI (Noors), ZIB-vertalingen                    │  │
│  │  🟠 NIEUW: wound_tissue_wcs_nl (C-1)                │  │
│  │  🟠 NIEUW: exam_diabetic_foot (C-3)                 │  │
│  │  🟠 NIEUW: monofilament_examination (C-3b)          │  │
│  │  🟠 NIEUW: sims_classification_nl (C-3c)            │  │
│  │  🟠 NIEUW: exam_stemmer_test (C-5)                  │  │
│  │  🟠 SNOMED-CT bindings (371087003, 420101004, etc.) │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  GDL2 Beslisregels (protocol-flowcharts)            │  │
│  │  • DM-laag activatie                                │  │
│  │  • EAI-interpretatie + compressiekeuze              │  │
│  │  • Charcot-alarm                                    │  │
│  │  • Sims-berekening uit monofilament + PAV           │  │
│  │  • ABPI-gate: zwachtelorder alleen als ratio ≥ 0.6  │  │
│  │  • Escalatie vakgroep                               │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  FHIR-Bridge (Stap 7)                               │  │
│  │  openEHR → ZIB FHIR-profielen (nictiz.fhir.nl.r4)  │  │
│  │  Voor MedMij / Landelijk Schakelpunt uitwisseling   │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```
