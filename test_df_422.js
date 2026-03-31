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
        'voetscreening_dm_sensire/category|code': '433',
        'voetscreening_dm_sensire/category|value': 'event',
        'voetscreening_dm_sensire/category|terminology': 'openehr',
        'ctx/language': 'nl',
        'ctx/territory': 'NL',
        'ctx/composer_name': 'Sensire Wondzorg Demo',
        'ctx/time': now,
        'ctx/setting': '227',
        'voetscreening_dm_sensire/probleem_diagnose/naam_van_het_probleem_de_diagnose': 'Diabetische voet screening',
        'voetscreening_dm_sensire/probleem_diagnose/klinische_beschrijving': 'DM voetscreening doorlopen.'
    };
    
    // Check if other ones are needed like health_risk_assessment
    comp['voetscreening_dm_sensire/bewertung_des_gesundheitsrisikos/health_risk'] = 'Diabetische Voet (Sims classificatie)';
    comp['voetscreening_dm_sensire/bewertung_des_gesundheitsrisikos/risikofaktoren:0/risk_factor'] = 'Wond / Ulcus op dit moment?';
    comp['voetscreening_dm_sensire/bewertung_des_gesundheitsrisikos/risikofaktoren:0/vorhandensein|code'] = 'at0019';
    comp['voetscreening_dm_sensire/bewertung_des_gesundheitsrisikos/risikofaktoren:0/vorhandensein|value'] = 'Fehlt';
    comp['voetscreening_dm_sensire/bewertung_des_gesundheitsrisikos/risikofaktoren:0/vorhandensein|terminology'] = 'local';
    comp['voetscreening_dm_sensire/bewertung_des_gesundheitsrisikos/risikobewertung/text_value'] = 'Sims 0';

    const compResp = await fetch('http://localhost:8080/ehrbase/rest/openehr/v1/ehr/' + ehrId + '/composition?format=FLAT&templateId=diabetic_foot_assessment_sensire', {
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
