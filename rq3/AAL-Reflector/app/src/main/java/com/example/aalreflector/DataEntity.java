package com.example.aalreflector;

public class DataEntity {

    public int apiLevel;

    public int reflectedClass;
    public int totalClass;
    public String getClassCell() {
        return reflectedClass + "/" + totalClass;
    }

    public int reflectedField;
    public int totalField;
    public String getFieldCell() {
        return reflectedField + "/" + totalField;
    }

    public int reflectedMethod;
    public int totalMethod;
    public String getMethodCell() {
        return reflectedMethod + "/" + totalMethod;
    }

    public DataEntity(int apiLevel, int reflectedClass, int totalClass, int reflectedField, int totalField, int reflectedMethod, int totalMethod) {
        this.apiLevel = apiLevel;
        this.reflectedClass = reflectedClass;
        this.totalClass = totalClass;
        this.reflectedField = reflectedField;
        this.totalField = totalField;
        this.reflectedMethod = reflectedMethod;
        this.totalMethod = totalMethod;
    }

    public DataEntity(int apiLevel, int totalClass, int totalField, int totalMethod) {
        this.apiLevel = apiLevel;
        this.totalClass = totalClass;
        this.totalField = totalField;
        this.totalMethod = totalMethod;
    }

}
