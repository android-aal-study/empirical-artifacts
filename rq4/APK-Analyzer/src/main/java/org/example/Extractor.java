package org.example;

import org.apache.commons.io.IOUtils;
import soot.*;
import soot.jimple.FieldRef;
import soot.jimple.InvokeExpr;
import soot.options.Options;
import soot.util.Chain;

import java.io.*;
import java.nio.charset.Charset;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;


public class Extractor {
    private final String apkPath;

    private final String androidJar;

    private final String veridexFolder;

    private final HashSet<String> allFields;

    private final HashSet<String> allMethods;

    public Extractor(String apkPath, String androidJar, String veridexFolder) {
        this.apkPath = apkPath;
        this.androidJar = androidJar;
        this.veridexFolder = veridexFolder;
        this.allFields = new HashSet<>();
        this.allMethods = new HashSet<>();
        setApiList();
    }

    private boolean isSdkOrJdk(String cl) {
        return isSdk(cl) || isJdk(cl);
    }

    private boolean isSdk(String cl) {
        return cl.startsWith("android.")
                || cl.startsWith("androidx.")
                || cl.startsWith("com.android.");
    }

    private static boolean isJdk(String cl) {
        return cl.startsWith("java.")
                || cl.startsWith("javax.")
                || cl.startsWith("sun.");
    }

    private void setApiList() {
        try {
            try (InputStream stream = getClass().getResourceAsStream("/all-fields.txt")) {
                for(String line: IOUtils.readLines(stream, Charset.defaultCharset())) {
                    allFields.add(line.replace("\n", ""));
                }
            }
            try (InputStream stream = getClass().getResourceAsStream("/all-methods.txt")) {
                for(String line: IOUtils.readLines(stream, Charset.defaultCharset())) {
                    allMethods.add(line.replace("\n", ""));
                }
            }
            if(allFields.isEmpty() || allMethods.isEmpty()) {
                System.err.println("API files unloaded!");
                System.exit(-1);
            }
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    private void setUpSoot() {
        G.reset();
        Options.v().set_src_prec(Options.src_prec_apk);
        String androidJarPath = Scene.v().getAndroidJarPath(androidJar, apkPath);
        List<String> pathList = new ArrayList<>();
        pathList.add(apkPath);
        pathList.add(androidJarPath);

        Options.v().set_process_dir(pathList);
        Options.v().set_force_android_jar(androidJar);
        Options.v().set_process_multiple_dex(true);
        Options.v().set_allow_phantom_refs(true);
        Options.v().set_no_writeout_body_releasing(true);
        Options.v().set_whole_program(false);

        Scene.v().loadNecessaryClasses();
    }

    private String transformFormat(String sootSignature) {
        sootSignature = sootSignature.replace("'", "");
        String namespace = sootSignature.substring(1, sootSignature.indexOf(":"));
        String name = sootSignature.substring(sootSignature.lastIndexOf(" ") + 1, sootSignature.lastIndexOf(">"));
        return namespace + "->" + name;
    }

    private void analyseSupperClassFields(SootField sootField, SootMethod caller, HashMap<String, HashSet<String>> call_api_map, HashMap<String, HashSet<String>> call_external_api_map) {
        SootClass declaringClass = sootField.getDeclaringClass();
        while (declaringClass.hasSuperclass()) {
            SootClass superClass = declaringClass.getSuperclass();
            String subSignature = sootField.getSubSignature();
            if (superClass.declaresField(subSignature)) {
                String transformedSupperSignature = transformFormat(superClass.getField(subSignature).getSignature());
                if (allFields.contains(transformedSupperSignature)) {
                    apiFinded(call_api_map, caller, superClass.getField(subSignature).getSignature());
                    break;
                }
                else if (isSdk(transformedSupperSignature)) {
                    apiFinded(call_external_api_map, caller, superClass.getField(subSignature).getSignature());
                    break;
                }
            }
            declaringClass = superClass;
        }
        //traverse the interfaces
        declaringClass = sootField.getDeclaringClass();
        if (declaringClass.getInterfaceCount() != 0) { //if the class implements interfaces
            Chain<SootClass> interfaces = declaringClass.getInterfaces();
            for(SootClass inter: interfaces) {
                String subSignature = sootField.getSubSignature();
                if (inter.declaresField(subSignature)) {
                    String transformedSupperSignature = transformFormat(inter.getField(subSignature).getSignature());
                    if (allFields.contains(transformedSupperSignature)) {
                        apiFinded(call_api_map, caller, inter.getField(subSignature).getSignature());
                    }
                    else if (isSdk(transformedSupperSignature)) {
                        apiFinded(call_external_api_map, caller, inter.getField(subSignature).getSignature());
                    }
                }
            }
        }
    }

    private void analyseSupperClassMethods(SootMethod sootMethod, SootMethod caller, HashMap<String, HashSet<String>> call_api_map, HashMap<String, HashSet<String>> call_external_api_map) {
        SootClass declaringClass = sootMethod.getDeclaringClass();
        while (declaringClass.hasSuperclass()) {
            SootClass superClass = declaringClass.getSuperclass();
            String subSignature = sootMethod.getSubSignature();
            if (superClass.declaresMethod(subSignature)) {
                String transformedSupperSignature = transformFormat(superClass.getMethod(subSignature).getSignature());
                if (allMethods.contains(transformedSupperSignature)) {
                    apiFinded(call_api_map, caller, superClass.getMethod(subSignature).getSignature());
                    break;
                }
                else if (isSdk(transformedSupperSignature)) {
                    apiFinded(call_external_api_map, caller, superClass.getMethod(subSignature).getSignature());
                    break;
                }
            }
            declaringClass = superClass;
        }
        //traverse the interfaces
        declaringClass = sootMethod.getDeclaringClass();
        if (declaringClass.getInterfaceCount() != 0) { //if the class implements interfaces
            Chain<SootClass> interfaces = declaringClass.getInterfaces();
            interfaces.forEach(inter -> {
                String subSignature = sootMethod.getSubSignature();
                if (inter.declaresMethod(subSignature)) {
                    String transformedSupperSignature = transformFormat(inter.getMethod(subSignature).getSignature());
                    if (allMethods.contains(transformedSupperSignature)) {
                        apiFinded(call_api_map, caller, inter.getMethod(subSignature).getSignature());
                    }
                    else if (isSdk(transformedSupperSignature)) {
                        apiFinded(call_external_api_map, caller, inter.getMethod(subSignature).getSignature());
                    }
                }
            });
        }
    }

    private void apiFinded(HashMap<String, HashSet<String>> map, SootMethod sm, String signature) {
        String callerSignature = sm.getSignature();
        //remove the char ' in the signature
        callerSignature = callerSignature.replace("'", "");
        signature = signature.replace("'", "");

        if (map.containsKey(callerSignature)) {
            map.get(callerSignature).add(signature);
        } else {
            HashSet<String> callApiSet = new HashSet<>();
            callApiSet.add(signature);
            map.put(sm.getSignature(), callApiSet);
        }
    }



    private String convert(String jni) {
        return jni;
    }
    private List<String> toList(String jni, List<String> previous) {
        if(jni.equals("")) {
            return previous;
        }
        else if(jni.startsWith("V")) {
            previous.add("void");
            return toList(jni.substring(1), previous);
        }
        else if(jni.startsWith("Z")) {
            previous.add("boolean");
            return toList(jni.substring(1), previous);
        }
        else if(jni.startsWith("B")) {
            previous.add("byte");
            return toList(jni.substring(1), previous);
        }
        else if(jni.startsWith("C")) {
            previous.add("char");
            return toList(jni.substring(1), previous);
        }
        else if(jni.startsWith("S")) {
            previous.add("short");
            return toList(jni.substring(1), previous);
        }
        else if(jni.startsWith("I")) {
            previous.add("int");
            return toList(jni.substring(1), previous);
        }
        else if(jni.startsWith("J")) {
            previous.add("long");
            return toList(jni.substring(1), previous);
        }
        else if(jni.startsWith("F")) {
            previous.add("float");
            return toList(jni.substring(1), previous);
        }
        else if(jni.startsWith("D")) {
            previous.add("double");
            return toList(jni.substring(1), previous);
        }
        else {
            int semi = jni.indexOf(';');
            String type = jni.substring(1, semi).replace("/", ".");
            previous.add(type);
            return toList(jni.substring(semi+1), previous);
        }
    }
    private String convertMethod(String jni, boolean nonSdkOnly) {
        Pattern p = Pattern.compile("^(.*?)->(.*?)\\((.*?)\\)(.*?)$");
        Matcher m = p.matcher(jni);
        if(m.find()) {
            String cls = m.group(1);
            String clsS = toList(cls, new LinkedList<>()).get(0);
            if(nonSdkOnly && isSdkOrJdk(clsS))
                return null;
            String name = m.group(2);
            String params = m.group(3);
            String paramsS = String.join(",", toList(params, new LinkedList<>()));
            String ret = m.group(4);
            String retS = toList(ret, new LinkedList<>()).get(0);
            return String.format("<%s: %s %s(%s)>", clsS, retS, name, paramsS);
        }
        else {
            return null;
        }
    }
    private void analyzeByVeridex(Map<String,HashSet<String>> map) {
        ProcessBuilder pb;
        if(System.getProperty("os.name").toLowerCase().contains("win")) {
            String convertVeridexPath = veridexFolder.replace("C:/", "/mnt/c/");
            String convertApkPath = apkPath.replace("C:/", "/mnt/c/");
            String appcompat = convertVeridexPath + "/appcompat.sh";
            String dexfile = "--dex-file=" + convertApkPath;
            pb = new ProcessBuilder("wsl", appcompat, dexfile);
        }
        else {
            String appcompat = veridexFolder+ "/appcompat.sh";
            String dexfile = "--dex-file=" + apkPath;
            pb = new ProcessBuilder(appcompat, dexfile);
        }
        try {
//            pb.inheritIO();
            Process p = pb.start();
//            try {
//                p.waitFor();
//            }catch (InterruptedException e) {}

            BufferedReader reader = new BufferedReader(new InputStreamReader(p.getInputStream()));
            String line = reader.readLine();
            while (line != null) {


                String nextLine = null;
                if(line.startsWith("#")) {
                    int index = line.indexOf(' ');
                    String usage = line.substring(index+1);

                    if(usage.startsWith("Reflection")) {
                        String api = convert(usage.split(" ")[2]);
                        List<String> callers = new LinkedList<>();
                        nextLine = reader.readLine();
                        while(nextLine.startsWith("  ")) {
                            String caller = convertMethod(nextLine.trim(), true);
                            if(caller != null)
                                callers.add(caller);
                            nextLine = reader.readLine();
                        }
                        for(String caller: callers) {
                            if(map.containsKey(caller))
                                map.get(caller).add(api);
                            else {
                                HashSet<String> set = new HashSet<>();
                                set.add(api);
                                map.put(caller, set);
                            }
                        }
                    }
                    else if(usage.startsWith("Linking")) {
                        // omit on-purpose
                    }
                    else {
                        System.out.println(line);
                        System.exit(-1);
                    }
                }

                if(nextLine == null)
                    line = reader.readLine();
                else
                    line = nextLine;
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

//        System.out.println();
    }



    public List<MyMethod> analyseSingleApk() {
        setUpSoot();
        HashMap<String, HashSet<String>> call_api_map = new HashMap<>(); //caller -> callee apis
        HashMap<String, HashSet<String>> call_external_api_map = new HashMap<>(); //caller -> callee external apis

        for (SootClass sc : Scene.v().getApplicationClasses()) {
            if (!isSdkOrJdk(sc.getName())) {
                for (SootMethod sm : sc.getMethods()) {
                    try { //try to retrieve active body
                        sm.retrieveActiveBody();
                    } catch (Exception ignored) {}
                    if (sm.hasActiveBody()) {
                        for (Unit unit : sm.getActiveBody().getUnits()) {
                            for (ValueBox box : unit.getUseAndDefBoxes()) {
                                if (box.getValue() instanceof FieldRef) {
                                    FieldRef ref = (FieldRef) box.getValue();
                                    SootField sootField = ref.getField();
                                    String transformedFormat = transformFormat(sootField.getSignature());
                                    if (allFields.contains(transformedFormat)) {
                                        apiFinded(call_api_map, sm, sootField.getSignature());
                                    }
                                    else if (isSdk(transformedFormat)) {
                                        apiFinded(call_external_api_map, sm, sootField.getSignature());
                                    }
                                    else { //analyse super class
                                        analyseSupperClassFields(sootField, sm, call_api_map, call_external_api_map);
                                    }
                                }
                                if (box.getValue() instanceof InvokeExpr) {
                                    InvokeExpr invokeExpr = (InvokeExpr) box.getValue();
                                    SootMethod sootMethod = invokeExpr.getMethod();
                                    String transformedFormat = transformFormat(sootMethod.getSignature());
                                    if (allMethods.contains(transformedFormat)) {
                                        apiFinded(call_api_map, sm, sootMethod.getSignature());
                                    }
                                    else if (isSdk(transformedFormat)) {
                                        apiFinded(call_external_api_map, sm, sootMethod.getSignature());
                                    }
                                    else { //analyse super class
                                        analyseSupperClassMethods(sootMethod, sm, call_api_map, call_external_api_map);
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }


        HashMap<String, HashSet<String>> call_reflect_api_map = new HashMap<>();
        analyzeByVeridex(call_reflect_api_map);


        HashMap<String, MyMethod> compassMethods = new HashMap<>(); //merge call_api_map and call_external_api_map

        for(String key: call_api_map.keySet()) {
            // initialize method item
            MyMethod compassMethod = new MyMethod();
            compassMethod.method = key;
            // put APIs into
            for(String api: call_api_map.get(key)) {
                String signature = api.replace("'", "");
                if(isJdk(signature.substring(1)))
                    continue;
                compassMethod.APIs.add(signature);
            }
            if(!(compassMethod.APIs.isEmpty() && compassMethod.externalAPIs.isEmpty() && compassMethod.reflectAPIs.isEmpty()))
                compassMethods.put(key, compassMethod);
        }

        for(String key: call_external_api_map.keySet()) {
            // initialize method item
            MyMethod compassMethod;
            if (compassMethods.containsKey(key)) {
                compassMethod = compassMethods.get(key);
            }
            else {
                compassMethod = new MyMethod();
            }
            compassMethod.method = key;
            // put externalAPIs into
            for(String api : call_external_api_map.get(key)) {
                String signature = api.replace("'", "");
                if(isJdk(signature.substring(1)))
                    continue;
                compassMethod.externalAPIs.add(signature);
            }
            if(!(compassMethod.APIs.isEmpty() && compassMethod.externalAPIs.isEmpty() && compassMethod.reflectAPIs.isEmpty()))
                compassMethods.put(key, compassMethod);
        }

        for(String key: call_reflect_api_map.keySet()) {
            // initialize method item
            MyMethod compassMethod;
            if (compassMethods.containsKey(key)) {
                compassMethod = compassMethods.get(key);
            }
            else {
                compassMethod = new MyMethod();
            }
            compassMethod.method = key;
            // put reflectAPIs into
            for(String api : call_reflect_api_map.get(key)) {
                String cls = api.split(";->")[0].substring(1).replace('/', '.');
                if(isJdk(cls))
                    continue;
                compassMethod.reflectAPIs.add(api);
            }
            if(!(compassMethod.APIs.isEmpty() && compassMethod.externalAPIs.isEmpty() && compassMethod.reflectAPIs.isEmpty()))
                compassMethods.put(key, compassMethod);
        }

        //return values to list
        return new ArrayList<>(compassMethods.values());
    }



}
