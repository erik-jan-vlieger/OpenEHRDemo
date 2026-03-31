import requests
import json

comp = {
    'voetscreening_dm_sensire/category|code': '433',
    'voetscreening_dm_sensire/category|value': 'event',
    'voetscreening_dm_sensire/category|terminology': 'openehr',
    'voetscreening_dm_sensire/context/start_time': '2026-03-31T09:00:00Z',
    'voetscreening_dm_sensire/context/setting|code': '227',
    'voetscreening_dm_sensire/context/setting|value': 'emergency care',
    'voetscreening_dm_sensire/context/setting|terminology': 'openehr',
    'voetscreening_dm_sensire/bewertung_des_gesundheitsrisikos/gesundheitsrisiko': 'Diabetische voet risicobeoordeling',
    'voetscreening_dm_sensire/probleem_diagnose/naam_van_het_probleem_de_diagnose': 'Diabetische voet screening',
    'voetscreening_dm_sensire/probleem_diagnose/klinische_beschrijving': 'DM voetscreening doorlopen. Risicoprofiel: Hoog',
    'voetscreening_dm_sensire/composer|name': 'Sensire Wondzorg Demo',
    'voetscreening_dm_sensire/language|code': 'nl',
    'voetscreening_dm_sensire/language|terminology': 'ISO_639-1',
    'voetscreening_dm_sensire/territory|code': 'NL',
    'voetscreening_dm_sensire/territory|terminology': 'ISO_3166-1',
}

ehr = requests.post(
    'http://localhost:8080/ehrbase/rest/openehr/v1/ehr', 
    auth=('ehrbase-user', 'SuperSecretPassword'),
    headers={'Prefer': 'return=representation', 'Accept': 'application/json'}
).json()
ehr_id = ehr['ehr_id']['value']

resp = requests.post(
    f'http://localhost:8080/ehrbase/rest/openehr/v1/ehr/{ehr_id}/composition?templateId=diabetic_foot_assessment_sensire&format=FLAT',
    auth=('ehrbase-user', 'SuperSecretPassword'),
    headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
    json=comp
)
print(resp.status_code, resp.text)
