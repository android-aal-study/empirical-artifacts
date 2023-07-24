import json

import pymysql
from urllib.parse import urlparse

from api_info import Androidjar_ApiConverter, Apiversions_ApiConverter, Currenttxt_ApiConverter, Hiddenapi_ApiConverter



def _java_to_jni(c):
    if c == 'boolean':
        return 'Z'
    elif c == 'byte':
        return 'B'
    elif c == 'char':
        return 'C'
    elif c == 'short':
        return 'S'
    elif c == 'int':
        return 'I'
    elif c == 'long':
        return 'J'
    elif c == 'float':
        return 'F'
    elif c == 'double':
        return 'D'
    elif c == 'void':
        return 'V'
    elif c.endswith('[]'):
        return '[' + _java_to_jni(c[:-2])
    else:
        return 'L' + c.replace('.', '/') + ';'

def _sub_to_jni(sub):
    if type(sub) == str:
        return _java_to_jni(sub)
    elif len(sub) == 2: # FieldSub
        cn, n = sub
        return f'{_java_to_jni(cn)}->{n}'
    elif len(sub) == 3: # MethodSub
        cn, n, pl = sub
        ps = ''.join(map(_java_to_jni, pl))
        return f'{_java_to_jni(cn)}->{n}({ps})'

def dumpRemovedApis(FROM=32, TO=33):

    def getAal(aal, level):
        path = f'android-{level}/'
        if aal == 'jar':
            return Androidjar_ApiConverter(path+'android.jar.txt')
        elif aal == 'xml':
            return Apiversions_ApiConverter(path+'api-versions.xml')
        elif aal == 'txt':
            return Currenttxt_ApiConverter(path+'current.txt.txt')
        elif aal == 'csv':
            return Hiddenapi_ApiConverter(path+'hiddenapi-flags.csv')

    for aal in ('jar', 'xml', 'txt', 'csv'):

        removed = {
            'classes': set(),
            'fields': set(),
            'methods': set(),
        }

        cur = getAal(aal, FROM)
        for v in range(FROM+1, TO+1):
            prev, cur = cur, getAal(aal, v)
            # print(f'In {v}, removed APIs from {aal.upper()}:') #, end='')

            for attr in ('classes', 'fields', 'methods'):
                api_prev = prev.__getattribute__(attr)
                api_cur = cur.__getattribute__(attr)
                api_removed = set(api_prev).difference(api_cur)
                # print(f' {attr}={len(api_removed)}', end=' ')
                removed[attr].update(api_removed)
            # print()

        with open(f'removed_apis/r_{aal}_{FROM}_{TO}.txt', 'w') as w:
            print(f'For {aal} AAL from {FROM} to {TO}')
            # print(f'For {aal} AAL, removed APIs: ') #, end='')
            for api, rapi in removed.items():
                # print(f'{api}={len(rapi)}', end=' ')
                w.write(api)
                w.write(':\n')
                for a in sorted(rapi):
                    w.write(_sub_to_jni(a))
                    w.write('\n')
                w.write('----------\n')
            # print()
            # sep()
    print('done')








def __join_annotation(r):
    return ','.join(a for a in r[:2] if a is not None)

def _is_removed(r1, r2):
    return (r1 is not None) and (r2 is None)

def _is_annotate_removed(r1, r2):
    a1 = __join_annotation(r1)
    a2 = __join_annotation(r2)
    return ('@Removed' not in a1) and ('@Removed' in a2)

def _is_deprecated(r1, r2):
    a1 = __join_annotation(r1)
    a2 = __join_annotation(r2)
    return ('@Deprecated' not in a1) and ('@Deprecated' in a2)

def _is_hidden(r1, r2):
    a1 = __join_annotation(r1)
    a2 = __join_annotation(r2)
    return ('@Hide' not in a1) and ('@Hide' in a2)

def db_search(FROM=32, TO=33):
    URI = open('removed_apis/.db_conn').read()
    CONFIG = urlparse(URI)

    conn = pymysql.connect(
        host=CONFIG.hostname,
        port=CONFIG.port,
        database=CONFIG.path[1:],
        user=CONFIG.username,
        passwd=CONFIG.password,
    )

    with conn:
        for aal in ('jar', 'xml', 'txt', 'csv'):
            fn = f'removed_apis/r_{aal}_{FROM}_{TO}.txt'
            content = open(fn).read()
            classes, fields, methods, _ = map(str.strip, content.split('----------'))

            results = {
                'class': {
                    'none': list(),
                    'removed': list(),
                    'annotate_remove': list(),
                    'deprecated': list(),
                    'hidden': list(),
                    'other': list(),
                },
                'field': {
                    'none': list(),
                    'removed': list(),
                    'annotate_remove': list(),
                    'deprecated': list(),
                    'hidden': list(),
                    'other': list(),
                },
                'method': {
                    'none': list(),
                    'removed': list(),
                    'annotate_remove': list(),
                    'deprecated': list(),
                    'hidden': list(),
                    'other': list(),
                },
            }

            # print('--------------- class -----------------')

            with conn.cursor() as cur:
                sql = "SELECT c1.annotations, c2.annotations " + \
                        "FROM (android_class c1 LEFT JOIN android_class c2 ON c1.belonging_class_id=c2.class_id) " + \
                            "WHERE c1.sub_signature=%s AND c1.api_level=%s;"
                for line in filter(bool, classes.split('\n')):
                    if line == 'classes:':
                        continue

                    cur.execute(sql, (line, FROM))
                    res1 = cur.fetchone()

                    cur.execute(sql, (line, TO))
                    res2 = cur.fetchone()

                    if (res1 is None) and (res2 is None):
                        results['class']['none'].append(line)
                    elif _is_removed(res1, res2):
                        results['class']['removed'].append(line)
                    elif _is_annotate_removed(res1, res2):
                        results['class']['annotate_remove'].append(line)
                    elif _is_deprecated(res1, res2):
                        results['class']['deprecated'].append(line)
                    elif _is_hidden(res1, res2):
                        results['class']['hidden'].append(line)
                    else:
                        results['class']['other'].append(line)

            # print('--------------- field -----------------')

            with conn.cursor() as cur:
                sql = "SELECT f.annotations, c.annotations, f.access_modifier " + \
                        "FROM (android_field f INNER JOIN android_class c ON f.belonging_class_id=c.class_id) " + \
                            "WHERE f.sub_signature=%s AND f.api_level=%s;"
                for line in filter(bool, fields.split('\n')):
                    if line == 'fields:':
                        continue

                    cur.execute(sql, (line, FROM))
                    res1 = cur.fetchone()

                    cur.execute(sql, (line, TO))
                    res2 = cur.fetchone()

                    if (res1 is None) and (res2 is None):
                        results['field']['none'].append(line)
                    elif _is_removed(res1, res2):
                        results['field']['removed'].append(line)
                    elif _is_annotate_removed(res1, res2):
                        results['field']['annotate_remove'].append(line)
                    elif _is_deprecated(res1, res2):
                        results['field']['deprecated'].append(line)
                    elif _is_hidden(res1, res2):
                        results['field']['hidden'].append(line)
                    else:
                        results['field']['other'].append(line)

            # print('--------------- method -----------------')

            with conn.cursor() as cur:
                sql = "SELECT m.annotations, c.annotations, m.access_modifier " + \
                        "FROM (android_method m INNER JOIN android_class c ON m.belonging_class_id=c.class_id) " + \
                            "WHERE m.sub_signature=%s AND m.api_level=%s;"
                for line in filter(bool, methods.split('\n')):
                    if line == 'methods:':
                        continue

                    cur.execute(sql, (line, FROM))
                    res1 = cur.fetchone()

                    cur.execute(sql, (line, TO))
                    res2 = cur.fetchone()

                    if (res1 is None) and (res2 is None):
                        results['method']['none'].append(line)
                    elif _is_removed(res1, res2):
                        results['method']['removed'].append(line)
                    elif _is_annotate_removed(res1, res2):
                        results['method']['annotate_remove'].append(line)
                    elif _is_deprecated(res1, res2):
                        results['method']['deprecated'].append(line)
                    elif _is_hidden(res1, res2):
                        results['method']['hidden'].append(line)
                    else:
                        results['method']['other'].append(line)

            print(f'---------------- {aal} ------------------')
            # pprint(results)

            with open(fn.replace('.txt', '.json'), 'w') as w:
                json.dump(results, w, indent=1)







if __name__ == '__main__':
    dumpRemovedApis(28, 29)
    dumpRemovedApis(29, 30)
    dumpRemovedApis(30, 31)
    dumpRemovedApis(31, 32)
    dumpRemovedApis(32, 33)
    # db_search(28, 29)
    # db_search(29, 30)
    # db_search(30, 31)
    # db_search(31, 32)
    # db_search(32, 33)
