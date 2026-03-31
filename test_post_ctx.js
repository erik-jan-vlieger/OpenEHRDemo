const http = require('http');

const comp = {
    'ctx/category': '433',
    'ctx/time': '2026-03-31T09:00:00Z',
    'ctx/setting': '227',
    'voetscreening_dm_sensire/bewertung_des_gesundheitsrisikos/gesundheitsrisiko': 'Diabetische voet risicobeoordeling',
    'voetscreening_dm_sensire/probleem_diagnose/naam_van_het_probleem_de_diagnose': 'Diabetische voet screening',
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
