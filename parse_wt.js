const fs = require('fs');
const wt = JSON.parse(fs.readFileSync('live_wt.json'));
function find(node) {
    if (node.id === 'vorhandensein') {
        console.log(JSON.stringify(node.inputs, null, 2));
    }
    for (const c of (node.children || [])) {
        find(c);
    }
}
find(wt.tree);
