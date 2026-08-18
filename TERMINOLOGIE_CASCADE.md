# Terminologie & Vertalingsbeleid: De 5-Staps Cascade

Dit document beschrijft de formele methodiek en beslisboom voor de Nederlandse terminologie, vertalingen en archetype-annotaties binnen het **OpenEHRDemo** project (Sensire Zorgpaden & ReAblement).

---

## Doel en Filosofie

openEHR archetypes zijn van oorsprong internationaal gemodelleerd in het Engels (`en`). Om te zorgen voor een naadloze aansluiting op de Nederlandse zorgpraktijk, het Elektronisch Patiëntendossier (EPD/ECD) en landelijke gegevensuitwisseling (Wegiz / CumuluZ), hanteert dit project een strikt **5-staps cascademodel** voor terminologie en vertalingen.

Wanneer een concept, archetype, data-element of keuzelijst vertaald of gemapt moet worden, wordt onderstaande prioritering doorlopen:

```
┌─────────────────────────────────────────────────────────────┐
│  Niveau 1: Nictiz ZIBs (Zorginformatiebouwstenen)           │
├─────────────────────────────────────────────────────────────┤
│  Niveau 2: SNOMED CT (Nederlandse Editie / Nictiz NRC)      │
├─────────────────────────────────────────────────────────────┤
│  Niveau 3: openEHR CKM Peer-Reviewed Vertalingen (NL)       │
├─────────────────────────────────────────────────────────────┤
│  Niveau 4: V&VN Richtlijnen & Beroepsstandaarden (Wijkzorg) │
├─────────────────────────────────────────────────────────────┤
│  Niveau 5: Specifieke Zorgpad Terminologie (Fallback)       │
└─────────────────────────────────────────────────────────────┘
```

---

## De 5 Stappen in Detail

### 1. Niveau 1: Nictiz ZIBs (Zorginformatiebouwstenen)
* **Bron**: [Nictiz ZIB Centrum](https://zibs.nl) / Health RI (bijv. ZIB Release 2020 / 2024).
* **Rol**: De officiële landelijke informatiestandaard voor de Nederlandse gezondheidszorg.
* **Toepassing**: 
  - Vaste Nederlandse veldnamen en conceptdefinities (bijv. *Verrichting*, *Doel*, *Probleem/Diagnose*, *Contact*, *Zelfmanagement*, *Behandelaanwijzing*).
  - Veldaliassen en mapping met ZIB-concepten via openEHR slots en archetypes.

### 2. Niveau 2: SNOMED CT (Nederlandse Editie)
* **Bron**: Nationaal Release Center (NRC) bij Nictiz / SNOMED International.
* **Rol**: De officiële semantische terminologiestandaard voor klinische concepten in Nederland.
* **Toepassing**:
  - Gecodeerde waardelijsten, diagnoses, symptomen, verrichtingen en interventies.
  - Officiële Nederlandse Fully Specified Name (FSN) en Preferred Terms (PT) worden overgenomen in `term_definitions["nl"]` en `bindings`.

### 3. Niveau 3: openEHR CKM Peer-Reviewed Vertalingen
* **Bron**: [openEHR Clinical Knowledge Manager (CKM)](https://ckm.openehr.org) en openEHR Nederland.
* **Rol**: Door klinische experts en informatici gereviewde en geautoriseerde Nederlandse archetype-vertalingen (o.a. aangedragen door Nedap Healthcare, Code24, UMC's en openEHR NL).
* **Toepassing**:
  - `ontology.term_definitions["nl"]` blokken voor internationale basis-archetypes (`COMPOSITION.encounter`, `OBSERVATION.blood_pressure`, `CLUSTER.anatomical_location`, `ACTION.health_education`, etc.).

### 4. Niveau 4: V&VN Richtlijnen & Beroepsstandaarden
* **Bron**: Verpleegkundigen & Verzorgenden Nederland (V&VN), NANDA-I, NIC, NOC, Omaha System.
* **Rol**: De professionele verpleegkundige vaktaal voor de wijkverpleging, extramurale zorg en ReAblement.
* **Toepassing**:
  - Specifieke terminologie rondom zelfredzaamheid, leefstijl, functionele status, mantelzorgbelasting en verpleegkundige indicatiestelling.

### 5. Niveau 5: Specifieke Zorgpad Terminologie (Fallback)
* **Bron**: De inhoudelijke zorgpadspecificaties, Mermaid processen en beslisbomen uit `SensireSpecieleBeslisOndersteuning`.
* **Rol**: **Leidende fallback** wanneer géén van de officiële bovenstaande standaarden een passend concept of formulering biedt.
* **Toepassing**:
  - Letterlijke formulering van **"Wat wil de cliënt?"** vragen (de 'wil-vraag' binnen ReAblement).
  - Specifieke lokale procesafspraken, instructies voor wijkverpleegkundigen, of Sensire-eigen coachingsinterventies.
  - Vrije tekst labels en specifieke actiebeschrijvingen in templates.

---

## Toepassing in dit Project

1. **Archetypes (`archetypes/international/` & `archetypes/custom/`)**:
   - Alle kernarchetypes bevatten een formele `translations["nl"]`, `description.details["nl"]` en `ontology.term_definitions["nl"]`.
   - Archetypes die niet in CKM vertaald waren (zoals `ACTION.health_education.v1`, `INSTRUCTION.care_plan_request.v0`, `ACTION.care_plan.v0`, `EVALUATION.clinical_synopsis.v1`) zijn conform niveau 1 t/m 4 vertaald.

2. **Templates (`templates/*.adlt`)**:
   - Templates erven de `["nl"]` terminologie uit de onderliggende archetypes.
   - Lokale verbijzonderingen en ReAblement-elementen worden via niveau 5 geannoteerd.

3. **Operationele Templates (`opts/*.opt`)**:
   - De gegenereerde OPT 1.4 XML-bestanden bevatten volledige `term_definitions` voor zowel de `en` (originele taal) als `nl` (Nederlandse doeltaal), waardoor EPD-systemen direct Nederlandstalige formulieren kunnen renderen.
