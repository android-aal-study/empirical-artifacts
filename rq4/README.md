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

Due to space limit and network issue, we do not upload all the APK files as well as the output JSON files.

## About Three Types of API Calls

This part presents detail API usages for direct, extra, and reflect API calls, all of them can be obtained from the resulting lists.

### Direct API call

|   App Set   | using APK number | JAR-only fields | XML-only fields | TXT-only fields | CSV-only fields | shared fields | total used fields | JAR-only methods | XML-only methods | TXT-only methods | CSV-only methods | shared methods | total used methods |
|:-----------:|:----------------:|:---------------:|:---------------:|:---------------:|:---------------:|:-------------:|:-----------------:|:----------------:|:----------------:|:----------------:|:----------------:|:--------------:|:------------------:|
|   F-Droid   |       4046       |        -        |       0/13      |        -        |   1537/189074   |   1738/26689  |        3291       |       6/959      |      27/241      |        0/4       |    3926/267089   |   15825/40613  |        21682       |
| Google Play |       12968      |        -        |       1/13      |        -        |    666/189074   |   2098/26689  |        2788       |      11/959      |      29/241      |        0/4       |    2228/267089   |   20125/40613  |        25412       |
|   Malware   |        745       |        -        |       0/13      |        -        |    19/189074    |   930/26689   |        962        |       2/959      |      18/241      |        0/4       |     56/267089    |   9703/40613   |        10892       |

Since we are more interested in exclusive APIs and shared APIs, thus we only display the usage of them. Specifically, JAR and TXT have no exclusive APIs, thus their cells have no data. All the shared APIs and exclusive APIs are **computed over all API-levels**, thus the numbers are different to the Venn4 diagrams shown in either the paper or in the `rq2` folder.

### Extra API call

|   App Set   | using APK number | all used fields | Support/AndroidX fields | used fields (no obf.) | Support/AndroidX fields (no obf.) | all used methods | Support/AndroidX methods | used methods (no obf.) | Support/AndroidX methods (no obf.) |
|:-----------:|:----------------:|:---------------:|:-----------------------:|:---------------------:|:---------------------------------:|:----------------:|:------------------------:|:----------------------:|:----------------------------------:|
|   F-Droid   |       3332       |      23156      |          22586          |          4449         |                4209               |      105077      |          102881          |          10006         |                9215                |
| Google Play |       12719      |      100679     |          90247          |         19582         |               15738               |      612253      |          569123          |          44608         |                37021               |
|   Malware   |        629       |       1567      |           1523          |          190          |                170                |       10562      |           9367           |          1092          |                 891                |

The columns with "(no obf.)" are numbers of used APIs that without the obfuscated ones. We detect obfuscated APIs by simple heuristics, i.e., the occurrences of single character or two characters identifiers (source code in the `call_api_info.py` script).

### Reflect API call



