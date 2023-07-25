import os
import pickle
import re
from pathlib import Path



from api_info import Androidjar_ApiConverter, Apiversions_ApiConverter, Currenttxt_ApiConverter, Hiddenapi_ApiConverter, FieldSub, MethodSub







global_cache = dict()

def get_or_load(aal, level):
    pickle_path = f'pickles/{aal}-{level}.pickle'
    if pickle_path in global_cache:
        return global_cache[pickle_path]
    elif os.path.isfile(pickle_path):
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
        global_cache[pickle_path] = ac
        return ac





def _to_field_sub(line):
    field = line.split()[-1]
    split = field.rfind('.')
    class_name, name = field[:split], field[split+1:]

    if line.startswith('public'):
        access = 'public'
    elif line.startswith('protected'):
        access = 'protected'
    elif line.startswith('private'):
        access = 'private'
    else:
        access = 'default'

    return FieldSub(class_name, name), access

def _to_method_sub(line):
    m = re.search(r'([^ ]+)\((.*?)\)', line)
    subsig, params = m.groups()
    split = subsig.rfind('.')
    class_name, name = subsig[:split], subsig[split+1:]

    if params:
        parameter_types = tuple(params.split(','))
    else:
        parameter_types = ()

    if line.startswith('public'):
        access = 'public'
    elif line.startswith('protected'):
        access = 'protected'
    elif line.startswith('private'):
        access = 'private'
    else:
        access = 'default'

    return MethodSub(class_name, name, parameter_types), access



def compute_all_nonaal(p, api):
    apis = set()
    level = int(p.name[8:10])
    jar = get_or_load('jar', level)
    xml = get_or_load('xml', level)
    txt = get_or_load('txt', level)
    csv = get_or_load('csv', level)

    if api == 'fields':
        with open(p/'all_fields.txt') as r:
            for line in r:
                field = _to_field_sub(line)
                if '$' not in field.name:
                    apis.add(field)
        for aal in (jar, xml, txt, csv):
            apis.difference_update(aal.fields)
    if api == 'methods':
        with open(p/'all_methods.txt') as r:
            for line in r:
                method = _to_method_sub(line)
                if '$' not in method.name:
                    apis.add(method)
        for aal in (jar, xml, txt, csv):
            apis.difference_update(aal.methods)
    return apis



def compute_all_nonaal_access(p, api):
    level = int(p.name[8:10])
    jar = get_or_load('jar', level)
    xml = get_or_load('xml', level)
    txt = get_or_load('txt', level)
    csv = get_or_load('csv', level)

    apis, total = set(), set()
    if api == 'fields':
        for aal in (jar, xml, txt, csv):
            total.update(aal.fields)
        with open(p/'all_fields.txt') as r:
            for line in r:
                field = _to_field_sub(line)
                if ('$' not in field[0].name) and (field[0] not in total):
                    apis.add(field)
    if api == 'methods':
        for aal in (jar, xml, txt, csv):
            total.update(aal.methods)
        with open(p/'all_methods.txt') as r:
            for line in r:
                method = _to_method_sub(line)
                if ('$' not in method[0].name) and (method[0] not in total):
                    apis.add(method)
    return apis







data_list = [
    ('android-30_redmi_note10',     'Redmi Note 10',        'MIUI 12.0.3'),
    ('android-30_samsung_a50s',     'Samsung Galaxy A50s',  'One UI 3.1'),
    ('android-30_virtual_stock',    'virtual',              'stock Android'),
    (),
    ('android-31_redmi_10X',        'Redmi 10X',            'MIUI 13.0.1'),
    ('android-31_vivo_Y33s',        'vivo Y33s',            'OriginOS ocean'),
    ('android-31_virtual_stock',    'virtual',              'stock Android'),
    (),
    ('android-33_redmi_note12',     'Redmi Note 12',        'MIUI 14.0.1'),
    ('android-33_samsung_a53',      'Samsung Galaxy A53',   'One UI 5.1'),
    ('android-33_virtual_stock',    'virtual',              'stock Android'),
]

def _get_version(p):
    if p.startswith('android-28'):
        return 'Android 9 (28)'
    elif p.startswith('android-29'):
        return 'Android 10 (29)'
    elif p.startswith('android-30'):
        return 'Android 11 (30)'
    elif p.startswith('android-31'):
        return 'Android 12 (31)'
    # elif p.startswith('android-32'):
    #     return 'Android 12L (32)'
    elif p.startswith('android-33'):
        return 'Android 13 (33)'

def _count_lines(fn):
    with open(fn) as r:
        return sum(1 for _ in r)

def drawTable7():
    for item in data_list:
        if item:
            p, device, system = item
            line = f'{device} & {system} & {_get_version(p)}'
            path = Path(f'{p}')
            for api in ('fields', 'methods'):
                for aal in ('JAR', 'XML', 'TXT', 'CSV'):
                    fn = f'{aal}_missing_{api}.txt'
                    c = _count_lines(path/fn)
                    line += f' & {c:,}'
                nonaal_api = compute_all_nonaal_access(path, api)
                public_api = sum(1 for _, acc in nonaal_api if acc=='public')
                line += f' & {public_api:,}/{len(nonaal_api):,}'
            line += r' \\'
        else:
            line = '\\midrule'
        print(line)




def _get_lines(fn):
    with open(fn) as r:
        return set(l.strip() for l in r)

def analyzeNonCsvOverlap():
    items30 = (30, ('android-30_redmi_note10',
                    'android-30_samsung_a50s',
                    # 'android-30_virtual_stock'
                    ))
    items31 = (31, ('android-31_redmi_10X',
                    'android-31_vivo_Y33s',
                    # 'android-31_virtual_stock'
                    ))
    items33 = (33, ('android-33_redmi_note12',
                    'android-33_samsung_a53',
                    # 'android-33_virtual_stock'
                    ))
    for v, items in (items30, items31, items33):
        overlap_field, overlap_method = set(), set()
        for p in items:

            fpath = f'{p}/csv_missing_fields.txt'
            fc = _get_lines(fpath)
            if overlap_field:
                overlap_field.intersection_update(fc)
            else:
                overlap_field.update(fc)

            mpath = f'{p}/csv_missing_methods.txt'
            mc = _get_lines(mpath)
            if overlap_method:
                overlap_method.intersection_update(mc)
            else:
                overlap_method.update(mc)
        print(v, len(overlap_field), len(overlap_method))






def analyzeNonAalPublic():
    device = data_list[10][0]
    path = Path(device)

    all_field = open('nonAALs/'+device+'-field.txt', 'w')
    public_field = open('nonAALs/'+device+'-field-public.txt', 'w')
    # public missing fields
    pmf = compute_all_nonaal_access(path, 'fields')
    # publicf = sum(1 for _, access in pmf if access=='public')
    for api, access in sorted(pmf):
        all_field.write(str(api))
        all_field.write('\n')
        if access == 'public':
            public_field.write(str(api))
            public_field.write('\n')
    all_field.close()
    public_field.close()

    all_method = open('nonAALs/'+device+'-method.txt', 'w')
    public_method = open('nonAALs/'+device+'-method-public.txt', 'w')
    # public missing methods
    pmm = compute_all_nonaal_access(path, 'methods')
    # publicm = sum(1 for _, access in pmm if access=='public')
    for api, access in sorted(pmm):
        all_method.write(str(api))
        all_method.write('\n')
        if access == 'public':
            public_method.write(str(api))
            public_method.write('\n')
    all_method.close()
    public_method.close()






if __name__ == '__main__':
    drawTable7()
    # analyzeNonCsvOverlap()
    # analyzeNonAalPublic()
