# Technische Presentatie: Sensire openEHR Ecosysteem & Runtime Architectuur

> **Doelgroep**: Enterprise Architecten, Solution Architecten, Lead Developers, Medisch Informatici (Architectuurboard)  
> **Auteur**: Sensire Digitale Innovatie & openEHR Werkgroep  
> **Status**: Definitief Architectuurvoorstel  

---

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        SENSIRE ENTERPRISE OPEN-EHR ECOSYSTEEM                          │
│                                                                                        │
│   [ 1. AUTEURSOMGEVING & REDACTIE ]       [ 2. KLINISCHE PRAKTIJK & DOSSIER ]          │
│   SensireSpecieleBeslisOndersteuning      Sensii Wijkverpleegkundig EPD                │
│   • 164 Zorgpaden (Mermaids / JSON)       • 58 Formulieren / Surveys                   │
│   • ReAble varianten                      • SFP Beslismotor / 8 Zorgfasen              │
│   • Actieve dagelijkse redactieworkflow   • Live Cliëntdossier & Omaha KBS             │
│                      │                                   │                             │
│                      │ (Klinische Inhoud)                │ (Surveys & Structuur)       │
│                      ▼                                   ▼                             │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ 3. DE SEMANTISCHE FABRIEK: OpenEHRDemo                                         │   │
│   │ • 730+ CKM & 7 Custom Nederlandse Archetypes (Gordon, GFI, Omaha, Regietrede)  │   │
│   │ • Archie Java Flattener & Python OPT 1.4 XML Postprocessing Pipeline           │   │
│   │ • 5-Staps Terminologiecascade (ZIB ➔ SNOMED CT NL ➔ openEHR ➔ V&VN ➔ Zorgpad) │   │
│   │ • 299 Gecompileerde & Gevalideerde OPT 1.4 XML Templates                       │   │
│   └──────────────────────────────────────┬─────────────────────────────────────────┘   │
│                                          │                                             │
│                   📦 CONTRACT-FIRST DATA DISTRIBUTIE                                   │
│                   (sensii_openehr_contract.json & carepaths_openehr_contract.json)     │
│                                          │                                             │
│                      ┌───────────────────┴───────────────────┐                         │
│                      ▼                                       ▼                         │
│   [ 4. IN-APP INSPECTOR & TWIN ]          [ 5. RUNTIME WRITE ENGINE NAAR CDR ]         │
│   • Live openEHR Inspector in Doorloop    • WebTemplate Parser (.wt.json)              │
│   • Lens 6: Blueprint & AQL Query Lab     • Form-Response ➔ FLAT JSON Mapper           │
│   • Zero runtime overhead in frontend     • EHRbase REST API (/ehr/{ehr_id}/composition│
│                                           • Audit, Versiebeheer & AQL Data Ontsluiting │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Executive Summary & Architectuurvisie

Sensire bouwt aan een **toekomstbestendig, leveranciersonafhankelijk gezondheidsplatform** conform de nationale NZa/VWS visie op databeschikbaarheid.

### De Drie Kernprincipes:
1. **Scheiding van Data en Applicatie**: Klinische data wordt opgeslagen in een gestandaardiseerd openEHR Clinical Data Repository (CDR / EHRbase), los van specifieke frontend-applicaties.
2. **Contract-First & Decoupled Lagenmodel**: De semantische modellering (archetypes, templates, terminologie) is strikt gescheiden van de applicatielogica en redactieworkflows.
3. **Zero-Burden voor de Zorgprofessional**: Zowel de wijkverpleegkundige als de zorgpadredacteur werkt in een intuïtieve, functionele interface; de openEHR-transformatie verloopt volledig geautomatiseerd op de achtergrond.

---

## 2. Deep Dive: Hoe werkt de Semantische Fabriek (`OpenEHRDemo`)?

`OpenEHRDemo` is het zenuwcentrum voor semantische interoperabiliteit. Het bevat geen applicatie-UI, maar fungeert als een **compiler- en validatiestraat**:

### A. De 7 Custom Archetypes voor de Nederlandse Wijkverpleging
Naast >730 internationale openEHR CKM archetypes zijn er 7 specifieke archetypes gemodelleerd en tweetalig (NL/EN) gecertificeerd:
1. `openEHR-EHR-OBSERVATION.groningen_frailty_indicator_nl.v0`: 15 items, 4 domeinen, somscore 0-15 en cutoff $\ge 4$.
2. `openEHR-EHR-OBSERVATION.self_management_regietrede_nl.v0`: 5 regietreden, motoradvies vs professional vs cliënt.
3. `openEHR-EHR-EVALUATION.omaha_assessment_nl.v0`: 42 aandachtsgebieden, 4 domeinen, 4 actiesoorten, 76 actievlakken en KBS-streefscores.
4. `openEHR-EHR-OBSERVATION.nursing_gordon_patterns_nl.v0`: 11 gezondheidspatronen van Gordon.
5. `openEHR-EHR-EVALUATION.triage_nursing_nl.v0`: Wijkverpleegkundige triage, passendheid en urgentie.
6. `openEHR-EHR-EVALUATION.nursing_vag_nl.v0`: Verpleegkundig adviesgesprek, eigen kracht en draagkracht.
7. `openEHR-EHR-ADMIN_ENTRY.care_funding_delivery_nl.v0`: Zvw/Wlz/Wmo indicaties en leveringsvormen (ZIN/PGB/VPT/MPT).

### B. De Compilatie- & Validatiepijplijn
```
[ Bron ADLT Templates ]
         │
         ▼
[ Nedap Archie Java Flattener ] (archetype slots expansie & RM validatie)
         │
         ▼
[ Python OPT 1.4 XML Postprocessor ] (full_opt14_lxml.py: namespace fix, type-injectie)
         │
         ▼
[ EHRbase 100% Conforme OPT 1.4 XML ] (299 gecompileerde bestanden in opts/)
```

### C. De 5-Staps Terminologiecascade
Geen enkel gegeven wordt ad-hoc gecodeerd. Er geldt een strikte cascade:
`1. Nictiz ZIBs` ➔ `2. SNOMED CT NL` ➔ `3. openEHR CKM` ➔ `4. V&VN / Omaha NL` ➔ `5. Zorgpad Fallback`.

---

## 3. Ingestion & Teruglevering: De Contract-First Interface

### Wat gaat er in? (Ingestion)
- **Uit `Sensii`**: De 58 formulieren (`contract/sections_sensii.json`) en het Omaha-model (`contract/omaha_v1.json`).
- **Uit `SensireSpecieleBeslisOndersteuning`**: De 164 zorgpad-definities (`4.Mermaids/*/v*_flow.json` + `ReAble/`).

### Wat levert `OpenEHRDemo` terug? (Contract Distributie)
`OpenEHRDemo` genereert via `scripts/sync_ecosystem.py --build` twee lichtgewicht, gevalideerde JSON-contracten:
1. [`sensii_openehr_contract.json`](file:///home/vlieger/Sensii/contract/sensii_openehr_contract.json):
   - Mapt alle 58 formulieren op specifieke archetypes, RM-typen (`OBSERVATION`, `EVALUATION`), en `at00xx` node-paden.
   - Bevat kant-en-klare AQL sample-queries per formulier.
   - Bevat triggers die Omaha-aandachtsgebieden koppelen aan speciële zorgpaden (bijv. *Huid ➔ Wondpaden*).
2. [`carepaths_openehr_contract.json`](file:///home/vlieger/SensireSpecieleBeslisOndersteuning/contract/carepaths_openehr_contract.json):
   - Overzicht van alle 164 zorgpaden (regulier & ReAble) met template-ID's en OPT bestandsgroottes.

> **Cruciaal Voordeel**: Noch `Sensii` noch `SensireSpecieleBeslisOndersteuning` hoeft Java, Gradle of zware openEHR tooling te draaien. Ze consumeren zuivere JSON.

---

## 4. Visualisatie & Inspectie: De Twee Perspectieven

### A. De Doorloop: Live openEHR Inspector & Data-Twin
In de doorloop (`sensii_doorloop.html`) kan de gebruiker schakelen tussen:
- **Klinisch Perspectief (Wijkverpleegkundige)**: Vriendelijke kaarten, Gordon patronen, KBS-meters, GFI-uitkomsten.
- **Technisch Perspectief (Architect / Developer)**: Live inspectie van het geactiveerde archetype, Reference Model pad, gegenereerde AQL query en de live FLAT JSON payload.

### B. De Meta-Visualisaties: Lens 6 (openEHR Blueprint & Query Lab)
In `sensii_visualisatie.html`:
- Overzicht van 100% dekkingsgraad over de 58 formulieren.
- Interactieve template-hiërarchie (Mermaid/D3).
- **AQL Query Lab**: Testen van query's direct tegen de openEHR informatiestructuur.

---

## 5. Runtime Roadmap: Wat is er nodig om écht naar EHRbase te schrijven?

Om de doorloop van Sensii en de zorgpaden live data te laten wegschrijven naar een draaiende **EHRbase CDR instance**, is de volgende 4-staps runtime-infrastructuur nodig:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                      RUNTIME WRITE PIPELINE NAAR EHRBASE CDR                           │
│                                                                                        │
│  [ 1. FRONTEND FORM STATE ]                                                            │
│  Wijkverpleegkundige rondt VAG of Omaha-beoordeling af in Sensii doorloop.             │
│  Payload: { "gfi_mobility": 1, "gfi_vision": 0, "omaha_area": "Huid", "kbs_status": 3 }│
│                            │                                                           │
│                            ▼                                                           │
│  [ 2. WEBTEMPLATE FLAT JSON TRANSFORMER ] (FastAPI / Node Service)                     │
│  Transformeert form-state naar openEHR Simplified / FLAT JSON formaat:                 │
│  {                                                                                     │
│    "sensii_h2/gfi/fysiek/mobiliteit": 1,                                              │
│    "sensii_h2/omaha_assessment/aandachtsgebied|code": "34",                           │
│    "sensii_h2/omaha_assessment/kbs_baseline/kennis": 3                                 │
│  }                                                                                     │
│                            │                                                           │
│                            ▼                                                           │
│  [ 3. EHRBASE REST API CLIENT ]                                                        │
│  POST https://ehr.sensire.nl/ehrbase/rest/openehr/v1/ehr/{ehr_id}/composition          │
│  Headers:                                                                              │
│    • Content-Type: application/openehr.flat.json                                       │
│    • openEHR-template-id: sensire_sensii_h2_anamnese_diagnostiek.v1                    │
│    • Authorization: Bearer <OAuth2 Token / Keycloak>                                   │
│                            │                                                           │
│                            ▼                                                           │
│  [ 4. EHRBASE CDR VERWERKING & PERSISTENTIE ]                                          │
│  • Valideert payload tegen OPT 1.4 XML definitie.                                      │
│  • Genereert unieke ObjectVersionID: 3a4b5c6d-...::ehr.sensire.nl::1                   │
│  • Schrijft naar PostgreSQL (versiebeheerd, onveranderlijk audit trail).               │
│  • Direct realtime bevraagbaar via AQL endpoint (/rest/openehr/v1/query/aql).          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Wat moet hiervoor nog gerealiseerd worden?
1. **EHRbase Omgeving**: Een draaiende EHRbase (Docker/Kubernetes) gekoppeld aan PostgreSQL, waar de 5 Sensii OPTs via `POST /rest/openehr/v1/definition/template/adl1.4` eenmalig worden geüpload.
2. **FLAT JSON Mapper Module**: Een compacte Python helper (`sensii_openehr_mapper.py` in Sensii's FastAPI backend) die de formulierantwoorden vertaalt naar het FLAT JSON formaat op basis van `sensii_openehr_contract.json`.
3. **EHR-ID Beheer**: Koppeling van het Sensire cliëntnummer (BSN/EPD-ID) aan een openEHR `ehr_id` via een veilige pseudonymisatie-tabel.
4. **Authenticatie & Autorisatie**: OAuth2 / OpenID Connect token injection (Keycloak / Azure AD).

---

## 6. Pragmatische Aanpak voor `SensireSpecieleBeslisOndersteuning`

### Het Dilemma
`SensireSpecieleBeslisOndersteuning` is een **actief gebruikte redactie-omgeving** waar zorgprofessionals en redacteurs continu zorgpaden aanpassen en verfijnen.
- ❌ **Foutief Scenario**: Opeens openEHR/Omaha-verplichtingen opleggen in hun invoerinterface leidt tot weerstand, verwarring en verstoring van hun dagelijkse werk.
- ✅ **Aanbevolen Strategie: De "Passieve Schaduw-Adapter" (Non-Invasive)**:

### Het 3-Fasen Adoptieplan:

| Fase | Actie in Speciële Beslisondersteuning | Impact op Redacteur |
| :--- | :--- | :--- |
| **Fase 1: Zero-Touch (Nu)** | De redacteur blijft 100% werken zoals nu (Markdown/Mermaids/JSON). `OpenEHRDemo` genereert op de achtergrond de OPTs en het contract zonder dat de redacteur er iets van merkt. | **Nul verstoring**. Geen enkele extra handeling. |
| **Fase 2: Passieve Info-Badge** | In de WebViewer verschijnt bij een zorgpad een subtiele, niet-storende badge: `[ 🧬 openEHR Template Beschikbaar ]`. Klikken toont de technische architectuur. | **Puur informatief**. Geen verplichte velden. |
| **Fase 3: Opt-in AI Suggesties** | Als de redacteur dat zélf wil, kan een "AI Terminologie Assistent" suggesties doen voor Omaha/SNOMED codes bij het toevoegen van een nieuwe stap. | **Hulp op verzoek**. Geen dwingende blokkades. |

---

## Conclusie voor de Architectuurboard

1. **Architectuur staat**: De scheiding tussen de semantische fabriek (`OpenEHRDemo`) en de consumenten (`Sensii`, `SensireSpecieleBeslisOndersteuning`) is waterdicht en contract-driven.
2. **100% Standaard Conform**: Gebaseerd op officiële openEHR Release 1.1.0 standaarden, gevalideerde OPT 1.4 XML, Nictiz ZIBs en SNOMED CT NL.
3. **Risicoloos & Schaalbaar**: Geen runtime-belasting in bestaande redactietools; directe doorgroeimogelijkheid naar live EHRbase CDR opslag zodra de runtime-pipeline wordt geactiveerd.
