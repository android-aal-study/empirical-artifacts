# RQ4

## About APK-Analyzer

APK-Analyzer is used to extract API calls in an Android package (APK) file. It is built on Maven, to build an executable, you should install Maven on your device. It will output an executable JAR to the `test` directory (can be configured in the `pom.xml` file).

```bash
cd APK-Analyzer
mvn clean package   # will output to ../test
cd ../test
java -jar ./analyzer-1.0-SNAPSHOT-jar-with-dependencies.jar <android-platform-directory> ./a2dp.Vol_169.apk ./output ./veridex-linux
```

The path `<android-platform-directory>` can be downloaded from [here](https://github.com/CirQ/android-platforms). The command above outputs a `.json` file in the `output` directory.

Each JSON file contains a list `compassMethods`, which is an array of the following item:

```json
{
    // the caller method
    "method":"<a2dp.Vol.ManageData: void setupActionBar()>",
    // list of direct calls to AAL APIs
    "call_APIs":["<android.app.Activity: android.app.ActionBar getActionBar()>","<android.app.ActionBar: void setDisplayHomeAsUpEnabled(boolean)>"],
    // list of extra calls to APIs start with "android." or "androidx." or "com.android."
    "call_external_APIs":[],
    // list of reflect API calls, output by veridex, with filtering
    "call_reflect_APIs":[]
}
```

## About APK Dataset

We have three APK datasets. They correspond to three typical app categories, open-source apps, commercial apps, and malware. You may check them in the three .txt files.


