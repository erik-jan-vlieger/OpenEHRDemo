package nl.sensire.openehr;

import com.nedap.archie.adl14.ADL14ConversionConfiguration;
import com.nedap.archie.adl14.ADL14Parser;
import com.nedap.archie.adlparser.ADLParser;
import com.nedap.archie.adlparser.ADLParseException;
import com.nedap.archie.aom.Archetype;
import com.nedap.archie.aom.OperationalTemplate;
import com.nedap.archie.flattener.Flattener;
import com.nedap.archie.flattener.SimpleArchetypeRepository;
import com.nedap.archie.rminfo.ArchieRMInfoLookup;
import com.nedap.archie.rminfo.ReferenceModels;
import com.nedap.archie.xml.JAXBUtil;

import javax.xml.bind.Marshaller;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.*;

public class OPTGenerator {

    private final Path archetypesDir;
    private final Path templatesDir;
    private final Path outputDir;
    private final SimpleArchetypeRepository repository;
    private final ADL14ConversionConfiguration convConfig;
    private final ADL14Parser adl14Parser;

    public OPTGenerator(Path archetypesDir, Path templatesDir, Path outputDir) {
        this.archetypesDir = archetypesDir;
        this.templatesDir = templatesDir;
        this.outputDir = outputDir;
        this.repository = new SimpleArchetypeRepository();
        this.convConfig = new ADL14ConversionConfiguration();
        this.adl14Parser = new ADL14Parser(null);
        this.adl14Parser.setLogEnabled(false);
    }

    public static void main(String[] args) throws Exception {
        Path archetypesDir = Paths.get("archetypes");
        Path templatesDir = Paths.get("templates");
        Path outputDir = Paths.get("opts");

        for (int i = 0; i < args.length; i++) {
            switch (args[i]) {
                case "--archetypes": archetypesDir = Paths.get(args[++i]); break;
                case "--templates": templatesDir = Paths.get(args[++i]); break;
                case "--output": outputDir = Paths.get(args[++i]); break;
            }
        }

        System.out.println("=== Sensire OpenEHR OPT Generator ===");
        System.out.println("Archetypes: " + archetypesDir.toAbsolutePath());
        System.out.println("Templates:  " + templatesDir.toAbsolutePath());
        System.out.println("Output:     " + outputDir.toAbsolutePath());
        System.out.println();

        OPTGenerator generator = new OPTGenerator(archetypesDir, templatesDir, outputDir);
        generator.run();
    }

    public void run() throws Exception {
        Files.createDirectories(outputDir);

        System.out.println("--- Stap 1: Archetypes laden ---");
        loadArchetypes(archetypesDir);
        System.out.println("Totaal geladen: " + repository.getAllArchetypes().size() + " archetypes\n");

        System.out.println("--- Stap 2: Templates verwerken ---");
        List<Path> templateFiles = findFiles(templatesDir, ".adlt", ".oet");

        if (templateFiles.isEmpty()) {
            System.out.println("WAARSCHUWING: Geen templates gevonden in " + templatesDir);
            return;
        }

        ReferenceModels models = new ReferenceModels();
        models.registerModel(ArchieRMInfoLookup.getInstance());

        for (Path templateFile : templateFiles) {
            processTemplate(templateFile, models);
        }

        System.out.println("\n=== Gereed ===");
        System.out.println("OPT-bestanden staan in: " + outputDir.toAbsolutePath());
    }

    private void loadArchetypes(Path dir) throws IOException {
        List<Path> adlFiles = findFiles(dir, ".adl", ".adls", ".adl2");

        int loaded = 0;
        int errors = 0;

        for (Path adlFile : adlFiles) {
            try {
                String content = stripBOM(new String(Files.readAllBytes(adlFile), StandardCharsets.UTF_8));
                Archetype archetype;

                if (isADL14(content)) {
                    try {
                        archetype = adl14Parser.parse(content, convConfig);
                    } catch (ADLParseException e) {
                        System.err.println("  FOUT in " + adlFile.getFileName() + " [ADL 1.4]:");
                        e.getErrors().getErrors().forEach(err ->
                            System.err.println("    - " + err.getMessage()));
                        errors++;
                        continue;
                    }
                } else {
                    ADLParser parser = new ADLParser();
                    parser.setLogEnabled(false);
                    try {
                        archetype = parser.parse(content);
                    } catch (ADLParseException e) {
                        System.err.println("  FOUT in " + adlFile.getFileName() + " [ADL2]:");
                        e.getErrors().getErrors().forEach(err ->
                            System.err.println("    - " + err.getMessage()));
                        errors++;
                        continue;
                    }
                }

                repository.addArchetype(archetype);
                System.out.println("  ✓ " + archetype.getArchetypeId().getFullId()
                    + " (" + adlFile.getFileName() + ")");
                loaded++;

            } catch (Exception e) {
                System.err.println("  FOUT bij laden " + adlFile.getFileName() + ": " + e.getMessage());
                errors++;
            }
        }

        System.out.println("Geladen: " + loaded + ", Fouten: " + errors);
    }

    private void processTemplate(Path templateFile, ReferenceModels models) {
        String fileName = templateFile.getFileName().toString();
        System.out.println("\nVerwerken: " + fileName);

        try {
            String content = stripBOM(new String(Files.readAllBytes(templateFile), StandardCharsets.UTF_8));

            ADLParser parser = new ADLParser();
            parser.setLogEnabled(false);
            Archetype parsed = parser.parse(content);

            repository.addArchetype(parsed);

            Flattener flattener = new Flattener(repository, models)
                .createOperationalTemplate(true);

            OperationalTemplate opt = (OperationalTemplate) flattener.flatten(parsed);

            String baseName = fileName.replaceAll("\\.(adlt|oet)$", "");
            Path outputFile = outputDir.resolve(baseName + ".opt");

            Marshaller marshaller = JAXBUtil.getArchieJAXBContext().createMarshaller();
            marshaller.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, Boolean.TRUE);
            marshaller.setProperty(Marshaller.JAXB_ENCODING, "UTF-8");

            try (OutputStream os = Files.newOutputStream(outputFile)) {
                marshaller.marshal(opt, os);
            }

            System.out.println("  ✓ OPT gegenereerd: " + outputFile.getFileName());
            System.out.println("    Template ID: " + opt.getArchetypeId().getFullId());

        } catch (Exception e) {
            System.err.println("  FOUT bij genereren OPT: " + e.getMessage());
            e.printStackTrace(System.err);
        }
    }

    static String stripBOM(String s) {
        if (s != null && !s.isEmpty() && s.charAt(0) == '\uFEFF') {
            return s.substring(1);
        }
        return s;
    }

    static boolean isADL14(String content) {
        return content.contains("adl_version=1.4")
            || content.contains("adl_version=1.5");
    }

    private List<Path> findFiles(Path dir, String... extensions) throws IOException {
        if (!Files.exists(dir)) {
            return Collections.emptyList();
        }

        Set<String> exts = Set.of(extensions);
        List<Path> result = new ArrayList<>();

        Files.walkFileTree(dir, new SimpleFileVisitor<>() {
            @Override
            public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
                String name = file.getFileName().toString().toLowerCase();
                for (String ext : exts) {
                    if (name.endsWith(ext)) {
                        result.add(file);
                        break;
                    }
                }
                return FileVisitResult.CONTINUE;
            }
        });

        result.sort(Comparator.comparing(Path::getFileName));
        return result;
    }
}
