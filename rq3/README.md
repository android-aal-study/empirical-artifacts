# RQ3

## About AAL-Reflector

AAL-Reflector is an Android app that display which APIs can be reflected on an Android device. It enables Java reflection on Android with the [FreeReflection](https://github.com/tiann/FreeReflection) library. We already provide a built [app](app-debug.apk) in this folder.

The app reflects the corresponding AALs in the device's system Android version, below is a screenshot running on an Android 13 (API-level 33) virtual device, which is a stock Android system.

![aal-reflector](AAL-Reflector/screenshot.png)

It will also save the reflected APIs into the app's local directory. To reflect non-AAL APIs, use the "ALL" tab, and follow the below instruction.


## About Device Files

We have 9 devices, correspond to 9 folders:

1. android-30_redmi_note10
2. android-30_samsung_a50s
3. android-30_virtual_stock
4. android-31_redmi_10X
5. android-31_vivo_Y33s
6. android-31_virtual_stock
7. android-33_redmi_note12
8. android-33_samsung_a53
9. android-33_virtual_stock

The files in each folder are:

+ `all_classes.txt`: All classes merged from the four AALs, under the device's `Build.VERSION.SDK_INT`
+ `all_fields.txt`: All fields reflected by invoking the `Class.getDeclaredFields()` methods on the classes in `all_classes.txt`
+ `all_methods.txt`: All methods reflected by invoking the `Class.getDeclaredMethods()` and `Class.getDeclaredConstructors()` methods on the classes in `all_classes.txt`
+ `CSV_missing_classes.txt`: the classes in the CSV list but cannot be reflected by `Class.forName(String)`
+ `CSV_missing_fields.txt`: the fields in the CSV list but cannot be reflected by `class.getDeclaredField(String)`
+ `CSV_missing_methods.txt`: the methods in the CSV list but cannot be reflected by `class.getDeclaredMethod(String,Class...)` or `class.getDeclaredConstructor(String,Class...)`
+ and so on ...

The non-AAL APIs should be computed by the `analyze.py` Python script, based on the `all_fields.txt` and `all_methods.txt` files, as shown below.

## Obtaining Empirical Finding Data

The API files for each devices were downloaded after we reflect all APIs on the devices, from the app's local data folder on the devices. The basic information can be obtained by directly running the `drawTable7()` function in `analyze.py`.

Example run:

```bash
$ python analyze.py
Redmi Note 10 & MIUI 12.0.3 & Android 11 (30) & 655 & 673 & 655 & 106 & 559/1,116 & 767 & 375 & 31 & 279 & 1,007/1,419 \\
Samsung Galaxy A50s & One UI 3.1 & Android 11 (30) & 655 & 673 & 655 & 108 & 7,622/12,657 & 767 & 375 & 31 & 311 & 8,519/10,525 \\
virtual & stock Android & Android 11 (30) & 655 & 673 & 655 & 85 & 81/195 & 767 & 375 & 31 & 209 & 189/281 \\
\midrule
Redmi 10X & MIUI 13.0.1 & Android 12 (31) & 655 & 675 & 334 & 17 & 470/878 & 903 & 386 & 13 & 59 & 1,003/1,227 \\
vivo Y33s & OriginOS ocean & Android 12 (31) & 655 & 675 & 334 & 58 & 1,283/2,951 & 903 & 386 & 13 & 72 & 3,392/3,931 \\
virtual & stock Android & Android 12 (31) & 655 & 675 & 334 & 4 & 7/10 & 903 & 386 & 13 & 3 & 9/14 \\
\midrule
Redmi Note 12 & MIUI 14.0.1 & Android 13 (33) & 659 & 679 & 338 & 57 & 634/1,378 & 961 & 392 & 19 & 1,776 & 2,869/3,184 \\
Samsung Galaxy A53 & One UI 5.1 & Android 13 (33) & 659 & 679 & 338 & 255 & 7,613/12,458 & 961 & 392 & 19 & 813 & 8,756/11,009 \\
virtual & stock Android & Android 13 (33) & 659 & 679 & 338 & 235 & 406/572 & 961 & 392 & 19 & 784 & 537/669 \\
```

## Other Findings

Run the `analyzeNonCsvOverlap` function to obtain empirical data about non-overlap non-existing APIs in CSV on customized devices.

```bash
$ python .\analyze.py
30 85 211
31 5 41
33 7 41
```

Run the `analyzeNonAalPublic` function to get a list of public non-AAL APIs. We have already run and save these files, stored in the `nonAALs/` folder. Each devices correspond to four files:

+ `*-field-public.txt`: non-AAL public fields on the device
+ `*-field.txt`: all non-AAL fields on the device
+ `*-method-public.txt`: non-AAL public methods (including constructors) on the device
+ `*-method.txt`: all non-AAL methods (including constructors) on the device
