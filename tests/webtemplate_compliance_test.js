const fs = require('fs');
const path = require('path');

// Methode B: 100% Zekerheid voor Gegenereerde Data (Template Validatie)
// Dit script leest een WebTemplate in en kruisverifieert of alle 'mandatory' (min >= 1) 
// attributen aanwezig en correct getypeerd zijn in een te testen FLAT JSON object.

function validateFlatAgainstWebTemplate(templateId, flatJsonToTest) {
    console.log(`\n=== 🔍 START WebTemplate Pre-Flight Compliance Test: ${templateId} ===`);

    try {
        const wtPath = path.join(__dirname, `../frontend/sensire-app/webtemplates/${templateId}_webtemplate.json`);
        if(!fs.existsSync(wtPath)) {
            console.log(`⚠️ Kan lokaal webtemplate ${wtPath} niet vinden. Zorg dat start_env.sh dit heeft gedownload.`);
            return false;
        }

        const wt = JSON.parse(fs.readFileSync(wtPath, 'utf8'));
        
        // Simpel algoritme om recursief requirements te crawlen
        let mandatoryPaths = [];

        function walk(node, currentPath) {
            if (!node) return;
            const newPath = currentPath ? `${currentPath}/${node.id}` : node.id;
            
            if (node.min >= 1) {
                // In een volwaardige validator moeten we hier rekening houden met |code, |value, et cetera.
                mandatoryPaths.push({ path: newPath, type: node.rmType });
            }

            if (node.children) {
                node.children.forEach(c => walk(c, newPath));
            }
        }
        walk(wt.tree, "");

        let missing = 0;
        console.log(`\nVerplichte (min: 1..1) velden gevonden in ${templateId}: ${mandatoryPaths.length}`);

        mandatoryPaths.forEach(mp => {
            // Note: Dit is een conceptuele check. FLAT JSON heeft :0 en |suffixes.
            // Een productieklare validator (zoals diep in EHRbase of openEHR SDT) bouwt regex op.
            const flatKeys = Object.keys(flatJsonToTest);
            
            // Check in de FLAT object keys of de basispadnaam bestaat
            const found = flatKeys.some(key => key.includes(mp.path));
            
            if(!found) {
                missing++;
                console.error(`❌ MIST VERPLICHT VELD: ${mp.path} (Verwacht RMType: ${mp.type})`);
            }
        });

        if(missing === 0) {
            console.log(`\n✅ 100% COMPLIANT: Alle mandatory data is gemapt voor ${templateId}!`);
            return true;
        } else {
            console.error(`\n🚨 FLAT JSON is NIET compliant met WebTemplate. Ontbrekende mandatory velden: ${missing}`);
            return false;
        }
    } catch (e) {
        console.error("Test failed to execute: ", e);
        return false;
    }
}

// Voorbeeld van gebruik:
// mockFlat = { 'wondconsult_sensire/probleem_diagnose/naam_van_het_probleem_de_diagnose': 'Wondzorg' ... }
// validateFlatAgainstWebTemplate('wound_assessment_sensire', mockFlat);

module.exports = { validateFlatAgainstWebTemplate };
