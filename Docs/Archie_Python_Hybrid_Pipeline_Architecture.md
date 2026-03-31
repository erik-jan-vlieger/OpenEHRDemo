# De Hybride Archie/Python OPT-Pipeline 🤖

Dit document beschrijft specifiek de architectuur en de rationale achter de "Toeters en Bellen" van de template compilatie (ADL 1.4 naar OPT 1.4) zoals opgebouwd in dit project. 

EHRbase (onze backend) werkt ten tijde van implementatie (2026) exclusief met **Operational Templates (OPT) versie 1.4**. Tools die out-of-the-box foutloze OPT's maken aan de hand van het complexe objectmodel zijn schaars. Daarom maken we gebruik van een tweedelig "hybride" proces:

## Waarom een Hybride Pipeline?
1. **De Archie Parser (Java)**: Archie is een open-source Java/Kotlin bibliotheek gesponsord door Nedap. Dit is verreweg de beste parser om ADL-bestanden semantisch correct in het geheugen in te lezen en constraints te reduceren (op basis van AOM2). Archie levert echter standaard OPT versie 2 bestanden af — die EHRbase categorisch weigert te uploaden.
2. **LXML Post-Processing (Python)**: Om de uitvoer van Archie toch compatibel met EHRbase te maken, hebben we Python-scripts ontwikkeld (`scripts/fix_opt14.py`). Deze scripts fungeren als een transformatielaag.

## De 3-Stappen Workflow
Het compileren van `.adlt` of `.oet` templates naar valide `.opt` bestanden gebeurt volledig autonoom in `start_env.sh` (via achterliggende calls of offline via ons `compiler` pakket). 

### Stap 1: Parsen & Vlak Slaan (Java/Archie)
Via de Java-bibliotheek worden het basis-archetype en de daaronder hangende sub-archetypes ingeladen. Archie genereert correct de gereduceerde boomstructuur (bijvoorbeeld het uitsluiten van willekeurige datatypes waar het template een expliciete keuze forceert) en rolt een eerste `XML`-draft uit.
- **Sterkpunt:** Exacte naleving van openEHR validatieregels en Reference Model constraint resolving.

### Stap 2: Schema Correcties (Python LXML)
Het pure XML-uitvoerbestand mist specifieke elementen of naamruimten die EHRbase eist:
- **`at0000` Nodale Injectie**: Sommige C_COMPLEX_OBJECT nodes misten hun verplichte root `node_id`. Het script loopt recursief door de boom en injecteert ontbrekende `node_id="at0000"` attributen in C_ATTRIBUTE takken.
- **Type-Casting Verhelpen**: Archie drukt soms elementen af als standaard `C_OBJECT`, terwijl de strictere validatie van EHRbase verwacht dat dit expliciet afgedwongen typen zijn (zoals `C_COMPLEX_OBJECT`). Python herschrijft de type-classes (`xsi:type`).

### Stap 3: Upload & WebTemplate Generatie (REST / curl)
1. **Upload**: Het resulterende gemodificeerde bestand in `/opts/*.opt` wordt met een simplere `curl -X PUT` (of `POST`) naar `http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4` gepusht.
2. **Download in JSON**: Zodra EHRbase de OPT accepteert, trekt een volgend `curl` script direct het afgewerkte `WebTemplate` eraf (in `.json` formaat) en plaatst het in de `frontend/sensire-app/webtemplates/` directory. Vanaf dat moment kan de frontend en onze 100%-Zekerheid Test-engine het gebruiken ter validatie!

---
> [!TIP]
> **Kritieke Ontwerpfout vermeden:** Het rechtstreeks knutselen of string-replacen binnen XML bestanden zonder formele parser (zoals lxml) leidt altijd tot fatale corruptie van het Operational Template. Verander of overrule de `fix_opt14.py` scriptregels alléén als een specifieke `HTTP 400` foutmelding van EHRbase in de logbestanden staat.
