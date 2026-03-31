const fs = require('fs');
async function run() {
  const auth = 'Basic ' + Buffer.from('ehrbase-user:SuperSecretPassword').toString('base64');
  let ehrId;
  const ehrRes = await fetch('http://localhost:8080/ehrbase/rest/openehr/v1/ehr', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Prefer': 'return=representation', 'Authorization': auth },
    body: JSON.stringify({ _type: 'EHR_STATUS', archetype_node_id: 'openEHR-EHR-EHR_STATUS.generic.v1', name: { value: 'EHR Status' }, subject: { _type: 'PARTY_SELF' }, is_queryable: true, is_modifiable: true })
  });
  if (ehrRes.ok) { ehrId = (await ehrRes.json()).ehr_id.value; }
  else { const q = await fetch('http://localhost:8080/ehrbase/rest/openehr/v1/query/aql', { method:'POST', headers:{'Content-Type':'application/json', 'Authorization': auth}, body: JSON.stringify({q:'SELECT e/ehr_id/value FROM EHR e LIMIT 1'}) }); ehrId = (await q.json()).rows[0][0]; }
  
  console.log('EHR_ID:', ehrId);
  
  const comp = JSON.parse(fs.readFileSync('test_voet4.json'));
  const res = await fetch(`http://localhost:8080/ehrbase/rest/openehr/v1/ehr/${ehrId}/composition?format=FLAT&templateId=diabetic_foot_assessment_sensire`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Prefer': 'return=representation', 'Authorization': auth },
    body: JSON.stringify(comp)
  });
  console.log('Status:', res.status);
  console.log(await res.text());
}
run();
