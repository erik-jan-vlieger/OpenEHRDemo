🏥

**openEHR Demo-omgeving**

Sensire Wondzorg — Volledig Uitvoeringsplan

*Versie 3.0  |  Debian Trixie / Chromebox  |  Maart 2026*

*Opgesteld op basis van:*

*Oorspronkelijk stappenplan v1.0 (Claude, maart 2026\)*

*Ervaringen en correcties uit implementatiesessie d.d. 16 maart 2026*

*Definitieve versie v3.0 — inclusief taalstrategie EN→NL en drie zorgpaden*

| ✅  Werkende demo bereikt op Chromebox met EHRbase v2.29.0 Docker \+ EHRbase draait op Debian Trixie Template sensire\_wound\_care geüpload en werkend Ulcus Cruris beslisboom volledig werkend als HTML demo-pagina Composities worden opgeslagen via FLAT JSON \+ bevestigd via AQL |
| :---- |

# **1\. Doel en Context**

## **1.1 Wat willen we bereiken?**

Het doel is een lokale, volledig werkende openEHR demo-omgeving opzetten op een Chromebox met Debian Linux. De omgeving toont het volledige concept levend: van internationale archetype-modellering tot patiëntdata-invoer via een beslisboom, met opslag in een lokaal openEHR EPD en bevraging via AQL.

De demo is bedoeld voor Sensire-collega's en stakeholders die nog niet bekend zijn met openEHR. Het moet aanschouwelijk maken:

* Waarom openEHR beter is dan een traditionele database voor klinische data

* Hoe internationale standaarden (CKM archetypes) gecombineerd worden met eigen klinische content (Sensire-specifieke archetypes)

* Hoe beslisondersteuning (Ulcus Cruris, Diabetische Voet, Algemeen Wondprotocol) kan worden geformaliseerd en gekoppeld aan openEHR data

* Dat data onafhankelijk van de applicatie bevraagbaar is via AQL — de kern van interoperabiliteit

* Hoe een Engelse archetype-basis vertaald wordt naar een Nederlandse interface — zonder de internationale semantiek te verliezen

## **1.2 Architectuur in vier lagen**

| Laag | Component | Doel |
| :---- | :---- | :---- |
| Kennislaag | Archetypes \+ Templates | Klinische betekenis vastleggen (CKM \+ eigen) |
| Repository-laag | EHRbase CDR (Docker) | openEHR server met REST API en Swagger UI |
| Beslissingslaag | GDL2 regels | Formele klinische beslislogica (EAI, compressie) |
| Presentatielaag | Browser demo-pagina | Beslisboom \+ formulier \+ AQL-bewijs |

## **1.3 Componentoverzicht**

Alle componenten van de complete stack, inclusief doel en hoe ze draaien:

| Component | Wat is het? | Waarom nodig? | Docker? |
| :---- | :---- | :---- | :---- |
| EHRbase | openEHR CDR — de 'database' voor alle openEHR records | Centrale opslag van archetypes, templates en patiëntcomposities. REST API voor alle interacties. | ✅ Ja |
| PostgreSQL | Relationele database als opslag backend | EHRbase vereist Postgres als persistentielaag. | ✅ Ja |
| Archetype Designer | Web-app van openEHR Foundation voor archetype- en templatemodellering | Bouw nieuwe archetypes (bv. CLUSTER.stemmer\_sign.v0) en templates voor jouw zorgpaden. | 🌐 Online |
| openEHR CKM | Clinical Knowledge Manager — internationale archetype-bibliotheek | Download bestaande internationale archetypen. Basis voor jouw implementatie. | 🌐 Online |
| Medblocks UI | Open-source web component library voor openEHR formulieren | Automatisch browser-formulieren genereren vanuit een openEHR template. | ✅ Lokaal |
| GDL2 Editor | Java-gebaseerde tool voor het schrijven en testen van beslisregels | Schrijf en test klinische beslislogica (EAI-drempelwaarden, compressiebeslissingen, escalatieregels). | ✅ Docker |
| pgAdmin | Grafische PostgreSQL browser | Visueel bewijs dat openEHR data echt in de database staat. Krachtig voor sceptische collega's. | ✅ Docker |
| Swagger UI | Grafische API-browser van EHRbase | Bekijk en test alle endpoints. Ideaal om aan collega's te demonstreren wat het systeem doet. | ⬜ Ingebouwd |
| openEHRTool | Open-source GUI browser voor EHRbase (github.com/crs4/openEHRTool) | Interactief browsen van EHRs, composities en templates voor niet-technische collega's. | ✅ Docker |

## **1.4 Wat is er al bereikt? (sessie 16 maart 2026\)**

| ✅  Bereikt ✅ Docker \+ EHRbase v2.29.0 draait op Chromebox (Debian Trixie) ✅ 5 internationale CKM archetypes gedownload en geïmporteerd in Archetype Designer ✅ Template sensire\_wound\_care gebouwd en geüpload naar EHRbase ✅ Test-EHR aangemaakt (EHR-ID: 196bbbe9-24b5-479a-a7aa-596bdf8a56c5) ✅ Ulcus Cruris beslisboom als volledig werkende HTML demo-pagina ✅ Composities worden opgeslagen via FLAT JSON POST en bevestigd via AQL |
| :---- |

## **1.5 Wat moet nog gebeuren?**

1. GDL2 beslisondersteuning formeel toevoegen (Stap 5\)

2. Eigen Sensire archetypes bouwen in Archetype Designer (Stap 2B) — met Engelse primaire taal \+ NL vertaling (zie Stap 3\)

3. Template uitbreiden met eigen archetypes (Stap 2C)

4. Demo-pagina's voor Diabetische Voet en Algemeen Wondprotocol toevoegen (Stap 4B \+ 4C)

5. pgAdmin en openEHRTool toevoegen voor visueel bewijs aan collega's (Stap 6\)

6. Git-versiebeheer voor archetypes en templates inrichten (Stap 7\)

7. Navigatiepagina (index) voor alle drie protocols maken (Stap 4D)

# **2\. Technische Omgeving**

## **2.1 Hardware en OS**

De omgeving draait op een Chromebox met Debian Trixie Linux (via Crostini). Alle zware componenten draaien in Docker containers.

| ⚠️  Debian Trixie — NIET Ubuntu De Chromebox draait Debian Trixie — dit is een kritiek verschil bij het installeren van Docker. Het oorspronkelijke plan gebruikte de Ubuntu Docker repo — dit geeft een 404 fout. Gebruik altijd de Debian repo (zie Stap 2.2). |
| :---- |

## **2.2 Docker installeren (Debian Trixie — correcte methode)**

\# Verwijder eventuele foute Ubuntu repo (als die al toegevoegd was)

sudo rm \-f /etc/apt/sources.list.d/docker.list

sudo rm \-f /etc/apt/keyrings/docker.gpg

\# Juiste Debian GPG key ophalen

curl \-fsSL https://download.docker.com/linux/debian/gpg | sudo gpg \\

  \--dearmor \-o /etc/apt/keyrings/docker.gpg

\# Juiste Debian repo toevoegen

echo "deb \[arch=$(dpkg \--print-architecture) \\

  signed-by=/etc/apt/keyrings/docker.gpg\] \\

  https://download.docker.com/linux/debian \\

  $(. /etc/os-release && echo $VERSION\_CODENAME) stable" \\

  | sudo tee /etc/apt/sources.list.d/docker.list \> /dev/null

\# Installeren

sudo apt-get update

sudo apt-get install \-y docker-ce docker-ce-cli containerd.io docker-compose-plugin

\# Gebruiker toevoegen aan docker groep

sudo usermod \-aG docker $USER

newgrp docker

\# Verificatie

docker \--version

docker compose version

| ℹ️  Na newgrp docker Als je een permissiefout krijgt op de socket na newgrp docker: sluit de terminal en open opnieuw. |
| :---- |

## **2.3 docker-compose.yml (volledige inhoud ter referentie)**

Het bestand staat al op \~/ehrbase-demo/docker-compose.yml. Onderstaande inhoud dient als referentie bij herstel of herinstallatie:

version: '3'

networks:

  ehrbase-net:

    driver: bridge

services:

  ehrdb:

    image: ehrbase/ehrbase-v2-postgres:16.2

    networks: \[ehrbase-net\]

    environment:

      POSTGRES\_USER: postgres

      POSTGRES\_PASSWORD: postgres

      EHRBASE\_USER\_ADMIN: ehrbase

      EHRBASE\_PASSWORD\_ADMIN: ehrbase

      EHRBASE\_USER: ehrbase\_restricted

      EHRBASE\_PASSWORD: ehrbase\_restricted

    ports: \['5432:5432'\]

    volumes:

      \- ehrbase\_data:/var/lib/postgresql/data

  ehrbase:

    image: ehrbase/ehrbase:latest

    networks: \[ehrbase-net\]

    depends\_on: \[ehrdb\]

    environment:

      DB\_URL: jdbc:postgresql://ehrdb:5432/ehrbase

      DB\_USER: ehrbase\_restricted

      DB\_PASS: ehrbase\_restricted

      DB\_USER\_ADMIN: ehrbase

      DB\_PASS\_ADMIN: ehrbase

      SECURITY\_AUTHTYPE: BASIC

      SECURITY\_AUTHUSER: ehrbase-user

      SECURITY\_AUTHPASSWORD: SuperSecretPassword

      SERVER\_NODENAME: sensire.ehrbase.local

    ports: \['8080:8080'\]

volumes:

  ehrbase\_data:

## **2.4 Overzicht draaiende services**

| Component | Status | Poort / URL |
| :---- | :---- | :---- |
| EHRbase CDR | ✅ Draait | http://localhost:8080 |
| Swagger UI | ✅ Ingebouwd | http://localhost:8080/ehrbase/swagger-ui.html |
| PostgreSQL | ✅ Draait | localhost:5432 |
| Medblocks UI / Demo | ✅ Draait | http://localhost:5173 |
| pgAdmin | ⏳ Nog installeren | http://localhost:5050 |
| GDL2 Editor | ⏳ Nog installeren | http://localhost:8090 |
| openEHRTool | ⏳ Nog installeren | http://localhost:8888 |

# **3\. Stap-voor-Stap Uitvoeringsplan**

## **Stap 1: EHRbase opstarten (al uitgevoerd)**

De docker-compose.yml staat al op \~/ehrbase-demo/ en is correct geconfigureerd.

cd \~/ehrbase-demo

docker compose up \-d

\# Verificatie (vereist credentials)

curl \-u ehrbase-user:SuperSecretPassword \\

  http://localhost:8080/ehrbase/rest/status

\# Verwacht: \<ehrbase\_version\>2.29.0\</ehrbase\_version\>

| ℹ️  Credentials Gebruiker: ehrbase-user  |  Wachtwoord: SuperSecretPassword EHR-ID testpatiënt: 196bbbe9-24b5-479a-a7aa-596bdf8a56c5 |
| :---- |

## **Stap 2: Archetypes en Templates**

### **2A — Internationale archetypes (al uitgevoerd)**

De volledige CKM-mirror staat al in \~/ehrbase-demo/archetypes/international/CKM-mirror/

De volgende 5 archetypes zijn gekopieerd naar \~/ehrbase-demo/archetypes/international/:

* openEHR-EHR-CLUSTER.oedema.v0.adl

* openEHR-EHR-CLUSTER.exam\_wound.v0.adl

* openEHR-EHR-OBSERVATION.diabetic\_wound\_wagner.v0.adl

* openEHR-EHR-EVALUATION.problem\_diagnosis.v1.adl

* openEHR-EHR-EVALUATION.health\_risk.v1.adl

| ⚠️  ankle\_brachial\_index niet in internationale CKM Dit archetype staat niet in de internationale CKM-mirror. Moet zelf gemaakt worden in Archetype Designer (zie Stap 2B). Staat wél in de Noorse CKM (niet publiek). |
| :---- |

### **2B — Eigen Sensire archetypes maken (nog te doen)**

Ga naar https://tools.openehr.org/designer/ en log in. Repository: Sensire-wondzorg (al aangemaakt).

Maak de volgende archetypes aan via New \> Archetype. Schrijf altijd de primaire beschrijving in het Engels (zie Stap 3 voor de NL lokalisatie).

| Archetype ID | RM Type | Doel |
| :---- | :---- | :---- |
| openEHR-EHR-OBSERVATION.ankle\_brachial\_index.v0 | OBSERVATION | EAI meting (enkel-arm index) |
| openEHR-EHR-CLUSTER.stemmer\_sign.v0 | CLUSTER | Teken van Stemmer (lymfoedeem vs. veneus) |
| openEHR-EHR-CLUSTER.wound\_stagnation\_assessment.v0 | CLUSTER | Stagnatiebeoordeling (\>2-3 weken) |
| openEHR-EHR-CLUSTER.wcs\_wound\_classification.v0 | CLUSTER | WCS kleurenclassificatie (rood/geel/zwart) |
| openEHR-EHR-CLUSTER.altis\_pain\_score.v0 | CLUSTER | ALTIS pijnscore |

Exporteer elk archetype als ADL 1.4 en sla op in \~/ehrbase-demo/archetypes/sensire/

### **2C — Template uitbreiden (na 2B)**

De huidige template sensire\_wound\_care gebruikt alleen de 5 internationale archetypes. Na het maken van de eigen archetypes in 2B: importeer ze in Archetype Designer, voeg toe aan de template, exporteer als OPT en upload naar EHRbase.

curl \-X POST \\

  http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4 \\

  \-u ehrbase-user:SuperSecretPassword \\

  \-H "Content-Type: application/xml" \\

  \--data-binary @\~/ehrbase-demo/sensire\_wound\_care.opt

## **Stap 3: Taalstrategie — Engels-eerst met Nederlandse lokalisatie**

Dit is een nieuwe sectie die niet in de eerdere versies stond, maar essentieel is voor de demo en voor het positioneren van het werk richting de internationale community.

### **Waarom Engels-eerst?**

openEHR archetypes zijn altijd primair in het Engels geschreven — dit is de internationale standaard. Redenen:

* Internationale CKM archetypes zijn altijd in het Engels

* Eigen archetypes kunnen later worden ingediend bij de internationale CKM als bijdrage

* Andere landen en systemen begrijpen het model direct

* Versiebeheer en peer review werkt internationaal

* De archetype path (gebruikt in AQL) is altijd in het Engels

| ℹ️  Sensire als pionier Door de Sensire-archetypes (Stemmer, WCS, ALTIS) in het Engels te bouwen en bij CKM in te dienen, kan Sensire bijdragen aan de internationale openEHR community — net als de Noorse en Australische zorgaanbieders die al archetypes hebben bijgedragen. Dit versterkt het verhaal richting Actiz en V\&VN. |
| :---- |

### **Hoe voeg je een Nederlandse vertaling toe in Archetype Designer?**

Procedure per archetype (na het bouwen in het Engels):

8. Open het archetype in Archetype Designer

9. Klik op het tabblad "Languages" (of "Translations")

10. Klik op "Add Language" → kies "Dutch (nl)"

11. Vul voor elk element de Nederlandse tekst in: term name, description, comment

12. Exporteer opnieuw als ADL 1.4 — het bestand bevat nu beide talen

| ℹ️  LLM-vertalingen Claude levert uitstekende medische vertalingen voor archetype-beschrijvingen. Workflow: exporteer het archetype als ADL-tekst, vraag Claude om een NL-vertaling per element te genereren, plak de vertalingen terug in Archetype Designer. Dit bespaart uren handmatig vertaalwerk. |
| :---- |

### **Hoe verhouden de EN en NL versies zich tot elkaar?**

| Aspect | Engels (primair) | Nederlands (vertaling) |
| :---- | :---- | :---- |
| Archetype ID | openEHR-EHR-CLUSTER.stemmer\_sign.v0 | Identiek — nooit vertaald |
| Archetype path (AQL) | items\[at0001\]/value | Identiek — altijd Engels |
| Term name | "Stemmer sign" | "Teken van Stemmer" |
| Description | "Test to differentiate lymphoedema..." | "Test om lymfoedeem te onderscheiden..." |
| Gecodeerde waarde | SNOMED: 416940007 (internationaal) | SNOMED NL: zelfde code, NL term |
| Browser-formulier | Toont Engelse labels | Toont Nederlandse labels |
| AQL query | Altijd in het Engels | Altijd in het Engels |
| ZIB-compatibiliteit | Via SNOMED/LOINC terminologie | Identiek — ZIB gebruikt dezelfde codes |

### **Aansluiting op ZIBs (Zorginformatiebouwstenen)**

ZIBs zijn de Nederlandse nationale klinische informatiestandaard, beheerd door Nictiz. Ze beschrijven dezelfde concepten als openEHR archetypes, maar dan specifiek voor de Nederlandse context.

| ZIB-concept | openEHR archetype | Relatie |
| :---- | :---- | :---- |
| ZIB Wond | openEHR-EHR-CLUSTER.exam\_wound | Sterke overlap, terminologieafstemming nodig |
| ZIB Bloeddruk | openEHR-EHR-OBSERVATION.blood\_pressure | Directe mapping via LOINC |
| ZIB Probleem | openEHR-EHR-EVALUATION.problem\_diagnosis | Directe mapping |
| ZIB Meting (EAI) | ankle\_brachial\_index (eigen) | Eigen archetype, ZIB-termen gebruiken |

Nuttige links: https://zibs.nl  |  https://github.com/nictiz  |  https://nictiz.nl/standaarden/hl7-fhir/

### **Demo-moment: EN → NL live tonen aan collega's**

Aanbevolen volgorde voor het "taalmoment" in de demo (3 minuten):

13. Open Archetype Designer → Sensire-wondzorg repository → CLUSTER.stemmer\_sign.v0

14. "Dit is de Engelse definitie — dit is wat we bijdragen aan de internationale community."

15. Klik op het tabblad "Dutch (nl)": "En dit is de Nederlandse vertaling — dit is wat de verpleegkundige straks te zien krijgt."

16. Toon in de browser-demo: het formulier verschijnt in het Nederlands

17. Open een terminal en voer een AQL query uit: "Zie je dit? De query is in het Engels — de taal van het formulier is een presentatiekeuze. De data staat altijd in internationaal formaat."

| ℹ️  Kernboodschap voor de demo "De schoonheid van openEHR is dat de taal van de interface niets uitmaakt.  De data zelf is altijd in een internationaal formaat. We beginnen in het Engels  om internationaal bij te dragen, maar de Sensire-verpleegkundige ziet gewoon  haar vertrouwde Nederlandse termen." |
| :---- |

## **Stap 4: Demo-pagina's voor alle drie beslisbomen**

### **4A — Ulcus Cruris demo-pagina (✅ al uitgevoerd)**

De volledig werkende HTML demo-pagina staat in \~/ehrbase-demo/frontend/sensire-app/index.html. De pagina doorloopt de Ulcus Cruris beslisboom interactief, slaat het resultaat op als openEHR compositie en bewijst opslag via AQL.

cd \~/ehrbase-demo/frontend/sensire-app

npm run dev

\# Open: http://localhost:5173

| ℹ️  Bekende correctie (al opgelost) health\_risk archetype vereist verplicht veld health\_risk/health\_risk. Dit is al opgelost in de huidige index.html. Medblocks v0.0.211 gebruikt form.export() i.p.v. form.data. |
| :---- |

### **4B — Diabetische Voet demo-pagina (nog te doen)**

Maak een tweede HTML-pagina op basis van dezelfde structuur als de Ulcus Cruris pagina, maar met de beslisboom voor Diabetische Voet. De beslisboom (Mermaid flowchart) is opgenomen als referentie in Appendix A.

Kernbeslissingen voor de HTML-implementatie:

* Anamnese: glucose geregeld, claudicatio, eerder ulcus, Charcot in voorgeschieden

* Voetinspectie: huidkleur, temp., pulsaties, monofilament gevoel, nagels, schoeisel

* Charcot vermoeden → arts dezelfde dag (MEEST URGENTE escalatie, rood markeren)

* Plantaire wond → arts binnen 24 uur

* Geen wond → preventieve zorg (groene flow)

* Wond → doorverwijzing naar Algemeen Wondprotocol met DM-laag geactiveerd

### **4C — Algemeen Wondprotocol demo-pagina (nog te doen)**

De Algemeen Wondprotocol beslisboom is het meest uitgebreid. Kernonderdelen voor de HTML-implementatie (zie Appendix A voor de volledige flowchart):

* Oncologische wond check → apart protocol

* Voorbereiding: werkveld, materialen (max 14 dgn na opening), handhygiëne, desinfectie

* Wondinspectie \+ DM voetinspectie (indien DM) \+ Charcot-check

* Pijnmanagement: ALTIS-score, systemisch vs. lokaal (Lidocaïne/EMLA)

* TIME \+ WCS analyse (Tissue, Infectie, Moisture, Edge; rood/geel/zwart)

* Debridement veiligheidscheck (stolling, diepe structuren, maligniteit)

* Infectiebeleid (lokaal antibact., arts bij koorts+DM, ernstige infectie DM)

* Verbandkeuze matrix: WCS-kleur × exsudaatniveau (droog/vochtig/nat)

* DM: drukontlasting (Stap B) \+ voorlichting (Stap C)

* Nazorg, rapportage (TIME+Foto wekelijks), escalatie Vakgroep Wond

### **4D — Navigatiepagina (nog te doen)**

Maak een index.html die als startscherm dient en links biedt naar alle drie de protocol-pagina's, de Swagger UI en pgAdmin. Dit is het startpunt van de demonstratie aan collega's.

## **Stap 5: GDL2 Beslisondersteuning toevoegen**

GDL2 (Guideline Definition Language versie 2\) is de officiële openEHR standaard voor het formaliseren van beslislogica. Dit vervangt de huidige JavaScript-beslislogica door formele openEHR-conforme regels.

| ⚠️  Huidige demo heeft beslislogica in JavaScript Dit werkt visueel maar is technisch niet openEHR-conform. GDL2 maakt het volledig correct. Alternatief (sneller): Python script dat AQL bevraagt — zie Appendix B. |
| :---- |

### **5A — GDL2 Editor installeren**

docker run \-d \--name gdl2-editor \\

  \-p 8090:8080 \\

  \-v \~/ehrbase-demo/gdl2:/app/gdl2 \\

  gdl-lang/gdl2-editor:latest

\# Open: http://localhost:8090

### **5B — GDL2 regels voor Ulcus Cruris (minimale startset)**

| Regel | Conditie | Actie |
| :---- | :---- | :---- |
| Compressie contra-indicatie | EAI \< 0.6 | Geen compressie — verwijs vaatchirurg |
| Gemengd vaatlijden | EAI 0.6 – 0.8 | UrgoK2 Lite — lichte druk |
| Veneus ulcus normaal | EAI 0.8 – 1.3 | UrgoK2 — normale compressie starten |
| EAI onbetrouwbaar | EAI \> 1.3 | Overleg huisarts — nader diagnostiek |
| Stagnatiebeoordeling | Wond \> 3 weken zonder verbetering | Vakgroep Wond inschakelen |

Zie Appendix B voor de volledige GDL2 regelstructuur en syntaxvoorbeeld.

## **Stap 6: Monitoring Tools toevoegen**

### **6A — pgAdmin (direct in de PostgreSQL database kijken)**

docker run \-d \--name pgadmin \\

  \-p 5050:80 \\

  \-e PGADMIN\_DEFAULT\_EMAIL=demo@sensire.nl \\

  \-e PGADMIN\_DEFAULT\_PASSWORD=demo \\

  dpage/pgadmin4

\# Open: http://localhost:5050

\# Verbind met: host=localhost, port=5432

\# Gebruiker: postgres  |  Wachtwoord: postgres

pgAdmin laat zien dat de openEHR data echt in PostgreSQL staat — krachtig bewijs voor sceptische collega's.

### **6B — openEHRTool (GUI browser voor EHRbase)**

docker run \-d \--name openehrtool \\

  \-p 8888:80 \\

  crs4/openehrtool:latest

\# Open: http://localhost:8888

\# Zie ook: https://github.com/crs4/openEHRTool

## **Stap 7: Versiebeheer Archetypes en Templates**

Om het verschil tussen internationale standaard en Sensire-eigen aanvullingen te demonstreren en te beheren:

mkdir \-p \~/ehrbase-demo/archetypes/international

mkdir \-p \~/ehrbase-demo/archetypes/sensire

mkdir \-p \~/ehrbase-demo/templates

mkdir \-p \~/ehrbase-demo/webtemplates

cd \~/ehrbase-demo && git init

\# Commit internationale archetypes apart van eigen aanvullingen

git add archetypes/international/

git commit \-m "feat: internationale CKM archetypes v2025"

git add archetypes/sensire/

git commit \-m "feat: Sensire eigen archetypes wondzorgpad v1.0"

| ℹ️  Zichtbaarheid richting community Met deze mappenstructuur kun je precies laten zien welke archetypes je hebt hergebruikt (international/) en welke je zelf hebt bijgedragen (sensire/). De eigen archetypes kun je later als "contribution" indienen bij CKM om het lichtende voorbeeld te zijn richting Actiz, V\&VN en HL7 Nederland. |
| :---- |

# **4\. Demo-script voor Collega's**

Aanbevolen volgorde voor een demonstratie aan Sensire-collega's en stakeholders. Totale duur circa 25 minuten.

## **4.1 Wat is openEHR? (2 minuten)**

Begin met de kernboodschap zonder jargon:

| "  Kernboodschap "openEHR is een internationale standaard die beschrijft hoe klinische data  gestructureerd moet worden opgeslagen — niet in een eigen database-formaat,  maar in een format dat iedere computer ter wereld begrijpt. Geen vendor lock-in,  echte interoperabiliteit, en data die over 20 jaar nog leesbaar is." |
| :---- |

## **4.2 Swagger UI — de openEHR API (3 minuten)**

Open http://localhost:8080/ehrbase/swagger-ui.html

18. Laat de Template Controller zien → GET /definition/template/adl1.4 → Execute

19. "Dit zijn onze Sensire zorgpaden, opgeslagen als internationale standaard."

20. Klik op de template → toon het OPT XML: "Dit zijn de internationale archetypes plus onze eigen aanvullingen."

## **4.3 Taalmoment — EN → NL (3 minuten)**

Dit is de nieuwe stap in de demo (zie Stap 3):

21. Open Archetype Designer → Sensire-wondzorg → CLUSTER.stemmer\_sign.v0

22. "Dit is de Engelse definitie — dit is wat we bijdragen aan de internationale community."

23. Klik op het tabblad "Dutch (nl)": "Dit is de Nederlandse vertaling — wat de verpleegkundige straks ziet."

24. Toon de browser-demo in het Nederlands

25. "De AQL query is altijd in het Engels. De taal van de interface is een presentatiekeuze."

## **4.4 Beslisboom doorlopen — Ulcus Cruris (5 minuten)**

Open http://localhost:5173

26. Vul een testpatiënt in: naam, geboortedatum, locatie

27. Doorloop de beslisboom: nieuwe cliënt, geen DM, oedeem aanwezig, Stemmer negatief

28. Voer een EAI waarde in: 0.85 (veneus, normaal)

29. "Dit is wat de verpleegkundige te zien krijgt." — toon het klinisch advies-tabblad

30. "Dit is de onderliggende gestructureerde data." — toon het openEHR Data-tabblad

31. Klik Opslaan — toon de compositie UID en het AQL bewijs-tabblad

## **4.5 AQL — data onafhankelijk van de applicatie (3 minuten)**

Open een terminal en voer uit:

curl \-u ehrbase-user:SuperSecretPassword \\

  \-H "Content-Type: application/json" \\

  "http://localhost:8080/ehrbase/rest/openehr/v1/query/aql" \\

  \--data-binary '{"q": "SELECT c/uid/value, c/name/value FROM EHR e CONTAINS COMPOSITION c"}'

| "  Script "Zie je dit? Dit is dezelfde data, maar nu bevraagd direct uit de database via  een internationale querytaal. Geen API van een leverancier — pure openEHR.  Een ander systeem dat ook openEHR spreekt kan dezelfde query uitvoeren en  dezelfde data teruglezen." |
| :---- |

## **4.6 pgAdmin — bewijs dat het echte data is (2 minuten)**

Open http://localhost:5050, log in en navigeer naar de ehrbase database.

| "  Script "En voor de echte sceptici: hier staan de raw openEHR records in PostgreSQL.  De structuur volgt het openEHR Reference Model exact." |
| :---- |

## **4.7 Archetype Designer — internationaal vs. eigen (3 minuten)**

Open https://tools.openehr.org/designer/ → Sensire-wondzorg repository

32. "Dit zijn de internationale archetypes die we hergebruiken — ontwikkeld door klinische experts over de hele wereld."

33. "En dit zijn de eigen Sensire archetypes — ons eigen klinische model, in het Engels geschreven zodat we het later kunnen indienen bij de internationale CKM."

# **5\. Bekende Problemen en Oplossingen**

Uit de implementatiesessie van 16 maart 2026\. Bewaar dit als naslagwerk.

| Probleem | Oorzaak | Oplossing |
| :---- | :---- | :---- |
| Docker repo 404 bij apt-get update | Plan gebruikte Ubuntu repo maar systeem is Debian Trixie | Gebruik download.docker.com/linux/debian ipv /linux/ubuntu |
| CKM zoekresultaat: 0 gevonden | Filter stond op "Active" i.p.v. "Published" | Klik op "Published" radiobutton vóór zoeken |
| ankle\_brachial\_index niet gevonden in CKM | Staat niet in internationale CKM, alleen in Noorse CKM (niet publiek) | Zelf maken in Archetype Designer als OBSERVATION |
| git clone vraagt om GitHub login | Geen SSH-key of token geconfigureerd | Gebruik Personal Access Token (PAT) via github.com/settings/tokens |
| EHR aanmaken geeft Bad Request | EHRbase v2 vereist archetype\_node\_id en subject veld | Gebruik volledige body met archetype\_node\_id en PARTY\_SELF |
| Template upload geeft 404 | Root archetype (COMPOSITION.encounter) nog niet geïmporteerd | Eerst encounter.v1.adl importeren in Archetype Designer |
| form.data is undefined in Medblocks UI | Medblocks v0.0.211 gebruikt form.export() ipv form.data | Vervang form.data door form.export() |
| POST compositie geeft 415 Unsupported Media Type | Verkeerde Content-Type header | Gebruik application/json met ?format=FLAT als query parameter |
| POST compositie geeft 422 — name ontbreekt | health\_risk archetype heeft verplicht veld health\_risk | Voeg health\_risk|value, |code, |terminology toe aan FLAT JSON |
| ecis/v1/composition geeft 404 | EHRbase v2 heeft ecis endpoint verwijderd | Gebruik /rest/openehr/v1/ehr/{ehr\_id}/composition?format=FLAT |

# **6\. Snelreferentie — Belangrijkste Commando's**

## **6.1 EHRbase beheer**

\# Starten

cd \~/ehrbase-demo && docker compose up \-d

\# Stoppen

docker compose down

\# Status controleren

curl \-u ehrbase-user:SuperSecretPassword http://localhost:8080/ehrbase/rest/status

\# Alle templates tonen

curl \-u ehrbase-user:SuperSecretPassword \\

  http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4

\# Template uploaden

curl \-X POST \\

  http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4 \\

  \-u ehrbase-user:SuperSecretPassword \\

  \-H "Content-Type: application/xml" \\

  \--data-binary @/pad/naar/template.opt

## **6.2 EHR aanmaken (EHRbase v2 — correcte syntax)**

curl \-X POST \\

  http://localhost:8080/ehrbase/rest/openehr/v1/ehr \\

  \-u ehrbase-user:SuperSecretPassword \\

  \-H "Content-Type: application/json" \\

  \-d '{

    "\_type": "EHR\_STATUS",

    "archetype\_node\_id": "openEHR-EHR-EHR\_STATUS.generic.v1",

    "name": {"value": "EHR Status"},

    "subject": {"\_type": "PARTY\_SELF"},

    "is\_queryable": true,

    "is\_modifiable": true

  }'

## **6.3 AQL queries**

\# Alle composities (met naam en UID)

curl \-u ehrbase-user:SuperSecretPassword \\

  \-H "Content-Type: application/json" \\

  "http://localhost:8080/ehrbase/rest/openehr/v1/query/aql" \\

  \--data-binary '{"q": "SELECT c/uid/value, c/name/value, c/context/start\_time/value

    FROM EHR e CONTAINS COMPOSITION c ORDER BY c/context/start\_time/value DESC LIMIT 10"}'

\# Alle EAI waarden (na toevoegen EAI archetype aan template)

'{"q": "SELECT o/data\[at0001\]/events\[at0002\]/data\[at0003\]/items/value

  FROM EHR e CONTAINS OBSERVATION o\[openEHR-EHR-OBSERVATION.ankle\_brachial\_index.v0\]"}'

## **6.4 Demo starten (complete stack)**

\# 1\. EHRbase starten

cd \~/ehrbase-demo && docker compose up \-d

\# 2\. Verificatie

curl \-u ehrbase-user:SuperSecretPassword http://localhost:8080/ehrbase/rest/status

\# 3\. pgAdmin starten (optioneel)

docker start pgadmin

\# 4\. Demo-pagina starten

cd \~/ehrbase-demo/frontend/sensire-app && npm run dev

\# 5\. Browser openen

\# Demo:    http://localhost:5173

\# Swagger: http://localhost:8080/ehrbase/swagger-ui.html

\# pgAdmin: http://localhost:5050

## **6.5 Credentials overzicht**

| Service | Gebruiker | Wachtwoord |
| :---- | :---- | :---- |
| EHRbase REST API | ehrbase-user | SuperSecretPassword |
| PostgreSQL | postgres | postgres |
| pgAdmin | demo@sensire.nl | demo |
| openEHR CKM / Archetype Designer | uw openEHR account | (eigen wachtwoord) |

## **6.6 Belangrijke paden**

\~/ehrbase-demo/                              \# Projecthoofdmap

\~/ehrbase-demo/docker-compose.yml            \# Docker configuratie

\~/ehrbase-demo/sensire\_wound\_care.opt        \# Huidige template

\~/ehrbase-demo/archetypes/international/     \# CKM archetypes

\~/ehrbase-demo/archetypes/sensire/           \# Eigen archetypes

\~/ehrbase-demo/frontend/sensire-app/         \# Vite dev server

\~/ehrbase-demo/frontend/sensire-app/index.html   \# Demo-pagina

\~/ehrbase-demo/gdl2/                         \# GDL2 regelbestanden

## **6.7 Nuttige URLs**

* EHRbase documentatie: https://docs.ehrbase.org

* openEHR CKM: https://ckm.openehr.org/ckm/

* Archetype Designer: https://tools.openehr.org/designer/

* CKM GitHub mirror: https://github.com/openEHR/CKM-mirror

* GDL2 tools: https://gdl-lang.org/the-project/tools/

* Medblocks UI docs: https://medblocks.com/docs/medblocks-ui

* EHRbase GitHub: https://github.com/ehrbase/ehrbase

* Nictiz ZIBs: https://zibs.nl  |  https://github.com/nictiz

# **Appendix A: Klinische Zorgpaden (Mermaid Flowcharts)**

De drie zorgpaden worden hieronder beschreven als referentie voor de HTML demo-implementatie. De Mermaid broncode is beschikbaar als afzonderlijk bestand. De zorgpaden zijn ontworpen voor Sensire Wondzorg.

| ℹ️  Mermaid rendering De volledige Mermaid broncode voor elk zorgpad is beschikbaar als afzonderlijk bestand. Voor rendering in de browser-demo: gebruik de Mermaid JavaScript library (CDN). Let op: max \~20 tekens per regel voor correcte rendering in Claude.ai / Mermaid online. |
| :---- |

## **A1 — Ulcus Cruris Protocol**

Het Ulcus Cruris zorgpad omvat: triage (nieuw vs. bestaand),diagnostiek (EAI-beoordeling, Stemmer-test, oedeem), compressiekeuze(UrgoK2 / UrgoK2 Lite), wondzorg via het Algemeen Wondprotocol, enafsluiting (steunkousen, evaluatie).Kernbeslissingen in de beslisboom:  • Nieuwe/bestaande cliënt \+ stagnatiebeoordeling (\>2-3 weken)  • Diabetes Mellitus? → doorverwijzing Diabetische Voet protocol  • Oedeem \+ Stemmer-test (veneus vs. lymfoedeem)  • EAI-waarde: \<0.6 (ernstig, geen compressie), 0.6-0.8 (gemengd,    UrgoK2 Lite), 0.8-1.3 (veneus, UrgoK2), \>1.3 (overleg HA)  • Zwachtelwerkinstructie \+ nazorg \+ afsluitingDe bijbehorende GDL2-regels (Stap 5\) formaliseren de EAI-drempels.

openEHR archetypes die dit zorgpad dekt:

* OBSERVATION.ankle\_brachial\_index.v0 (EAI)

* CLUSTER.stemmer\_sign.v0 (Stemmer-test)

* CLUSTER.wound\_stagnation\_assessment.v0 (stagnatiebeoordeling)

* CLUSTER.oedema.v0 (oedeem)

* EVALUATION.problem\_diagnosis.v1 (diagnose HA)

## **A2 — Diabetische Voet Protocol**

Het Diabetische Voet zorgpad omvat: anamnese (glucose, claudicatio,eerder ulcus, Charcot voorgeschiedenis), voetinspectie (beide voeten:huidkleur, temp., pulsaties, monofilament gevoel, nagels, schoeisel),Charcot-vermoeden screening, en splitsing op wond aanwezig/afwezig.Kernbeslissingen:  • Charcot vermoeden (rode, warme, gezwollen voet zonder trauma)    → arts dezelfde dag — MEEST URGENTE ESCALATIE  • Geen wond → preventieve zorg (huid invetten, niet blootsvoets,    medisch pedicure, dagelijkse inspectie)  • Wond aanwezig → doorverwijzing naar Algemeen Wondprotocol    met DM-laag geactiveerd (Stap A/B/C)

openEHR archetypes die dit zorgpad dekt:

* OBSERVATION.diabetic\_wound\_wagner.v0 (Wagner classificatie)

* CLUSTER.exam\_wound.v0 (wondinspectie)

* CLUSTER.altis\_pain\_score.v0 (pijnscore)

* EVALUATION.problem\_diagnosis.v1 (diagnose)

## **A3 — Algemeen Wondprotocol**

Het Algemeen Wondprotocol is het meest uitgebreide zorgpad en dientals gemeenschappelijke basis voor alle wondtypen, met optioneleDM-specifieke uitbreidingen (Stap A/B/C).Kernonderdelen:  • Oncologische wond check (apart protocol, niet dit pad)  • Voorbereiding: werkveld, materialen (max 14 dgn), handhygiëne,    desinfectie schaar/pincet  • Wondinspectie: verband beoordelen, wond inspecteren (grootte,    kleur, geur, exsudaat, wondranden)  • DM-laag: voetinspectie, Charcot-check, plantaire wond (arts \<24u)  • Pijnmanagement: ALTIS-score, systemisch vs. lokaal (Lidocaïne/EMLA)  • TIME \+ WCS analyse (Tissue/Infectie/Moisture/Edge; rood/geel/zwart)  • Debridement veiligheidscheck (stolling, diepe structuren, maligniteit)  • Infectiebeleid (lokaal antibact., arts bij koorts+DM, ernstige infectie)  • Verbandkeuze matrix: WCS-kleur × exsudaatniveau (droog/vochtig/nat)  • DM: drukontlasting (Stap B) \+ voorlichting (Stap C)  • Nazorg: rapportage (TIME+Foto wekelijks), escalatie Vakgroep Wond

openEHR archetypes die dit zorgpad dekt (volledig):

* CLUSTER.exam\_wound.v0 (TIME: T \= weefsel, M \= exsudaat, E \= wondranden)

* CLUSTER.wcs\_wound\_classification.v0 (WCS kleurclassificatie)

* CLUSTER.altis\_pain\_score.v0 (pijnmanagement voor wondzorg)

* CLUSTER.oedema.v0 (oedeem wondomgeving)

* EVALUATION.health\_risk.v1 (infectierisico / escalatie)

* EVALUATION.problem\_diagnosis.v1 (oncologisch, DM, etc.)

* Alle DM-specifieke lagen: voetinspectie (A), drukontlasting (B), voorlichting (C)

# **Appendix B: GDL2 Regelstructuur en Syntaxvoorbeeld**

Volledig GDL2 syntaxvoorbeeld voor de EAI-compressieregel (Ulcus Cruris beslisboom). Dit is de formele openEHR-conforme beslislogica die de JavaScript-implementatie in de demo vervangt.

guideline: (GUIDELINE) \<

  id \= \<"sensire\_eai\_compressie\_v1"\>

  concept \= \<\[local::gt0001\]\>

  language \= (LANGUAGE) \<original\_language \= \<\[ISO\_639-1::en\]\>\>

  description \= (RESOURCE\_DESCRIPTION) \<

    details \= \<

      \["en"\] \= (RESOURCE\_DESCRIPTION\_ITEM) \<

        purpose \= \<"EAI-based compression decision for venous ulcer care"\>

        use \= \<"Use with ankle\_brachial\_index archetype data from EHRbase"\>

      \>

    \>

  \>

  ...

  rules \= \<

    \["Compression contraindication"\] \= (RULE) \<

      when \= \<"$eai\_ratio \< 0.6"\>

      then \= \<"$recommendation \= 'Contra-indicatie compressie. Verwijs naar vaatchirurg.'"\>

    \>

    \["Mixed venous/arterial"\] \= (RULE) \<

      when \= \<"$eai\_ratio \>= 0.6", "$eai\_ratio \<= 0.8"\>

      then \= \<"$recommendation \= 'UrgoK2 Lite — lichte druk (gemengd vaatlijden)'"\>

    \>

    \["Normal venous ulcer"\] \= (RULE) \<

      when \= \<"$eai\_ratio \> 0.8", "$eai\_ratio \<= 1.3"\>

      then \= \<"$recommendation \= 'UrgoK2 — normale compressie starten'"\>

    \>

    \["Unreliable EAI"\] \= (RULE) \<

      when \= \<"$eai\_ratio \> 1.3"\>

      then \= \<"$recommendation \= 'EAI onbetrouwbaar — overleg huisarts'"\>

    \>

  \>

\>

| ℹ️  Alternatief: Python \+ AQL Voor de eerste demo is het ook prima om de beslislogica als Python script te implementeren dat de openEHR REST API bevraagt en aanbevelingen terugschrijft als EVALUATION.recommendation.v2 composities. Functioneel equivalent aan GDL2, maar sneller te bouwen. GDL2 is de stap die de demo volledig openEHR-conform maakt. |
| :---- |

# **Appendix C: Realistische Tijdlijn**

Indicatieve tijdlijn voor het voltooien van de complete demo-omgeving (vanaf huidige stand, 16 maart 2026):

| Dag | Activiteit | Resultaat | Tools |
| :---- | :---- | :---- | :---- |
| 1 (✅) | Docker \+ EHRbase opstarten | Werkende CDR op localhost:8080 | Docker Compose, Swagger UI |
| 2 (✅) | CKM archetypes \+ template | Eerste OPT bestand klaar \+ in EHRbase | CKM, Archetype Designer |
| 3 (✅) | Ulcus Cruris HTML demo | Werkende browser-decisie \+ AQL bewijs | Medblocks UI, curl |
| 4 | Eigen archetypes (EN \+ NL) | ankle\_brachial\_index, stemmer\_sign, etc. | Archetype Designer |
| 5 | Taalstrategie: NL vertalingen | Alle archetypes in EN \+ NL | Archetype Designer \+ Claude |
| 6 | Diabetische Voet demo-pagina | Tweede werkende browser-demo | Vite, Medblocks UI |
| 7 | Algemeen Wondprotocol demo | Derde werkende browser-demo | Vite, Medblocks UI |
| 8 | pgAdmin \+ openEHRTool | Visueel databewijs compleet | Docker |
| 9 | GDL2 regels schrijven \+ testen | Eerste beslisondersteuning actief | GDL2 Editor |
| 10 | Demo inrichten \+ collega's | Volledige demo draaiend — 25 min script | Alle tools |

# **Appendix D: Veelgestelde Vragen**

Vragen die vaak gesteld worden bij het presenteren van openEHR aan nieuwe stakeholders.

## **Kan dit allemaal op een Chromebox?**

Ja. EHRbase \+ PostgreSQL vereisen samen \~1-2 GB RAM. Een moderne Chromebox met 4-8 GB RAM loopt dit prima. Het aandachtspunt is de Linux-omgeving: de Chromebox draait Debian Trixie via Crostini. Dit werkt uitstekend zolang de Debian Docker repo wordt gebruikt (niet Ubuntu, zie Stap 2.2).

## **Bestaan er al implementaties die ik kan gebruiken?**

Ja, meerdere:

* EHRbase — de CDR, volledig productie-ready, open source (Apache 2.0)

* Medblocks UI — open source form renderer, npm package

* openEHRTool — open source EHRbase browser GUI (GitHub: crs4/openEHRTool)

* GDL2 Editor — open source Java tool voor beslisregels

* Archetype Designer — online, gratis, van openEHR Foundation

## **Hoe verhoudt openEHR zich tot FHIR?**

FHIR (HL7) is gericht op uitwisseling van klinische berichten; openEHR is gericht op persistente, semantisch rijke opslag van klinische data. Ze zijn complementair: openEHR voor de CDR (persistentie en semantiek), FHIR voor de uitwisseling met externe systemen. Nictiz werkt aan NL ZIB-gebaseerde FHIR-profielen die goed aansluiten op openEHR-archetypes.

## **Kan ik vanuit openEHR beslisregels de beslisboom op de commandline draaien?**

Ja, via twee wegen. Optie 1: de GDL2 Engine van gdl-lang.org als library integreren in een Python of Java script dat de openEHR REST API bevraagt. Optie 2 (pragmatischer voor een demo): een Python script dat AQL queries uitvoert op EHRbase en op basis van de resultaten aanbevelingen genereert — volledig gebaseerd op de openEHR data, maar de beslislogica zit in Python.

## **Wat is het meest intelligente pad als ik iets verkeerd begrijp?**

Het meest voorkomende misverstand bij openEHR-starters is denken dat je alles van scratch moet bouwen. De volgorde is: (1) CKM plunderen voor bestaande archetypes, (2) pas als iets echt ontbreekt een eigen archetype maken in Archetype Designer, (3) alles samenstellen in een template, (4) template uploaden naar EHRbase, (5) Medblocks UI gebruiken voor de frontend. De tools doen het zware werk — jij definieert de klinische inhoud.

## **Kunnen de Sensire-archetypes worden bijgedragen aan de internationale community?**

Absoluut. De archetypes CLUSTER.stemmer\_sign.v0, CLUSTER.wcs\_wound\_classification.v0 en CLUSTER.altis\_pain\_score.v0 zijn waarschijnlijk nergens anders formeel gemodelleerd in openEHR. Door ze in het Engels te bouwen en in te dienen bij de internationale CKM, kan Sensire een lichtend voorbeeld zijn voor de Nederlandse thuiszorg — vergelijkbaar met wat Noorse en Australische zorgaanbieders al gedaan hebben.

*Sensire / Instituut Bedrijfskunde — openEHR Demo Blueprint v3.0 — Maart 2026*