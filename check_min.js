const fs = require('fs');
const wt = JSON.parse(fs.readFileSync('live_wt.json'));
function find(node) {
    if (node.id === 'risikofaktoren') {
        console.log("risikofaktoren min:", node.min, "max:", node.max);
    }
    for (const c of (node.children || [])) {
        find(c);
    }
}
find(wt.tree);
