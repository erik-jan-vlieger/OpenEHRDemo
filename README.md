# 🏥 OpenEHRDemo — Sensire Wondzorg

Een werkende openEHR demo-omgeving voor wondzorg bij [Sensire](https://www.sensire.nl) (thuiszorgorganisatie). Demonstreert het volledige openEHR concept: van internationale archetype-modellering tot patiëntdata-invoer via klinische beslisbomen, met opslag in een openEHR Clinical Data Repository en bevraging via AQL.

## Wat kun je zien?

- **Drie klinische beslisbomen**: Ulcus Cruris, Diabetische Voet, Algemeen Wondprotocol
- **Internationale + eigen archetypes**: CKM hergebruik + 5 Sensire-specifieke uitbreidingen (ADL 1.4)
- **Live data-opslag**: Composities worden als FLAT JSON opgeslagen in EHRbase en bewezen via AQL
- **Klinische beslisondersteuning**: EAI-drempels, Charcot SPOED-detectie, WCS×exsudaat verbandkeuze matrix
- **Volledige transparantie**: pgAdmin en openEHRTool voor visueel bewijs

## Vereisten

- **OS**: Debian Trixie (of vergelijkbare Linux-distributie)
- **RAM**: 4+ GB (EHRbase + PostgreSQL gebruiken ~1-2 GB)
- **Docker**: Wordt geïnstalleerd door `setup.sh` indien nodig
- **Node.js**: 18+ (voor de frontend)

## Snelstart

```bash
# 1. Repository clonen
git clone https://github.com/erik-jan-vlieger/OpenEHRDemo.git
cd OpenEHRDemo

# 2. Alles opzetten (Docker, EHRbase, template, test-EHR)
./setup.sh

# 3. Frontend starten
cd frontend/sensire-app
npm run dev

# 4. Open de demo
#    → http://localhost:5173
```

## Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Demo frontend** | http://localhost:5173 | — |
| **EHRbase REST API** | http://localhost:8080 | `ehrbase-user` / `SuperSecretPassword` |
| **Swagger UI** | http://localhost:8080/ehrbase/swagger-ui/ | (zelfde als EHRbase) |
| **pgAdmin** ¹ | http://localhost:5050 | `demo@sensire.nl` / `demo` |
| **openEHRTool** ¹ | http://localhost:8888 | — |

¹ Start met: `docker compose --profile tools up -d`

## Projectstructuur

```
OpenEHRDemo/
├── docker-compose.yml        # EHRbase + PostgreSQL + tools
├── setup.sh                  # Bootstrap script (Debian-specifiek)
├── Docs/                     # Uitvoeringsplan + Mermaid zorgpaden
├── archetypes/
│   ├── international/        # CKM archetypes (hergebruik)
│   └── sensire/              # Eigen Sensire archetypes
├── templates/                # OPT bestanden
├── webtemplates/             # Webtemplate JSON
├── gdl2/                     # (gereserveerd voor CDS engine)
├── scripts/                  # Hulpscripts (upload, EHR, AQL)
└── frontend/sensire-app/     # Vite frontend demo
```

## Beheer

```bash
# Stack starten
docker compose up -d

# Stack stoppen
docker compose down

# Status controleren
curl -u ehrbase-user:SuperSecretPassword http://localhost:8080/ehrbase/rest/status

# Template opnieuw uploaden
./scripts/upload-template.sh

# AQL query testen
./scripts/test-aql.sh

# Extra tools starten (pgAdmin + openEHRTool)
docker compose --profile tools up -d
```

## Architectuur

| Laag | Component | Doel |
|------|-----------|------|
| **Kennislaag** | Archetypes + Templates | Klinische betekenis vastleggen |
| **Repository-laag** | EHRbase CDR (Docker) | openEHR server met REST API |
| **Beslissingslaag** | JavaScript in browser | Klinische beslislogica (EAI, Charcot, WCS) |
| **Presentatielaag** | Vite frontend | Beslisboom + data-tab + AQL-bewijs |

## Sensire Archetypes

| Archetype | Type | Doel |
|-----------|------|------|
| `ankle_brachial_index.v0` | OBSERVATION | EAI meting + compressieadvies |
| `stemmer_sign.v0` | CLUSTER | Lymfoedeem vs. veneus oedeem |
| `wound_stagnation_assessment.v0` | CLUSTER | Stagnatiebeoordeling + escalatie |
| `wcs_wound_classification.v0` | CLUSTER | WCS kleurenclassificatie |
| `altis_pain_score.v0` | CLUSTER | ALTIS pijnscore |

## Documentatie

Zie de map `Docs/` voor:
- [Uitvoeringsplan v3.0](Docs/2026-03-17%20openEHR_Demo_Uitvoeringsplan_v3.md) — volledig stappenplan
- Mermaid flowcharts van alle drie zorgpaden

## Licentie

Dit project is ontwikkeld voor demonstratiedoeleinden bij Sensire.
