package org.example;

import com.alibaba.fastjson.annotation.JSONField;

import java.util.LinkedList;
import java.util.List;


class MyMethod {

    @JSONField(name="method", ordinal=1)
    public String method;

    @JSONField(name="call_APIs", ordinal=2)
    public List<String> APIs = new LinkedList<>();

    @JSONField(name="call_external_APIs", ordinal=3)
    public List<String> externalAPIs = new LinkedList<>();

    @JSONField(name="call_reflect_APIs", ordinal=4)
    public List<String> reflectAPIs = new LinkedList<>();

}
