async function check(tId, rootPrefix) {
    const r = await fetch('http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4/' + tId, {
        headers: {
            'Accept': 'application/openehr.wt+json',
            'Authorization': 'Basic ' + Buffer.from('ehrbase-user:SuperSecretPassword').toString('base64')
        }
    });
    const wt = await r.json();
    let found = [];
    function walk(node, currentPath) {
        if (!node) return;
        const path = currentPath ? currentPath + '/' + node.id : node.id;
        if (path.includes('datum') || path.includes('date_time') || path.includes('tijd')) {
            found.push(path);
        }
        if (node.children) node.children.forEach(c => walk(c, path));
    }
    walk(wt.tree, "");
    console.log("TEMPLATE:", tId, found.filter(f => f.includes('probleem_diagnose')));
}

async function run() {
    await check('wound_assessment_sensire', 'wondconsult_sensire');
    await check('ulcus_cruris_assessment_sensire', 'ulcus_cruris_consult_sensire');
    await check('diabetic_foot_assessment_sensire', 'voetscreening_dm_sensire');
}
run();
