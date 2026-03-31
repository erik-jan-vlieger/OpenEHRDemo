# Sensire Wondprotocollen — OpenEHR Project

Compleet openEHR-project voor de drie klinische wondprotocollen van Sensire:

1. **Wound_Assessment_Sensire.v1** — Algemeen Wondprotocol
2. **Diabetic_Foot_Assessment_Sensire.v1** — Diabetische Voet Protocol
3. **Ulcus_Cruris_Assessment_Sensire.v1** — Ulcus Cruris Protocol

## Projectstructuur

```
sensire-openehr/
├── archetypes/
│   ├── international/          ← CKM archetypes (te downloaden)
│   │   ├── openEHR-EHR-COMPOSITION.encounter.v1.adl
│   │   ├── openEHR-EHR-EVALUATION.problem_diagnosis.v1.adl
│   │   └── ... (~25 bestanden)
│   └── custom/                 ← Sensire-specifieke archetypes (meegeleverd)
│       ├── openEHR-EHR-CLUSTER.wound_tissue_wcs_nl.v0.adl        (C-1)
│       ├── openEHR-EHR-CLUSTER.exam_diabetic_foot.v0.adl          (C-3)
│       ├── openEHR-EHR-OBSERVATION.monofilament_examination.v0.adl (C-3b)
│       ├── openEHR-EHR-EVALUATION.sims_classification_nl.v0.adl   (C-3c)
│       └── openEHR-EHR-CLUSTER.exam_stemmer_test.v0.adl           (C-5)
├── templates/                  ← ADL2 templates (meegeleverd)
│   ├── Wound_Assessment_Sensire.v1.adlt
│   ├── Diabetic_Foot_Assessment_Sensire.v1.adlt
│   └── Ulcus_Cruris_Assessment_Sensire.v1.adlt
├── opts/                       ← Gegenereerde OPT bestanden (output)
├── src/main/java/              ← Java broncode voor OPT-generatie
├── scripts/
│   └── download_ckm_archetypes.sh
├── build.gradle
├── settings.gradle
└── README.md
```

## Vereisten

- **Java 17+** (OpenJDK 17 of 21 aanbevolen)
- **Gradle** (wordt automatisch gedownload via wrapper als je die installeert)
- **Internettoegang** voor het downloaden van archetypes en Maven dependencies

### Java installeren (indien nodig)

```bash
# Ubuntu/Debian
sudo apt install openjdk-21-jdk

# macOS (Homebrew)
brew install openjdk@21

# Controleer
java -version
```

### Gradle Wrapper installeren

```bash
# Als je Gradle al hebt:
cd sensire-openehr
gradle wrapper

# Of handmatig de wrapper downloaden:
# Ga naar https://gradle.org/install/ en volg de instructies
# Voer daarna uit: gradle wrapper
```

## Stapsgewijze instructies

### Stap 1: Internationale archetypes downloaden

```bash
chmod +x scripts/download_ckm_archetypes.sh
./scripts/download_ckm_archetypes.sh
```

Dit downloadt ~20 published archetypes uit de openEHR CKM GitHub-mirror.

**Handmatig te downloaden** (incubator/draft, niet in GitHub-mirror):

| Archetype | Bron | Instructie |
|-----------|------|------------|
| `CLUSTER.exam_wound` | CKM Incubator | Zoek "exam wound" op https://ckm.openehr.org |
| `CLUSTER.wound_assertion_details` | CKM Incubator | Zoek "wound assertion" |
| `OBSERVATION.diabetic_wound_wagner.v0` | CKM Incubator | Zoek "Wagner" |
| `OBSERVATION.ankle_brachial_pressure_index.v0` | Noorse CKM | https://arketyper.no/ckm/ → zoek "ABPI" |
| `OBSERVATION.pain_scale.v0` | CKM Draft | Zoek "pain scale" |

Plaats alle gedownloade .adl-bestanden in `archetypes/international/`.

### Stap 2: Archetypes valideren

```bash
./gradlew validateArchetypes
```

Dit parseert alle ADL-bestanden en rapporteert eventuele fouten.

### Stap 3: OPT bestanden genereren

```bash
./gradlew generateOPT
```

De drie OPT-bestanden verschijnen in de `opts/` directory:
- `Wound_Assessment_Sensire.v1.opt`
- `Diabetic_Foot_Assessment_Sensire.v1.opt`
- `Ulcus_Cruris_Assessment_Sensire.v1.opt`

### Stap 4: OPT uploaden naar EHRbase

```bash
# Upload elk OPT naar je EHRbase-instantie
curl -X POST \
  http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4 \
  -H "Content-Type: application/xml" \
  -d @opts/Wound_Assessment_Sensire.v1.opt

curl -X POST \
  http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4 \
  -H "Content-Type: application/xml" \
  -d @opts/Diabetic_Foot_Assessment_Sensire.v1.opt

curl -X POST \
  http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4 \
  -H "Content-Type: application/xml" \
  -d @opts/Ulcus_Cruris_Assessment_Sensire.v1.opt
```

## Custom archetypes — overzicht

### C-1: `CLUSTER.wound_tissue_wcs_nl.v0`
**WCS-kleurclassificatie wondbed** — Registreert de primaire, secundaire en
tertiaire weefselkleur (Zwart/Geel/Rood) plus percentages per kleur en
epithelialisatie (Roze). Plugt in het 'Specific details'-slot van
`CLUSTER.exam_wound`.

### C-3: `CLUSTER.exam_diabetic_foot.v0`
**Diabetische voetinspectie** — Bilateraal: huidkleur, temperatuur
(met asymmetrie-flag), eelt, fissuren, standsafwijkingen, pulsaties
(a. dorsalis pedis + a. tibialis posterior), nagels, oedeem,
schoeisel-beoordeling, Charcot-vermoeden.

### C-3b: `OBSERVATION.monofilament_examination.v0`
**Semmes-Weinstein 10g monofilament-test** — 8-punts plantaire
locatiematrix per voet (hallux, 3 metatarsaalkoppen, 2 middenvoet,
2 hiel), totaalscore (0-8), PS-verlies boolean. Levert input voor
Sims-berekening via GDL2.

### C-3c: `EVALUATION.sims_classification_nl.v0`
**Sims-risicoclassificatie** — Ordinale uitslag (categorie 0-3) met
onderliggende factoren (PS-verlies, PAV, standsafwijkingen,
ulcushistorie, amputatiehistorie, Charcot-VG). Bepaalt
controlefrequentie.

### C-5: `CLUSTER.exam_stemmer_test.v0`
**Stemmer-test** — Resultaat (positief/negatief), testlocatie
(2e teen dorsaal), interpretatie (lymfoedeem vs veneus oedeem).

## Taalondersteuning

Alle custom archetypes en templates zijn tweetalig (nl + en), met
Nederlands als primaire taal. De internationale archetypes uit CKM zijn
in het Engels; de NL-vertalingen kunnen worden toegevoegd als
template-constraint of via het CKM-vertaalproces (actie C-6 uit het
mapping-document).

## GDL2 beslisregels

De drie GDL2-bestanden (`sensire_*_v2_gdl2.json`) bevatten de
klinische beslislogica die refereert aan de archetype-paden in deze
templates. Zij worden apart gedeployd naar een CDS-engine
(bijv. GDL2 Reference Implementation of CDS Hooks).

## Volgende stappen

1. **C-6**: NL-vertalingen toevoegen voor internationale archetypes
2. **C-7**: SNOMED-CT terminologiebindings (371087003, 420101004, etc.)
3. **Testcomposities**: Voorbeeld-JSON per template genereren
4. **AQL-queries**: Voorbeeldqueries schrijven voor rapportage
5. **FHIR-bridge**: Terugmapping naar ZIB FHIR-profielen

## Licentie

Custom archetypes: Creative Commons Attribution-ShareAlike 4.0
Internationale archetypes: Zie individuele licenties in CKM
