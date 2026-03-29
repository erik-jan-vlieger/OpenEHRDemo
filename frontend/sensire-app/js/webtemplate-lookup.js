/**
 * WebTemplate Lookup Utility
 * Laadt het sensire_wound_care WebTemplate JSON en bouwt een flat lookup-tabel.
 * Gebruikt door alle beslisboompagina's, de Live Monitor en de Template Explorer.
 */

// Bekende Sensire-eigen archetypes (groen in Template Explorer)
const SENSIRE_ARCHETYPES = [
  'ankle_brachial_index',
  'stemmer_sign',
  'wound_stagnation_assessment',
  'wcs_wound_classification',
  'altis_pain_score'
];

// CKM links voor internationale archetypes
const CKM_LINKS = {
  'exam_wound': 'https://ckm.openehr.org/ckm/archetypes/1013.1.3591',
  'oedema': 'https://ckm.openehr.org/ckm/archetypes/1013.1.15',
  'diabetic_wound_wagner': 'https://ckm.openehr.org/ckm/search',
  'problem_diagnosis': 'https://ckm.openehr.org/ckm/archetypes/1013.1.166',
  'health_risk': 'https://ckm.openehr.org/ckm/archetypes/1013.1.169',
  'encounter': 'https://ckm.openehr.org/ckm/archetypes/1013.1.240'
};

// Nederlandse labels voor de meest gebruikte paden (handmatig aangevuld omdat de template geen NL-vertaling heeft)
const NL_OVERRIDES = {
  'sensire_wound_care': 'Wondzorg Compositie',
  'context/start_time': 'Starttijd',
  'context/setting': 'Setting',
  'category': 'Categorie',
  'composer': 'Behandelaar',
  'language': 'Taal',
  'territory': 'Land',
  // Health risk
  'health_risk_assessment': 'Gezondheidsrisicobeoordeling',
  'health_risk_assessment/health_risk': 'Gezondheidsrisico',
  'health_risk_assessment/risk_factors': 'Risicofactoren',
  'health_risk_assessment/risk_factors/risk_factor': 'Risicofactor',
  'health_risk_assessment/risk_factors/presence': 'Aanwezigheid',
  'health_risk_assessment/risk_factors/description': 'Beschrijving',
  'health_risk_assessment/risk_assessment': 'Risicobeoordeling',
  // Problem/Diagnosis
  'problem_diagnosis': 'Probleem/Diagnose',
  'problem_diagnosis/problem_diagnosis_name': 'Diagnose naam',
  'problem_diagnosis/clinical_description': 'Klinische beschrijving',
  'problem_diagnosis/body_site': 'Lichaamslocatie',
  'problem_diagnosis/severity': 'Ernst',
  'problem_diagnosis/diagnostic_certainty': 'Diagnostische zekerheid',
  'problem_diagnosis/date_time_of_onset': 'Datum van onset',
  'problem_diagnosis/comment': 'Opmerking',
  // Wagner
  'diabetic_wound_classification_wagner': 'Diabetische wondclassificatie (Wagner)',
  'diabetic_wound_classification_wagner/point_in_time/examined_foot': 'Onderzochte voet',
  'diabetic_wound_classification_wagner/point_in_time/classification': 'Wagner Classificatie',
  'diabetic_wound_classification_wagner/point_in_time/comment': 'Opmerking',
};

// Nederlandse labels voor at-codes (coded values)
const NL_CODE_VALUES = {
  'at0018': 'Aanwezig',
  'at0019': 'Afwezig',
  'at0026': 'Onbepaald',
  'at0005': 'Linkervoet',
  'at0006': 'Rechtervoet',
  'at0009': '0 — Intacte huid',
  'at0010': 'I — Oppervlakkig ulcus',
  'at0011': 'II — Pees/diepe structuren bloot',
  'at0012': 'III — Diep ulcus + abces/osteomyelitis',
  'at0013': 'IV — Partiële gangreen',
  'at0014': 'V — Uitgebreide gangreen',
  'at0047': 'Licht',
  'at0048': 'Matig',
  'at0049': 'Ernstig',
  'at0074': 'Vermoed',
  'at0075': 'Waarschijnlijk',
  'at0076': 'Bevestigd',
  'at0021': 'Relatief risico',
  'at0022': 'Absoluut risico',
};

/**
 * Bouw een flat lookup-tabel uit een WebTemplate node (recursief).
 * Resultaat: { 'template_id/section/field': { en, nl, inputs, archetypeId } }
 */
function buildLookupFromNode(node, pathPrefix, lookup) {
  const nodePath = pathPrefix ? `${pathPrefix}/${node.id}` : node.id;

  if (node.id && node.name) {
    const nlLabel = NL_OVERRIDES[nodePath] || NL_OVERRIDES[node.id] || node.localizedName || node.name;
    lookup[nodePath] = {
      en: node.localizedName || node.name,
      nl: nlLabel,
      rmType: node.rmType,
      nodeId: node.nodeId,
      archetypeId: node.nodeId || null,
      inputs: node.inputs || [],
      aqlPath: node.aqlPath || null
    };
  }

  if (node.children && node.children.length > 0) {
    for (const child of node.children) {
      buildLookupFromNode(child, nodePath, lookup);
    }
  }
}

/**
 * Laad en parse het WebTemplate JSON.
 * Geeft een object terug met { lookup, tree, templateId }
 */
async function loadWebTemplate(url) {
  const resolvedUrl = url || '/webtemplates/sensire_wound_care_webtemplate.json';
  const resp = await fetch(resolvedUrl);
  if (!resp.ok) throw new Error(`WebTemplate laden mislukt: ${resp.status}`);
  const wt = await resp.json();

  const lookup = {};
  if (wt.tree) {
    buildLookupFromNode(wt.tree, '', lookup);
  }

  return { lookup, tree: wt.tree, templateId: wt.templateId, raw: wt };
}

/**
 * Vertaal een FLAT JSON sleutel naar een leesbaar Nederlands label.
 * Verwijdert de template-prefix en indexen zoals ":0", ":1".
 */
function translateFlatKey(flatKey, lookup, templateId) {
  // Verwijder template prefix (bijv. "sensire_wound_care/")
  const prefix = templateId ? templateId + '/' : '';
  let stripped = flatKey.startsWith(prefix) ? flatKey.slice(prefix.length) : flatKey;

  // Verwijder suffix (|code, |value, |magnitude, |unit, |terminology)
  const suffixMatch = stripped.match(/^(.*?)\|(\w+)$/);
  const suffix = suffixMatch ? suffixMatch[2] : null;
  if (suffixMatch) stripped = suffixMatch[1];

  // Verwijder numerieke indexen zoals ":0", ":1"
  const normalized = stripped.replace(/:(\d+)/g, '');

  // Zoek in lookup
  const entry = lookup[templateId + '/' + normalized] || lookup[normalized];

  let label = entry ? entry.nl : normalized.split('/').pop();

  // Voeg suffix toe als context
  const suffixLabels = {
    'code': ' (code)',
    'value': '',
    'magnitude': ' (waarde)',
    'unit': ' (eenheid)',
    'terminology': ' (terminologie)',
    'name': ' (naam)'
  };
  if (suffix && suffix !== 'value') {
    label += (suffixLabels[suffix] || ` (${suffix})`);
  }

  return { label, entry, suffix, normalizedKey: normalized };
}

/**
 * Vertaal een at-code of waarde naar een leesbare Nederlandse string.
 */
function translateValue(value, entry) {
  if (!value) return '—';

  // Directe at-code lookup
  if (typeof value === 'string' && NL_CODE_VALUES[value]) {
    return NL_CODE_VALUES[value];
  }

  // Zoek in de inputs van het entry
  if (entry && entry.inputs) {
    for (const input of entry.inputs) {
      if (input.list) {
        const found = input.list.find(item => item.value === value);
        if (found) {
          return found.localizedLabels?.nl || found.localizedLabels?.en || found.label || value;
        }
      }
    }
  }

  return String(value);
}

/**
 * Render een FLAT JSON compositie als driekolommen-HTML-tabel.
 * Slaat interne/context-velden over die niet klinisch relevant zijn voor de demo.
 */
function renderFlatAsThreeColumns(flatJson, lookup, templateId) {
  const SKIP_PATTERNS = [
    /\/_uid$/, /\/category\|/, /\/context\/setting\|/, /\/language$/, /\/language\|/,
    /\/territory$/, /\/territory\|/, /\/encoding/, /\/subject\//, /\/composer\|id/,
    /\/composer\|id_scheme/, /\/composer\|id_namespace/, /\/time$/
  ];

  const rows = [];
  for (const [key, val] of Object.entries(flatJson)) {
    if (!val && val !== 0) continue;
    if (SKIP_PATTERNS.some(p => p.test(key))) continue;

    const { label, entry, suffix } = translateFlatKey(key, lookup, templateId);

    // Bij |code: sla de ruwe code op voor combinatie met |value
    if (suffix === 'code') continue; // Toon alleen |value of gecombineerd

    let displayVal = val;
    // Probeer at-code te vertalen via de waarde
    if (typeof val === 'string' && val.startsWith('at')) {
      displayVal = NL_CODE_VALUES[val] || translateValue(val, entry);
    }

    rows.push({ key, label, value: displayVal });
  }

  if (rows.length === 0) {
    return '<p style="color: var(--color-text-secondary); padding: 1rem;">Geen klinische data gevonden in deze compositie.</p>';
  }

  return `
    <table class="three-col-table">
      <thead>
        <tr>
          <th>openEHR Pad</th>
          <th>Nederlands Label</th>
          <th>Waarde</th>
        </tr>
      </thead>
      <tbody>
        ${rows.map(r => `
          <tr>
            <td class="three-col-table__path"><code>${escapeHtml(r.key)}</code></td>
            <td class="three-col-table__label">${escapeHtml(r.label)}</td>
            <td class="three-col-table__value">${escapeHtml(String(r.value))}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/**
 * Bepaal of een archetype Sensire-eigen of internationaal is.
 */
function classifyArchetype(nodeId) {
  if (!nodeId) return 'unknown';
  const id = nodeId.toLowerCase();
  for (const sensire of SENSIRE_ARCHETYPES) {
    if (id.includes(sensire)) return 'sensire';
  }
  return 'international';
}
