import json
import os
import pickle
import random
import sys

import pandas as pd

from api_info import Androidjar_ApiConverter, Apiversions_ApiConverter, Currenttxt_ApiConverter, Hiddenapi_ApiConverter, sep



LEVEL = int(sys.argv[1])



def get_or_load(aal, level=LEVEL):
    pickle_path = f'pickles/{aal}-{level}.pickle'
    if os.path.isfile(pickle_path):
        return pickle.load(open(pickle_path, 'rb'))
    else:
        _path = f'../rq1/android-{level}'
        if aal == 'jar':
            ac = Androidjar_ApiConverter(_path+'/android.jar.txt')
        elif aal == 'xml':
            ac = Apiversions_ApiConverter(_path+'/api-versions.xml')
        elif aal == 'txt':
            ac = Currenttxt_ApiConverter(_path+'/current.txt.txt')
        elif aal == 'csv':
            ac = Hiddenapi_ApiConverter(_path+'/hiddenapi-flags.csv')
        pickle.dump(ac, open(pickle_path, 'wb'))
        return ac



jar = get_or_load('jar')
xml = get_or_load('xml')
txt = get_or_load('txt')
csv = get_or_load('csv')


# finding 3
def analyze_class_intersection4():
    classes = set(jar.classes)
    classes.intersection_update(xml.classes)
    classes.intersection_update(txt.classes)
    classes.intersection_update(csv.classes)
    results = {
        'android.*': 0,
        'org.apache.http.*': 0,
        'javax.microedition.khronos.*': 0,
        'others': 0,
    }
    for c in sorted(classes):
        if c.startswith('android.'):
            results['android.*'] += 1
        elif c.startswith('org.apache.http.'):
            results['org.apache.http.*'] += 1
        elif c.startswith('javax.microedition.khronos.'):
            results['javax.microedition.khronos.*'] += 1
        else:
            results['others'] += 1
    print(results, 'total:', len(classes))

    fields = set(jar.fields)
    fields.intersection_update(xml.fields)
    fields.intersection_update(txt.fields)
    fields.intersection_update(csv.fields)
    if LEVEL == 33:
        assert len(fields) == 20331
    for f in sorted(fields):
        if f[0] not in classes:
            print('not in common:', f)
            break
    else:
        print('all shared fields from shared classes')

    methods = set(jar.methods)
    methods.intersection_update(xml.methods)
    methods.intersection_update(txt.methods)
    methods.intersection_update(csv.methods)
    if LEVEL == 33:
        assert len(methods) == 25815
    for m in sorted(methods):
        if m[0] not in classes:
            print('not in common:', m)
            break
    else:
        print('all shared methods from shared classes')



# finding 4
def analyze_csv_exclusive():
    classes = set(csv.classes)
    classes.difference_update(jar.classes)
    classes.difference_update(xml.classes)
    classes.difference_update(txt.classes)
    if LEVEL == 33:
        assert len(classes) == 23694

    # population = sorted(classes)
    # sample = random.sample(population, 379)
    # df = pd.DataFrame(sorted(sample), columns=['class'])
    # df.to_excel('sample_379.xlsx', index=False)
    # return

    fields = set(csv.fields)
    fields.difference_update(jar.fields)
    fields.difference_update(xml.fields)
    fields.difference_update(txt.fields)
    if LEVEL == 33:
        assert len(fields) == 166148
    exclusive_class_fields = 0
    for f in sorted(fields):
        if f.class_name in classes:
            # print(f)
            exclusive_class_fields += 1
    ratio = exclusive_class_fields / len(fields)
    print(f'{exclusive_class_fields} ({ratio}) fields from exclusive classes')


    methods = set(csv.methods)
    methods.difference_update(jar.methods)
    methods.difference_update(xml.methods)
    methods.difference_update(txt.methods)
    if LEVEL == 33:
        assert len(methods) == 230117
    exclusive_class_methods = 0
    for m in sorted(methods):
        if m.class_name in classes:
            # print(m)
            exclusive_class_methods += 1
    ratio = exclusive_class_methods / len(methods)
    print(f'{exclusive_class_methods} ({ratio}) methods from non-exclusive classes')



def analyze_csv_sampling():
    df = pd.read_excel('sample_379-labels.xlsx', keep_default_na=False)
    assert df.shape[0] == 379

    results = {
        'hide': [],                 # labeled with @hide
        'remove': [],               # labeled with @removed
        'access': [],               # access level of private, protected, default
        'internal': [],             # internal Android module

        'aidl': [],                 # generated from .aidl file
        'proto': [],                # generated from .proto file
        'hpp': [],                  # generated from .h file in CPP class
        'sysprop': [],              # generated from .sysprop file

        'repackaged-jdk': [],       # repackaged from JDK libraries
        'repackaged-other': [],     # repackaged from external libraries
    }
    for row in [tuple(r[1]) for r in df.iterrows()]:
        if row[1] == 'aidl':
            results['aidl'].append(row[0])
        elif row[1] == 'proto':
            results['proto'].append(row[0])
        elif row[1] == 'hpp':
            results['hpp'].append(row[0])
        elif row[1] == 'sysprop':
            results['sysprop'].append(row[0])

        elif row[5] in {'external-inline', 'external'}:
            if row[0].startswith('java') or row[0].startswith('sun'):
                results['repackaged-jdk'].append(row[0])
            else:
                results['repackaged-other'].append(row[0])
        elif row[5] == 'internal':
            results['internal'].append(row[0])

        elif row[3] in {'hide', 'package-level hide', 'hide/deprecated'}:
            results['hide'].append(row[0])
        elif row[4] in {'private', 'protected', 'default'}:
            results['access'].append(row[0])
        elif row[3] in {'removed', 'removed/deprecated'}:
            results['remove'].append(row[0])

        else:
            print(row)
            break
    print({k: len(v) for k, v in results.items()})
    with open('sample_379-labels-final.json', 'w') as w:
        json.dump(results, w, indent=2)




# finding 5
def analyze_xml_exclusive():
    classes = set(xml.classes)
    classes.difference_update(jar.classes)
    classes.difference_update(txt.classes)
    classes.difference_update(csv.classes)
    if LEVEL == 33:
        assert len(classes) == 62

    class_result = { 'test': 0, }
    for c in sorted(classes):
        if c.startswith('android.test.') or c.startswith('junit.'):
            class_result['test'] += 1
        else:
            print(c)
    print(class_result)
    sep()

    fields = set(xml.fields)
    fields.difference_update(jar.fields)
    fields.difference_update(txt.fields)
    fields.difference_update(csv.fields)
    if LEVEL == 33:
        assert len(fields) == 20
    exclusive_class_fields = 0
    for f in sorted(fields):
        if f.class_name in classes:
            exclusive_class_fields += 1
        else:
            print(f)
    else:
        print(f'{exclusive_class_fields} fields from exclusive classes')
    sep()

    methods = set(xml.methods)
    methods.difference_update(jar.methods)
    methods.difference_update(txt.methods)
    methods.difference_update(csv.methods)
    if LEVEL == 33:
        assert len(methods) == 374
    exclusive_class_methods = 0
    for m in sorted(methods):
        if m.class_name in classes:
            exclusive_class_methods += 1
        else:
            print(m)
    else:
        print(f'{exclusive_class_methods} methods from non-exclusive classes')


def analyze_jar_class_method_exclusive():
    classes = set(jar.classes)
    classes.difference_update(xml.classes)
    classes.difference_update(txt.classes)
    classes.difference_update(csv.classes)
    if LEVEL == 33:
        assert len(classes) == 4
    print(classes)
    sep()

    method = set(jar.methods)
    method.difference_update(xml.methods)
    method.difference_update(txt.methods)
    method.difference_update(csv.methods)
    if LEVEL == 33:
        assert len(method) == 936
    default_init_count = 0
    init_count = 0
    remain = 0
    for m in sorted(method):
        if m.name == '<init>' and m.parameter_types == ():
            default_init_count += 1
            # print(m)
        elif m.name == '<init>':
            init_count += 1
            # print(m)
        else:
            remain += 1
            print(m)
    print(f'{remain} exclusive methods')
    sep()
    print(f"default <init> count in JAR: {default_init_count}")
    print(f"other <init> count in JAR: {init_count}")
    print('(all <init> are default constructors)')




# empty classes, thus not in CSV
def analyze_non_csv_classes():
    classes = set(jar.classes)
    classes.intersection_update(xml.classes)
    classes.difference_update(csv.classes)
    if LEVEL == 33:
        assert len(classes) == 40+20
    print("JAR+XML:")
    for c in sorted(classes):
        if c not in txt.classes:
            print(c)
    sep()
    print("JAR+XML+TXT")
    for c in sorted(classes):
        if c in txt.classes:
            print(c)


# inlined fields
def analyze_non_csv_fields():
    fields = set(jar.fields)
    fields.intersection_update(xml.fields)
    fields.difference_update(csv.fields)
    if LEVEL == 33:
        assert len(fields) == 321+338
    print("JAR+XML:")
    for f in sorted(fields):
        if f not in txt.fields:
            print(f)
    sep()
    print("JAR+XML+TXT")
    for f in sorted(fields):
        if f in txt.fields:
            print(f)

# inlined methods
def analyze_non_csv_methods():
    methods = set(jar.methods)
    methods.intersection_update(xml.methods)
    methods.intersection_update(txt.methods)
    methods.difference_update(csv.methods)
    if LEVEL == 33:
        assert len(methods) == 12
    print("JAR+XML+TXT")
    for m in sorted(methods):
        print(m)








if __name__ == '__main__':
    analyze_class_intersection4()
    # analyze_csv_exclusive()
    # analyze_csv_sampling()
    # analyze_xml_exclusive()
    # analyze_jar_class_method_exclusive()
    # analyze_non_csv_classes()
    # analyze_non_csv_fields()
    # analyze_non_csv_methods()
