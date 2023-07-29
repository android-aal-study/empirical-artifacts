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

|   App Set   | using APK number | used fields | Support/AndroidX fields | used methods | Support/AndroidX methods | used fields (no obf.) | Support/AndroidX fields (no obf.) | used methods (no obf.) | Support/AndroidX methods (no obf.) |
| :---------: | :--------------: | :---------: | :---------------------: | :----------: | :----------------------: | :-------------------: | :-------------------------------: | :--------------------: | :--------------------------------: |
|   F-Droid   |       3332       |    23156    |          22586          |    105077    |          102881          |         4449          |               4209                |         10006          |                9215                |
| Google Play |      12719       |   100679    |          90247          |    612253    |          569123          |         19582         |               15738               |         44608          |               37021                |
|   Malware   |       629        |    1567     |          1523           |    10562     |           9367           |          190          |                170                |          1092          |                891                 |

The columns with "(no obf.)" are numbers of used APIs that without the obfuscated ones. We detect obfuscated APIs by simple heuristics, i.e., the occurrence of single character or two-characters identifiers (source code in the `call_api_info.py` script). More reliable obfuscation detection is out of our study scope.

### Reflect API call

|   App Set   | using APK number | CSV-only APIs | shared APIs | non-AAL APIs | total used APIs |
|:-----------:|:----------------:|:-------------:|:-----------:|:------------:|:---------------:|
|   F-Droid   |       1601       |   474/420630  |   12/60658  |       0      |       487       |
| Google Play |       11609      |  1518/420630  |   34/60658  |       1      |       1556      |
|   Malware   |        360       |   220/420630  |   10/60658  |       0      |       230       |

We only list CSV-only APIs and shared APIs and non-AAL APIs here. There can be reflected APIs appear in more than one AAL, thus the API numbers on each row may not necessarily sum up to total.

Also note that, since the detection results of veridex do not distinguish fields and methods, thus we sum their occurrence up and only present the numbers of APIs for each column.



## Printing the Table

Due to the large size of raw data cannot be uploaded, we only use the intermediate results to draw the tables in this replication package. To get the raw data, you should uncompress the [app_results.7z](app_results.7z) archive file (high compress ratio!). To draw the table of API calls in apps, simply run the `general_stat_for_body()` function in `call_api_info.py` script. Sample run:

```bash
$ python ./call_api_info.py 
------------------------ Table for body ---------------------------
F-Droid & 4,046 & 24,973 & 4,046 & 128,233 & 3,332 & 487 & 1,601 \\
Google Play & 12,968 & 28,200 & 12,968 & 712,932 & 12,719 & 1,556 & 11,609 \\
Malware & 745 & 11,854 & 745 & 12,129 & 629 & 230 & 360 \\
-----------------------------------------------------------------
```

To dump detailed tables, run the `general_stat_for_appendix()` function, it has a boolean parameter `contain_obfuscate`, means whether to output table that includes obfuscated APIs.

Running with `contain_obfuscate=True`:

```bash
$ python ./call_api_info.py
---------------------Table for appendix: call_APIs (contain obfuscate=True)------------------------
fdroid & 4,046 & - & 0/13 & - & 1,537/189,074 & 1,738/26,689 & 0 & 3,291 & 0 & 6/959 & 27/241 & 0/4 & 3,926/267,089 & 15,825/40,613 & 0 & 21,682 & 0\\
gplay & 12,968 & - & 1/13 & - & 666/189,074 & 2,098/26,689 & 0 & 2,788 & 0 & 11/959 & 29/241 & 0/4 & 2,228/267,089 & 20,125/40,613 & 0 & 25,412 & 0\\
malware & 745 & - & 0/13 & - & 19/189,074 & 930/26,689 & 0 & 962 & 0 & 2/959 & 18/241 & 0/4 & 56/267,089 & 9,703/40,613 & 0 & 10,892 & 0\\
---------------------------------------------------------------------
---------------------Table for appendix: call_external_APIs (contain obfuscate=True)------------------------
fdroid & 3,332 & - & 0/13 & - & 0/189,074 & 0/26,689 & 23,156 & 23,156 & 22,586 & 0/959 & 0/241 & 0/4 & 0/267,089 & 0/40,613 & 105,077 & 105,077 & 102,881\\
gplay & 12,719 & - & 0/13 & - & 0/189,074 & 0/26,689 & 100,679 & 100,679 & 90,247 & 0/959 & 0/241 & 0/4 & 0/267,089 & 0/40,613 & 612,253 & 612,253 & 569,123\\
malware & 629 & - & 0/13 & - & 0/189,074 & 0/26,689 & 1,567 & 1,567 & 1,523 & 0/959 & 0/241 & 0/4 & 0/267,089 & 0/40,613 & 10,562 & 10,562 & 9,367\\
---------------------------------------------------------------------
---------------------Table for appendix: call_reflect_APIs (contain obfuscate=True)------------------------
fdroid & 1,601 & 0/61 & 0/195 & - & 474/420,630 & 12/60,658 & 0 & 487 & 0\\
gplay & 11,609 & 0/61 & 0/195 & - & 1,518/420,630 & 34/60,658 & 1 & 1,556 & 0\\
malware & 360 & 0/61 & 0/195 & - & 220/420,630 & 10/60,658 & 0 & 230 & 0\\
---------------------------------------------------------------------
```

Running with `contain_obfuscate=False`:

```bash
$ python .\call_api_info.py
---------------------Table for appendix: call_APIs (contain obfuscate=False)------------------------
fdroid & 4,046 & - & 0/13 & - & 1,537/189,074 & 1,738/26,689 & 0 & 3,291 & 0 & 6/959 & 27/241 & 0/4 & 3,926/267,089 & 15,825/40,613 & 0 & 21,682 & 0\\
gplay & 12,968 & - & 1/13 & - & 666/189,074 & 2,098/26,689 & 0 & 2,788 & 0 & 11/959 & 29/241 & 0/4 & 2,228/267,089 & 20,125/40,613 & 0 & 25,412 & 0\\
malware & 745 & - & 0/13 & - & 19/189,074 & 930/26,689 & 0 & 962 & 0 & 2/959 & 18/241 & 0/4 & 56/267,089 & 9,703/40,613 & 0 & 10,892 & 0\\
---------------------------------------------------------------------
---------------------Table for appendix: call_external_APIs (contain obfuscate=False)------------------------
fdroid & 3,332 & - & 0/13 & - & 0/189,074 & 0/26,689 & 4,449 & 4,449 & 4,209 & 0/959 & 0/241 & 0/4 & 0/267,089 & 0/40,613 & 10,006 & 10,006 & 9,215\\
gplay & 12,719 & - & 0/13 & - & 0/189,074 & 0/26,689 & 19,582 & 19,582 & 15,738 & 0/959 & 0/241 & 0/4 & 0/267,089 & 0/40,613 & 44,608 & 44,608 & 37,021\\
malware & 629 & - & 0/13 & - & 0/189,074 & 0/26,689 & 190 & 190 & 170 & 0/959 & 0/241 & 0/4 & 0/267,089 & 0/40,613 & 1,092 & 1,092 & 891\\
---------------------------------------------------------------------
---------------------Table for appendix: call_reflect_APIs (contain obfuscate=False)------------------------
fdroid & 1,601 & 0/61 & 0/195 & - & 474/420,630 & 12/60,658 & 0 & 487 & 0\\
gplay & 11,609 & 0/61 & 0/195 & - & 1,518/420,630 & 34/60,658 & 1 & 1,556 & 0\\
malware & 360 & 0/61 & 0/195 & - & 220/420,630 & 10/60,658 & 0 & 230 & 0\\
---------------------------------------------------------------------
```

The tables' data are exactly the same as the previous part. We make it more pretty for readability.

## Other Findings

They can be printed by the `indepth_findings.py` script.

### Finding 10

Run the function `find_extra_cutomized_apis()` to obtain the list of used non-aal APIs from apps.

```bash
$ python ./indepth_findings.py
('fdroid', 'field', '') total 23156 support/androidx 22586 non-aal 2
('fdroid', 'method', '') total 105077 support/androidx 102881 non-aal 1
('gplay', 'field', '') total 100679 support/androidx 90247 non-aal 8
('gplay', 'method', '') total 612253 support/androidx 569123 non-aal 70
('malware', 'field', '') total 1567 support/androidx 1523 non-aal 0
('malware', 'method', '') total 10562 support/androidx 9367 non-aal 0
```

The results will be printed into the [covered_non_aal](covered_non_aal) folder.

To see which apps use the non-AAL APIs, we run the `backtrack_nonaal_apis()` function. However, since we cannot upload the raw data, we can only present the output, as shown in the source in `indepth_findings.py`.

### Finding 11

Run the function `backtrack_nonsdk_interfaces()` to see which non-SDK interfaces are invoked in apps. Outputs are:

```bash
output of fdroid:
---
fdroid {'total': 487, 'public': 12, 'unsupport': 295, 'conditional': 164, 'block': 16}
======================================================================================================
output of gplay:
---
gplay {'total': 1556, 'public': 35, 'unsupport': 924, 'conditional': 535, 'block': 62}
======================================================================================================
output of malware:
---
malware {'total': 230, 'public': 11, 'unsupport': 138, 'conditional': 70, 'block': 11}
```

