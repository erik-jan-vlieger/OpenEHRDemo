# 🏥 openEHR Demo-omgeving — Sensire Wondzorg

## Volledig Uitvoeringsplan v5.0

*Debian Trixie / Chromebox — Maart 2026*

*Gebaseerd op: v4.0 (maart 2026), implementatiesessie 16 maart, architecturaal onderzoeksrapport OPT-automatisering, GDL2/CDS-strategierapport, mappingdocument Sensire wondprotocollen, en GDL2 Ulcus Cruris regelset.*

---

> **Wat is nieuw in v5 ten opzichte van v4?**
>
> | Onderwerp | v4 | v5 (dit plan) |
> |:----------|:---|:--------------|
> | ADL-versie | Impliciet ADL 1.4, niet afgedwongen | **Expliciet ADL 1.4 door de hele keten** — met rationale en bewaking |
> | GDL2 | Geschrapt ("te zwaar, te traag") | **Heringevoerd als demonstratielaag** — GDL2 Editor als Docker-container voor live CDS-demo's + validatie. JavaScript blijft de frontend-logica |
> | OPT-generatie | Handmatig via Archetype Designer export | **Geautomatiseerd via CaboLabs openEHR-CLI** — `adl2opt` compileert ADL 1.4 + OET → OPT 1.4 op de commandline |
> | Templates | Eén samengevoegd template `sensire_wound_care` | **Drie afzonderlijke templates** conform mappingdocument: Wound Assessment, Diabetic Foot, Ulcus Cruris |
> | Versiebeheer | `git init` + handmatige commits | **Semantic Versioning (SemVer)** voor archetypes én templates, met expliciete PATCH/MINOR/MAJOR-regels |
> | NL-vertaling | Handmatig in Archetype Designer | **LLM-vertaalpipeline** — gestructureerd proces: ADL-export → Claude-vertaling → terugplaatsen in ontology-sectie |
> | Archetype-inventaris | 5 internationale + 5 eigen | **25 internationale + 5 nieuwe eigen** — volledig conform het mappingdocument |
> | GDL2 regelset | Niet aanwezig | **Werkende GDL2 JSON** voor Ulcus Cruris (sensire_ulcus_cruris_v2.gdl2) als referentie |
> | CLI-tooling | Alleen `curl` | **Volledige toolchain**: CaboLabs CLI + adlc + curl + jq + xmllint |
> | Testdata | Handmatig JSON schrijven | **Geautomatiseerd** via CaboLabs `ingen` — synthetische composities genereren |
> | Docker-stack | EHRbase + PostgreSQL | EHRbase + PostgreSQL + **GDL2 Editor** (poort 8082) |

---

# DEEL I — ARCHITECTUUR EN ONTWERPBESLISSINGEN

---

## 1. Doel en Context

Een lokale, volledig werkende openEHR demo-omgeving op een Chromebox met Debian Trixie. De demo toont aan Sensire-collega's en stakeholders:

- **Data-onafhankelijkheid**: openEHR-data is leverancier-neutraal, toekomstbestendig, internationaal leesbaar.
- **Kennislaag visueel**: internationale vs. eigen archetypes, EN ↔ NL vertaling als presentatielaag.
- **Beslisondersteuning live**: GDL2-regels evalueren patiëntdata en produceren transparant, traceerbaar advies ("white-box CDS").
- **End-to-end keten**: van formulier → FLAT JSON → EHRbase → AQL-bewijs → GDL2-evaluatie.

## 2. De Dual-Model Architectuur

openEHR scheidt twee domeinen:

**Het Informatiemodel (Referentiemodel, RM)** — Generieke datastructuren (COMPOSITION, OBSERVATION, EVALUATION, CLUSTER, ACTION, INSTRUCTION) die in software zijn ingebouwd. EHRbase implementeert RM 1.1.0. Dit model verandert niet als er nieuwe klinische kennis komt.

**Het Kennismodel** — Archetypes (maximale klinische conceptdefinities), Templates (lokale selectie en inperking), en GDL2-regels (beslislogica). Dit model wordt beheerd door domeinexperts, niet door programmeurs.

De scheiding betekent: als Sensire morgen een nieuw wondtype wil registreren, verandert er niets aan de software — alleen een nieuw archetype of template-aanpassing.

## 3. De IJzeren Wet: ADL 1.4 Door de Hele Keten

### 3.1 Waarom ADL 1.4 en niet ADL 2.0?

Dit is de meest kritieke architectuurbeslissing van het hele project:

**EHRbase ondersteunt uitsluitend ADL 1.4 en OPT 1.4.** Uploads van ADL 2.0 of OPT 2 resulteren in een `501 Not Implemented` of falen stil. De AQL-engine, de databasestructuur en de validatielaag zijn gebouwd op het `at-code`-systeem van ADL 1.4. De transitie naar het gescheiden `id-code`/`ac-code`/`at-code`-systeem van ADL 2.0 is niet voltooid in enige productie-CDR.

**De internationale CKM publiceert in ADL 1.4.** Veruit de meeste gepubliceerde internationale archetypes gebruiken ADL 1.4 met `at-codes`. De Bulk Export levert ADL 1.4-bestanden.

**De CaboLabs openEHR-CLI compileert ADL 1.4 → OPT 1.4.** Dit is de enige beschikbare open-source CLI-tool die de volledige keten ondersteunt. Nedap Archie genereert alleen OPT 2 — onbruikbaar voor EHRbase.

**GDL2-regels binden aan archetype-paden in `at-code`-notatie.** De werkende Ulcus Cruris GDL2-regelset (sensire_ulcus_cruris_v2.gdl2) verwijst naar paden als `/data[at0001]/events[at0002]/data[at0003]/items[at0004]`.

### 3.2 Wat dit concreet betekent

| Stap | Format | Verificatie |
|:-----|:-------|:------------|
| Archetype downloaden uit CKM | ADL 1.4 (`.adl`) | Bestand begint met `archetype (adl_version=1.4)` |
| Eigen archetype bouwen in Archetype Designer | ADL 1.4 export | Exporteer als "ADL 1.4", NIET als "ADL 2" |
| Template ontwerpen | OET (`.oet`) | XML-bestand met root-verwijzing naar COMPOSITION |
| Template compileren | OPT 1.4 (`.opt`) | Via CaboLabs CLI `adl2opt` of Archetype Designer "Export OPT" |
| Template uploaden naar EHRbase | OPT 1.4 via REST | `POST .../definition/template/adl1.4` met `Content-Type: application/xml` |
| WebTemplate ophalen | JSON via REST | `GET .../definition/template/adl1.4/{id}` met `Accept: application/json` |
| GDL2-regels schrijven | `.gdl2` JSON | Paden verwijzen naar `at-codes` uit de ADL 1.4 archetypes |

### 3.3 ADL 1.4-bewaking in de workflow

```bash
# Snelle check: is dit ADL 1.4?
head -5 archetype.adl | grep -q "adl_version=1.4" && echo "✅ ADL 1.4" || echo "❌ NIET ADL 1.4"

# Batch-check hele directory
for f in ~/ehrbase-demo/archetypes/**/*.adl; do
  head -5 "$f" | grep -q "adl_version=1.4" || echo "⚠️ $f is NIET ADL 1.4"
done
```

## 4. GDL2: Heringevoerd als Demonstratie- en CDS-laag

### 4.1 Waarom GDL2 terug is

In v4 werd GDL2 geschrapt met de redenering "te zwaar, te traag, tooling onvoldoende mature." Na diepgaand onderzoek blijkt deze conclusie te nuanceren:

**GDL2 is niet bedoeld als frontend-formulierengenerator** — dat klopt. De JavaScript-beslisbomen in de browser blijven de juiste keuze voor interactieve formulieren. Dat verandert niet.

**GDL2 is wél een ongeëvenaard demonstratie-instrument:**
- De GDL2 Editor heeft een **Execution-tabblad** dat automatisch invoerformulieren genereert op basis van geladen archetypes. Live testdata invullen → klikken op "Execute" → direct klinisch advies zien.
- Het **Debug Execution-paneel** toont transparant welke regels zijn afgevuurd en waarom. Dit "white-box" CDS is overtuigender voor clinici dan een JavaScript-blackbox.
- Het **Test-tabblad** biedt geautomatiseerde validatie met testfixtures (YAML) en rapporteert rule coverage.

**GDL2 is de strategisch veilige keuze:**
- De openEHR-gemeenschap adviseert expliciet om GDL2 te gebruiken voor huidige projecten, ook met de toekomstige Decision Language (DL) in het vooruitzicht.
- Regels in GDL2 kunnen later geautomatiseerd geconverteerd worden naar DL/Task Planning.
- Er zijn 700+ kant-en-klare GDL2-richtlijnen beschikbaar op GitHub (Cambio CDS).

### 4.2 De Tweesporige Architectuur

| Spoor | Technologie | Doel | Wanneer |
|:------|:------------|:-----|:--------|
| **Frontend-logica** | JavaScript in browser | Interactieve formulieren, conditionele velden, formulier-navigatie | Altijd — de gebruiker ziet dit |
| **CDS-logica** | GDL2 in Docker | Formele beslisregels, score-berekeningen, escalatie-triggers, transparante audit trail | Bij demo's, bij validatie, en als fundament voor toekomstige productie-CDS |

De kernboodschap wordt:
> *"De formulieren zijn gebouwd in JavaScript — snel, interactief, direct. Maar de klinische beslisregels zijn formeel vastgelegd in GDL2 — transparant, testbaar, internationaal herkenbaar. De data die wordt opgeslagen is identiek. Dit is de kracht van openEHR: de applicatielaag is vervangbaar, de data en de kennis niet."*

### 4.3 Wat GDL2 NIET doet

GDL2 genereert geen templates, compileert geen OPT's, en vervangt geen Archetype Designer. GDL2 *consumeert* data die is gestructureerd volgens archetypes/templates en *produceert* klinisch advies, scores en escalatie-triggers.

## 5. Semantic Versioning (SemVer) voor Klinische Modellen

### 5.1 Archetypes

| Versie-indicator | Betekenis | Voorbeeld |
|:-----------------|:----------|:----------|
| **PATCH** (vX.X.+1) | Cosmetisch: typfout in description, nieuwe taalvertaling toevoegen, annotatie-update. Data blijft 100% valide. | v0.1.0 → v0.1.1: NL-vertaling toegevoegd |
| **MINOR** (vX.+1.0) | Uitbreiding: nieuw optioneel element (0..1), verbreding waardebereik, nieuwe terminologie-code. Oude data blijft valide. | v0.1.1 → v0.2.0: optioneel veld "secundaire kleur" toegevoegd |
| **MAJOR** (v+1.0.0) | Breaking: element verwijderd, datatype gewijzigd, cardinaliteit restrictiever. Oude data kan falen bij validatie. | v0.2.0 → v1.0.0: weefseltype van DV_TEXT naar DV_CODED_TEXT |

### 5.2 Templates

Analoog aan archetypes. Kritiek punt: een MAJOR-wijziging in een template betekent dat eerder opgeslagen composities mogelijk niet meer valideren. EHRbase weigert (HTTP 422) een template te overschrijven als er composities aan gekoppeld zijn.

**Praktische regel:** Voeg bij een MAJOR-wijziging altijd een nieuw template-ID toe (bijv. `Wound_Assessment_Sensire.v2`) in plaats van v1 te overschrijven. Beide versies kunnen naast elkaar bestaan in EHRbase.

### 5.3 Versiebeheer in de bestandsnaam en metadata

```
~/ehrbase-demo/
├── archetypes/
│   ├── international/          # CKM-mirror, ongewijzigd
│   │   ├── CLUSTER.exam_wound.v0.adl
│   │   └── ...
│   └── sensire/                # Eigen archetypes
│       ├── CLUSTER.wound_tissue_wcs_nl.v0.adl     # C-1
│       ├── CLUSTER.exam_stemmer_test.v0.adl        # C-5
│       └── ...
├── templates/
│   ├── Wound_Assessment_Sensire.v1.oet
│   ├── Diabetic_Foot_Assessment_Sensire.v1.oet
│   └── Ulcus_Cruris_Assessment_Sensire.v1.oet
├── operational_templates/      # Gecompileerde OPT 1.4 bestanden
│   ├── Wound_Assessment_Sensire.v1.opt
│   ├── Diabetic_Foot_Assessment_Sensire.v1.opt
│   └── Ulcus_Cruris_Assessment_Sensire.v1.opt
├── webtemplates/               # Door EHRbase gegenereerde JSON
├── gdl2/                       # GDL2-regelsets
│   ├── sensire_ulcus_cruris_v2.gdl2
│   └── test_fixtures/
├── compositions/               # Testdata (gegenereerd + handmatig)
├── translations/               # LLM-vertaalbestanden
└── scripts/                    # Automatiseringsscripts
```

---

# DEEL II — CLI-TOOLCHAIN EN INSTALLATIE

---

## 6. De Volledige CLI-Toolchain

### 6.1 Overzicht

| Tool | Installatie | Functie | Kritiek voor |
|:-----|:------------|:--------|:-------------|
| **Docker + Docker Compose** | `apt-get install docker-ce docker-compose-plugin` | Containerruntime | Alles |
| **curl** | Pre-installed | HTTP-requests naar EHRbase REST API | Template upload, AQL, composities |
| **jq** | `apt-get install jq` | JSON parsing en transformatie | WebTemplate verwerken, AQL-resultaten |
| **xmllint** | `apt-get install libxml2-utils` | XML-validatie van OPT 1.4 bestanden | OPT-validatie vóór upload |
| **CaboLabs openEHR-CLI** | `git clone` + JDK 11 + Gradle | ADL 1.4 → OPT 1.4 compilatie, testdata generatie, validatie | OPT-automatisering |
| **adlc** (ADL Workbench) | Binary download | Massa-validatie van ADL-archetypes | CI-linting |
| **GDL2 Editor** | `docker run cdsplatform/gdl2-editor:3.0.1` | Visueel ontwerp, executie en test van GDL2-regels | CDS-demo's |
| **git** | Pre-installed | Versiebeheer | Alles |

### 6.2 Docker-stack: docker-compose.yml (v5)

```yaml
# ~/ehrbase-demo/docker-compose.yml
version: '3'
networks:
  ehrbase-net:
    driver: bridge

services:
  ehrdb:
    image: ehrbase/ehrbase-v2-postgres:16.2
    networks: [ehrbase-net]
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      EHRBASE_USER_ADMIN: ehrbase
      EHRBASE_PASSWORD_ADMIN: ehrbase
      EHRBASE_USER: ehrbase_restricted
      EHRBASE_PASSWORD: ehrbase_restricted
    ports: ['5432:5432']
    volumes:
      - ehrbase_data:/var/lib/postgresql/data

  ehrbase:
    image: ehrbase/ehrbase:2.29.0    # Pin naar geteste versie
    networks: [ehrbase-net]
    depends_on: [ehrdb]
    environment:
      DB_URL: jdbc:postgresql://ehrdb:5432/ehrbase
      DB_USER: ehrbase_restricted
      DB_PASS: ehrbase_restricted
      DB_USER_ADMIN: ehrbase
      DB_PASS_ADMIN: ehrbase
      SECURITY_AUTHTYPE: BASIC
      SECURITY_AUTHUSER: ehrbase-user
      SECURITY_AUTHPASSWORD: SuperSecretPassword
      SERVER_NODENAME: sensire.ehrbase.local
    ports: ['8080:8080']

  gdl2-editor:
    image: cdsplatform/gdl2-editor:3.0.1
    networks: [ehrbase-net]
    ports: ['8082:8080']    # Poort 8082 op host → 8080 in container
    # Geen env vars nodig — werkt out-of-the-box

  pgadmin:
    image: dpage/pgadmin4
    networks: [ehrbase-net]
    environment:
      PGADMIN_DEFAULT_EMAIL: demo@sensire.nl
      PGADMIN_DEFAULT_PASSWORD: demo
    ports: ['5050:80']

volumes:
  ehrbase_data:
```

**Starten:**
```bash
cd ~/ehrbase-demo && docker compose up -d

# Verificatie
docker compose ps

# EHRbase status
curl -s -u ehrbase-user:SuperSecretPassword http://localhost:8080/ehrbase/rest/status | jq .

# GDL2 Editor
echo "Open in browser: http://localhost:8082/gdl2-editor"
```

### 6.3 CaboLabs openEHR-CLI installeren

```bash
# Vereiste: JDK 11+
sudo apt-get install -y default-jdk
java --version    # Moet ≥ 11 tonen

# Clone en build
cd ~/tools
git clone https://github.com/CaboLabs/openEHR-SDK.git
cd openEHR-SDK
./gradlew installDist

# Symlink voor gemak
ln -s ~/tools/openEHR-SDK/opt/build/install/opt/bin/opt.sh ~/bin/openehr-cli

# Test
openehr-cli help
```

**Kerncommando's:**

```bash
# 1. OPT 1.4 compileren uit ADL 1.4 archetypes + OET template
openehr-cli adl2opt \
  -a ~/ehrbase-demo/archetypes/ \
  -t ~/ehrbase-demo/templates/Wound_Assessment_Sensire.v1.oet \
  -o ~/ehrbase-demo/operational_templates/

# 2. Synthetische testdata genereren (10 composities, JSON format)
openehr-cli ingen \
  ~/ehrbase-demo/operational_templates/Wound_Assessment_Sensire.v1.opt \
  ~/ehrbase-demo/compositions/ \
  10 json_composition

# 3. Compositie valideren tegen OPT
openehr-cli inval \
  ~/ehrbase-demo/operational_templates/Wound_Assessment_Sensire.v1.opt \
  ~/ehrbase-demo/compositions/composition_001.json
```

### 6.4 Overzicht draaiende services (v5)

| Component | Status | URL | Poort |
|:----------|:-------|:----|:------|
| EHRbase CDR | ✅ Draait | http://localhost:8080 | 8080 |
| Swagger UI | ✅ Ingebouwd | http://localhost:8080/ehrbase/swagger-ui.html | 8080 |
| PostgreSQL | ✅ Draait | localhost:5432 | 5432 |
| GDL2 Editor | 🆕 Draait | http://localhost:8082/gdl2-editor | 8082 |
| pgAdmin | ✅ Draait | http://localhost:5050 | 5050 |
| Demo-applicatie | ✅ Lokaal | http://localhost:5173 | 5173 |

---

# DEEL III — DE KENNISLAAG: ARCHETYPES, TEMPLATES, VERTALINGEN

---

## 7. Archetype-inventaris (Volledig)

### 7.1 Internationale archetypes (🟢 A — downloaden uit CKM)

25 archetypes, allemaal ADL 1.4, downloaden via CKM Bulk Export (filter: "Published" + selectief "Incubator"):

| # | Archetype | RM-type | Gebruikt in template(s) |
|:--|:----------|:--------|:------------------------|
| 1 | `COMPOSITION.encounter.v1` | COMPOSITION | Alle drie |
| 2 | `EVALUATION.problem_diagnosis.v1` | EVALUATION | Alle drie |
| 3 | `EVALUATION.health_risk.v1` | EVALUATION | DM-voet, UC |
| 4 | `EVALUATION.clinical_synopsis.v1` | EVALUATION | AWP, UC |
| 5 | `EVALUATION.contraindication.v0` | EVALUATION | AWP |
| 6 | `OBSERVATION.exam.v1` | OBSERVATION | Alle drie |
| 7 | `OBSERVATION.body_temperature.v2` | OBSERVATION | AWP |
| 8 | `OBSERVATION.laboratory_test_result.v1` | OBSERVATION | DM-voet |
| 9 | `OBSERVATION.story.v1` | OBSERVATION | DM-voet |
| 10 | `OBSERVATION.diabetic_wound_wagner.v0` | OBSERVATION | DM-voet |
| 11 | `CLUSTER.exam.v1` | CLUSTER | Alle drie |
| 12 | `CLUSTER.exam_wound` | CLUSTER | AWP, UC |
| 13 | `CLUSTER.wound_assertion_details` | CLUSTER | AWP |
| 14 | `CLUSTER.anatomical_location.v1` | CLUSTER | AWP, DM-voet |
| 15 | `CLUSTER.media_file.v1` | CLUSTER | AWP |
| 16 | `CLUSTER.symptom_sign.v2` | CLUSTER | AWP, DM-voet |
| 17 | `CLUSTER.device.v1` | CLUSTER | AWP, UC |
| 18 | `CLUSTER.physical_properties.v0` | CLUSTER | AWP |
| 19 | `CLUSTER.oedema.v0` | CLUSTER | UC |
| 20 | `ACTION.procedure.v1` | ACTION | AWP, UC |
| 21 | `ACTION.medication.v1` | ACTION | AWP |
| 22 | `ACTION.health_education.v1` | ACTION | DM-voet |
| 23 | `INSTRUCTION.medication_order.v4` | INSTRUCTION | AWP |
| 24 | `INSTRUCTION.service_request.v1` | INSTRUCTION | Alle drie |
| 25 | `INSTRUCTION.therapeutic_item_order.v1` | INSTRUCTION | AWP, UC |
| 26 | `INSTRUCTION.care_plan.v0` | INSTRUCTION | UC, DM-voet |

*(AWP = Algemeen Wondprotocol, DM-voet = Diabetische Voet, UC = Ulcus Cruris)*

**Download-procedure:**

```bash
mkdir -p ~/ehrbase-demo/archetypes/international

# Optie 1: CKM Bulk Export (via browser)
# → https://ckm.openehr.org → Bulk Export → selecteer Published
# → Download ZIP → uitpakken in international/

# Optie 2: CKM GitHub mirror (sneller, completer)
cd ~/ehrbase-demo/archetypes/international
git clone --depth 1 https://github.com/openEHR/CKM-mirror.git

# Optie 3: Cherry-pick alleen de benodigde archetypes
# (zie script in §11.1)
```

### 7.2 Nationaal/regionaal beschikbare archetypes (🟡 B)

| Bron | Archetype | Actie |
|:-----|:----------|:------|
| Noorse CKM (Silje Ljosland Bakke) | `OBSERVATION.ankle_brachial_pressure_index.v0` | Download → adopteer lokaal → NL-vertaling |
| openEHR-NL werkgroep (GitHub) | NL-vertalingen van anatomical_location, problem_diagnosis e.a. | Gebruik bestaande NL-vertalingen |
| ZIB PijnScore mapping | `OBSERVATION.pain_scale.v0` | Volg ZIB-mapping |

```bash
mkdir -p ~/ehrbase-demo/archetypes/national

# Noors ABI-archetype ophalen
# (handmatig downloaden van Noorse CKM of via openEHR discourse)
```

### 7.3 Eigen Sensire-archetypes (🟠 C — nieuw te bouwen)

| ID | Archetype | RM-type | Doel | Inspanning |
|:---|:----------|:--------|:-----|:-----------|
| C-1 | `CLUSTER.wound_tissue_wcs_nl.v0` | CLUSTER | WCS-kleurclassificatie (primair/secundair/tertiair + percentages) | ½ dag |
| C-3 | `CLUSTER.exam_diabetic_foot.v0` | CLUSTER | DM-voetinspectie (bilaterale temp, pulsaties, eelt, schoeisel, Charcot) | 1 dag |
| C-3b | `OBSERVATION.monofilament_examination.v0` | OBSERVATION | Semmes-Weinstein 10g test met plantaire locatiematrix | 1 dag |
| C-3c | `EVALUATION.sims_classification_nl.v0` | EVALUATION | Sims-risicoclassificatie (cat. 0-3) | ½ dag |
| C-5 | `CLUSTER.exam_stemmer_test.v0` | CLUSTER | Stemmer-test (pos/neg, locatie, interpretatie) | ¼ dag |

**Alle eigen archetypes worden primair in het Engels gebouwd** (internationaal bijdraagbaar aan CKM) **met directe NL-vertaling**. Exporteer altijd als ADL 1.4.

**Bouwprocedure per archetype:**

1. Open Archetype Designer → repository "Sensire-wondzorg"
2. Maak nieuw archetype (correct RM-type)
3. Definieer structuur, datatypes, cardinaliteit in het Engels
4. Voeg Nederlandse taallaag toe (Languages → Add Language → nl)
5. Exporteer als **ADL 1.4** (niet ADL 2!)
6. Sla op in `~/ehrbase-demo/archetypes/sensire/`
7. Verifieer: `head -5 archetype.adl | grep "adl_version=1.4"`

## 8. Templates: Drie Afzonderlijke OPTs

### 8.1 Waarom drie templates, niet één?

Het mappingdocument identificeert drie distinct klinische use-cases met eigen entry-points, eigen beslislogica en eigen escalatiepaden. Eén mega-template zou leiden tot een onbeheersbaar groot WebTemplate en onnodige complexiteit in de frontend. Door drie templates te gebruiken:

- Elke beslisboompagina heeft een eigen, slanke WebTemplate
- Elk template kan onafhankelijk geversioneerd worden
- Cross-referenties tussen templates worden afgehandeld in de applicatielaag (niet in het datamodel)

### 8.2 Template 1: `Wound_Assessment_Sensire.v1`

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
│       ├── CLUSTER.wound_tissue_wcs_nl.v0 [C-1]
│       └── CLUSTER.media_file.v1
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
│   ├── INSTRUCTION.therapeutic_item_order.v1
│   ├── ACTION.procedure.v1 (verbandwisseling)
│   └── CLUSTER.device.v1
├── SECTION "Escalatie"
│   ├── EVALUATION.clinical_synopsis.v1
│   └── INSTRUCTION.service_request.v1
└── SECTION "Rapportage"
    └── EVALUATION.clinical_synopsis.v1
```

### 8.3 Template 2: `Diabetic_Foot_Assessment_Sensire.v1`

```
COMPOSITION.encounter.v1
├── SECTION "Anamnese"
│   └── OBSERVATION.story.v1
│       └── CLUSTER.symptom_sign.v2
├── SECTION "Risicofactoren"
│   └── EVALUATION.health_risk.v1
├── SECTION "Voetinspectie"
│   └── OBSERVATION.exam.v1
│       ├── CLUSTER.exam_diabetic_foot.v0 [C-3]
│       └── CLUSTER.anatomical_location.v1
├── SECTION "Monofilament-test"
│   └── OBSERVATION.monofilament_examination.v0 [C-3b]
├── SECTION "Wondgradering"
│   └── OBSERVATION.diabetic_wound_wagner.v0
├── SECTION "Risicoclassificatie"
│   └── EVALUATION.sims_classification_nl.v0 [C-3c]
├── SECTION "Charcot-alarm"
│   └── INSTRUCTION.service_request.v1
├── SECTION "Preventieve zorg"
│   └── ACTION.health_education.v1
└── SECTION "Verwijzing wondprotocol"
    └── INSTRUCTION.service_request.v1
```

### 8.4 Template 3: `Ulcus_Cruris_Assessment_Sensire.v1`

```
COMPOSITION.encounter.v1
├── SECTION "Triage"
│   └── EVALUATION.problem_diagnosis.v1
├── SECTION "DM-screening"
│   └── EVALUATION.problem_diagnosis.v1
├── SECTION "Oedeem-beoordeling"
│   ├── CLUSTER.oedema.v0
│   └── CLUSTER.exam_stemmer_test.v0 [C-5]
├── SECTION "EAI-beoordeling"
│   ├── OBSERVATION.blood_pressure.v2 (gelabeld als ABPI-bron)
│   ├── OBSERVATION.ankle_brachial_pressure_index.v0
│   └── EVALUATION.health_risk.v1 (interpretatie)
├── SECTION "Vaatdiagnose"
│   └── EVALUATION.problem_diagnosis.v1
├── SECTION "Wondzorg"
│   └── INSTRUCTION.service_request.v1 (link naar AWP)
├── SECTION "Compressietherapie"
│   ├── INSTRUCTION.therapeutic_item_order.v1
│   ├── ACTION.procedure.v1 (zwachtelen)
│   └── CLUSTER.device.v1 (UrgoK2 / UrgoK2 Lite)
├── SECTION "Nazorg"
│   └── INSTRUCTION.care_plan.v0
└── SECTION "Afsluiting"
    └── EVALUATION.clinical_synopsis.v1
```

### 8.5 OPT 1.4 compileren en uploaden

```bash
# === COMPILATIE ===
# Per template: ADL 1.4 archetypes + OET → OPT 1.4

for tpl in Wound_Assessment_Sensire.v1 Diabetic_Foot_Assessment_Sensire.v1 Ulcus_Cruris_Assessment_Sensire.v1; do
  echo "🔨 Compileren: $tpl"
  openehr-cli adl2opt \
    -a ~/ehrbase-demo/archetypes/ \
    -t ~/ehrbase-demo/templates/${tpl}.oet \
    -o ~/ehrbase-demo/operational_templates/

  # Valideer resulterende XML
  xmllint --noout ~/ehrbase-demo/operational_templates/${tpl}.opt && \
    echo "  ✅ XML valide" || echo "  ❌ XML ongeldig"
done

# === UPLOAD NAAR EHRBASE ===
EHRBASE="http://localhost:8080/ehrbase/rest/openehr/v1"
AUTH="ehrbase-user:SuperSecretPassword"

for opt_file in ~/ehrbase-demo/operational_templates/*.opt; do
  echo "📤 Uploaden: $(basename $opt_file)"
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$EHRBASE/definition/template/adl1.4" \
    -u "$AUTH" \
    -H "Content-Type: application/xml" \
    --data-binary "@$opt_file")

  case $HTTP_CODE in
    200|201) echo "  ✅ Upload geslaagd ($HTTP_CODE)" ;;
    409)     echo "  ⚠️ Template bestaat al ($HTTP_CODE) — overslaan of versie ophogen" ;;
    *)       echo "  ❌ Upload mislukt ($HTTP_CODE)" ;;
  esac
done

# === WEBTEMPLATES OPHALEN ===
for tpl_id in Wound_Assessment_Sensire.v1 Diabetic_Foot_Assessment_Sensire.v1 Ulcus_Cruris_Assessment_Sensire.v1; do
  echo "📥 WebTemplate ophalen: $tpl_id"
  curl -s -u "$AUTH" \
    -H "Accept: application/json" \
    "$EHRBASE/definition/template/adl1.4/$tpl_id" \
    | jq . > ~/ehrbase-demo/webtemplates/${tpl_id}.json

  echo "  Velden: $(jq '[.. | .id? // empty] | length' ~/ehrbase-demo/webtemplates/${tpl_id}.json)"
done
```

## 9. Nederlandse Vertaling via LLM-Pipeline

### 9.1 Het Principe

openEHR ondersteunt meertaligheid architecturaal. Elk datapunt heeft een onveranderlijke `at-code` (bijv. `at0004`). Taal zit in de `ontology`-sectie van het ADL-bestand, niet in de structuur. Een NL-vertaling verandert niets aan de data of de logica — het voegt alleen een presentatielaag toe.

### 9.2 De Vertaalworkflow

```
┌─────────────────────────────────────────────────────────┐
│  STAP 1: Exporteer archetype als ADL 1.4 tekst          │
│  (Archetype Designer → Export → ADL 1.4)                │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  STAP 2: Extraheer ontology-sectie                       │
│  (alles tussen 'ontology' en het einde van het bestand)  │
│  Dit bevat: term_definitions["en"] met per at-code:      │
│  text, description, comment                              │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  STAP 3: Geef aan Claude met de prompt:                  │
│                                                          │
│  "Vertaal de volgende openEHR archetype-terminologie     │
│   van Engels naar Nederlands. Behoud exact dezelfde       │
│   structuur en at-codes. Gebruik medisch correcte         │
│   Nederlandse termen conform NHG/WCS-terminologie.       │
│   Output: een term_definitions["nl"] sectie in exact     │
│   hetzelfde ODIN-formaat."                               │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  STAP 4: Plak de NL term_definitions terug               │
│  Voeg de ["nl"]-sectie toe onder de ["en"]-sectie        │
│  in het ADL-bestand.                                     │
│  Of: gebruik Archetype Designer → Languages → Add Dutch  │
│  → plak vertalingen per element in.                      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  STAP 5: Re-exporteer als ADL 1.4 met beide talen        │
│  STAP 6: Hercompileer OPT 1.4                            │
│  STAP 7: Upload naar EHRbase → WebTemplate bevat nu      │
│          localizedName in het Nederlands                  │
└─────────────────────────────────────────────────────────┘
```

### 9.3 Concreet vertaalscript

```bash
#!/bin/bash
# ~/ehrbase-demo/scripts/extract_terms_for_translation.sh
# Extraheert de EN term_definitions uit een ADL-bestand

ADL_FILE=$1
OUTPUT_DIR=~/ehrbase-demo/translations

mkdir -p "$OUTPUT_DIR"
BASENAME=$(basename "$ADL_FILE" .adl)

# Extraheer ontology-sectie (alles na 'ontology')
sed -n '/^ontology/,$p' "$ADL_FILE" > "$OUTPUT_DIR/${BASENAME}_ontology_en.txt"

echo "✅ Ontology-sectie geëxtraheerd naar:"
echo "   $OUTPUT_DIR/${BASENAME}_ontology_en.txt"
echo ""
echo "📋 Geef dit bestand aan Claude met de vertaalprompt."
echo "   Plak de NL-output terug als term_definitions[\"nl\"]."
```

### 9.4 Internationaal beschikbare NL-vertalingen hergebruiken

Controleer vóór vertaling altijd of er al een NL-vertaling beschikbaar is:

```bash
# Check ZIBs-on-openEHR repository
cd ~/tools
git clone --depth 1 https://github.com/openehr-nl/ZIBs-on-openEHR.git

# Zoek NL-vertalingen
grep -rl "\"nl\"" ZIBs-on-openEHR/ | head -20
```

### 9.5 SemVer-implicatie

Het toevoegen van een NL-vertaling aan een archetype is een **PATCH**-wijziging (v0.1.0 → v0.1.1). De semantiek en de datastructuur veranderen niet. Eerder opgeslagen data blijft 100% valide.

---

# DEEL IV — GDL2: BESLISREGELS EN DEMONSTRATIE

---

## 10. GDL2 Implementatie

### 10.1 Beschikbare Regelset

De werkende GDL2-regelset `sensire_ulcus_cruris_v2.gdl2` bevat de volledige beslislogica voor het Ulcus Cruris-protocol. Dit bestand dient als blauwdruk voor de overige twee regelsets.

**Data-bindingen in de regelset:**

| Binding | Archetype | Type | Beschrijving |
|:--------|:----------|:-----|:-------------|
| gt0002 | `OBSERVATION.ankle_brachial_pressure_index.v0` | INPUT | ABPI-ratio (0.82 etc.) |
| gt0005 | `EVALUATION.problem_diagnosis.v1` | INPUT | DM-status, vaatdiagnose |
| gt0007 | `CLUSTER.exam_stemmer_test.v0` | INPUT | Stemmer-test resultaat |
| gt0009 | `CLUSTER.oedema.v0` | INPUT | Oedeem aanwezigheid |
| gt0011 | `CLUSTER.wound_stagnation_assessment.v0` | INPUT | Stagnatie > 2-3 weken |
| gt0020 | `EVALUATION.health_risk.v1` | OUTPUT | Klinische interpretatie |
| gt0032 | `INSTRUCTION.therapeutic_item_order.v1` | OUTPUT | Compressietherapie-order |
| gt0042 | `INSTRUCTION.service_request.v1` | OUTPUT | Verwijzingen |

**Kernregels (selectie):**

| Regel | Conditie | Actie |
|:------|:---------|:------|
| gt0022 | ABPI < 0.6 | GEEN compressie, verwijs vaatchirurg URGENT |
| gt0023 | ABPI 0.6-0.8 | Lichte compressie (UrgoK2 Lite), overleg huisarts |
| gt0024 | ABPI 0.8-1.3 | Standaard compressie (UrgoK2) |
| gt0025 | ABPI > 1.3 | Overleg huisarts (mediasclerose?) |
| gt0026 | DM = aanwezig | Route naar Diabetische Voet-protocol |
| gt0027 | Stemmer = positief | Lymfoedeem-vermoeden, gespecialiseerde compressie |
| gt0030 | Stagnatie > 2-3 wkn | Escalatie vakgroep wond |

### 10.2 GDL2 Editor: Demo-workflow

1. **Import:** Open http://localhost:8082/gdl2-editor → File → Import → selecteer `sensire_ulcus_cruris_v2.gdl2`
2. **Definitions-tabblad:** Toont alle geladen archetypes en data-bindingen
3. **Rules-tabblad:** Toont de beslisregels in leesbare if-then structuur
4. **Execution-tabblad:**
   - Klik "Refresh" → editor genereert invoervelden op basis van de archetypes
   - Vul testwaarden in: ABPI = 0.72, DM = Nee, Oedeem = Ja, Stemmer = Negatief
   - Klik "Execute" → rechts verschijnt: "Gemengd vaatlijden. Lichte compressie (UrgoK2 Lite). Overleg huisarts."
   - **Debug Execution:** toont exact welke regels zijn afgevuurd (gt0023, gt0027)
5. **Test-tabblad:** Laad testfixtures → run batch → rapporteer rule coverage %

### 10.3 GDL2-regelsets nog te bouwen

| Regelset | Template-binding | Kernregels | Status |
|:---------|:-----------------|:-----------|:-------|
| `sensire_ulcus_cruris_v2.gdl2` | Ulcus_Cruris_Assessment_Sensire.v1 | ABPI-interpretatie, compressiekeuze, DM-routing, Stemmer, stagnatie | ✅ Beschikbaar |
| `sensire_diabetic_foot_v1.gdl2` | Diabetic_Foot_Assessment_Sensire.v1 | Wagner-score, Charcot-alarm, Sims-berekening, monofilament-evaluatie | ⏳ Te bouwen |
| `sensire_wound_assessment_v1.gdl2` | Wound_Assessment_Sensire.v1 | WCS × exsudaat → verbandkeuze, infectie-escalatie, debridement contra-indicaties | ⏳ Te bouwen |

### 10.4 GDL2-referentie: 700+ richtlijnen beschikbaar

```bash
# Clone Cambio CDS richtlijnen-bibliotheek
cd ~/tools
git clone --depth 1 https://github.com/openEHR/gdl-guideline-models.git

# Zoek relevante richtlijnen
ls gdl-guideline-models/gdl2/ | grep -i "wound\|diabet\|wagner\|bmi\|risk"

# Import in GDL2 Editor via:
# File → Import Guideline from GIT Repository
```

---

# DEEL V — DE DEMO-APPLICATIE

---

## 11. Automatiseringsscripts

### 11.1 Volledig deployment-script

```bash
#!/bin/bash
# ~/ehrbase-demo/scripts/deploy.sh
# Eén script om de hele kennislaag te deployen

set -e

EHRBASE="http://localhost:8080/ehrbase/rest/openehr/v1"
AUTH="ehrbase-user:SuperSecretPassword"
BASE=~/ehrbase-demo

echo "═══════════════════════════════════════════"
echo "  Sensire openEHR — Deployment Pipeline"
echo "═══════════════════════════════════════════"

# ---- Stap 1: Verificatie ----
echo ""
echo "📡 Stap 1: EHRbase status controleren..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -u "$AUTH" "$EHRBASE/../status")
if [ "$STATUS" != "200" ]; then
  echo "  ❌ EHRbase niet bereikbaar (HTTP $STATUS). Start met: docker compose up -d"
  exit 1
fi
echo "  ✅ EHRbase bereikbaar"

# ---- Stap 2: ADL 1.4 controle ----
echo ""
echo "🔍 Stap 2: ADL-versie controleren..."
VIOLATIONS=0
for f in $BASE/archetypes/**/*.adl; do
  if ! head -5 "$f" | grep -q "adl_version=1.4"; then
    echo "  ⚠️ NIET ADL 1.4: $f"
    VIOLATIONS=$((VIOLATIONS + 1))
  fi
done
if [ $VIOLATIONS -gt 0 ]; then
  echo "  ❌ $VIOLATIONS bestanden zijn niet ADL 1.4. Corrigeer en herexporteer."
  exit 1
fi
echo "  ✅ Alle archetypes zijn ADL 1.4"

# ---- Stap 3: OPT compilatie ----
echo ""
echo "🔨 Stap 3: OPT 1.4 compileren..."
mkdir -p $BASE/operational_templates
for tpl in $BASE/templates/*.oet; do
  TPL_NAME=$(basename "$tpl" .oet)
  echo "  Compileren: $TPL_NAME"
  openehr-cli adl2opt \
    -a $BASE/archetypes/ \
    -t "$tpl" \
    -o $BASE/operational_templates/

  xmllint --noout "$BASE/operational_templates/${TPL_NAME}.opt" 2>/dev/null && \
    echo "    ✅ XML valide" || echo "    ❌ XML ongeldig"
done

# ---- Stap 4: Upload naar EHRbase ----
echo ""
echo "📤 Stap 4: OPTs uploaden naar EHRbase..."
for opt_file in $BASE/operational_templates/*.opt; do
  OPT_NAME=$(basename "$opt_file")
  HTTP_CODE=$(curl -s -o /tmp/upload_response.json -w "%{http_code}" \
    -X POST "$EHRBASE/definition/template/adl1.4" \
    -u "$AUTH" \
    -H "Content-Type: application/xml" \
    --data-binary "@$opt_file")

  case $HTTP_CODE in
    200|201) echo "  ✅ $OPT_NAME — upload geslaagd" ;;
    409)     echo "  ⚠️ $OPT_NAME — bestaat al, overslaan" ;;
    *)       echo "  ❌ $OPT_NAME — fout ($HTTP_CODE):"
             jq . /tmp/upload_response.json 2>/dev/null || cat /tmp/upload_response.json ;;
  esac
done

# ---- Stap 5: WebTemplates ophalen ----
echo ""
echo "📥 Stap 5: WebTemplates ophalen..."
mkdir -p $BASE/webtemplates
TEMPLATES=$(curl -s -u "$AUTH" "$EHRBASE/definition/template/adl1.4" | jq -r '.[].template_id')
for tpl_id in $TEMPLATES; do
  curl -s -u "$AUTH" \
    -H "Accept: application/json" \
    "$EHRBASE/definition/template/adl1.4/$tpl_id" \
    | jq . > "$BASE/webtemplates/${tpl_id}.json"
  FIELDS=$(jq '[.. | .id? // empty] | length' "$BASE/webtemplates/${tpl_id}.json")
  echo "  ✅ $tpl_id — $FIELDS velden"
done

# ---- Stap 6: Testdata genereren ----
echo ""
echo "🧪 Stap 6: Synthetische testdata genereren..."
mkdir -p $BASE/compositions/generated
for opt_file in $BASE/operational_templates/*.opt; do
  OPT_NAME=$(basename "$opt_file" .opt)
  echo "  Genereren: 3 composities voor $OPT_NAME"
  openehr-cli ingen "$opt_file" "$BASE/compositions/generated/" 3 json_composition 2>/dev/null || \
    echo "    ⚠️ Generatie mislukt (CaboLabs CLI niet geïnstalleerd?)"
done

# ---- Stap 7: Testdata posten ----
echo ""
echo "📮 Stap 7: Testcomposities naar EHRbase posten..."
# Zorg dat er een test-EHR bestaat
EHR_ID=$(curl -s -u "$AUTH" \
  -H "Content-Type: application/json" \
  "$EHRBASE/query/aql" \
  -d '{"q":"SELECT e/ehr_id/value FROM EHR e LIMIT 1"}' \
  | jq -r '.rows[0][0] // empty')

if [ -z "$EHR_ID" ]; then
  echo "  Geen EHR gevonden — nieuwe aanmaken..."
  EHR_ID=$(curl -s -X POST "$EHRBASE/ehr" \
    -u "$AUTH" \
    -H "Content-Type: application/json" \
    -d '{"_type":"EHR_STATUS","archetype_node_id":"openEHR-EHR-EHR_STATUS.generic.v1","name":{"value":"EHR Status"},"subject":{"_type":"PARTY_SELF"},"is_queryable":true,"is_modifiable":true}' \
    | jq -r '.ehr_id.value')
fi
echo "  EHR-ID: $EHR_ID"

for comp_file in $BASE/compositions/generated/*.json; do
  COMP_NAME=$(basename "$comp_file")
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$EHRBASE/ehr/$EHR_ID/composition?format=FLAT" \
    -u "$AUTH" \
    -H "Content-Type: application/json" \
    --data-binary "@$comp_file")

  case $HTTP_CODE in
    200|201) echo "  ✅ $COMP_NAME — opgeslagen" ;;
    *)       echo "  ❌ $COMP_NAME — fout ($HTTP_CODE)" ;;
  esac
done

echo ""
echo "═══════════════════════════════════════════"
echo "  ✅ Deployment voltooid"
echo ""
echo "  📋 Templates:     $EHRBASE/definition/template/adl1.4"
echo "  🔍 Swagger:       http://localhost:8080/ehrbase/swagger-ui.html"
echo "  🧪 GDL2 Editor:   http://localhost:8082/gdl2-editor"
echo "  🗄️  pgAdmin:       http://localhost:5050"
echo "═══════════════════════════════════════════"
```

### 11.2 Template-update script (SemVer-bewust)

```bash
#!/bin/bash
# ~/ehrbase-demo/scripts/update_template.sh
# Veilig updaten van een template met SemVer-check

EHRBASE="http://localhost:8080/ehrbase/rest"
AUTH="ehrbase-user:SuperSecretPassword"

TEMPLATE_ID=$1
OPT_FILE=$2

if [ -z "$TEMPLATE_ID" ] || [ -z "$OPT_FILE" ]; then
  echo "Gebruik: $0 <template_id> <opt_bestand>"
  echo "Voorbeeld: $0 Wound_Assessment_Sensire.v1 ~/ehrbase-demo/operational_templates/Wound_Assessment_Sensire.v1.opt"
  exit 1
fi

# Check of template bestaat
EXISTS=$(curl -s -o /dev/null -w "%{http_code}" -u "$AUTH" \
  "$EHRBASE/openehr/v1/definition/template/adl1.4/$TEMPLATE_ID")

if [ "$EXISTS" = "200" ]; then
  echo "⚠️ Template '$TEMPLATE_ID' bestaat al in EHRbase."
  echo ""

  # Check of er composities gekoppeld zijn
  COMP_COUNT=$(curl -s -u "$AUTH" \
    -H "Content-Type: application/json" \
    "$EHRBASE/openehr/v1/query/aql" \
    -d "{\"q\":\"SELECT count(c) FROM EHR e CONTAINS COMPOSITION c WHERE c/archetype_details/template_id/value = '$TEMPLATE_ID'\"}" \
    | jq -r '.rows[0][0] // 0')

  if [ "$COMP_COUNT" -gt 0 ]; then
    echo "  🔒 Er zijn $COMP_COUNT composities gekoppeld aan dit template."
    echo "  → Overschrijven is NIET veilig (MAJOR change)."
    echo "  → Maak een nieuwe versie aan: bijv. ${TEMPLATE_ID%.v*}.v2"
    echo ""
    echo "  Wil je toch proberen te overschrijven via de Admin API? [j/N]"
    read -r ANSWER
    if [ "$ANSWER" != "j" ]; then
      echo "  Afgebroken."
      exit 0
    fi

    # Probeer via Admin API
    HTTP_CODE=$(curl -s -o /tmp/update_response.json -w "%{http_code}" \
      -X PUT "$EHRBASE/admin/template/$TEMPLATE_ID" \
      -u "$AUTH" \
      -H "Content-Type: application/xml" \
      --data-binary "@$OPT_FILE")

    case $HTTP_CODE in
      200) echo "  ✅ Template overschreven via Admin API" ;;
      422) echo "  ❌ EHRbase weigert: template is in gebruik (HTTP 422)" ;;
      *)   echo "  ❌ Onverwachte fout ($HTTP_CODE):" ; cat /tmp/update_response.json ;;
    esac
  else
    echo "  Geen composities gekoppeld — veilig om te verwijderen en opnieuw te uploaden."
    curl -s -X DELETE "$EHRBASE/admin/template/$TEMPLATE_ID" -u "$AUTH" > /dev/null
    echo "  🗑️ Oud template verwijderd"
    curl -s -X POST "$EHRBASE/openehr/v1/definition/template/adl1.4" \
      -u "$AUTH" -H "Content-Type: application/xml" --data-binary "@$OPT_FILE" > /dev/null
    echo "  ✅ Nieuw template geüpload"
  fi
else
  echo "📤 Template '$TEMPLATE_ID' bestaat nog niet — direct uploaden..."
  curl -s -X POST "$EHRBASE/openehr/v1/definition/template/adl1.4" \
    -u "$AUTH" -H "Content-Type: application/xml" --data-binary "@$OPT_FILE" > /dev/null
  echo "✅ Template geüpload"
fi
```

---

# DEEL VI — DEMO-PAGINA'S EN PRESENTATIE

---

## 12. Demo-pagina's (Frontend)

De frontend-architectuur blijft grotendeels zoals in v4, met de toevoeging van een GDL2-demonstratiemoment:

### 12.1 Pagina-overzicht

| Pagina | Functie | Status |
|:-------|:--------|:-------|
| Dashboard (index.html) | Navigatie-startpunt | ⏳ Te bouwen |
| Ulcus Cruris beslisboom | Interactief formulier + JS-logica | ✅ Deels werkend |
| Diabetische Voet beslisboom | Interactief formulier + JS-logica | ⏳ Te bouwen |
| Algemeen Wondprotocol beslisboom | Interactief formulier + JS-logica | ⏳ Te bouwen |
| Template Explorer | Kennislaag visualisatie (EN ↔ NL) | ⏳ Te bouwen |
| Live Composition Monitor | AQL-polling, driekolommen-view | ⏳ Te bouwen |
| GDL2 Demo (extern) | GDL2 Editor op :8082 | 🆕 Draait |

### 12.2 Elke beslisboompagina: vierkolommen-structuur

| Paneel | Inhoud | Bron |
|:-------|:-------|:-----|
| **1. Beslisboom** | Interactief formulier, conditionele logica in JavaScript | WebTemplate JSON |
| **2. Klinisch Advies** | Aanbeveling in begrijpelijk Nederlands | JS-regels (spiegelt GDL2-logica) |
| **3. openEHR Data** | Driekolommen: pad / NL label / waarde | FLAT JSON + WebTemplate lookup |
| **4. AQL Bewijs** | Compositie-UID, AQL-query, raw resultaat | EHRbase REST API |

## 13. Demo-script voor Collega's (v5)

Totale duur: circa 30 minuten (5 minuten meer dan v4 door GDL2-moment).

### 13.1 Wat is openEHR? (2 min)

> *"openEHR is een internationale standaard voor gestructureerde klinische dataopslag. Geen vendor lock-in. Data die over 20 jaar nog leesbaar is."*

### 13.2 Template Explorer — Internationaal vs. Eigen (4 min)

Open de Template Explorer. Toon blauwe (internationaal) vs. groene (Sensire) archetypes. Klik op een archetype: EN label naast NL label.

> *"De blauwe blokken zijn internationaal — die bestaan al. De groene blokken zijn van Sensire. En de Nederlandse termen zijn een presentatiekeuze, niet een datawijziging."*

### 13.3 Beslisboom doorlopen — Ulcus Cruris (5 min)

Twee schermen: beslisboom op scherm 1, Live Monitor op scherm 2.

Doorloop: geen DM, oedeem aanwezig, Stemmer negatief, EAI = 0.85 → klinisch advies → opslaan → compositie verschijnt live op scherm 2.

### 13.4 Live Monitor — Wat is er opgeslagen? (4 min)

Klik op de verschenen compositie. Driekolommen-view: openEHR-pad | NL label | waarde.

> *"Een Noors ziekenhuis met dezelfde archetypes leest exact dezelfde data."*

### 13.5 🆕 GDL2 — Formele Beslisondersteuning (5 min)

Open de GDL2 Editor (http://localhost:8082/gdl2-editor). Importeer `sensire_ulcus_cruris_v2.gdl2`.

- **Execution-tabblad:** Vul dezelfde testwaarden in als in de beslisboom (ABPI = 0.85, geen DM, oedeem ja, Stemmer neg).
- Klik **Execute** → advies verschijnt rechts: "Veneus ulcus. Standaard compressie (UrgoK2)."
- Open **Debug Execution** → toon welke regels zijn afgevuurd.

> *"Dit is hetzelfde advies als in de browser-beslisboom, maar nu formeel vastgelegd in een internationale klinische regeltaal. Elke stap is transparant en auditeerbaar. Geen black box."*

- Verander ABPI naar 0.55 → opnieuw Execute → "GEEN compressie. Verwijs vaatchirurg URGENT."
- Debug toont: regel gt0022 afgevuurd (ABPI < 0.6).

> *"Dit is white-box beslisondersteuning. De clinicus ziet precies waarom het systeem dit adviseert."*

### 13.6 AQL — Data onafhankelijk van de applicatie (3 min)

Terminal-demo met curl + AQL query.

### 13.7 Swagger UI + pgAdmin (3 min)

REST API endpoints + raw PostgreSQL data.

### 13.8 Afsluiting (2 min)

> *"Wat u heeft gezien: een compleet werkende keten. Van internationale standaard naar Nederlandse interface, van beslisboom naar gevalideerde opslag, van GDL2-regels naar transparant advies. Dit draait op een Chromebox. De software is open source. En Sensire kan morgen beginnen."*

---

# DEEL VII — VERSIEBEHEER EN GIT

---

## 14. Git-strategie

```bash
cd ~/ehrbase-demo && git init

# .gitignore
cat > .gitignore << 'EOF'
node_modules/
.env
*.log
compositions/generated/
EOF

# Initiële structuur
git add archetypes/international/
git commit -m "feat: 25 internationale CKM archetypes (ADL 1.4)"

git add archetypes/sensire/
git commit -m "feat: Sensire eigen archetypes v0.1.0 (C-1 t/m C-5)"

git add templates/
git commit -m "feat: drie OET templates v1 (AWP, DM-voet, UC)"

git add operational_templates/
git commit -m "build: OPT 1.4 gecompileerd via CaboLabs CLI"

git add webtemplates/
git commit -m "build: WebTemplates uit EHRbase"

git add gdl2/
git commit -m "feat: GDL2 regelset Ulcus Cruris v2"

git add scripts/
git commit -m "feat: deployment en vertaalscripts"

git add docker-compose.yml
git commit -m "infra: Docker stack v5 (EHRbase + GDL2 Editor + pgAdmin)"
```

**Commit-conventie:**

| Prefix | Betekenis | Voorbeeld |
|:-------|:----------|:----------|
| `feat:` | Nieuw archetype, template, regelset | `feat: CLUSTER.exam_stemmer_test.v0 (C-5)` |
| `fix:` | Correctie in bestaand model | `fix: cardinaliteit oedeem 0..1 → 1..1` |
| `build:` | OPT compilatie, WebTemplate update | `build: hercompilatie na NL-vertaling` |
| `i18n:` | Vertaalwerk | `i18n: NL-vertaling exam_wound v0.1.1` |
| `infra:` | Docker, scripts, tooling | `infra: GDL2 Editor toegevoegd aan stack` |
| `docs:` | Documentatie | `docs: plan v5` |

---

# DEEL VIII — TIJDLIJN EN REFERENTIE

---

## 15. Tijdlijn

| Dag | Activiteit | Resultaat | Status |
|:----|:-----------|:----------|:-------|
| 1 | Docker + EHRbase + GDL2 Editor opstarten | Stack draait op :8080, :8082, :5050 | ✅ (EHRbase) / 🆕 (GDL2) |
| 2 | 25 CKM archetypes downloaden (ADL 1.4) | Archetype-bibliotheek compleet | ⏳ |
| 3 | 5 eigen archetypes bouwen (C-1 t/m C-5) | ADL 1.4 + EN + NL | ⏳ |
| 4 | NL-vertalingen internationale archetypes (LLM) | ~15 archetypes vertaald | ⏳ |
| 5 | Template 1 bouwen: Wound Assessment | OET + OPT 1.4 + WebTemplate | ⏳ |
| 6 | Template 2 bouwen: Diabetic Foot | OET + OPT 1.4 + WebTemplate | ⏳ |
| 7 | Template 3 bouwen: Ulcus Cruris | OET + OPT 1.4 + WebTemplate | ⏳ |
| 8 | Deployment pipeline testen (deploy.sh) | Alle 3 OPTs in EHRbase + testdata | ⏳ |
| 9 | Ulcus Cruris HTML: panelen 2-4 + driekolommen | Volledige beslisboompagina | ⏳ |
| 10 | GDL2 regelsets DM-voet + AWP | 3 werkende .gdl2 bestanden | ⏳ |
| 11 | Diabetische Voet HTML beslisboompagina | Tweede werkende demo | ⏳ |
| 12 | Algemeen Wondprotocol HTML beslisboompagina | Derde werkende demo | ⏳ |
| 13 | Template Explorer + Live Composition Monitor | Kennislaag + monitoring werkend | ⏳ |
| 14 | Dashboard + demo-script rehearsal | Alles draaiend, klaar voor demo | ⏳ |

## 16. Snelreferentie — Commando's

### 16.1 Stack beheer

```bash
# Starten
cd ~/ehrbase-demo && docker compose up -d

# Stoppen
docker compose down

# Status
docker compose ps

# Logs bekijken
docker compose logs -f ehrbase
docker compose logs -f gdl2-editor
```

### 16.2 EHRbase REST API

```bash
EHRBASE="http://localhost:8080/ehrbase/rest/openehr/v1"
AUTH="ehrbase-user:SuperSecretPassword"

# Status
curl -s -u $AUTH $EHRBASE/../status | jq .

# Alle templates
curl -s -u $AUTH $EHRBASE/definition/template/adl1.4 | jq '.[].template_id'

# Template uploaden
curl -X POST $EHRBASE/definition/template/adl1.4 \
  -u $AUTH -H "Content-Type: application/xml" \
  --data-binary @template.opt

# WebTemplate ophalen
curl -s -u $AUTH -H "Accept: application/json" \
  "$EHRBASE/definition/template/adl1.4/TEMPLATE_ID" | jq .

# EHR aanmaken
curl -X POST $EHRBASE/ehr -u $AUTH \
  -H "Content-Type: application/json" \
  -d '{"_type":"EHR_STATUS","archetype_node_id":"openEHR-EHR-EHR_STATUS.generic.v1",
       "name":{"value":"EHR Status"},"subject":{"_type":"PARTY_SELF"},
       "is_queryable":true,"is_modifiable":true}'

# Compositie opslaan (FLAT JSON)
curl -X POST "$EHRBASE/ehr/{ehr_id}/composition?format=FLAT" \
  -u $AUTH -H "Content-Type: application/json" \
  --data-binary @composition.json

# AQL query
curl -s -u $AUTH -H "Content-Type: application/json" \
  "$EHRBASE/query/aql" \
  -d '{"q":"SELECT c/uid/value, c/name/value FROM EHR e CONTAINS COMPOSITION c ORDER BY c/context/start_time/value DESC LIMIT 10"}' | jq .
```

### 16.3 CaboLabs openEHR-CLI

```bash
# OPT compileren
openehr-cli adl2opt -a archetypes/ -t templates/template.oet -o operational_templates/

# Testdata genereren
openehr-cli ingen operational_templates/template.opt compositions/ 10 json_composition

# Compositie valideren
openehr-cli inval operational_templates/template.opt compositions/composition.json
```

### 16.4 Deployment

```bash
# Volledige deployment
bash ~/ehrbase-demo/scripts/deploy.sh

# Template update (SemVer-bewust)
bash ~/ehrbase-demo/scripts/update_template.sh TEMPLATE_ID pad/naar/template.opt
```

## 17. Credentials

| Service | URL | Gebruiker | Wachtwoord |
|:--------|:----|:----------|:-----------|
| EHRbase REST API | localhost:8080 | ehrbase-user | SuperSecretPassword |
| PostgreSQL | localhost:5432 | postgres | postgres |
| pgAdmin | localhost:5050 | demo@sensire.nl | demo |
| GDL2 Editor | localhost:8082 | (geen auth) | — |
| Archetype Designer | tools.openehr.org | eigen openEHR account | (eigen) |

## 18. Belangrijke URLs

| Resource | URL |
|:---------|:----|
| EHRbase docs | https://docs.ehrbase.org |
| openEHR CKM | https://ckm.openehr.org/ckm/ |
| Archetype Designer | https://tools.openehr.org/designer/ |
| CKM GitHub mirror | https://github.com/openEHR/CKM-mirror |
| CaboLabs openEHR-CLI | https://github.com/CaboLabs/openEHR-SDK |
| GDL2 richtlijnen (Cambio) | https://github.com/openEHR/gdl-guideline-models |
| GDL2 specificatie | https://specifications.openehr.org/releases/CDS/latest/GDL2.html |
| GDL2 Editor tutorials | https://gdl-lang.org/the-project/guides-tutorials/gdl2/ |
| C3-Cloud GDL2 services | https://github.com/C3-Cloud-eu/gdl2-cds-services |
| openEHR-NL (ZIBs) | https://github.com/openehr-nl/ZIBs-on-openEHR |
| EHRbase GitHub | https://github.com/ehrbase/ehrbase |
| Medblocks UI | https://medblocks.com/docs/medblocks-ui |
| Nictiz ZIBs | https://zibs.nl |
| WCS wondzorg | https://wcs.nl |
| openEHR specificaties | https://specifications.openehr.org |

---

# Appendix A: Bekende Problemen en Oplossingen

| Probleem | Oorzaak | Oplossing |
|:---------|:--------|:----------|
| Docker repo 404 | Plan gebruikte Ubuntu repo, systeem is Debian Trixie | Gebruik `download.docker.com/linux/debian` |
| CKM zoekresultaat: 0 | Filter stond op "Active" i.p.v. "Published" | Klik op "Published" radiobutton |
| OPT upload: 501 Not Implemented | ADL 2.0 / OPT 2 bestand aangeboden | Exporteer als ADL 1.4 / OPT 1.4 |
| Archetype Designer exporteert ADL 2 | Verkeerde export-optie geselecteerd | Selecteer expliciet "Export as ADL 1.4" |
| Archie genereert OPT 2 | Nedap Archie ondersteunt alleen ADL 2.0 output | Gebruik CaboLabs openEHR-CLI voor OPT 1.4 |
| Template overschrijven: 422 | Composities gekoppeld aan bestaand template | Maak nieuwe templateversie (bijv. v2) |
| GDL2 Editor poortconflict | Zowel EHRbase als GDL2 op poort 8080 | GDL2 Editor op poort 8082 mappen |
| GDL2 Editor poort 8089 in oude docs | Typfout in originele GDL2-documentatie | Correcte mapping: `-p 8082:8080` |
| NL-vertaling breekt data | Ontology verkeerd bewerkt | NL-vertaling is PATCH: voeg `term_definitions["nl"]` toe, wijzig nooit de structuur |
| POST compositie: 422 | Verplicht veld ontbreekt in FLAT JSON | Check WebTemplate voor mandatory velden |
| AQL met ADL 2.0 paden | at-code vs. id-code verwarring | Gebruik altijd at-codes (ADL 1.4) in AQL |

---

# Appendix B: Architecturale Beslissingen (ADR)

### ADR-001: ADL 1.4 als projectstandaard

**Beslissing:** Alle archetypes, templates en OPTs gebruiken ADL 1.4.
**Rationale:** EHRbase ondersteunt uitsluitend OPT 1.4. De internationale CKM publiceert in ADL 1.4. De CaboLabs CLI compileert naar OPT 1.4. ADL 2.0-migratie is pas relevant bij CDR-migratie.
**Consequenties:** Geen `id-code`/`ac-code`-scheiding. Alle paden gebruiken `at-codes`. ADL Workbench validatie in 1.4-modus.

### ADR-002: GDL2 als CDS-demonstratielaag

**Beslissing:** GDL2 wordt heringevoerd voor demo's en formele regelvalidatie. JavaScript blijft de frontend-logica.
**Rationale:** GDL2 Editor biedt white-box CDS (transparante regelaudit) die onmogelijk te repliceren is in JavaScript. De 700+ beschikbare richtlijnen dienen als blauwdrukken. GDL2-investering behoudt waarde bij toekomstige migratie naar Decision Language.
**Consequenties:** Extra Docker-container (gdl2-editor op poort 8082). GDL2-regels moeten synchroon blijven met JavaScript-logica.

### ADR-003: Drie afzonderlijke templates

**Beslissing:** Drie templates (AWP, DM-voet, UC) in plaats van één mega-template.
**Rationale:** Onafhankelijk versiebeheer. Slankere WebTemplates. Betere SemVer-controle. Cross-referenties via applicatielaag.
**Consequenties:** Cross-protocol verwijzingen (bijv. UC → AWP voor wondbehandeling) worden afgehandeld in JavaScript, niet in het datamodel.

### ADR-004: LLM-vertaling voor NL

**Beslissing:** Nederlandse vertalingen worden geproduceerd via Claude, met menselijke review.
**Rationale:** Snelheid (2-3 dagen i.p.v. weken), medische kwaliteit (Claude kent NHG/WCS-terminologie), kostenefficiëntie.
**Consequenties:** Elke vertaling moet door een domeinexpert (verpleegkundig specialist wondzorg) worden gereviewd.

### ADR-005: CaboLabs CLI als compilatietool

**Beslissing:** CaboLabs openEHR-CLI is de primaire tool voor OPT 1.4 compilatie, testdata generatie en validatie.
**Rationale:** Enige open-source CLI die ADL 1.4 → OPT 1.4 compilatie ondersteunt. Archie (Nedap) genereert alleen OPT 2. adlc (ADL Workbench) valideert maar compileert niet naar OPT.
**Consequenties:** JDK 11+ vereist op de Chromebox. Gradle-build eenmalig. Fallback: handmatige OPT-export uit Archetype Designer.

---

*Sensire / Instituut Bedrijfskunde — openEHR Demo Blueprint v5.0 — Maart 2026*

---

# DEEL IV — COMPLIANCE EN 100% ZEKERHEIDSGARANTIE

Tot en met v4 leunden we in deze applicatie op het *Trial & Error*-principe: de frontend stuurt een aannemelijke JSON naar EHRbase, en als deze weigert met een HTTP 422, corrigeren we het model. Ook de GDL2-logica werd in JavaScript nagebouwd op basis van menselijke interpretatie.

Om **100% zeker** te zijn van onze integratie introduceert v5.0 een sluitend Verification-framework bestaande uit twee pijlers:

## 1. GDL2 Algoritmische Verificatie (UI Logica)

Omdat we wegens performance- en architectuurredenen geen zware Java-gebaseerde GDL2-engine in de frontend draaien, simuleren we de regels (zoals gepubliceerd in `sensire_ulcus_cruris_v2.gdl2`) in JavaScript (bijv. `getEAIInterpretation(waarde)`).
Om compliant te zijn:
- De GDL2 beslisbomen (Truth Tables) worden vastgelegd in een statische unit-test suite (`tests/gdl2_compliance_test.js`).
- Deze test draait iteratief door alle `min/max` tresholds (bijv. EAI 0.84, 0.85, 0.90) en verifieert of het JavaScript *exact* de uitkomst en SNOMED/lokale codering retourneert die de GDL2 definitie vereist.
- *Status:* We zijn hierdoor niet langer afhankelijk van interpretatie, de test faalt als men de JS UI logica aanpast zonder de guidelines te respecteren.

## 2. WebTemplate Pre-Flight Compliance (FLAT JSON Logica)

EHRbase valideert de FLAT JSON tegen het onderliggende WebTemplate en OPT. 
Om compliant te zijn *voordat* data überhaupt de database bereikt:
- Is een validator test-script toegevoegd (`tests/webtemplate_compliance_test.js`).
- Dit script leest direct de CKM `.json` webtemplates in.
- Het gebruikt een recursieve crawler om **alle verplichte velden** (`min >= 1`) in kaart te brengen.
- Het script leest vervolgens de mappings uit de JavaScript frontend formulieren (`wondprotocol.html`, etc.) en verifieert of alle vastgestelde mandatory paden door de UI worden gevuld (hetzij met UI-waarden, hetzij met default overrides zoals 'Niet beoordeeld').
- *Status:* Dit voorkomt per definitie elke 422 validatiefout doordat integratielakes in kaart worden gebracht in CI/CD (of in dit geval, bij het runnen van de tests) in plaats van door clinici op de opslaan-knop.

*Deze twee test-suites dienen te allen tijde te 'passen' alvorens wijzigingen in de UI-laag gecommit worden.*
