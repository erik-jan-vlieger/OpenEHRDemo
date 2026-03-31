const http = require('http');

const comp = {
    'voetscreening_dm_sensire/category|code': '433',
    'voetscreening_dm_sensire/category|value': 'event',
    'voetscreening_dm_sensire/category|terminology': 'openehr',
    'voetscreening_dm_sensire/start_time': '2026-03-31T09:00:00Z',
    'voetscreening_dm_sensire/setting|code': '227',
    'voetscreening_dm_sensire/setting|value': 'emergency care',
    'voetscreening_dm_sensire/setting|terminology': 'openehr',
    'voetscreening_dm_sensire/bewertung_des_gesundheitsrisikos/gesundheitsrisiko': 'Diabetische voet risicobeoordeling',
    'voetscreening_dm_sensire/probleem_diagnose/naam_van_het_probleem_de_diagnose': 'Diabetische voet screening',
    'voetscreening_dm_sensire/language|code': 'nl',
    'voetscreening_dm_sensire/language|terminology': 'ISO_639-1',
    'voetscreening_dm_sensire/territory|code': 'NL',
    'voetscreening_dm_sensire/territory|terminology': 'ISO_3166-1',
    'voetscreening_dm_sensire/composer|name': 'Sensire Demo'
};

async function run() {
    const ehrResp = await fetch('http://localhost:8080/ehrbase/rest/openehr/v1/ehr', {
        method: 'POST',
        headers: {
            'Authorization': 'Basic ' + Buffer.from('ehrbase-user:SuperSecretPassword').toString('base64'),
            'Accept': 'application/json',
            'Prefer': 'return=representation'
        }
    });
    const ehrId = (await ehrResp.json()).ehr_id.value;
    const res = await fetch(`http://localhost:8080/ehrbase/rest/openehr/v1/ehr/${ehrId}/composition?templateId=diabetic_foot_assessment_sensire&format=FLAT`, {
        method: 'POST',
        headers: {
            'Authorization': 'Basic ' + Buffer.from('ehrbase-user:SuperSecretPassword').toString('base64'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(comp)
    });
    console.log(res.status, await res.text());
}
run();
