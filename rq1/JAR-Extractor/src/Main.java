import soot.*;
import soot.options.Options;

import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;


public class Main {
    public static void bundledAnalyze(String txtPath) throws IOException {
        int classNum = 0, fieldNum = 0, methodNum = 0;

        try(FileWriter fileWriter = new FileWriter(txtPath)) {
            for(SootClass sootClass : Scene.v().getClasses(SootClass.BODIES)) {
                classNum += 1;

                String name = sootClass.getName();
                fileWriter.write(name);
                fileWriter.write('\n');

                for (SootField field : sootClass.getFields()) {
                    fieldNum += 1;

                    //remove the char ' in the signature
                    String sig = field.getSignature().replace("'", "");
                    fileWriter.write(sig);
                    fileWriter.write('\n');
                }

                for (SootMethod method : sootClass.getMethods()) {
                    if(sootClass.isEnum() && method.isConstructor())
                        continue;

                    methodNum += 1;

                    //remove the char ' in the signature
                    String sig = method.getSignature().replace("'", "");
                    fileWriter.write(sig);
                    fileWriter.write('\n');
                }
            }
        }

        System.out.println("loaded class: " + classNum);
        System.out.println("loaded field: " + fieldNum);
        System.out.println("loaded method: " + methodNum);
    }


    public static void setUp(String jarPath) {
        Options.v().set_src_prec(Options.src_prec_class);
        Options.v().set_output_format(Options.output_format_none);

        List<String> pathList = new ArrayList<>();
        pathList.add(jarPath);

        Options.v().set_process_dir(pathList);
        Options.v().set_allow_phantom_refs(true);
        Options.v().set_prepend_classpath(true);
        Options.v().set_validate(true);

        try {
            Scene.v().loadNecessaryClasses();
        } catch (Exception e) {
            System.out.println("error in loadNecessaryClasses");
        }

        System.out.println("setup for jar: " + jarPath);
    }


    public static void runAll(String path) {
        try {
            Path dataPath = Paths.get(path);
            if (Files.isDirectory(dataPath) && dataPath.getFileName().endsWith("data")) {
                for (int v = 28; v < 34; v++) {
                    Path parentPath = dataPath.resolve("android-" + v);

                    String inputJarPath = parentPath.resolve("raw/android.jar").toString();
                    setUp(inputJarPath);

                    String outputTxtPath = parentPath.resolve("android.jar.txt").toString();
                    bundledAnalyze(outputTxtPath);

                    G.reset();
                }
                return;
            }
        } catch (Exception ignore) {}

        System.err.println("Usage:");
        System.err.println("    java -jar executable.jar <data-path>");
    }


    public static void runOne() {
        try {
            String path = "../data/android-33/raw/android.jar";
            setUp(path);
            bundledAnalyze("debug.txt");
        } catch (Exception ignore) {}
    }


    public static void main(String[] args) {
//        runOne();
        runAll(args[0]);
    }
}
