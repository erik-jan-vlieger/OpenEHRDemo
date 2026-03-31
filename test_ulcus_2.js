async function test() {
    const ehrResp = await fetch('http://localhost:8080/ehrbase/rest/openehr/v1/ehr', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + Buffer.from('ehrbase-user:SuperSecretPassword').toString('base64'),
            'Prefer': 'return=representation'
        },
        body: JSON.stringify({
            "_type": "EHR_STATUS",
            "archetype_node_id": "openEHR-EHR-EHR_STATUS.generic.v1",
            "name": { "value": "EHR Status" },
            "subject": { "_type": "PARTY_SELF" },
            "is_queryable": true,
            "is_modifiable": true
        })
    });
    const ehrData = await ehrResp.json();
    const ehrId = ehrData.ehr_id.value;

    const now = new Date().toISOString();
    const comp = {
        'ulcus_cruris_consult_sensire/category|code': '433',
        'ulcus_cruris_consult_sensire/category|value': 'event',
        'ulcus_cruris_consult_sensire/category|terminology': 'openehr',
        'ctx/language': 'nl',
        'ctx/territory': 'NL',
        'ctx/composer_name': 'Sensire Wondzorg Demo',
        'ctx/time': now,
        'ctx/setting': '227',
        'ulcus_cruris_consult_sensire/probleem_diagnose/naam_van_het_probleem_de_diagnose': 'Ulcus Cruris',
        'ulcus_cruris_consult_sensire/probleem_diagnose/klinische_beschrijving': 'Ulcus Cruris protocol doorlopen.',
        'ulcus_cruris_consult_sensire/klinische_synopsis/synopsis': 'Ulcus Cruris protocol doorlopen.',
        'ulcus_cruris_consult_sensire/ergebnisse_der_körperlichen_untersuchung/jedes_ereignis/beschreibung': 'Teken van Stemmer',
        'ulcus_cruris_consult_sensire/ergebnisse_der_körperlichen_untersuchung/jedes_ereignis/time': now
    };
    
    // Add interpretation as text
    comp['ulcus_cruris_consult_sensire/ergebnisse_der_körperlichen_untersuchung/jedes_ereignis/interpretation'] = 'Normaal';

    const compResp = await fetch('http://localhost:8080/ehrbase/rest/openehr/v1/ehr/' + ehrId + '/composition?format=FLAT&templateId=ulcus_cruris_assessment_sensire', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + Buffer.from('ehrbase-user:SuperSecretPassword').toString('base64'),
            'Prefer': 'return=representation'
        },
        body: JSON.stringify(comp)
    });
    console.log("STATUS:", compResp.status);
    console.log("RESPONSE:", await compResp.text());
}
test();
