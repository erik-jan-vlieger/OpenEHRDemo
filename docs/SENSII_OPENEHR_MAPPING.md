# Sensii openEHR Architectuur & Mapping

Dit document beschrijft de volledige openEHR afspiegeling van **Sensii** (`/home/vlieger/Sensii`), het integrale verpleegkundig proces voor de wijkverpleging van Sensire, inclusief de aansluiting op de 164 speciële zorgpaden (regulier en ReAble).

---

## 1. Kernarchitectuur & Positie in het EPD-landschap

Sensii modelleert het complete methodische zorgproces van de wijkverpleegkundige volgens de V&VN-richtlijnen en de Omaha Systematiek. Waar de **Speciële Zorgpaden** fungeren als gespecialiseerde protocollen (bijv. wondzorg, hartfalen, palliatieve sedatie), vormt **Sensii** de overkoepelende klinische en administratieve kapstok waarin alle gegevens samenkomen.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                    SENSIRE SENSIËEL VERPLEEGKUNDIG DOSSIER                       │
│        (sensire_sensii_verpleegkundig_proces_integraal.v1 / Hoofdstuk 1-4)       │
├──────────────────────────┬──────────────────────────┬────────────────────────────┤
│ Hoofdstuk 1: Wie cliënt is│ Hoofdstuk 2: Wat er speelt│ Hoofdstuk 3 & 4: Zorgplan  │
│  - Triage                │  - 11 Gordon patronen    │  - Omaha Zorgplan (4 slots)│
│  - VAG Gesprek           │  - GFI Kwetsbaarheid     │  - Actievlakken & Interv.  │
│  - Eigen regie baseline  │  - Huidige Regietrede    │  - Financiering & Inzet    │
│  - Levensverhaal         │  - Omaha Classificatie   │  - Evaluatie & Herbeoord.  │
└────────────┬─────────────┴────────────┬─────────────┴──────────────┬─────────────┘
             │                          │                            │
             ▼                          ▼                            ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│              164 MODULAIRE SPECIËLE ZORGPADEN (Regulier + ReAble)                │
│   (Diabetische voet, Hartfalen, Decubitus, COPD, Tracheacanule, ReAble ADL, ...) │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Overzicht van de 5 Sensii openEHR Templates

Alle 5 templates zijn beschikbaar als ADLT-broncode in [`templates/`](file:///home/vlieger/OpenEHRDemo/templates/) en gecompileerd naar gevalideerde OPT 1.4 XML in [`opts/`](file:///home/vlieger/OpenEHRDemo/opts/):

| Template ID | Bestand (.adlt / .opt) | Type / Scope | Doel & Inhoud |
| :--- | :--- | :--- | :--- |
| **`sensire_sensii_h1_intake_triage_vag.v1`** | `sensire_sensii_h1_intake_triage_vag.v1` | Encounter Composition | **Hoofdstuk 1: Wie deze cliënt is**<br>Wijkverpleegkundige triage, Verpleegkundig Adviesgesprek (VAG), ordening van lasten, persoonlijke- en netwerkkracht, levensverhaal, behoeften & wensen, start regietrede. |
| **`sensire_sensii_h2_anamnese_diagnostiek.v1`** | `sensire_sensii_h2_anamnese_diagnostiek.v1` | Encounter Composition | **Hoofdstuk 2: Wat er speelt**<br>De 11 Gezondheidspatronen van Gordon, Groningen Frailty Indicator (GFI score 0-15), inschaling regietrede 1-5, Omaha probleemclassificatie voor 4 geprioriteerde gebieden, klinisch redeneren en dilemma's. |
| **`sensire_sensii_h3_zorgplan_inzet.v1`** | `sensire_sensii_h3_zorgplan_inzet.v1` | Encounter Composition | **Hoofdstuk 3: Wat we gaan doen**<br>Omaha zorgplan met de 4 actievlakken, streefscores KBS (Kennis, Gedrag, Status), zorgplaninstructies, financieringskader (Zvw/Wlz/Wmo/PGB/ZIN), geïndiceerde minuten en eHealth inzet. |
| **`sensire_sensii_h4_evaluatie.v1`** | `sensire_sensii_h4_evaluatie.v1` | Encounter Composition | **Hoofdstuk 4: Evaluatie van zorg**<br>Periodieke evaluatie per Omaha aandachtsgebied, evaluatie KBS progressie, hermeting regietrede, GFI hermeting, wensen/doelen evaluatie en vervolgbesluit (continueren/afschalen). |
| **`sensire_sensii_verpleegkundig_proces_integraal.v1`** | `sensire_sensii_verpleegkundig_proces_integraal.v1` | Care Plan / Integral Composition | **Het Integrale Sensii Dossier**<br>Overkoepelende holistische compositie die het complete verpleegkundige proces van intake tot en met evaluatie verenigt. |

---

## 3. Ontwikkelde & Gevalideerde Custom Archetypes

In [`archetypes/custom/`](file:///home/vlieger/OpenEHRDemo/archetypes/custom/) zijn de volgende openEHR archetypes ontwikkeld met volledige tweetalige ondersteuning (`nl` primair, `en` vertaling):

1. **`openEHR-EHR-OBSERVATION.groningen_frailty_indicator_nl.v0.adl`**
   - *Groningen Frailty Indicator (GFI)*: 15 items verdeeld over Fysiek (boodschappen, mobiliteit, ADL, toilet, fitheid, visus, gehoor, gewichtsverlies, polyfarmacie), Cognitief (geheugen), Sociaal (leegte, gemis, verlatenheid) en Psychisch (stemming, angst).
   - Somscore 0 t/m 15 met grenswaarde cutoff $\ge 4$ voor kwetsbaarheid.
2. **`openEHR-EHR-OBSERVATION.self_management_regietrede_nl.v0.adl`**
   - *Regietrede en Zelfredzaamheid*: 5 treden van eigen regie (Trede 1: Regieovername .. Trede 5: Volledige eigen regie).
   - Vergelijkt Sensii motorvoorstel met professioneel oordeel van de verpleegkundige en het cliëntperspectief; legt draagkracht/draaglast balans en start Kennis/Gedrag scores vast.
3. **`openEHR-EHR-EVALUATION.omaha_assessment_nl.v0.adl`**
   - *Omaha System Probleem en Zorgplanbeoordeling*: 4 domeinen, 42 aandachtsgebieden, prioriteitsslots (1 t/m 4), aard van probleem, doelgroep, signalen/symptomen.
   - Volledige KBS 5-puntsschalen (Kennis, Gedrag, Status) voor Baseline, Streefdoel en Evaluatie.
   - De 4 Omaha actiesoorten (1. Adviseren/Instrueren, 2. Behandelen/Procedures, 3. Bewaken/Monitoren, 4. Casemanagement/Samenwerken) gekoppeld aan 76 actievlakken.
4. **`openEHR-EHR-OBSERVATION.nursing_gordon_patterns_nl.v0.adl`**
   - *Gezondheidspatronen van Gordon Anamnese*: De 11 functionele gezondheidspatronen van Marjory Gordon met risicomarkeringen en klinische observaties.
5. **`openEHR-EHR-EVALUATION.triage_nursing_nl.v0.adl`**
   - *Wijkverpleegkundige Triage*: Passendheid voor wijkverpleging, urgentiecategorieën (planbaar, dringend, urgent), type zorgrelatie (Langer thuis route vs kortdurend herstel) en vervolgadvies.
6. **`openEHR-EHR-EVALUATION.nursing_vag_nl.v0.adl`**
   - *Verpleegkundig Adviesgesprek (VAG)*: Cliënthulpvraag, gewenste situatie, persoonlijke kracht, netwerkkracht, mantelzorgbelasting en ordening van lasten.
7. **`openEHR-EHR-ADMIN_ENTRY.care_funding_delivery_nl.v0.adl`**
   - *Zorgfinanciering en leveringsvorm*: Wettelijk kader (Zvw, Wlz, Wmo, Jeugdwet), leveringsvorm (ZIN, PGB, VPT, MPT), zorgomvang in minuten/week en inzet van eHealth/beeldschermzorg.

---

## 4. Samenhang met de Speciële Zorgpaden & ReAble Varianten

Wanneer een cliënt in Sensii wordt gediagnosticeerd op een specifiek verpleegkundig domein (bijvoorbeeld Omaha aandachtsgebied *Huid*, *Uitscheiding* of *Ademhaling*), start het corresponderende speciële zorgpad:

```
[Sensii Hoofdstuk 2: Omaha Probleemselectie]
          │
          ├──> Probleem = "Huid" ──> Zorgpad: openEHR-EHR-COMPOSITION.sensire_w5_diabetische_voet_triage_o.v1
          │                                 of openEHR-EHR-COMPOSITION.sensire_w20_decubitus.v1
          │
          ├──> Probleem = "Medicatie" ─> Zorgpad: openEHR-EHR-COMPOSITION.sensire_n26_medicatie_management_stri_reable.v1
          │                                 (ReAble variant gericht op zelftoediening / herstel)
          │
          └──> Probleem = "Mobiliteit" ─> Zorgpad: openEHR-EHR-COMPOSITION.sensire_n14_valpreventie_multifactori_reable.v1
```

De uitkomsten en metingen van deze speciële zorgpaden vloeien automatisch terug in de evaluatiecyclus (Hoofdstuk 4) van Sensii, waar de KBS-scores en regietrede opnieuw worden gewogen.

---

## 5. Technische Validatiestatus

- **Archie ADLT Flattener**: Alle 5 Sensii templates compileren zonder fouten naar operational templates.
- **OPT 1.4 XML Generator (`full_opt14_lxml.py`)**: 100% compliant met openEHR Release 1.0.4 / 1.1.0 specificaties.
- **EHRbase REST API Ready**: Alle templates kunnen direct via `POST /definition/template/adl1.4` worden ingeladen in het openEHR platform.
