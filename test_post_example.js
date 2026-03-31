const http = require('http');
const fs = require('fs');

const comp = JSON.parse(fs.readFileSync('diabetic_example.json'));

async function run() {
    const ehrResp = await fetch('http://localhost:8080/ehrbase/rest/openehr/v1/ehr', {
        method: 'POST',
        headers: {
            'Authorization': 'Basic ' + Buffer.from('ehrbase-user:SuperSecretPassword').toString('base64'),
            'Accept': 'application/json',
            'Prefer': 'return=representation'
        }
    });
    const ehr = await ehrResp.json();
    const ehrId = ehr.ehr_id.value;

    const res = await fetch(`http://localhost:8080/ehrbase/rest/openehr/v1/ehr/${ehrId}/composition?templateId=diabetic_foot_assessment_sensire&format=FLAT`, {
        method: 'POST',
        headers: {
            'Authorization': 'Basic ' + Buffer.from('ehrbase-user:SuperSecretPassword').toString('base64'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify(comp)
    });
    console.log(res.status, await res.text());
}
run();
