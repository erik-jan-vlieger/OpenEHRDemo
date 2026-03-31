package nl.sensire.openehr;

import com.nedap.archie.adl14.ADL14ConversionConfiguration;
import com.nedap.archie.adl14.ADL14Parser;
import com.nedap.archie.adlparser.ADLParser;
import com.nedap.archie.adlparser.ADLParseException;
import com.nedap.archie.aom.Archetype;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.*;

public class ArchetypeValidator {

    public static void main(String[] args) throws Exception {
        Path dir = args.length > 0 ? Paths.get(args[0]) : Paths.get("archetypes");

        System.out.println("=== Sensire OpenEHR — Archetype Validator ===");
        System.out.println("Directory: " + dir.toAbsolutePath());
        System.out.println();

        List<Path> adlFiles = new ArrayList<>();
        Files.walkFileTree(dir, new SimpleFileVisitor<>() {
            @Override
            public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
                String name = file.getFileName().toString().toLowerCase();
                if (name.endsWith(".adl") || name.endsWith(".adl2") || name.endsWith(".adls")) {
                    adlFiles.add(file);
                }
                return FileVisitResult.CONTINUE;
            }
        });

        adlFiles.sort(Comparator.comparing(Path::getFileName));

        int valid = 0;
        int errors = 0;

        ADL14ConversionConfiguration convConfig = new ADL14ConversionConfiguration();
        ADL14Parser adl14Parser = new ADL14Parser(null);
        adl14Parser.setLogEnabled(false);

        for (Path file : adlFiles) {
            try {
                String content = stripBOM(new String(Files.readAllBytes(file), StandardCharsets.UTF_8));
                Archetype archetype;

                if (isADL14(content)) {
                    try {
                        archetype = adl14Parser.parse(content, convConfig);
                    } catch (ADLParseException e) {
                        System.out.println("  ✗ " + file.getFileName() + " [ADL 1.4]");
                        e.getErrors().getErrors().forEach(err ->
                            System.out.println("      FOUT: " + err.getMessage()));
                        errors++;
                        continue;
                    }
                    System.out.println("  ✓ " + file.getFileName()
                        + " — " + archetype.getArchetypeId().getFullId() + " [ADL 1.4]");
                } else {
                    ADLParser adl2Parser = new ADLParser();
                    adl2Parser.setLogEnabled(false);
                    try {
                        archetype = adl2Parser.parse(content);
                    } catch (ADLParseException e) {
                        System.out.println("  ✗ " + file.getFileName() + " [ADL2]");
                        e.getErrors().getErrors().forEach(err ->
                            System.out.println("      FOUT: " + err.getMessage()));
                        errors++;
                        continue;
                    }
                    System.out.println("  ✓ " + file.getFileName()
                        + " — " + archetype.getArchetypeId().getFullId() + " [ADL2]");
                }
                valid++;

            } catch (Exception e) {
                System.out.println("  ✗ " + file.getFileName()
                    + " — FOUT: " + e.getMessage());
                errors++;
            }
        }

        System.out.println();
        System.out.println("=== Resultaat ===");
        System.out.println("Totaal:  " + adlFiles.size());
        System.out.println("Geldig:  " + valid);
        System.out.println("Fouten:  " + errors);

        if (errors > 0) {
            System.out.println("\n⚠ Er zijn " + errors + " archetype(s) met fouten.");
            System.exit(1);
        } else {
            System.out.println("\n✓ Alle archetypes zijn geldig.");
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
}
