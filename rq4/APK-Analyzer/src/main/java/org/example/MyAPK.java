package org.example;

import com.alibaba.fastjson.annotation.JSONField;

import java.util.ArrayList;
import java.util.List;

class MyAPK {
    @JSONField(name = "compassMethods", ordinal = 1)
    public List<MyMethod> compassMethods = new ArrayList<>();
}
