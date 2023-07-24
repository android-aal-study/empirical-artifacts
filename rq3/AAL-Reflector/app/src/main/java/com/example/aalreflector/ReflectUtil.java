package com.example.aalreflector;

import androidx.annotation.Nullable;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class ReflectUtil {

    private static final Map<String, Class<?>> classCache = new HashMap<>();
    private static final Set<String> nonExistClass = new HashSet<>();

    private static final boolean ALL_MODE = false;

    private static String toJniName(String name) {
        if("boolean".equals(name)) {
            return "Z";
        }
        else if("char".equals(name)) {
            return "C";
        }
        else if("byte".equals(name)) {
            return "B";
        }
        else if("short".equals(name)) {
            return "S";
        }
        else if("int".equals(name)) {
            return "I";
        }
        else if("long".equals(name)) {
            return "J";
        }
        else if("float".equals(name)) {
            return "F";
        }
        else if("double".equals(name)) {
            return "D";
        }
        else {
            return "L" + name + ";";
        }
    }

    public static @Nullable Class<?> getClass(String name) {
        if (classCache.containsKey(name)) {
            return classCache.get(name);
        }
        else if (nonExistClass.contains(name)) {
            return null;
        }
        else {
            try {
                Class<?> clazz;
                if("boolean".equals(name)) {
                    clazz = boolean.class;
                }
                else if("char".equals(name)) {
                    clazz = char.class;
                }
                else if("byte".equals(name)) {
                    clazz = byte.class;
                }
                else if("short".equals(name)) {
                    clazz = short.class;
                }
                else if("int".equals(name)) {
                    clazz = int.class;
                }
                else if("long".equals(name)) {
                    clazz = long.class;
                }
                else if("float".equals(name)) {
                    clazz = float.class;
                }
                else if("double".equals(name)) {
                    clazz = double.class;
                }
                else if(name.endsWith("[]")) {
                    String tmpName = name;
                    String reflectName = "";
                    while(tmpName.endsWith("[]")) {
                        reflectName = "[" + reflectName;
                        tmpName = tmpName.substring(0, tmpName.length()-2);
                    }
                    reflectName += toJniName(tmpName);
                    clazz = Class.forName(reflectName);
                }
                else {
                    clazz = Class.forName(name);
                }
                classCache.put(name, clazz);
                return clazz;
            } catch (ClassNotFoundException | ExceptionInInitializerError e) {
                nonExistClass.add(name);
                return null;
            }
        }
    }


    public static @Nullable Field getField(String className, String name) {
        Class<?> clazz = getClass(className);
        if(clazz != null) {
            try {
                return clazz.getDeclaredField(name);
            } catch (NoSuchFieldException e) {
                if(ALL_MODE) {
                    try {
                        return clazz.getField(name);
                    } catch (NoSuchFieldException ignored) {
                    }
                }
            }
        }
        return null;
    }


    private static Class<?>[] toParameterClassList(String[] types) {
        Class<?>[] classes = new Class<?>[types.length];
        for(int i = 0; i < types.length; i++) {
            Class<?> clazz = getClass(types[i]);
            classes[i] = clazz;
        }
        return classes;
    }

    public static @Nullable Method getMethod(String className, String name, String[] parameters) {
        Class<?> clazz = getClass(className);
        if(clazz != null) {
            Class<?>[] params = toParameterClassList(parameters);
            assert params.length == parameters.length;
            try {
                return clazz.getDeclaredMethod(name, params);
            } catch (NoSuchMethodException e) {
                if(ALL_MODE) {
                    try {
                        return clazz.getMethod(name, params);
                    } catch (NoSuchMethodException ignored) {
                    }
                }
            }
        }
        return null;
    }

    public static @Nullable Constructor<?> getConstructor(String className, String[] parameters) {
        Class<?> clazz = getClass(className);
        if(clazz != null) {
            Class<?>[] params = toParameterClassList(parameters);
            assert params.length == parameters.length;
            try {
                return clazz.getDeclaredConstructor(params);
            } catch (NoSuchMethodException e) {
                if(ALL_MODE) {
                    try {
                        return clazz.getConstructor(params);
                    } catch (NoSuchMethodException ignored) {
                    }
                }
            }
        }
        return null;
    }

}
