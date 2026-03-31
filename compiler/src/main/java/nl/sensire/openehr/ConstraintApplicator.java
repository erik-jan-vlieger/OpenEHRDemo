package nl.sensire.openehr;

import com.nedap.archie.aom.*;
import com.nedap.archie.base.MultiplicityInterval;
import com.nedap.archie.xml.JAXBUtil;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import javax.xml.bind.Marshaller;
import javax.xml.bind.Unmarshaller;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.regex.*;

/**
 * Past occurrence-constraints toe op gegenereerde OPT-bestanden
 * op basis van JSON-configuratiebestanden.
 *
 * Gebruik:
 *   ./gradlew applyConstraints
 *
 * Leest: opts/*.opt + constraints/*.json
 * Schrijft: opts/*.opt (overschrijft)
 */
public class ConstraintApplicator {

    private static final ObjectMapper JSON = new ObjectMapper();
    private static final Pattern PATH_SEGMENT = Pattern.compile("([a-z_]+)\\[([a-z]+[0-9.]+)\\]");

    public static void main(String[] args) throws Exception {
        Path optsDir = Paths.get("opts");
        Path constraintsDir = Paths.get("constraints");

        for (int i = 0; i < args.length; i++) {
            switch (args[i]) {
                case "--opts": optsDir = Paths.get(args[++i]); break;
                case "--constraints": constraintsDir = Paths.get(args[++i]); break;
            }
        }

        System.out.println("=== Sensire OpenEHR — Constraint Applicator ===");
        System.out.println("OPTs:        " + optsDir.toAbsolutePath());
        System.out.println("Constraints: " + constraintsDir.toAbsolutePath());
        System.out.println();

        int applied = 0;
        int skipped = 0;
        int errors = 0;

        // Process each constraint JSON
        File[] jsonFiles = constraintsDir.toFile().listFiles((d, n) -> n.endsWith(".json"));
        if (jsonFiles == null || jsonFiles.length == 0) {
            System.out.println("Geen constraint-bestanden gevonden in " + constraintsDir);
            return;
        }

        for (File jsonFile : jsonFiles) {
            JsonNode config = JSON.readTree(jsonFile);
            String templateId = config.get("template_id").asText();
            String optFileName = templateId + ".opt";
            Path optPath = optsDir.resolve(optFileName);

            if (!Files.exists(optPath)) {
                System.out.println("⊘ OPT niet gevonden: " + optFileName + " — overgeslagen");
                skipped++;
                continue;
            }

            System.out.println("--- " + templateId + " ---");

            try {
                // Load OPT
                Unmarshaller unmarshaller = JAXBUtil.getArchieJAXBContext().createUnmarshaller();
                OperationalTemplate opt;
                try (InputStream is = Files.newInputStream(optPath)) {
                    opt = (OperationalTemplate) unmarshaller.unmarshal(is);
                }

                int rulesApplied = 0;
                int rulesFailed = 0;

                // Process each archetype's constraints
                for (JsonNode archetypeBlock : config.get("constraints")) {
                    String archetypeId = archetypeBlock.get("archetype").asText();
                    JsonNode rules = archetypeBlock.get("rules");

                    // Find all CArchetypeRoot nodes matching this archetype
                    List<CArchetypeRoot> roots = findArchetypeRoots(opt.getDefinition(), archetypeId);

                    if (roots.isEmpty()) {
                        System.out.println("  ⚠ Archetype niet gevonden in OPT: " + archetypeId);
                        continue;
                    }

                    for (JsonNode rule : rules) {
                        String path = rule.get("path").asText();
                        String occStr = rule.get("occurrences").asText();
                        String label = rule.has("label") ? rule.get("label").asText() : path;
                        MultiplicityInterval occ = parseOccurrences(occStr);

                        boolean found = false;
                        for (CArchetypeRoot root : roots) {
                            CObject target = findNodeByPath(root, path);
                            if (target != null) {
                                target.setOccurrences(occ);
                                found = true;
                            }
                        }

                        if (found) {
                            System.out.println("  ✓ " + occStr + "  " + label);
                            rulesApplied++;
                        } else {
                            System.out.println("  ✗ Pad niet gevonden: " + path + " (" + label + ")");
                            rulesFailed++;
                        }
                    }
                }

                // Write modified OPT back
                Marshaller marshaller = JAXBUtil.getArchieJAXBContext().createMarshaller();
                marshaller.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, Boolean.TRUE);
                marshaller.setProperty(Marshaller.JAXB_ENCODING, "UTF-8");

                try (OutputStream os = Files.newOutputStream(optPath)) {
                    marshaller.marshal(opt, os);
                }

                System.out.println("  → " + rulesApplied + " constraints toegepast, "
                    + rulesFailed + " paden niet gevonden");
                System.out.println("  → OPT bijgewerkt: " + optFileName);
                applied++;

            } catch (Exception e) {
                System.err.println("  FOUT bij " + templateId + ": " + e.getMessage());
                e.printStackTrace(System.err);
                errors++;
            }
            System.out.println();
        }

        System.out.println("=== Resultaat ===");
        System.out.println("Verwerkt:    " + applied);
        System.out.println("Overgeslagen: " + skipped);
        System.out.println("Fouten:      " + errors);

        if (errors > 0) System.exit(1);
    }

    /**
     * Find all CArchetypeRoot nodes in the tree that match the given archetype ID prefix.
     * Searches recursively through the entire OPT tree.
     */
    static List<CArchetypeRoot> findArchetypeRoots(CComplexObject root, String archetypeIdPrefix) {
        List<CArchetypeRoot> results = new ArrayList<>();
        findArchetypeRootsRecursive(root, archetypeIdPrefix, results);
        return results;
    }

    private static void findArchetypeRootsRecursive(CObject node, String archetypeIdPrefix, List<CArchetypeRoot> results) {
        if (node instanceof CArchetypeRoot) {
            CArchetypeRoot ar = (CArchetypeRoot) node;
            String aid = ar.getArchetypeRef();
            if (aid != null && aid.startsWith(archetypeIdPrefix)) {
                results.add(ar);
            }
        }

        if (node instanceof CComplexObject) {
            CComplexObject complex = (CComplexObject) node;
            for (CAttribute attr : complex.getAttributes()) {
                for (CObject child : attr.getChildren()) {
                    findArchetypeRootsRecursive(child, archetypeIdPrefix, results);
                }
            }
        }
    }

    /**
     * Navigate to a specific node using an ADL-style path like:
     * /data[at0001]/items[at0002]
     *
     * Each segment is attribute_name[node_id].
     */
    static CObject findNodeByPath(CComplexObject start, String path) {
        if (path == null || path.isEmpty()) return start;

        String cleanPath = path.startsWith("/") ? path.substring(1) : path;
        List<String[]> segments = new ArrayList<>();

        Matcher m = PATH_SEGMENT.matcher(cleanPath);
        while (m.find()) {
            segments.add(new String[]{ m.group(1), m.group(2) });
        }

        CComplexObject current = start;
        for (int i = 0; i < segments.size(); i++) {
            String attrName = segments.get(i)[0];
            String nodeId = segments.get(i)[1];

            CAttribute attr = current.getAttribute(attrName);
            if (attr == null) return null;

            CObject found = null;
            for (CObject child : attr.getChildren()) {
                if (nodeId.equals(child.getNodeId())) {
                    found = child;
                    break;
                }
            }

            if (found == null) return null;

            if (found instanceof CComplexObject) {
                current = (CComplexObject) found;
            } else {
                // Leaf node — only valid if this is the last segment
                return (i == segments.size() - 1) ? found : null;
            }
        }

        return current;
    }

    /**
     * Parse an occurrences string like "0..0", "1..1", "0..1", "1..*" into MultiplicityInterval.
     */
    static MultiplicityInterval parseOccurrences(String occ) {
        return MultiplicityInterval.createFromString(occ);
    }
}
