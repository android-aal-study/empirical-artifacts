import os
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import namedtuple, defaultdict
from pprint import pprint

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import matplotlib.patches as ptc
import numpy as np
import seaborn as sns

from class_utils import is_anonymous_field, is_anonymous_method, is_anonymous_or_lambda



plt.rcParams["font.family"] = "Times New Roman"


FieldSub = namedtuple('FieldSub', ['class_name', 'name'])
MethodSub = namedtuple('MethodSub', ['class_name', 'name', 'parameter_types'])




class ApiConverter:

    @staticmethod
    def jni_to_java_single(jni_type):
        if jni_type.startswith('Z'):
            return 'boolean', jni_type[1:]
        elif jni_type.startswith('B'):
            return 'byte', jni_type[1:]
        elif jni_type.startswith('C'):
            return 'char', jni_type[1:]
        elif jni_type.startswith('S'):
            return 'short', jni_type[1:]
        elif jni_type.startswith('I'):
            return 'int', jni_type[1:]
        elif jni_type.startswith('J'):
            return 'long', jni_type[1:]
        elif jni_type.startswith('F'):
            return 'float', jni_type[1:]
        elif jni_type.startswith('D'):
            return 'double', jni_type[1:]
        elif jni_type.startswith('V'):
            return 'void', jni_type[1:]
        elif jni_type.startswith('L'):
            end = jni_type.index(';')
            type_str = jni_type[1:end].replace('/', '.')
            return type_str, jni_type[end+1:]
        elif jni_type.startswith('['):
            remain = jni_type[1:]
            t, jni_type = ApiConverter.jni_to_java_single(remain)
            return f'{t}[]', jni_type

    @staticmethod
    def jni_to_java(type_str):
        types = []
        while type_str:
            t, type_str = ApiConverter.jni_to_java_single(type_str)
            types.append(t)
        return tuple(types)

    # example: ApiConverter("android-33/hiddenapi-flags.csv")
    def __init__(self, file_path):
        self.api_level = 0
        self.api_file = ''
        self.classes = []
        self.fields = []
        self.methods = []

    def report(self):
        print(f'{self.api_file}({self.api_level}): #class={len(self.classes)}, #field={len(self.fields)}, #method={len(self.methods)}')

    def to_sublist(self, store_path):

        def inclusion_exclusion(c): # generated class already dropped at loading
            return True
            # return is_android_package(c) and not is_external(c)

        class_lines = []
        for clazz in self.classes:
            if inclusion_exclusion(clazz):
                class_line = clazz + '\n'
                class_lines.append(class_line)
        class_lines.sort()
        class_filename = f'/{self.api_file}-class.txt'
        with open(store_path+class_filename, 'w') as w:
            for class_line in class_lines:
                w.write(class_line)

        field_lines = []
        for field in self.fields:
            if inclusion_exclusion(field.class_name):
                field_line = f'{field.class_name}->{field.name}\n'
                field_lines.append(field_line)
        field_lines.sort()
        field_filename = f'/{self.api_file}-field.txt'
        with open(store_path+field_filename, 'w') as w:
            for field_line in field_lines:
                w.write(field_line)

        method_lines = []
        for method in self.methods:
            if inclusion_exclusion(method.class_name):
                parameters = ','.join(method.parameter_types)
                method_line = f'{method.class_name}->{method.name}({parameters})\n'
                method_lines.append(method_line)
        method_lines.sort()
        method_filename = f'/{self.api_file}-method.txt'
        with open(store_path+method_filename, 'w') as w:
            for method_line in method_lines:
                w.write(method_line)

    def get_apis(self):
        return self.classes, self.fields, self.methods


class Hiddenapi_ApiConverter(ApiConverter):

    report_category = 'Hidden-APIs'
    field_pattern = r'^(.+?)->(.+?):(.+?)$'
    method_pattern = r'^(.+?)->(.+?)\((.*?)\)(.+?)$'

    def __init__(self, file_path):
        super().__init__(file_path)
        assert(file_path.endswith('hiddenapi-flags.csv'))
        self.api_level = int(re.search(r'android-(\d+)', file_path)[1])
        self.api_file = 'CSV'
        classes = set()
        with open(file_path) as r:
            for line in r:
                api = line.split(',')[0]
                fm = re.match(self.field_pattern, api)
                mm = re.match(self.method_pattern, api)
                if fm:
                    cn, name, t = fm.groups()
                    class_name = self.jni_to_java(cn)[0]
                    if is_anonymous_or_lambda(class_name):
                        continue
                    if is_anonymous_field(name, class_name):
                        continue
                    assert name.isidentifier(), api

                    # type = self.jni_to_java(t)[0]
                    field = FieldSub(class_name, name)
                    # print(field)
                    self.fields.append(field)
                    classes.add(class_name)
                elif mm:
                    cn, name, p, t = mm.groups()
                    class_name = self.jni_to_java(cn)[0]
                    if is_anonymous_or_lambda(class_name):
                        continue
                    if is_anonymous_method(name, class_name) or name=='<clinit>':
                        continue
                    assert name=='<init>' or name.isidentifier(), api

                    parameter_types = self.jni_to_java(p)
                    # return_type = self.jni_to_java(t)[0]
                    method = MethodSub(class_name, name, parameter_types)
                    # print(method)
                    self.methods.append(method)
                    classes.add(class_name)
                else:
                    print('error: ' + api)
                    exit()
        self.classes.extend(classes)


class Apiversions_ApiConverter(ApiConverter):

    method_pattern = r'^(.+?)\((.*?)\)(.+?)$'

    def __init__(self, file_path):
        super().__init__(file_path)
        assert(file_path.endswith('api-versions.xml'))
        self.api_level = int(re.search(r'android-(\d+)', file_path)[1])
        self.api_file = 'XML'
        classes = set()
        tree = ET.parse(file_path)
        for clazz in tree.findall('./class'):
            if clazz.get('removed') is not None:
                continue
            class_name = clazz.get('name').replace('/', '.')
            classes.add(class_name)
            for field in clazz.findall('./field'):
                if field.get('removed') is not None:
                    continue
                name = field.get('name')
                field = FieldSub(class_name, name)
                # print(field)
                self.fields.append(field)
            for method in clazz.findall('./method'):
                if method.get('removed') is not None:
                    continue
                mm = re.match(self.method_pattern, method.get('name'))
                name, p, t = mm.groups()
                parameter_types = self.jni_to_java(p)
                # return_type = self.jni_to_java(t)[0]
                method = MethodSub(class_name, name, parameter_types)
                # print(method)
                self.methods.append(method)
        self.classes.extend(classes)


class Androidjar_ApiConverter(ApiConverter):

    field_pattern = r'^<(.*?): (.*?) ([^()]*?)>$'
    method_pattern = r'^<(.*?): (.*?) (.*?)\((.*?)\)>$'

    def __init__(self, file_path):
        super().__init__(file_path)
        assert(file_path.endswith('android.jar.txt'))
        self.api_level = int(re.search(r'android-(\d+)', file_path)[1])
        self.api_file = 'JAR'
        classes = set()
        with open(file_path) as r:
            for api in r:
                fm = re.match(self.field_pattern, api)
                mm = re.match(self.method_pattern, api)
                if fm:
                    class_name = fm.group(1)
                    name = fm.group(3)

                    if name in {'$VALUES', 'this$0'}:
                        continue

                    field = FieldSub(class_name, name)
                    self.fields.append(field)
                elif mm:
                    class_name = mm.group(1)
                    name = mm.group(3)

                    if name in {'<clinit>'}:
                        continue

                    parameters = mm.group(4)
                    if parameters == '':
                        parameter_types = tuple()
                    else:
                        parameter_types = tuple(p for p in parameters.split(','))
                    method = MethodSub(class_name, name, parameter_types)
                    # print('method '+ class_name + ' ' + name + ' ' + parameter_types)
                    self.methods.append(method)
                else:
                    class_name = api.strip()
                    if re.search(r'\$\d+$', class_name):
                        continue
                    classes.add(class_name)
        self.classes.extend(classes)


class Currenttxt_ApiConverter(ApiConverter):
    field_pattern = r'^<(.*?): (.*?) ([^()]*?)>$'
    method_pattern = r'^<(.*?): (.*?) (.*?)\((.*?)\)>$'
    def __init__(self, file_path):
        super().__init__(file_path)
        assert(file_path.endswith('current.txt.txt'))
        self.api_level = int(re.search(r'android-(\d+)', file_path)[1])
        self.api_file = 'TXT'
        with open(file_path, mode='r', encoding='utf-8-sig') as r:
            classes = set()
            for api in map(str.strip, r):
                fm = re.match(self.field_pattern, api)
                mm = re.match(self.method_pattern, api)
                if fm:
                    class_name = fm.group(1)
                    name = fm.group(3)
                    field = FieldSub(class_name, name)
                    self.fields.append(field)
                    classes.add(class_name)
                elif mm:
                    class_name = mm.group(1)
                    name = mm.group(3)
                    parameters = mm.group(4)
                    if parameters == '':
                        parameter_types = tuple()
                    else:
                        parameter_types = tuple(p for p in parameters.split(','))
                    method = MethodSub(class_name, name, parameter_types)
                    self.methods.append(method)
                    classes.add(class_name)
                else:
                    classes.add(api)
            self.classes.extend(classes)




def sep():
    print('-' * 80)
def bsep():
    print('=' * 80)



TARGETS = [
    ('pie-release', 28),
    ('android10-release', 29),
    ('android11-release', 30),
    ('android12-release', 31),
    ('android12L-release', 32),
    ('android13-release', 33),
]

LAV = TARGETS[-1][1] # latest Android version

def convertToSubLists():
    for _, level in TARGETS:
        path = f'android-{level}/'
        dest_path = f'../AAL-Reflector/app/src/main/assets/sublist/android-{level}/'
        os.makedirs(dest_path, exist_ok=True)
        Androidjar_ApiConverter(path+'android.jar.txt').to_sublist(dest_path)
        Apiversions_ApiConverter(path+'api-versions.xml').to_sublist(dest_path)
        Currenttxt_ApiConverter(path+'current.txt.txt').to_sublist(dest_path)
        Hiddenapi_ApiConverter(path+'hiddenapi-flags.csv').to_sublist(dest_path)
    print('done')


def mergeFieldMethodLists():
    fields, methods = set(), set()
    for _, level in TARGETS:
        jar = Androidjar_ApiConverter(f'android-{level}/android.jar.txt')
        xml = Apiversions_ApiConverter(f'android-{level}/api-versions.xml')
        txt = Currenttxt_ApiConverter(f'android-{level}/current.txt.txt')
        csv = Hiddenapi_ApiConverter(f'android-{level}/hiddenapi-flags.csv')
        for aal in (jar, xml, txt, csv):
            _, f, m = aal.get_apis()
            fields.update(f)
            methods.update(m)
    path = '../APK-Analyzer/src/main/resources/'
    with open(path+'all-fields.txt', 'w') as w:
        for field in fields:
            field_line = f'{field.class_name}->{field.name}\n'
            w.write(field_line)
    with open(path+'all-methods.txt', 'w') as w:
        for method in methods:
            parameters = ','.join(method.parameter_types)
            method_line = f'{method.class_name}->{method.name}({parameters})\n'
            w.write(method_line)
    print('done')


def displayTable4():
    cache = dict()
    for b, level in TARGETS:
        cache[level] = dict()
        path = f'android-{level}/'
        jar = Androidjar_ApiConverter(path+'android.jar.txt')
        xml = Apiversions_ApiConverter(path+'api-versions.xml')
        txt = Currenttxt_ApiConverter(path+'current.txt.txt')
        csv = Hiddenapi_ApiConverter(path+'hiddenapi-flags.csv')
        row = f'\\texttt{{{b}}} & {level}'
        for attr in ('classes', 'fields', 'methods'):
            cache[level][attr] = dict()
            for aal in (jar, xml, txt, csv):
                num = len(set(aal.__getattribute__(attr)))
                cache[level][attr][aal.api_file] = num
                row += f' & {num:,}'
                if level-1 in cache and num < cache[level-1][attr][aal.api_file]:
                    row += '\\downredarrow'
                if level-1 in cache and num > cache[level-1][attr][aal.api_file]*2:
                    row += '\\upgreenarrow'
        row += r' \\'
        print(row)



def drawPairwiseTxtAddRemovedTable():
    path = 'android-{}/current.txt.txt'
    cur = Currenttxt_ApiConverter(path.format(28))
    for v in range(29, 34):
        prev, cur = cur, Currenttxt_ApiConverter(path.format(v))

        class30 = set(prev.classes)
        class31 = set(cur.classes)
        a_class = class31.difference(class30)
        r_class = class30.difference(class31)

        field30 = set(prev.fields)
        field31 = set(cur.fields)
        a_field = field31.difference(field30)
        r_field = field30.difference(field31)

        method30 = set(prev.methods)
        method31 = set(cur.methods)
        a_method = method31.difference(method30)
        r_method = method30.difference(method31)

        row = '~~~~{}~\\ding{{213}}~{} &'.format(prev.api_level, cur.api_level)
        row += f' {len(a_class):,} & {len(r_class):,} &'
        row += f' {len(a_field):,} & {len(r_field):,} &'
        row += f' {len(a_method):,} & {len(r_method):,} \\\\'
        print(row)


def analyzeTxt31Decrease():
    path = 'android-{}/current.txt.txt'
    txt30 = Currenttxt_ApiConverter(path.format(30))
    txt31 = Currenttxt_ApiConverter(path.format(31))

    class30 = set(txt30.classes)
    class31 = set(txt31.classes)
    # a_class = class31.difference(class30)
    r_class = class30.difference(class31)

    field30 = set(txt30.fields)
    field31 = set(txt31.fields)
    # a_field = field31.difference(field30)
    r_field = field30.difference(field31)

    method30 = set(txt30.methods)
    method31 = set(txt31.methods)
    # a_method = method31.difference(method30)
    r_method = method30.difference(method31)

    # print('removed_field not in removed_class')
    from_rc = 0
    for rf in sorted(r_field):
        if rf.class_name not in r_class:
            pass
            # print(rf)
        else:
            from_rc += 1
    print(f'{from_rc}/{len(r_field)} fields from removed classes')

    # print('removed_method not in removed_class')
    from_rc = 0
    for rm in sorted(r_method):
        if rm.class_name not in r_class:
            pass
            # print(rm)
        else:
            from_rc += 1
    print(f'{from_rc}/{len(r_method)} methods from removed_classes')

    sep()

    with open(f'removed_classes_{txt31.api_level}.txt', 'w') as w:
        for rc in sorted(r_class):
            w.write(rc)
            w.write('\n')
    print('write to removed_classes_31.txt file')

    sep()


def drawRemovedClassesAggregate():
    path = 'android-{}/current.txt.txt'
    txt30 = Currenttxt_ApiConverter(path.format(30))
    txt31 = Currenttxt_ApiConverter(path.format(31))
    r_class = set(txt30.classes).difference(txt31.classes)

    aggregate = defaultdict(int)    
    order = ['android', 'dalvik', 'java', 'javax', 'org']
    for rc in r_class:
        seg = rc.split('.')[0]
        aggregate[seg] += 1
    print(aggregate)


    # colors = sns.color_palette("hls", len(order))
    colors = ['#FED9B7', '#F07167', '#FDFCDC', '#00AFB9', '#0081A7']

    fig, ax = plt.subplots(figsize=(5, 1))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    start = 0
    for colname, color in zip(order, colors):
        width = aggregate[colname]
        label = colname + '.*'
        rects = ax.barh(0, width, left=start, height=1.6, label=label, color=color)

        r, g, b = (int(color[i+1:i+2+1], 16) for i in (0, 2, 4))
        text_color = 'white' if r * g * b < 0.5 else '#666'
        ax.bar_label(rects, label_type='center', color=text_color)

        start += width
    
    font = fm.FontProperties(family='Consolas', style='normal', size=9.5)

    ax.legend(ncols=len(order), bbox_to_anchor=(0.5, 1), loc='lower center', columnspacing=0.6, handletextpad=0.2, prop=font)
    ax.set_xlim(0, sum(aggregate.values()))
    ax.set_ylim(-1, 1)

    fig.tight_layout()

    fig_name = 'removed-class-31.pdf'
    plt.savefig(fig_name)
    # plt.show()
    subprocess.run(['pdfcrop', fig_name, fig_name])



def analyzeCsvSynthesizedApis():
    micro_numerator_j, micro_denominator_j = 0, 0
    macro_sum_j = 0

    for _, level in TARGETS:
        file_path = f'android-{level}/hiddenapi-flags.csv'
        with open(file_path) as r:
            total = 0
            synthesized_java = 0
            valid_field, valid_method = set(), set()
            for line in r:
                api = line.split(',')[0]
                total += 1

                fm = re.match(Hiddenapi_ApiConverter.field_pattern, api)
                mm = re.match(Hiddenapi_ApiConverter.method_pattern, api)

                if fm:
                    cn, name, t = fm.groups()
                    class_name = Hiddenapi_ApiConverter.jni_to_java(cn)[0]
                    if is_anonymous_or_lambda(class_name):
                        synthesized_java += 1
                    elif is_anonymous_field(name, class_name):
                        synthesized_java += 1
                    else:
                        valid_field.add((class_name, name))
                elif mm:
                    cn, name, p, t = mm.groups()
                    class_name = Hiddenapi_ApiConverter.jni_to_java(cn)[0]
                    if is_anonymous_or_lambda(class_name):
                        synthesized_java += 1
                    elif is_anonymous_method(name, class_name) or name=='<clinit>':
                        synthesized_java += 1
                    else:
                        pt = Hiddenapi_ApiConverter.jni_to_java(p)
                        valid_method.add((class_name, name, pt))

            micro_numerator_j += synthesized_java
            micro_denominator_j += total
            macro_sum_j += synthesized_java / total

        print(f'in android-{level}, {total} in total, {synthesized_java}({synthesized_java/total}) synthesized from java, {len(valid_field)} valid fields, {len(valid_method)} valid methods')

    print(f'---')
    print(f'for java:')
    print(f'micro average: {micro_numerator_j/micro_denominator_j}, macro average: {macro_sum_j/len(TARGETS)}')










if __name__ == '__main__':
    # # For Data Collection and Preprocessing
    # analyzeCsvSynthesizedApis()

    # # For RQ2 and RQ3
    # convertToSubLists()
    # mergeFieldMethodLists()

    # # For Finding 1
    displayTable4()
    # drawPairwiseTxtAddRemovedTable()
    # analyzeTxt31Decrease()

    # # For Finding 2
    # drawRemovedClassesAggregate()
