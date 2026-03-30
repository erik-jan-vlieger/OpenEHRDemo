# OpenEHR OPT Compilatie — Kennisdocument Sensire

## Doel
Genereren van valide OPT 1.4 XML bestanden vanuit ADL 1.4 archetypes, zodat ze via de EHRbase REST API geregistreerd kunnen worden als klinische templates.

---

## Projectstructuur

### Twee parallelle compiler-projecten

**1. Maven compiler (tools/opt-compiler/)**
```
/home/vlieger/OpenEHRDemo/tools/opt-compiler/
├── pom.xml                          # Maven config met archie 3.17.0
├── src/main/java/nl/sensire/opt/
│   └── OPTCompiler.java             # CLI: java -jar opt-compiler.jar <adl-dir> <template.adl> <output.opt>
└── target/opt-compiler-1.0.0.jar   # Uber-JAR (29MB)
```

**2. Gradle project (sensire-openehr/)**
```
/home/vlieger/OpenEHRDemo/sensire-openehr/sensire-openehr/
├── build.gradle
├── archetypes/       # 33 ADL 1.4 bestanden
├── templates/        # 3 .adlt bestanden (ADL 2 template formaat)
│   ├── Ulcus_Cruris_Assessment_Sensire.v1.adlt
│   ├── Wound_Assessment_Sensire.v1.adlt
│   └── Diabetic_Foot_Assessment_Sensire.v1.adlt
├── opts/             # Output: gegenereerde OPT XML bestanden
└── src/main/java/nl/sensire/openehr/
    ├── OPTGenerator.java
    └── ArchetypeValidator.java
```

---

## Kernkennis: Twee verschillende ADL formaten

| Formaat | Keyword | Parser | Bestanden |
|---------|---------|--------|-----------|
| **ADL 1.4** | `archetype (adl_version=1.4; ...)` | `ADL14Parser` | Internationale CKM archetypes, eigen Sensire archetypes |
| **ADL 2 template** | `template (adl_version=2.0.6; ...)` | `ADLParser` (ADL2) | `.adlt` template bestanden |

**Kritieke fout:** De originele code gebruikte overal `ADLParser` (ADL2-only). Die verwerpt alle ADL 1.4 bestanden met `"Error: Encountered metadata tag 'adl_version' with an invalid version id: 1.4"`.

**Oplossing:** Gebruik twee parsers:
- `ADL14Parser` voor `.adl` archetypes (ADL 1.4)
- `ADLParser` voor `.adlt` templates (ADL 2.0.6)

---

## Archie 3.17.0 API — Correcte aanpak

### Dependencies (Maven/Gradle)
```xml
<!-- Maven -->
<dependency>
    <groupId>com.nedap.healthcare.archie</groupId>
    <artifactId>aom</artifactId>
    <version>3.17.0</version>
</dependency>
<dependency>
    <groupId>com.nedap.healthcare.archie</groupId>
    <artifactId>tools</artifactId>
    <version>3.17.0</version>
</dependency>
<dependency>
    <groupId>com.nedap.healthcare.archie</groupId>
    <artifactId>grammars</artifactId>   <!-- Vereist voor ADL14Parser -->
    <version>3.17.0</version>
</dependency>
```

```groovy
// Gradle
implementation 'com.nedap.healthcare.archie:aom:3.17.0'
implementation 'com.nedap.healthcare.archie:tools:3.17.0'
implementation 'com.nedap.healthcare.archie:grammars:3.17.0'
implementation 'com.nedap.healthcare.archie:openehr-rm:3.17.0'
```

### Java code — Correcte pipeline

```java
// Setup (eenmalig)
ReferenceModels referenceModels = new ReferenceModels();
referenceModels.registerModel(ArchieRMInfoLookup.getInstance());
MetaModels metaModels = new MetaModels(referenceModels, null);
ADL14ConversionConfiguration config = new ADL14ConversionConfiguration();
ADL14Parser adl14Parser = new ADL14Parser(metaModels);
InMemoryFullArchetypeRepository repository = new InMemoryFullArchetypeRepository();

// Stap 1: Laad alle ADL 1.4 archetypes in repository
String content = new String(Files.readAllBytes(adlFile), StandardCharsets.UTF_8);
if (content.startsWith("\uFEFF")) content = content.substring(1);  // Strip BOM
content = content.replace("\r\n", "\n");  // CRLF → LF
Archetype archetype = adl14Parser.parse(content, config);
repository.addArchetype(archetype);

// Stap 2: Parse het template (ADL 2 .adlt formaat)
ADLParser adl2Parser = new ADLParser();
Archetype template = adl2Parser.parse(templateContent);
repository.addArchetype(template);

// Stap 3: Flatten naar OPT
Flattener flattener = new Flattener(repository, referenceModels)
    .createOperationalTemplate(true);
OperationalTemplate opt = (OperationalTemplate) flattener.flatten(template);

// Stap 4: Serialiseer naar OPT XML (EHRbase-compatibel)
Marshaller marshaller = JAXBUtil.getArchieJAXBContext().createMarshaller();
marshaller.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, Boolean.TRUE);
marshaller.setProperty(Marshaller.JAXB_ENCODING, "UTF-8");
marshaller.marshal(opt, outputStream);
```

> **Let op:** `SimpleArchetypeRepository` bestaat **niet** in archie 3.x. Gebruik `InMemoryFullArchetypeRepository`.

---

## EHRbase Upload

### Endpoint
```
POST http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4
Content-Type: application/xml;charset=UTF-8
Accept: application/json
Authorization: Basic <base64(user:pass)>
```

### Vereist formaat
EHRbase verwacht **OPT 1.4 XML** — het `<template xmlns="http://schemas.openehr.org/v1">` formaat.
**NIET** de ADL tekstvorm (`operational_template (adl_version=1.4; generated)`).

### Werkend voorbeeld
```bash
curl -X POST "http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4" \
  -H "Authorization: Basic $(echo -n 'ehrbase-user:SuperSecretPassword' | base64)" \
  -H "Content-Type: application/xml;charset=UTF-8" \
  -H "Accept: application/json" \
  -d "@templates/sensire_wound_care.opt"
```

### HTTP respons bij succes: `201 Created`

---

## Valkuilen & Gevonden Bugs

### 1. Corrupte bestanden (120.864 bytes)
Bestanden die zijn gedownload via Chromebook Files-app kunnen corrupt raken op het 9P/virtiofs filesystem. Symptoom: `cat` of `wc -c` hangt oneindig. Diagnose: `stat` geeft exact 120.864 bytes op `Device: 0,51`.

**Verwijderde mappen (waren allemaal corrupt):**
- `archetypes/` root (12 bestanden)
- `archetypes/ulcus-cruris/` (9 bestanden)
- `archetypes/wond/` (alle bestanden)
- `archetypes/diabetische-voet/` (alle bestanden)

**Leesbare, correcte mappen:**
- `archetypes/uc/` (14 bestanden)
- `archetypes/international/` (6 bestanden)
- `archetypes/sensire/` (5 bestanden)

### 2. BOM en CRLF
Internationale CKM archetypes kunnen UTF-8 BOM en/of Windows CRLF line endings hebben. De ADL14Parser faalt hierop met `token recognition error at: '﻿'`.

**Fix in Java:**
```java
if (content.startsWith("\uFEFF")) content = content.substring(1);
content = content.replace("\r\n", "\n");
```

### 3. Gradle + Java 21
Gradle 8.7 vereist `sourceCompatibility = '21'` (niet `'17'`) en `targetCompatibility = '21'` om correct te werken met Java 21.0.10.

### 4. ADLArchetypeSerializer geeft ADL tekst, niet XML
`com.nedap.archie.serializer.adl.ADLArchetypeSerializer` (en `ADLOperationalTemplateSerializer`) genereert het ADL tekst-formaat, niet de OPT XML die EHRbase verwacht. Gebruik `JAXBUtil.getArchieJAXBContext().createMarshaller()` voor XML.

### 5. Maven Gradle wrapper versie
Het project had `gradle-6.x` waardoor Java 21 niet ondersteund werd. Fix: `sed -i 's|gradle-.*-bin.zip|gradle-8.7-bin.zip|' gradle/wrapper/gradle-wrapper.properties`

---

## Gegenereerde OPT bestanden (in templates/)

| Bestand | Grootte | Status | Formaat |
|---------|---------|--------|---------|
| `sensire_wound_care.opt` | 185KB | ✅ Werkend in EHRbase | XML `<template xmlns=...>` |
| `ulcus_cruris_assessment_sensire.opt` | 175KB | ⚠️ Dubbel xmlns:xsi | XML (bug in generator) |
| `ulcus_cruris_sensire_v2.opt` | 189KB | ✅ Correcte XML | Gegenereerd door Python script |
| `ulcus_cruris_sensire.opt` | 44KB | ❌ Verkeerd formaat | ADL tekst (niet XML) |

---

## Python Alternatief (tools/generate_uc_opt_xml.py)

Als de Java pipeline problemen geeft, kan ook puur Python de OPT XML genereren met `xml.etree.ElementTree`. Dit werkt direct zonder Java en genereert de correcte `<template xmlns="http://schemas.openehr.org/v1">` structuur.

```bash
python3 tools/generate_uc_opt_xml.py
# Genereert: templates/ulcus_cruris_sensire_v2.opt
```

---

## Gradle Taken

```bash
cd /home/vlieger/OpenEHRDemo/sensire-openehr/sensire-openehr

./gradlew validateArchetypes   # Valideer alle 33 ADL archetypes (Result: 33/33 ✅)
./gradlew generateOPT          # Genereer OPT XML voor alle 3 templates
./gradlew compileJava          # Compileer Java bronbestanden
```

### Validatie resultaat (na ADL14Parser fix)
```
Totaal:  33
Geldig:  33
Fouten:  0
✓ Alle archetypes zijn geldig.
```

---

## EHRbase 500 Errors & AOM2 vs OPT 1.4 XMLBeans Parsing

Het genereren van OPTs via de standaard Archie toolchain levert *AOM2* gebaseerde XML structuur op. EHRbase gebruikt echter Apache XMLBeans ontworpen voor sterke **OPT 1.4** structuurvalidatie. Zonder post-processing geeft uploaden altijd een `HTTP 500 Internal Server Error` met een `NullPointerException` (vaak in `OPTParser.parseCARCHETYPEROOT` of `OPTParser.buildNode`). 

Om Archie XML te converteren naar EHRbase OPT 1.4 XML moeten drie structurele wijzigingen worden doorgevoerd (momenteel gedaan via `full_opt14_lxml.py`):

### 1. `C_ARCHETYPE_ROOT` Architectuur Verschillen
* **AOM 2** bewaart type metadata als attributen: `<children xsi:type="C_ARCHETYPE_ROOT" rm_type_name="OBSERVATION" node_id="id4">`
* **OPT 1.4** verwacht expliciete kind-elementen, exact gebaseerd op de XSD Sequence:
  1. `rm_type_name`
  2. `occurrences`
  3. `node_id`
  4. `attributes`
  5. `archetype_id`
  6. `term_definitions`

### 2. Ontbrekende `archetype_id` en `<definition>`
XMLBeans crasht direct bij `CARCHETYPEROOT.getArchetypeId()` als er geen `archetype_id` in de tag staat.
* **AOM 2** gebruikt vaak `archetype_ref`, of negeert het id in child-elements als die aliassen gebruiken (`node_id="id4"`) gemapt via externe `.adlt` mappen. Ook heeft de basis `<definition>` tag zelf vaak geen id.
* **Oplossing**: De compiler leest de originele `.adlt`-mappen (zoekt op `use_archetype`) en injecteert de ontbrekende originele Archetype Codelabels (`openEHR-EHR-...`) handmatig als `<archetype_id><value>...</value></archetype_id>` tags, strikt direct achter `<attributes>`.

### 3. Ontbrekende geneste `term_definitions` (Crash in `java.util.Map.get()`)
Als *archetype_id* is opgelost, parseert EHRbase de nodes, maar crasht hij op `Map.get(nodeId) is null` in `OPTParser.buildNode`.
* **Issue**: AOM 2 perst *alle vertalingen* van het gehele template in één gigantisch platgeslagen `<terminology>` of `<component_terminologies>` blok onderaan de XML. Maar OPT 1.4 verwacht dat specifieke termen *diep lokaal genest* zitten in elke individuele `<children xsi:type="C_ARCHETYPE_ROOT">`. Bovendien hernoemt de AOM2 root compositie zijn anker-archetypes intern naar id's als `id4`, wat crasht met de subarchetype codes die op `at0000` rekenen.
* **Oplossing**: Het script (`full_opt14_lxml.py`):
    - Parset en wist de globale terminology blokken in AOM2.
    - Transformeert deze (`items` inside `items`) naar de OPT 1.4 structuur `<term_definitions code="at0000">`.
    - Injecteert deze lokaal direct ónder elke `C_ARCHETYPE_ROOT` (en injecteert specifiek ge-aliaste idX termen als safety-net, mocht EHRbase daarnaar zoeken).
