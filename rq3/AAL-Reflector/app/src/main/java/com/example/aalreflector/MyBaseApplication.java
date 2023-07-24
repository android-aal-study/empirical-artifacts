package com.example.aalreflector;

import android.app.Application;
import android.content.Context;

import me.weishu.reflection.Reflection;

public class MyBaseApplication extends Application {
    @Override
    protected void attachBaseContext(Context base) {
        super.attachBaseContext(base);
        Reflection.unseal(base);
    }
}
