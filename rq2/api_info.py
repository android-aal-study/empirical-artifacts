import re
import xml.etree.ElementTree as ET
from collections import namedtuple

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import matplotlib.patches as ptc
import numpy as np
import seaborn as sns
# from myvenn import venn     # we cannot redistribute it as it violates GPLv3
from venn import venn





def is_anonymous_or_lambda(c):
    # three condition: anonymous class, lambda expression at >= 30, lambda expression at < 30
    return re.search(r'\$\d+$', c) or re.search(r'\$\$ExternalSyntheticLambda\d+$', c) or re.search(r'-\$\$Lambda\$', c) or c.endswith('$$')

def is_anonymous_field(f, c):
    return '$' in f

def is_anonymous_method(m, c):
    return '$' in m




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





def drawVenn4(level=LAV):
    path = f'../rq1/android-{level}/'
    jar = Androidjar_ApiConverter(path+'android.jar.txt')
    xml = Apiversions_ApiConverter(path+'api-versions.xml')
    txt = Currenttxt_ApiConverter(path+'current.txt.txt')
    csv = Hiddenapi_ApiConverter(path+'hiddenapi-flags.csv')

    fig, axs = plt.subplots(3, 1, figsize=(4, 9), height_ratios=(9, 8, 8))
    plt.subplots_adjust(left=0, bottom=0.03, right=1, top=1, wspace=0, hspace=0.15)

    for i, attr in enumerate(('classes', 'fields', 'methods')):
        label_dict = dict()
        total = set()
        for aal in (jar, xml, txt, csv):
            label = aal.__getattribute__(attr)
            label_dict[aal.api_file] = set(label)
            total.update(label)

        ax = axs[i]
        # ax.add_patch(ptc.Rectangle((0,0), 100, 100, color="green"))
        if i == 0:
            venn(label_dict, legend_loc='upper center', fontsize=11, ax=ax)
            ax.set_ylim(.1, .9)
        else:
            venn(label_dict, legend_loc=None, fontsize=11, ax=ax)
            ax.set_ylim(.1, .8)

        ax.set_xlim(0.03, 0.96)
        fmt = '(%s) %s (total=%d)'
        idx = chr(97 + i)
        api = re.sub(r'e?s$', '', attr)
        num = len(total)
        xlabel = fmt % (idx, api, num)
        ax.set_xlabel(xlabel, fontsize=14)

    # fig.tight_layout()
    fig_name = f'venn4-{level}.png'
    plt.savefig(fig_name)








if __name__ == '__main__':
    drawVenn4(28)
    drawVenn4(29)
    drawVenn4(30)
    drawVenn4(31)
    drawVenn4(32)
    drawVenn4(33)
