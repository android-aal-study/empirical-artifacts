import json
import re

__all__ = ['is_android_package', 'is_anonymous_or_lambda', 'is_anonymous_field', 'is_anonymous_method', 'is_aidl_or_proto', 'is_external']






def is_android_package(c):
    return c.startswith('android.') or c.startswith('com.android.') or c.startswith('dalvik.')

def is_external(c):
    if __is_framework(c):
        return False
    base = c.split('$')[0]
    query = classes_source.get(base, {})
    if query:
        return any(__externalHeuristic(base, ps[2]) for ps in query['parsed'])
    return False


def is_anonymous_or_lambda(c):
    # three condition: anonymous class, lambda expression at >= 30, lambda expression at < 30
    return re.search(r'\$\d+$', c) or re.search(r'\$\$ExternalSyntheticLambda\d+$', c) or re.search(r'-\$\$Lambda\$', c) or c.endswith('$$')

def is_anonymous_field(f, c):
    # return re.search(r'\d+$', f) or (('$' in f) and is_anonymous_or_lambda(c))
    return '$' in f

def is_anonymous_method(m, c):
    # return re.search(r'\d+$', m) or (('$' in m) and re.search(r'\$?lambda\$?|-\$\$', m))
    return '$' in m

def is_aidl_or_proto(c):
    return __is_aidl(c) or __is_proto(c)





# base is without \$ after
def __frameworkHeuristic(base, path):
    fn_post = base.replace('.', '/') + '.java'
    return path.startswith('frameworks/base/') and path.endswith(fn_post)

def __externalHeuristic(base, path):
    seg = base.split('.')
    last_pkg, cls_name = seg[-2], seg[-1]
    fn_post = f'{last_pkg}/{cls_name}.java'
    return path.startswith('external/') and path.endswith(fn_post)



# `c' is the fully-qualified name`
def __is_framework(c):
    base = c.split('$')[0]
    query = classes_source.get(base, {})
    if query:
        return any(__frameworkHeuristic(base, ps[2]) for ps in query['parsed'])
    return False


def __is_aidl(c):
    if __is_framework(c):
        return False
    base = c.split('$')[0]
    query = classes_source.get(base, {})
    if query:
        aidl_name = f'{base.split(".")[-1]}.aidl'
        parsed_suggestions = query['parsed']
        # isAidl = any(s[0].endswith('.aidl') for s in parsed_suggestions)
        # isAidl = any(s[0]==f'{base.split(".")[-1]}.aidl' for s in parsed_suggestions)
        return any(ps[0]==aidl_name for ps in parsed_suggestions)
    return False


def __is_proto(c):
    if __is_framework(c):
        return False
    base = c.split('$')[0]
    query = classes_source.get(base, {})
    if query and base.endswith('Proto'):
        parsed_suggestions = query['parsed']
        return any(ps[2].endswith('.proto') for ps in parsed_suggestions)
    return False


    
