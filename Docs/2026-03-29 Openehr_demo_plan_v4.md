# 🏥 openEHR Demo-omgeving — Sensire Wondzorg

## Volledig Uitvoeringsplan v4.0

*Debian Trixie / Chromebox — Maart 2026*

*Gebaseerd op: Uitvoeringsplan v3.0 (maart 2026), implementatiesessie 16 maart, architecturaal onderzoeksrapport, en voortschrijdend inzicht.*

---

> **Status na sessie 16 maart 2026**
>
> ✅ Docker + EHRbase v2.29.0 draait op Chromebox (Debian Trixie)
> ✅ 5 internationale CKM archetypes gedownload en geïmporteerd
> ✅ Template `sensire_wound_care` gebouwd en geüpload naar EHRbase
> ✅ Test-EHR aangemaakt (EHR-ID: `196bbbe9-24b5-479a-a7aa-596bdf8a56c5`)
> ✅ Ulcus Cruris beslisboom volledig werkend als HTML demo-pagina
> ✅ Composities worden opgeslagen via FLAT JSON POST + bevestigd via AQL

---

# 1. Doel, Context en Architectuur

## 1.1 Wat willen we bereiken?

Een lokale, volledig werkende openEHR demo-omgeving op een Chromebox met Debian Linux. De demo toont het volledige concept levend aan Sensire-collega's en stakeholders die nog niet bekend zijn met openEHR:

- **Waarom openEHR?** Data onafhankelijk van de applicatie. Geen vendor lock-in. Data die over 20 jaar nog leesbaar is.
- **Hoe werkt het?** Internationale standaarden (CKM archetypes) gecombineerd met eigen klinische content (Sensire-specifieke archetypes).
- **Wat levert het op?** Beslisondersteuning voor Ulcus Cruris, Diabetische Voet en Algemeen Wondprotocol, formeel gekoppeld aan gestandaardiseerde data.
- **Hoe bewijzen we het?** Live monitoring van wat er werkelijk in de database wordt opgeslagen — in openEHR-formaat, vertaalbaar naar begrijpelijk Nederlands.

## 1.2 De Dual-Model Architectuur (wat je collega's moeten begrijpen)

openEHR scheidt twee dingen die in traditionele EPD's altijd door elkaar lopen:

**Het Kennisdomein** — *"Wat kan er bestaan?"*
Archetypes en Templates definiëren de structuur en betekenis van klinische data. Een archetype beschrijft maximaal alle mogelijke parameters voor één klinisch concept (bijv. wondinspectie). Een template selecteert en beperkt hieruit wat Sensire nodig heeft.

**Het Datadomein** — *"Wat is er daadwerkelijk geregistreerd?"*
De Clinical Data Repository (CDR) — in ons geval EHRbase — slaat de concrete patiëntgegevens op. Elk dataveld verwijst via zijn *path* terug naar een archetype in het kennisdomein.

Fysiek is dit **één systeem** (EHRbase met PostgreSQL), maar logisch zijn het twee gescheiden lagen. De template is het contract; de compositie is de data. Dit onderscheid is de kern van de demo.

**Kernboodschap voor collega's:**
> *"In een traditioneel EPD zit de kennis over wat een wond is opgesloten in de software van de leverancier. In openEHR is die kennis expliciet, beheerbaar, en internationaal gestandaardiseerd. Als we morgen van leverancier willen wisselen, nemen we onze data én onze definities mee."*

## 1.3 Architectuur in vier lagen

| Laag | Component | Doel |
|:-----|:----------|:-----|
| Kennislaag | Archetypes + Templates | Klinische betekenis vastleggen (CKM + eigen) |
| Repository-laag | EHRbase CDR (Docker) | openEHR server met REST API |
| Applicatielaag | JavaScript beslisbomen | Interactieve formulieren + conditionele logica |
| Presentatielaag | Browser demo-pagina's | Beslisboom + monitoring + template explorer |

## 1.4 Wat is anders ten opzichte van plan v3?

| Onderdeel | v3 | v4 (dit plan) |
|:----------|:---|:--------------|
| Beslislogica | GDL2 regels (nog te bouwen) | JavaScript in de browser — GDL2 geschrapt |
| Monitoring | pgAdmin (raw SQL) | **Live Composition Monitor** — eigen webpagina |
| Template inzicht | Archetype Designer online | **Template Explorer** — eigen webpagina |
| Data-inzicht | AQL in terminal | **Driekolommen-view** in elke beslisboompagina |
| Navigatie | Nog niet gebouwd | **Dashboard** als startpunt van de demo |

De belangrijkste strategische keuze is het **schrappen van GDL2**. GDL2 is ontworpen als server-side rule engine voor Clinical Decision Support. Voor het dynamisch tonen van formulieren en beslisbomen is het te zwaar, te traag, en de open-source tooling is onvoldoende mature. De beslislogica verhuist naar JavaScript in de browser: direct, responsief, en begrijpelijk voor elke webontwikkelaar.

De kernboodschap wordt:
> *"De beslislogica zit nu in JavaScript, maar de data die wordt opgeslagen is 100% openEHR-conform. Als we later GDL2 of een andere engine willen, verandert er niets aan de data. Dat is het punt: de data is onafhankelijk van de applicatie."*

## 1.5 Componentoverzicht

| Component | Wat is het? | Docker? | Status |
|:----------|:------------|:--------|:-------|
| EHRbase CDR | openEHR server — REST API voor alles | ✅ Ja | ✅ Draait |
| PostgreSQL | Opslagbackend voor EHRbase | ✅ Ja | ✅ Draait |
| Archetype Designer | Web-app voor archetype/template-modellering | 🌐 Online | ✅ In gebruik |
| openEHR CKM | Internationale archetype-bibliotheek | 🌐 Online | ✅ In gebruik |
| Demo-applicatie | Vite dev server met HTML/JS pagina's | ✅ Lokaal | ✅ Deels (Ulcus Cruris) |
| pgAdmin | PostgreSQL browser (visueel bewijs) | ✅ Docker | ⏳ Nog installeren |
| Swagger UI | API-browser (ingebouwd in EHRbase) | ⬜ Ingebouwd | ✅ Beschikbaar |

**Geschrapt uit v3:** GDL2 Editor, openEHRTool (niet nodig — we bouwen betere eigen visualisatie).

---

# 2. Technische Omgeving

## 2.1 Hardware en OS

De omgeving draait op een Chromebox met Debian Trixie Linux (via Crostini). Alle zware componenten draaien in Docker containers.

> ⚠️ **Debian Trixie — NIET Ubuntu.** De Chromebox draait Debian Trixie. Gebruik altijd de Debian Docker repo (`download.docker.com/linux/debian`), niet Ubuntu. Dit verschil veroorzaakte een 404 fout in de eerste sessie.

## 2.2 Docker installeren (Debian Trixie — correcte methode)

```bash
# Verwijder eventuele foute Ubuntu repo
sudo rm -f /etc/apt/sources.list.d/docker.list
sudo rm -f /etc/apt/keyrings/docker.gpg

# Juiste Debian GPG key ophalen
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg \
  --dearmor -o /etc/apt/keyrings/docker.gpg

# Juiste Debian repo toevoegen
echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installeren
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Gebruiker toevoegen aan docker groep
sudo usermod -aG docker $USER
newgrp docker

# Verificatie
docker --version
docker compose version
```

> ℹ️ Na `newgrp docker`: bij een permissiefout op de socket, sluit de terminal en open opnieuw.

## 2.3 docker-compose.yml

Het bestand staat op `~/ehrbase-demo/docker-compose.yml`:

```yaml
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
    image: ehrbase/ehrbase:latest
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
volumes:
  ehrbase_data:
```

## 2.4 Overzicht draaiende services

| Component | Status | URL |
|:----------|:-------|:----|
| EHRbase CDR | ✅ Draait | http://localhost:8080 |
| Swagger UI | ✅ Ingebouwd | http://localhost:8080/ehrbase/swagger-ui.html |
| PostgreSQL | ✅ Draait | localhost:5432 |
| Demo-applicatie | ✅ Draait | http://localhost:5173 |
| pgAdmin | ⏳ Nog installeren | http://localhost:5050 |

---

# 3. Het Kennisdomein: Archetypes en Templates

## 3.1 Wat zijn archetypes en templates?

**Archetype** = een maximaal gedefinieerd, herbruikbaar datamodel voor één klinisch concept. Geschreven in de Archetype Definition Language (ADL). Voorbeeld: het archetype voor wondinspectie bevat *elke denkbare parameter* die wereldwijd relevant zou kunnen zijn voor een wond.

**Template** = een lokale samenstelling en inperking van meerdere archetypes voor een specifieke use-case. Het template bepaalt welke velden uit de archetypes Sensire daadwerkelijk gebruikt, welke verplicht zijn, en welke waardenlijsten zijn toegestaan.

**Operational Template (OPT)** = de gecompileerde versie van het template, geüpload naar EHRbase. Dit is het "contract" — EHRbase valideert elke inkomende compositie tegen dit OPT.

**WebTemplate** = een JSON-representatie van het template, bedoeld voor de frontend. Bevat alle metadata, labels in alle talen, en de structuur die nodig is om formulieren te genereren en data te vertalen.

## 3.2 Internationale archetypes (al beschikbaar)

De volledige CKM-mirror staat in `~/ehrbase-demo/archetypes/international/CKM-mirror/`.

De volgende archetypes zijn geïmporteerd in Archetype Designer:

- `openEHR-EHR-CLUSTER.oedema.v0.adl`
- `openEHR-EHR-CLUSTER.exam_wound.v0.adl`
- `openEHR-EHR-OBSERVATION.diabetic_wound_wagner.v0.adl`
- `openEHR-EHR-EVALUATION.problem_diagnosis.v1.adl`
- `openEHR-EHR-EVALUATION.health_risk.v1.adl`

> ⚠️ **ankle_brachial_index** staat niet in de internationale CKM. Moet zelf gemaakt worden (zie §3.4).

## 3.3 "VerNederlandsen" — Vertaling zonder de standaard te breken

openEHR ondersteunt meertaligheid op architecturaal niveau. Elk datapunt heeft een unieke, onveranderlijke technische identificator (een `at-code`, bijvoorbeeld `at0004`). De taal zit niet in de logica maar in de ontologiesectie van het ADL-bestand.

**Het principe:** Het archetype wordt *niet* gedupliceerd. Via Archetype Designer voeg je een Nederlandse taallaag toe aan het bestaande archetype. De `at-code` `at0004` krijgt naast het Engelse label "Wound Depth" ook het Nederlandse label "Wonddiepte". Bij dataopslag wordt altijd de universele `at0004` gebruikt. De presentatietaal is een keuze van de frontend.

**Procedure per archetype:**

1. Open het archetype in Archetype Designer
2. Klik op "Languages" → "Add Language" → kies "Dutch (nl)"
3. Vul voor elk element de Nederlandse tekst in: term name, description, comment
4. Exporteer opnieuw als ADL 1.4 — het bestand bevat nu beide talen

> ℹ️ **LLM-vertalingen:** Claude levert uitstekende medische vertalingen. Workflow: exporteer het archetype als ADL-tekst, vraag Claude om een NL-vertaling per element, plak de vertalingen terug in Archetype Designer.

**Hoe verhouden EN en NL zich tot elkaar?**

| Aspect | Engels (primair) | Nederlands (vertaling) |
|:-------|:-----------------|:-----------------------|
| Archetype ID | `openEHR-EHR-CLUSTER.stemmer_sign.v0` | Identiek — nooit vertaald |
| Archetype path (AQL) | `items[at0001]/value` | Identiek — altijd Engels |
| Term name | "Stemmer sign" | "Teken van Stemmer" |
| Description | "Test to differentiate lymphoedema..." | "Test om lymfoedeem te onderscheiden..." |
| Gecodeerde waarde | SNOMED: 416940007 | Zelfde code, NL term |
| Browser-formulier | Engelse labels | Nederlandse labels |
| AQL query | Altijd in het Engels | Altijd in het Engels |

## 3.4 "VerSensiren" — Eigen archetypes bouwen

Sensire heeft klinische concepten die nog niet in de internationale CKM bestaan. Deze bouwen we zelf in Archetype Designer, primair in het Engels (zodat ze later aan de internationale CKM bijgedragen kunnen worden), met directe NL-vertaling.

| Archetype ID | RM Type | Doel |
|:-------------|:--------|:-----|
| `openEHR-EHR-OBSERVATION.ankle_brachial_index.v0` | OBSERVATION | EAI meting (enkel-arm index) |
| `openEHR-EHR-CLUSTER.stemmer_sign.v0` | CLUSTER | Teken van Stemmer (lymfoedeem vs. veneus) |
| `openEHR-EHR-CLUSTER.wound_stagnation_assessment.v0` | CLUSTER | Stagnatiebeoordeling (>2-3 weken) |
| `openEHR-EHR-CLUSTER.wcs_wound_classification.v0` | CLUSTER | WCS kleurenclassificatie (rood/geel/zwart) |
| `openEHR-EHR-CLUSTER.altis_pain_score.v0` | CLUSTER | ALTIS pijnscore |

Exporteer elk archetype als ADL 1.4 en sla op in `~/ehrbase-demo/archetypes/sensire/`.

> ℹ️ **Sensire als pionier.** Door deze archetypes in het Engels te bouwen en bij CKM in te dienen, draagt Sensire bij aan de internationale openEHR community — net als Noorse en Australische zorgaanbieders die al archetypes hebben bijgedragen.

## 3.5 Template uitbreiden en exporteren

Na het bouwen van de eigen archetypes: importeer ze in Archetype Designer, voeg toe aan de template `sensire_wound_care`, pas constraints toe (verplichte velden, beperkte waardenlijsten), en exporteer:

1. **OPT** (Operational Template) → uploaden naar EHRbase:

```bash
curl -X POST \
  http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4 \
  -u ehrbase-user:SuperSecretPassword \
  -H "Content-Type: application/xml" \
  --data-binary @~/ehrbase-demo/sensire_wound_care.opt
```

2. **WebTemplate** (JSON) → ophalen uit EHRbase na OPT-upload:

```bash
curl -u ehrbase-user:SuperSecretPassword \
  -H "Accept: application/json" \
  "http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4/sensire_wound_care" \
  > ~/ehrbase-demo/webtemplates/sensire_wound_care.json
```

Dit WebTemplate is het "woordenboek" dat de frontend gebruikt om openEHR-paden te vertalen naar Nederlandse labels.

## 3.6 Aansluiting op ZIBs (Zorginformatiebouwstenen)

ZIBs zijn de Nederlandse nationale klinische informatiestandaard (Nictiz). Ze beschrijven dezelfde concepten als openEHR archetypes, maar dan voor de Nederlandse context.

| ZIB-concept | openEHR archetype | Relatie |
|:------------|:------------------|:--------|
| ZIB Wond | `CLUSTER.exam_wound` | Sterke overlap, terminologieafstemming nodig |
| ZIB Bloeddruk | `OBSERVATION.blood_pressure` | Directe mapping via LOINC |
| ZIB Probleem | `EVALUATION.problem_diagnosis` | Directe mapping |
| ZIB Meting (EAI) | `ankle_brachial_index` (eigen) | Eigen archetype, ZIB-termen gebruiken |

---

# 4. De Datastromen: Van Formulier naar Database

## 4.1 FLAT JSON — het dataformaat

Wanneer een verpleegkundige het beslisboomformulier invult, genereert de frontend geen complexe XML-boom maar een "platte" lijst van sleutel-waarde paren. Dit heet FLAT JSON (formeel: simplified Data Template / simSDT).

Voorbeeld van hoe opgeslagen data eruitziet:

```json
{
  "wondverzorging/context/start_time": "2026-03-29T10:30:00",
  "wondverzorging/wondinspectie:0/wondbed/weefseltype|code": "at0012",
  "wondverzorging/wondinspectie:0/wondbed/weefseltype|value": "Necrotisch",
  "wondverzorging/wondinspectie:0/wondbed/lengte|magnitude": 12.5,
  "wondverzorging/wondinspectie:0/wondbed/lengte|unit": "cm",
  "wondverzorging/wondinspectie:0/exsudaat_niveau|value": "Vochtig",
  "wondverzorging/wondinspectie:0/wcs_kleur|code": "at0002",
  "wondverzorging/wondinspectie:0/wcs_kleur|value": "Geel",
  "wondverzorging/pijn/altis_score|magnitude": 4,
  "wondverzorging/dm_status|code": "at0001",
  "wondverzorging/dm_status|value": "Aanwezig"
}
```

De structuur: hiërarchisch pad (gescheiden door `/`), indexen voor herhalende velden (`:0`), en pipe-tekens (`|`) voor specifieke attributen van het datatype (`|magnitude`, `|unit`, `|code`, `|value`).

## 4.2 WebTemplate — het vertaalwoordenboek

Het WebTemplate (JSON) is de sleutel om ruwe openEHR-data leesbaar te maken. Het bevat voor elk knooppunt in het template:

- `id`: de technische string die in het FLAT JSON pad staat
- `name`: het internationale Engelse label
- `localizedName`: het Nederlandse label (als je de NL-vertaling hebt toegevoegd)
- `aqlPath`: het formele AQL-pad om dit datapunt in de database terug te vinden
- `inputs`: de mogelijke waarden (bij keuzelijsten)

De frontend laadt dit WebTemplate eenmalig en bouwt er een lookup-tabel van: pad → `{ en: "Tissue type", nl: "Weefseltype", mogelijke_waarden: [...] }`.

## 4.3 De volledige datastroom

```
┌─────────────────────────────────────────────────────────────────┐
│  1. MODELLERING (eenmalig)                                      │
│                                                                  │
│  CKM archetypes ──→ Archetype Designer ──→ Template             │
│                          + NL vertaling      + constraints       │
│                                                                  │
│  Template ──export──→ OPT (naar EHRbase)                        │
│                   ──→ WebTemplate JSON (naar frontend)           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. DAGELIJKS GEBRUIK                                           │
│                                                                  │
│  Verpleegkundige vult beslisboom in                              │
│         │                                                        │
│         ▼                                                        │
│  Frontend genereert FLAT JSON                                    │
│         │                                                        │
│         ▼                                                        │
│  POST /ehr/{ehr_id}/composition?format=FLAT                     │
│         │                                                        │
│         ▼                                                        │
│  EHRbase valideert tegen OPT ──→ ❌ Afwijzing bij ongeldige     │
│         │                           data (datakwaliteit!)        │
│         ▼                                                        │
│  ✅ Compositie opgeslagen in PostgreSQL                          │
│         │                                                        │
│         ▼                                                        │
│  Bevraagbaar via AQL (onafhankelijk van de applicatie)           │
└─────────────────────────────────────────────────────────────────┘
```

---

# 5. De Demo-pagina's

## 5.1 Navigatiepagina (Dashboard)

De `index.html` is het startpunt van de demo. Alle onderdelen zijn bereikbaar vanuit één overzichtelijke pagina:

```
┌──────────────────────────────────────────────────┐
│  🏥 Sensire openEHR Demo                         │
│                                                   │
│  ┌─ KENNISLAAG ─────────────────────────────┐    │
│  │  📋 Template Explorer                     │    │
│  │     Internationaal vs. Sensire            │    │
│  │     EN ↔ NL vertalingen                   │    │
│  └───────────────────────────────────────────┘    │
│                                                   │
│  ┌─ BESLISBOMEN ────────────────────────────┐    │
│  │  🩹 Ulcus Cruris Protocol                 │    │
│  │  🦶 Diabetische Voet Protocol             │    │
│  │  🏥 Algemeen Wondprotocol                 │    │
│  └───────────────────────────────────────────┘    │
│                                                   │
│  ┌─ MONITORING ─────────────────────────────┐    │
│  │  📡 Live Composition Monitor              │    │
│  │     Realtime: wat wordt er opgeslagen?    │    │
│  └───────────────────────────────────────────┘    │
│                                                   │
│  ┌─ TECHNISCH ──────────────────────────────┐    │
│  │  🔧 Swagger UI (REST API)                 │    │
│  │  🗄️  pgAdmin (PostgreSQL)                 │    │
│  └───────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘
```

## 5.2 Beslisboompagina's — Structuur

Elke beslisboompagina (Ulcus Cruris, Diabetische Voet, Algemeen Wondprotocol) volgt dezelfde structuur met vier panelen:

### Paneel 1: De Beslisboom (hoofdscherm)

Een interactief formulier dat de verpleegkundige door de klinische beslisboom leidt. De conditionele logica zit in JavaScript: velden verschijnen of verdwijnen op basis van eerdere antwoorden. Alle formulierelementen zijn gebonden aan openEHR-paden uit het WebTemplate.

**Technische aanpak:** Elke beslisboompagina laadt het WebTemplate JSON en bouwt daaruit de formuliervelden. De conditionele logica (bijv. "toon DM-voetinspectie alleen als DM = Aanwezig") is geschreven als JavaScript event-listeners die DOM-elementen tonen/verbergen.

### Paneel 2: Klinisch Advies

Gebaseerd op de ingevulde waarden toont dit paneel het klinisch advies in begrijpelijk Nederlands. Bijvoorbeeld: "EAI: 0.85 → Veneus ulcus. Start compressie met UrgoK2." Dit is de JavaScript-implementatie van wat in v3 als GDL2-regels was voorzien.

### Paneel 3: openEHR Data (na opslaan)

Na het opslaan toont dit paneel de opgeslagen data in drie kolommen:

| openEHR Path | Nederlands Label | Waarde |
|:-------------|:-----------------|:-------|
| `wound_care/.../tissue_type\|code` | Weefseltype (TIME-T) | `at0005` → "Necrose (zwart)" |
| `wound_care/.../exudate_level\|value` | Exsudaatniveau (TIME-M) | "Vochtig" |
| `wound_care/.../wcs_colour\|value` | WCS-kleur | "Geel" |

De vertaling van openEHR-pad naar Nederlands label komt uit het WebTemplate. De vertaling van `at-code` naar leesbare waarde komt uit de `inputs`-sectie van datzelfde WebTemplate.

### Paneel 4: AQL Bewijs (na opslaan)

Toont de compositie-UID, de AQL-query die de data terughaalt, en het ruwe JSON-resultaat. Dit bewijst dat de data onafhankelijk van de applicatie bevraagbaar is.

## 5.3 Ulcus Cruris Protocol (✅ deels werkend)

De Ulcus Cruris beslisboom is al werkend als HTML pagina. De bestaande pagina wordt uitgebreid met de panelen 3 en 4.

**Kernbeslissingen in de beslisboom:**
- Nieuwe/bestaande cliënt + stagnatiebeoordeling (>2-3 weken)
- Diabetes Mellitus? → doorverwijzing Diabetische Voet protocol
- Oedeem + Stemmer-test (veneus vs. lymfoedeem)
- EAI-waarde: <0.6 (ernstig, geen compressie), 0.6-0.8 (gemengd, UrgoK2 Lite), 0.8-1.3 (veneus, UrgoK2), >1.3 (overleg HA)
- Zwachtelwerkinstructie + nazorg + afsluiting

**openEHR archetypes:**
- `OBSERVATION.ankle_brachial_index.v0` (EAI)
- `CLUSTER.stemmer_sign.v0` (Stemmer-test)
- `CLUSTER.wound_stagnation_assessment.v0` (stagnatiebeoordeling)
- `CLUSTER.oedema.v0` (oedeem)
- `EVALUATION.problem_diagnosis.v1` (diagnose HA)

## 5.4 Diabetische Voet Protocol (nog te bouwen)

**Kernbeslissingen:**
- Anamnese: glucose geregeld, claudicatio, eerder ulcus, Charcot in voorgeschiedenis
- Voetinspectie: huidkleur, temp., pulsaties, monofilament gevoel, nagels, schoeisel
- **Charcot vermoeden** (rode, warme, gezwollen voet zonder trauma) → arts dezelfde dag — MEEST URGENTE ESCALATIE
- Plantaire wond → arts binnen 24 uur
- Geen wond → preventieve zorg (groene flow)
- Wond → doorverwijzing naar Algemeen Wondprotocol met DM-laag geactiveerd

**openEHR archetypes:**
- `OBSERVATION.diabetic_wound_wagner.v0` (Wagner classificatie)
- `CLUSTER.exam_wound.v0` (wondinspectie)
- `CLUSTER.altis_pain_score.v0` (pijnscore)
- `EVALUATION.problem_diagnosis.v1` (diagnose)

## 5.5 Algemeen Wondprotocol (nog te bouwen)

Het meest uitgebreide zorgpad. De beslisboom (Wondverzorging.mermaid) is de referentie.

**Kernonderdelen:**
- Oncologische wond check (apart protocol, niet dit pad)
- Voorbereiding: werkveld, materialen (max 14 dgn), handhygiëne, desinfectie schaar/pincet
- Wondinspectie: verband beoordelen, wond inspecteren (grootte, kleur, geur, exsudaat, wondranden)
- DM-laag: voetinspectie, Charcot-check, plantaire wond (arts <24u)
- Pijnmanagement: ALTIS-score, systemisch vs. lokaal (Lidocaïne/EMLA)
- TIME + WCS analyse (Tissue/Infectie/Moisture/Edge; rood/geel/zwart)
- Debridement veiligheidscheck (stolling, diepe structuren, maligniteit)
- Infectiebeleid (lokaal antibact., arts bij koorts+DM, ernstige infectie)
- Verbandkeuze matrix: WCS-kleur × exsudaatniveau (droog/vochtig/nat)
- DM: drukontlasting (Stap B) + voorlichting (Stap C)
- Nazorg: rapportage (TIME+Foto wekelijks), escalatie Vakgroep Wond

**openEHR archetypes (volledig):**
- `CLUSTER.exam_wound.v0` (TIME: T = weefsel, M = exsudaat, E = wondranden)
- `CLUSTER.wcs_wound_classification.v0` (WCS kleurclassificatie)
- `CLUSTER.altis_pain_score.v0` (pijnmanagement)
- `CLUSTER.oedema.v0` (oedeem wondomgeving)
- `EVALUATION.health_risk.v1` (infectierisico / escalatie)
- `EVALUATION.problem_diagnosis.v1` (oncologisch, DM, etc.)

## 5.6 Datamodellering: Hoe de beslisboom-data mapt naar openEHR

De data uit de wondverzorging-beslisboom mapt als volgt naar openEHR Reference Model klassen:

| Klinisch gegeven | RM-klasse | Waarom? |
|:-----------------|:----------|:--------|
| Oncologische wond: ja/nee | EVALUATION.problem_diagnosis | Vastgestelde medische conditie |
| DM status: aanwezig/afwezig | EVALUATION.problem_diagnosis | Persistente comorbiditeit |
| Wondafmetingen (l×b×d) | OBSERVATION + CLUSTER.dimensions | Meting op een tijdstip |
| Weefseltype (TIME-T) | CLUSTER.exam_wound | Inspectie-bevinding |
| WCS-kleur (rood/geel/zwart) | CLUSTER.wcs_wound_classification | Gecodeerde classificatie |
| Exsudaatniveau (droog/vochtig/nat) | CLUSTER.exam_wound | Inspectie-bevinding |
| ALTIS pijnscore | CLUSTER.altis_pain_score | Meting op een tijdstip |
| EAI-waarde | OBSERVATION.ankle_brachial_index | Meting op een tijdstip |
| Stemmer-test (pos/neg) | CLUSTER.stemmer_sign | Testresultaat |
| Charcot vermoeden | EVALUATION.health_risk | Klinisch oordeel / risico |
| Wondreiniging uitgevoerd | ACTION.procedure | Uitgevoerde handeling |
| Pijnstilling toegediend | ACTION.medication | Uitgevoerde medicatie |

---

# 6. Live Composition Monitor (nieuw)

## 6.1 Doel

Een webpagina die de EHRbase database live in de gaten houdt. Doel: live bewijzen dat de beslisboomdata daadwerkelijk wordt opgeslagen, dat het openEHR-formaat wordt gebruikt, en wat die data betekent in het Nederlands.

## 6.2 Technische architectuur: AQL Polling

De monitor pollt elke 3-5 seconden de EHRbase API met een AQL-query:

```sql
SELECT
  e/ehr_id/value AS ehr_id,
  c/uid/value AS composition_id,
  c/name/value AS formulier,
  c/context/start_time/value AS tijdstip,
  c/composer/name AS behandelaar
FROM EHR e
CONTAINS COMPOSITION c
ORDER BY c/context/start_time/value DESC
LIMIT 10
```

De JavaScript `setInterval()` loop vergelijkt de binnengekomen composition IDs met de reeds getoonde. Bij een nieuw ID: highlight als nieuw item met animatie.

## 6.3 Driekolommen-view: De vertaalslag

Klik op een compositie → haal de volledige FLAT JSON op:

```bash
GET /ehrbase/rest/openehr/v1/ehr/{ehr_id}/composition/{uid}?format=FLAT
```

Toon vervolgens drie kolommen:

| openEHR Path (technisch) | Label (NL, uit WebTemplate) | Waarde |
|:-------------------------|:----------------------------|:-------|
| `wound_care/.../tissue_type\|code` | Weefseltype (TIME-T) | `at0005` → "Necrose (zwart)" |
| `wound_care/.../exudate_level\|value` | Exsudaatniveau (TIME-M) | "Vochtig" |
| `wound_care/.../wcs_colour\|value` | WCS-kleur | "Geel" |
| `wound_care/.../altis_score\|magnitude` | ALTIS pijnscore | 4 |

De vertaallogica:
1. Laad het WebTemplate JSON eenmalig
2. Bouw een lookup: `flatPath → { en: "...", nl: "...", inputs: [...] }`
3. Voor elke key in de FLAT JSON: zoek de Nederlandse label op in de lookup
4. Voor `at-codes`: zoek de leesbare waarde op in de `inputs` van het WebTemplate

## 6.4 Demo-moment

Twee schermen naast elkaar:
- **Scherm 1:** Een collega vult het beslisboomformulier in
- **Scherm 2:** De Live Composition Monitor

De collega klikt "Opslaan" op scherm 1. Binnen enkele seconden verschijnt de compositie op scherm 2, met een highlight. Klik erop: de driekolommen-view toont precies wat er is opgeslagen, in openEHR-formaat én in het Nederlands.

> **Kernboodschap:** "Kijk, dit is wat er nu live opgeslagen wordt. Elk veld verwijst naar een internationaal gedefinieerd archetype. Een Noors ziekenhuis dat dezelfde archetypes gebruikt, leest exact dezelfde data — zonder vertaalslag, zonder mapping, zonder IT-project."

## 6.5 Toekomstperspectief: Event Triggers

Voor de demo is polling ideaal (eenvoudig, geen extra infrastructuur). In productie met duizenden gebruikers zou je Event Triggers gebruiken: de database stuurt automatisch een signaal (via AMQP/RabbitMQ/Kafka) op het moment dat een compositie wordt opgeslagen, en een WebSocket pusht de update naar het dashboard. Dit is enterprise-functionaliteit die beschikbaar is in HIP EHRbase. Benoem dit kort richting stakeholders als bewijs dat de architectuur schaalbaar is.

---

# 7. Template Explorer (nieuw)

## 7.1 Doel

Een webpagina die de kennislaag visualiseert: welke archetypes zitten in het Sensire template, welke zijn internationaal, welke zijn eigen, en hoe verhouden ze zich tot elkaar.

## 7.2 Wat de pagina toont

Het WebTemplate als een interactieve boomstructuur (tree view):

- Elke node toont: archetype-ID, EN label, NL label
- **Kleurcodering:**
  - 🔵 Blauw = internationale CKM archetype (bijv. `CLUSTER.exam_wound.v0`)
  - 🟢 Groen = Sensire eigen archetype (bijv. `CLUSTER.stemmer_sign.v0`)
- Klik op een internationale archetype → toon beschrijving + link naar CKM
- Klik op een Sensire archetype → toon beschrijving + "Dit is onze bijdrage aan de community"

## 7.3 Diff-weergave

Voor internationale archetypes: toon hoeveel velden het origineel heeft vs. hoeveel Sensire er gebruikt. Bijvoorbeeld: "Het CKM origineel exam_wound heeft 23 velden. Sensire gebruikt er 12 in dit template."

Dit illustreert het template-mechanisme: je *selecteert* uit een archetype wat je nodig hebt. Je gooit niets weg — je beperkt het voor jouw use-case.

## 7.4 Taalweergave

Voor elk knooppunt: toon naast elkaar het Engelse label en het Nederlandse label. Dit maakt direct zichtbaar dat de vertaling een presentatielaag is, niet een wijziging van de data.

## 7.5 Demo-moment

> **Kernboodschap:** "Dit is onze template. De blauwe blokken zijn internationaal — ontwikkeld door klinische experts over de hele wereld. Die hebben we gewoon gepakt. De groene blokken zijn van ons. Het WCS-kleurensysteem, de ALTIS-pijnscore — die bestaan nog nergens als openEHR archetype. Die hebben wij gebouwd. En straks geven we ze terug aan de internationale community."

---

# 8. Monitoring Tools

## 8.1 pgAdmin (PostgreSQL browser)

```bash
docker run -d --name pgadmin \
  --network ehrbase-demo_ehrbase-net \
  -p 5050:80 \
  -e PGADMIN_DEFAULT_EMAIL=demo@sensire.nl \
  -e PGADMIN_DEFAULT_PASSWORD=demo \
  dpage/pgadmin4
```

Verbind met: host=ehrdb, port=5432, gebruiker=postgres, wachtwoord=postgres.

pgAdmin is het "visueel bewijs voor sceptici": de openEHR data staat echt in een echte database.

> ℹ️ **Let op het network.** pgAdmin moet in hetzelfde Docker network draaien als EHRbase om `ehrdb` als hostname te kunnen gebruiken. Gebruik `--network ehrbase-demo_ehrbase-net` (de exacte naam hangt af van je docker-compose project naam).

## 8.2 Swagger UI (ingebouwd)

Beschikbaar op http://localhost:8080/ehrbase/swagger-ui.html. Laat alle REST API endpoints zien. Ideaal om aan te tonen wat het systeem kan.

---

# 9. Versiebeheer

```bash
mkdir -p ~/ehrbase-demo/archetypes/international
mkdir -p ~/ehrbase-demo/archetypes/sensire
mkdir -p ~/ehrbase-demo/templates
mkdir -p ~/ehrbase-demo/webtemplates

cd ~/ehrbase-demo && git init

git add archetypes/international/
git commit -m "feat: internationale CKM archetypes v2025"

git add archetypes/sensire/
git commit -m "feat: Sensire eigen archetypes wondzorgpad v1.0"

git add templates/ webtemplates/
git commit -m "feat: Sensire wound care template + webtemplate"
```

De mappenstructuur maakt direct zichtbaar welke archetypes internationaal zijn en welke eigen bijdragen.

---

# 10. Demo-script voor Collega's

Aanbevolen volgorde voor een demonstratie. Totale duur circa 25 minuten.

## 10.1 Wat is openEHR? (2 minuten)

> *"openEHR is een internationale standaard die beschrijft hoe klinische data gestructureerd opgeslagen moet worden. Niet in het format van een leverancier, maar in een format dat iedere computer ter wereld begrijpt. Geen vendor lock-in. Data die over 20 jaar nog leesbaar is."*

## 10.2 Template Explorer — Internationaal vs. Eigen (4 minuten)

Open de Template Explorer.

- "Dit is ons wondzorg-template. De blauwe blokken zijn internationaal — die bestaan al."
- "De groene blokken zijn van Sensire. Het WCS-kleurensysteem, de ALTIS-pijnscore — die hebben wij gemodelleerd."
- Klik op een archetype: toon het Engelse label naast het Nederlandse.
- "De data wordt altijd opgeslagen in internationaal formaat. De Nederlandse termen zijn een presentatiekeuze."

## 10.3 Beslisboom doorlopen — Ulcus Cruris (5 minuten)

Open de Ulcus Cruris pagina. Stel de Live Composition Monitor open op een tweede scherm.

1. Vul een testpatiënt in: naam, geboortedatum
2. Doorloop de beslisboom: geen DM, oedeem aanwezig, Stemmer negatief
3. Voer een EAI waarde in: 0.85 (veneus, normaal)
4. "Dit is wat de verpleegkundige te zien krijgt." → toon klinisch advies
5. Klik Opslaan
6. Wijs naar het tweede scherm: "Kijk — de compositie verschijnt live."

## 10.4 Live Monitor — Wat is er opgeslagen? (5 minuten)

Op het tweede scherm, klik op de zojuist verschenen compositie.

- "Dit zijn de openEHR-paden — de technische taal."
- "Dit zijn de Nederlandse labels — uit ons template."
- "En dit zijn de waarden die de verpleegkundige heeft ingevuld."
- "Als een Noors ziekenhuis dezelfde archetypes gebruikt, begrijpen zij exact dezelfde data."

## 10.5 AQL — Data onafhankelijk van de applicatie (3 minuten)

Open een terminal:

```bash
curl -u ehrbase-user:SuperSecretPassword \
  -H "Content-Type: application/json" \
  "http://localhost:8080/ehrbase/rest/openehr/v1/query/aql" \
  --data-binary '{"q": "SELECT c/uid/value, c/name/value FROM EHR e CONTAINS COMPOSITION c"}'
```

> *"Dit is dezelfde data, maar nu bevraagd direct uit de database via een internationale querytaal. Geen API van een leverancier — pure openEHR. Een ander systeem dat openEHR spreekt kan dezelfde query uitvoeren."*

## 10.6 Swagger UI — De REST API (2 minuten)

Open Swagger UI. Toon de Template Controller → GET templates.

> *"Dit zijn onze zorgpaden, opgeslagen als internationale standaard. Elk systeem met een REST API client kan hier tegenaan praten."*

## 10.7 pgAdmin — Het echte bewijs (2 minuten)

Open pgAdmin, navigeer naar de ehrbase database.

> *"En voor de echte sceptici: hier staan de raw openEHR records in PostgreSQL. Echte data, echte database, open standaard."*

## 10.8 Afsluiting en Discussie (2 minuten)

> *"Wat jullie hebben gezien: een compleet werkende keten. Van internationale standaard naar Nederlandse interface, van beslisboom naar gevalideerde opslag, van ruwe data naar leesbaar dossier. Dit draait op een Chromebox. De software is open source. De standaard is internationaal. En Sensire kan morgen beginnen."*

---

# 11. Tijdlijn

| Dag | Activiteit | Resultaat | Status |
|:----|:-----------|:----------|:-------|
| 1 | Docker + EHRbase opstarten | Werkende CDR op localhost:8080 | ✅ |
| 2 | CKM archetypes + template | OPT geüpload + werkend | ✅ |
| 3 | Ulcus Cruris HTML beslisboom | Werkende browser-demo + AQL bewijs | ✅ |
| 4 | Eigen archetypes bouwen (EN + NL) | stemmer_sign, wcs, altis, eai | ⏳ |
| 5 | Template uitbreiden + WebTemplate exporteren | Volledig template met NL labels | ⏳ |
| 6 | Ulcus Cruris: driekolommen-view + klinisch advies | Panelen 2, 3, 4 werkend | ⏳ |
| 7 | Diabetische Voet beslisboompagina | Tweede werkende demo | ⏳ |
| 8 | Algemeen Wondprotocol beslisboompagina | Derde werkende demo | ⏳ |
| 9 | Template Explorer + Live Composition Monitor | Kennislaag + monitoring werkend | ⏳ |
| 10 | Navigatiepagina + pgAdmin + demo-script | Alles draaiend, klaar voor demo | ⏳ |

---

# 12. Snelreferentie — Commando's

## 12.1 EHRbase beheer

```bash
# Starten
cd ~/ehrbase-demo && docker compose up -d

# Stoppen
docker compose down

# Status
curl -u ehrbase-user:SuperSecretPassword http://localhost:8080/ehrbase/rest/status

# Alle templates
curl -u ehrbase-user:SuperSecretPassword \
  http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4

# Template uploaden (OPT)
curl -X POST \
  http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4 \
  -u ehrbase-user:SuperSecretPassword \
  -H "Content-Type: application/xml" \
  --data-binary @~/ehrbase-demo/sensire_wound_care.opt

# WebTemplate ophalen (JSON)
curl -u ehrbase-user:SuperSecretPassword \
  -H "Accept: application/json" \
  "http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4/sensire_wound_care"
```

## 12.2 EHR aanmaken

```bash
curl -X POST \
  http://localhost:8080/ehrbase/rest/openehr/v1/ehr \
  -u ehrbase-user:SuperSecretPassword \
  -H "Content-Type: application/json" \
  -d '{
    "_type": "EHR_STATUS",
    "archetype_node_id": "openEHR-EHR-EHR_STATUS.generic.v1",
    "name": {"value": "EHR Status"},
    "subject": {"_type": "PARTY_SELF"},
    "is_queryable": true,
    "is_modifiable": true
  }'
```

## 12.3 AQL queries

```bash
# Alle composities (recent eerst)
curl -u ehrbase-user:SuperSecretPassword \
  -H "Content-Type: application/json" \
  "http://localhost:8080/ehrbase/rest/openehr/v1/query/aql" \
  --data-binary '{"q": "SELECT c/uid/value, c/name/value, c/context/start_time/value
    FROM EHR e CONTAINS COMPOSITION c
    ORDER BY c/context/start_time/value DESC LIMIT 10"}'

# Specifieke wonddata
'{"q": "SELECT o/data[at0001]/events[at0002]/data[at0003]/items/value
  FROM EHR e CONTAINS OBSERVATION o[openEHR-EHR-OBSERVATION.ankle_brachial_index.v0]"}'
```

## 12.4 Demo starten (complete stack)

```bash
# 1. EHRbase
cd ~/ehrbase-demo && docker compose up -d

# 2. Verificatie
curl -u ehrbase-user:SuperSecretPassword http://localhost:8080/ehrbase/rest/status

# 3. pgAdmin (optioneel)
docker start pgadmin

# 4. Demo-applicatie
cd ~/ehrbase-demo/frontend/sensire-app && npm run dev

# 5. Browser
# Dashboard:  http://localhost:5173
# Swagger:    http://localhost:8080/ehrbase/swagger-ui.html
# pgAdmin:    http://localhost:5050
```

## 12.5 Credentials

| Service | Gebruiker | Wachtwoord |
|:--------|:----------|:-----------|
| EHRbase REST API | ehrbase-user | SuperSecretPassword |
| PostgreSQL | postgres | postgres |
| pgAdmin | demo@sensire.nl | demo |
| Archetype Designer | eigen openEHR account | (eigen wachtwoord) |

## 12.6 Belangrijke paden

```
~/ehrbase-demo/                              # Projecthoofdmap
~/ehrbase-demo/docker-compose.yml            # Docker configuratie
~/ehrbase-demo/sensire_wound_care.opt        # Huidige OPT template
~/ehrbase-demo/archetypes/international/     # CKM archetypes
~/ehrbase-demo/archetypes/sensire/           # Eigen archetypes
~/ehrbase-demo/templates/                    # Template bronbestanden
~/ehrbase-demo/webtemplates/                 # WebTemplate JSON
~/ehrbase-demo/frontend/sensire-app/         # Alle demo-pagina's
```

## 12.7 Nuttige URLs

- EHRbase documentatie: https://docs.ehrbase.org
- openEHR CKM: https://ckm.openehr.org/ckm/
- Archetype Designer: https://tools.openehr.org/designer/
- CKM GitHub mirror: https://github.com/openEHR/CKM-mirror
- Medblocks UI docs: https://medblocks.com/docs/medblocks-ui
- EHRbase GitHub: https://github.com/ehrbase/ehrbase
- Nictiz ZIBs: https://zibs.nl
- WCS wondzorg: https://wcs.nl

---

# Appendix A: Bekende Problemen en Oplossingen

Uit de implementatiesessie van 16 maart 2026.

| Probleem | Oorzaak | Oplossing |
|:---------|:--------|:----------|
| Docker repo 404 | Plan gebruikte Ubuntu repo, systeem is Debian Trixie | Gebruik `download.docker.com/linux/debian` |
| CKM zoekresultaat: 0 | Filter stond op "Active" i.p.v. "Published" | Klik op "Published" radiobutton |
| ankle_brachial_index niet in CKM | Staat niet in internationale CKM | Zelf maken in Archetype Designer als OBSERVATION |
| git clone vraagt login | Geen SSH-key of token | Gebruik Personal Access Token |
| EHR aanmaken: Bad Request | EHRbase v2 vereist archetype_node_id en subject | Gebruik volledige body met PARTY_SELF |
| Template upload: 404 | Root archetype (COMPOSITION.encounter) ontbreekt | Eerst encounter.v1.adl importeren |
| form.data is undefined | Medblocks v0.0.211 | Gebruik `form.export()` i.p.v. `form.data` |
| POST compositie: 415 | Verkeerde Content-Type | Gebruik `application/json` met `?format=FLAT` |
| POST compositie: 422 | health_risk verplicht veld ontbreekt | Voeg health_risk|value, |code, |terminology toe |
| ecis/v1/composition: 404 | EHRbase v2 heeft ecis verwijderd | Gebruik `/rest/openehr/v1/ehr/{ehr_id}/composition?format=FLAT` |

---

# Appendix B: Veelgestelde Vragen

## Kan dit allemaal op een Chromebox?

Ja. EHRbase + PostgreSQL vereisen samen ~1-2 GB RAM. Een moderne Chromebox met 4-8 GB loopt dit prima. Aandachtspunt: gebruik de Debian Docker repo (niet Ubuntu).

## Hoe verhoudt openEHR zich tot FHIR?

FHIR (HL7) is gericht op uitwisseling van berichten; openEHR is gericht op persistente, semantisch rijke opslag. Ze zijn complementair: openEHR voor de CDR (persistentie en semantiek), FHIR voor uitwisseling met externe systemen. Nictiz werkt aan NL ZIB-gebaseerde FHIR-profielen die goed aansluiten op openEHR.

## Waarom geen GDL2?

GDL2 is ontworpen als server-side rule engine voor geautomatiseerde klinische beslissingsondersteuning (CDS). Voor interactieve formulieren en beslisbomen is het te zwaar en te traag. De open-source tooling is onvoldoende mature. JavaScript in de browser is sneller te bouwen, directer voor de gebruiker, en de opgeslagen data is identiek. GDL2 kan later alsnog worden toegevoegd als de use-case dat vereist — de data verandert niet.

## Kunnen de Sensire-archetypes bijdragen aan de internationale community?

Absoluut. `CLUSTER.stemmer_sign.v0`, `CLUSTER.wcs_wound_classification.v0` en `CLUSTER.altis_pain_score.v0` bestaan nog nergens als formeel openEHR archetype. Door ze in het Engels te bouwen en in te dienen bij CKM, kan Sensire een lichtend voorbeeld zijn — vergelijkbaar met Noorse en Australische zorgaanbieders.

## Wat is het meest intelligente pad als ik iets verkeerd begrijp?

(1) CKM plunderen voor bestaande archetypes, (2) pas als iets echt ontbreekt een eigen archetype maken, (3) alles samenstellen in een template, (4) template uploaden naar EHRbase, (5) WebTemplate ophalen voor de frontend. De tools doen het zware werk — jij definieert de klinische inhoud.

---

*Sensire / Instituut Bedrijfskunde — openEHR Demo Blueprint v4.0 — Maart 2026*
