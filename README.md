# 🏥 OpenEHRDemo — Sensire Zorgpaden & Sensii EPD Architectuur

Een complete openEHR demo- en referentie-omgeving voor wijkverpleging en specialistische zorgpaden bij [Sensire](https://www.sensire.nl). Demonstreert het volledige openEHR concept: van internationale en nationale archetype-modellering (ZIB / SNOMED CT / Omaha System) tot het integrale **Sensii Verpleegkundig Dossier** en **164 specialistische & ReAble zorgpaden**, met opslag in een openEHR Clinical Data Repository (EHRbase) en bevraging via AQL.

---

## 🌟 Belangrijkste Functionaliteiten

1. **Sensii Integraal Verpleegkundig Dossier** ([`docs/SENSII_OPENEHR_MAPPING.md`](file:///home/vlieger/OpenEHRDemo/docs/SENSII_OPENEHR_MAPPING.md)):
   - **Hoofdstuk 1: Wie deze cliënt is** — Triage, Verpleegkundig Adviesgesprek (VAG), ordening van lasten, levensverhaal, persoonlijke kracht & netwerkkracht.
   - **Hoofdstuk 2: Wat er speelt** — 11 Gezondheidspatronen van Gordon, Groningen Frailty Indicator (GFI score 0-15), regietrede 1-5, Omaha probleemclassificatie (4 prioriteitsslots) en klinisch redeneren.
   - **Hoofdstuk 3: Wat we gaan doen** — Omaha Zorgplan met 4 actievlakken, streefscores KBS (Kennis, Gedrag, Status), financieringskader (Zvw/Wlz/Wmo) en leveringsvormen (ZIN/PGB/VPT/MPT).
   - **Hoofdstuk 4: Evaluatie van zorg** — Periodieke herbeoordeling van KBS-scores, groei in zelfregie, hermeting van kwetsbaarheid en evaluatie van cliëntdoelen.
   - **Integraal Verpleegkundig Proces** — Holistische overkoepelende compositie waarin alle fasen samenkomen.

2. **164 Specialistische Zorgpaden (Regulier + ReAble)**:
   - 148 reguliere en 16 ReAble-geactiveerde zorgpaden (Hartfalen, COPD, Diabetische voet, Decubitus, Tracheacanule, Zelfredzaamheid ADL, Valpreventie, etc.).
   - ReAble varianten leggen nadruk op zelfmanagement, mantelzorgtraining en gerichte afbouwschema's via `ACTION.health_education` en `INSTRUCTION.care_plan_request`.

3. **Strikte Terminologiecascade** ([`TERMINOLOGIE_CASCADE.md`](file:///home/vlieger/OpenEHRDemo/TERMINOLOGIE_CASCADE.md)):
   - 5-staps terminologiebeleid: 1. Nictiz ZIBs → 2. SNOMED CT NL → 3. openEHR CKM → 4. V&VN / Omaha NL → 5. Zorgpad Fallback.

4. **100% Validatie & Compilatie Pipeline**:
   - Geautomatiseerde ADLT → OPT 1.4 XML compilatie via Nedap Archie (v3.17.0) en Python postprocessing ([`compiler/full_opt14_lxml.py`](file:///home/vlieger/OpenEHRDemo/compiler/full_opt14_lxml.py)).
   - Volledig compatibel met openEHR Release 1.0.4 / 1.1.0 en EHRbase CDR.

---

## 🚀 Snelstart

```bash
# 1. Start de Docker stack (EHRbase, PostgreSQL, pgAdmin, GDL2)
./start_env.sh

# 2. Batch generatie en compilatie van zorgpaden
python3 scripts/generate_carepath_openehr.py --all

# 3. Compilatie van de Sensii templates
cd compiler && ./gradlew generateOPT
```

---

## 📊 Services & Endpoints

| Service | URL | Toegang / Credentials |
| :--- | :--- | :--- |
| **EHRbase REST API** | `http://localhost:8080/ehrbase` | `ehrbase-user` / `SuperSecretPassword` |
| **Swagger UI** | `http://localhost:8080/ehrbase/swagger-ui/` | (zelfde als EHRbase) |
| **PostgreSQL (ehrdb)** | `localhost:5432` | `ehrbase` / `SuperSecretPassword` |
| **pgAdmin 4** | `http://localhost:5050` | `demo@sensire.nl` / `demo` |
| **GDL2 Editor** | `http://localhost:8082` | — |

---

## 📁 Projectstructuur

```
OpenEHRDemo/
├── templates/                # openEHR ADL 2 template definities (.adlt)
├── opts/                     # Gecompileerde openEHR OPT 1.4 XML bestanden (.opt)
├── archetypes/
│   ├── international/        # CKM internationale archetypes (vertaald naar nl)
│   ├── custom/               # Sensii & NL maatwerk archetypes (GFI, Regietrede, Omaha, Gordon, VAG, Triage)
│   └── ckm-mirror/           # Volledige mirror van openEHR CKM catalogus
├── compiler/                 # Java Archie flattener & Python OPT 1.4 postprocessor
├── scripts/                  # Batch generators, indexers en CLI search tools
├── docs/                     # Architectuurdocumentatie (Sensii mapping)
├── TERMINOLOGIE_CASCADE.md   # 5-staps terminologiebeleid
├── metadocumenten.md         # Persistent architectuurhandboek & SSOT
├── metameta.md               # Documentatie-governance & changelog
└── docker-compose.yml        # Docker stack definitie
```

---

## 📚 Documentatie-index

- 📘 [`metadocumenten.md`](file:///home/vlieger/OpenEHRDemo/metadocumenten.md): Het centrale, persistente architectuurhandboek en runbook.
- 📙 [`metameta.md`](file:///home/vlieger/OpenEHRDemo/metameta.md): Documentatie-governance en changelog.
- 📕 [`TERMINOLOGIE_CASCADE.md`](file:///home/vlieger/OpenEHRDemo/TERMINOLOGIE_CASCADE.md): Formeel 5-staps terminologiebeleid.
- 📗 [`docs/SENSII_OPENEHR_MAPPING.md`](file:///home/vlieger/OpenEHRDemo/docs/SENSII_OPENEHR_MAPPING.md): Sensii verpleegkundig proces architectuur en openEHR mapping.
