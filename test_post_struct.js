const http = require('http');

const comp = {
  "_type": "COMPOSITION",
  "name": {"_type": "DV_TEXT", "value": "diabetic_foot_assessment_sensire"},
  "archetype_details": {
    "archetype_id": {"value": "openEHR-EHR-COMPOSITION.encounter.v1"},
    "template_id": {"value": "diabetic_foot_assessment_sensire"},
    "rm_version": "1.0.4"
  },
  "language": {"_type": "CODE_PHRASE", "terminology_id": {"value": "ISO_639-1"}, "code_string": "nl"},
  "territory": {"_type": "CODE_PHRASE", "terminology_id": {"value": "ISO_3166-1"}, "code_string": "NL"},
  "category": {"_type": "DV_CODED_TEXT", "value": "event", "defining_code": {"_type": "CODE_PHRASE", "terminology_id": {"value": "openehr"}, "code_string": "433"}},
  "composer": {"_type": "PARTY_IDENTIFIED", "name": "Sensire Wondzorg Demo"},
  "context": {
    "_type": "EVENT_CONTEXT",
    "start_time": {"_type": "DV_DATE_TIME", "value": "2026-03-31T09:00:00Z"},
    "setting": {"_type": "DV_CODED_TEXT", "value": "emergency care", "defining_code": {"_type": "CODE_PHRASE", "terminology_id": {"value": "openehr"}, "code_string": "227"}}
  },
  "content": []
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

    const ehr = await ehrResp.json();
    const ehrId = ehr.ehr_id.value;

    const res = await fetch(`http://localhost:8080/ehrbase/rest/openehr/v1/ehr/${ehrId}/composition?templateId=diabetic_foot_assessment_sensire`, {
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
