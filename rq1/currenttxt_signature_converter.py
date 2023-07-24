import re

"""
How to use?
    1. run the command `python signature_converter.py INPUT_PATH OUTPUT_PATH
    2. check the output.txt
"""


class SC:
    class Util:

        tag_pattern = r"<.*?>"
        remove_annotations_pattern = r'@[\w\.]+\s*'

        class_pattern1 = r"class\s+(.*?)\s*extends"
        class_pattern2 = r"class\s+(.*?)\s*implements"
        class_pattern3 = r"class\s+(.*?)\s*{"
        class_pattern4 = r"interface\s+(.*?)\s*extends"
        class_pattern5 = r"interface\s+(.*?)\s*implements"
        class_pattern6 = r"interface\s+(.*?)\s*{"
        class_pattern7 = r"@interface\s+(.*?)\s*{"
        class_pattern8 = r"enum\s+(.*?)\s*extends"
        class_pattern9 = r"enum\s+(.*?)\s*implements"
        class_pattern10 = r"enum\s+(.*?)\s*{"

        # find the parameter list in ctor
        ctor_pattern = r"\((.*?)\)"

        # param pattern
        param_pattern = r"(?<=\().*(?=\))"

        field_pattern1 = r"final\s+(.*?)\s*="
        field_pattern2 = r"final\s+(.*?)\s*;"
        field_pattern3 = r"static\s+(.*?)\s*;"
        field_pattern4 = r"field\s+(.*?)\s*;"

        method_pattern1 = r"static\s+(.*?)\s*;"
        method_pattern2 = r"final\s+(.*?)\s*;"
        method_pattern3 = r"method\s+(.*?)\s*;"

        enum_pattern = r"enum_constant\s+(.*?)\s*;"

        class_pattern_lst = [class_pattern1, class_pattern2, class_pattern3, class_pattern4, class_pattern5,
                             class_pattern6, class_pattern7, class_pattern8, class_pattern9, class_pattern10]

        field_pattern_lst = [field_pattern1, field_pattern2, field_pattern3, field_pattern4]

        method_pattern_lst = [method_pattern1, method_pattern2, method_pattern3]

        class_generic_parameter = {}

        method_generic_parameter = {}

        @staticmethod
        # remove the tags in string a:
        # abc<3213> -> abc
        def handle_generic_type(a: str, mark: str = 0) -> (str, dict):

            mapping = {}

            def remove_chars(text):
                index = text.find("<")
                if index != -1:
                    text = text[:index]
                return text

            # 这里的代码存在漏洞, 存在多个类型参数时，会出现问题

            m = re.search(SC.Util.tag_pattern, a)
            if m:
                type_param_list = m.group(0)[1:-1].split(",")
                # print(type_param_list)
                for type_param in type_param_list:

                    if "extends" not in type_param: continue
                    tmp = type_param.split()
                    if "?" == tmp[0]: continue

                    assert (len(tmp) == 3 or (tmp[3] == '&' or tmp[3] == 'super')) and tmp[1] == 'extends' and tmp[
                        0].isupper()
                    # 这里只添加了一个类型参数，但是可能存在多个类型参数的情况
                    mapping[tmp[0]] = remove_chars(tmp[2])
                    mapping[tmp[0] + "[]"] = remove_chars(tmp[2]) + "[]"  # add array type

            clean_text, stack = "", []
            for char in a:
                if char == '<':
                    stack.append(char)
                elif char == '>':
                    stack.pop()
                elif len(stack) == 0:
                    clean_text += char

            # add new plugin to mapping_plugin
            if mark == "class":
                SC.Util.class_generic_parameter.update(mapping)

            if mark == "method":
                SC.Util.method_generic_parameter.update(mapping)

            return clean_text

        @staticmethod
        def recursive_remove_annotations(text):

            string, stack = "", []
            start = False
            for char in text:
                if not start:
                    if char == '@':
                        start = True
                    else:
                        string += char
                else:
                    if char == '(':
                        stack.append(char)
                    elif char == ')':
                        stack.pop()
                        if len(stack) == 0:
                            start = False
                    elif char == ' ':
                        if len(stack) == 0:
                            start = False

            return string

        uni_class = set()

        @staticmethod
        def type_mapping(parameter):

            parameter = parameter.strip()

            # java.lang.Object... -> java.lang.Object[]
            # android.animation.Keyframe... -> android.animation.Keyframe[]
            if parameter.endswith("..."):
                parameter = parameter[:-3] + "[]"

            # android.view.ViewGroup.LayoutParams -> android.view.ViewGroup$LayoutParams
            # android.view.ViewGroup.LayoutParams -> android.view.ViewGroup$LayoutParams
            lst = parameter.split('.')
            check = False
            new_param = ''

            for idx in range(len(lst)):
                if len(lst[idx]) == 0: continue
                new_param += ('$' if check else '.') + lst[idx]
                if lst[idx][0].isupper(): check = True

            param = new_param[1:]

            # handle void param
            if param.lower() == "void":
                return ""

            # handle class generic param
            if param in SC.Util.method_generic_parameter.keys():
                return SC.Util.method_generic_parameter[param]

            # handle class generic param
            if param in SC.Util.class_generic_parameter.keys():
                return SC.Util.class_generic_parameter[param]

            # handle java.lang...
            if len(param) == 1 and param[0].isupper() \
                    or param == "Params" \
                    or param == "Result" \
                    or param == "Progress":
                return "java.lang.Object"
            elif len(param) == 3 and param[0].isupper() and "[]" in param \
                    or param == "Params[]" \
                    or param == "Result[]" \
                    or param == "Progress[]":
                return "java.lang.Object[]"
            elif len(param) > 1 and param[0].isupper():
                SC.Util.uni_class.add(param)
                return "java.lang." + param
            else:
                return param

        @staticmethod
        def get_class_info(line):

            line = SC.Util.handle_generic_type(line, "class")
            for pattern in SC.Util.class_pattern_lst:
                m = re.search(pattern, line)
                if m:
                    return m.group(1).replace('.', '$')

        @staticmethod
        def get_param_list(string):
            """
            (@NonNull android.media.AudioManager.OnAudioFocusChangeListener, @NonNull android.os.Handler)
            ->
            (android.media.AudioManager$OnAudioFocusChangeListener,android.os.Handler)
            """
            lst = [SC.Util.type_mapping(SC.Util.recursive_remove_annotations(x)).strip()
                   for x in string.split(",")]

            return ",".join(lst)

        @staticmethod
        def get_ctor_info(line):

            line = SC.Util.handle_generic_type(line)

            line = SC.Util.recursive_remove_annotations(line)
            # line = SC.Util.remove_annotations_from_string(line)

            m = re.search(SC.Util.ctor_pattern, line)
            if m:
                return SC.Util.get_param_list(m.group(1))
            else:
                raise ValueError("Unmatch ctor_para_list: " + line)

        @staticmethod
        # get the field type and name
        def get_field_info(line):
            line = SC.Util.handle_generic_type(line)
            line = SC.Util.recursive_remove_annotations(line)
            # line = SC.Util.remove_annotations_from_string(line)
            for idx in range(len(SC.Util.field_pattern_lst)):
                m = re.search(SC.Util.field_pattern_lst[idx], line)
                if m:
                    lst = m.group(1).split(' ')
                    assert " " not in lst, lst
                    assert len(lst) == 2 or len(lst) == 3 or len(lst) == 4, lst
                    return SC.Util.type_mapping(lst[-2]), lst[-1]
            raise ValueError("Unmatch field_info: " + line)

        @staticmethod
        # get the method return type , name and parameter list
        def get_method_info(line):

            # remove annotation with ()
            def remove_exceptions(string):
                throws_index = string.find("throws")
                if throws_index != -1:
                    return string[:throws_index - 1]
                return string

            def remove_default(string):
                default_index = string.find(") default ")
                if default_index != -1:
                    return string[:default_index + 1]
                return string

            line = SC.Util.handle_generic_type(line, "method")
            for idx in range(len(SC.Util.method_pattern_lst)):
                m = re.search(SC.Util.method_pattern_lst[idx], line)
                if m:

                    lst = remove_default(m.group(1))

                    lst = remove_exceptions(lst)

                    lst = SC.Util.recursive_remove_annotations(lst)

                    params_str = re.search(SC.Util.ctor_pattern, lst)

                    if params_str:
                        lst = lst.replace('(' + params_str.group(1) + ')', "")
                        params = SC.Util.get_param_list(params_str.group(1))
                    else:
                        raise ValueError("Unmatch method_para_list: " + "list:" + lst + "line:" + line)

                    lst = lst.split(' ')

                    return SC.Util.type_mapping(lst[-2]), lst[-1], params

            raise ValueError("Unmatch field_info: " + line)

        @staticmethod
        def get_enum_constant_info(line):
            line = SC.Util.handle_generic_type(line)
            m = re.search(SC.Util.enum_pattern, line)
            if m:
                lst = m.group(1).split(' ')
                # enum_constant type, name
                return SC.Util.type_mapping(lst[-2]), lst[-1]
            else:
                raise ValueError("Unmatch enum_constant: " + line)

    class Package:
        def __init__(self, identifier):
            self.identifier = identifier
            self.classes = []

    class Class:
        def __init__(self, identifier, package):
            self.identifier = identifier
            self.package = package
            self.fields = []
            self.methods = []

    def __init__(self, input_path):
        self.path = input_path
        self.packages = []

    def convert(self, out):

        # clazz_stack must be cleared before each package
        package_stack, clazz_stack = [], []

        def void_param_handler(return_param):
            return return_param if len(return_param) != 0 else "void"

        in_nonstatic_nested_class_context = False

        with open(self.path, 'r') as FILE:
            for line in FILE:
                # split the lines in the input.txt
                # keep the tree structure of the input.txt at the same time

                if line.startswith('//'): continue

                if line == '\n': continue

                lst = line.split(' ')

                # package domain start
                if line.startswith('package') and line.endswith('{\n') and len(lst) == 3:

                    name = line.split(' ')[1]
                    head = self.Package(name)
                    self.packages.append(head)
                    package_stack.append(head)


                # package domain end
                elif '}\n' in line and clazz_stack == []:
                    package_stack.clear()

                # class domain start
                elif (("class" in lst or "interface" in lst or "enum" in lst)
                      and "ctor" not in lst
                      and "method" not in lst
                      and "field" not in lst) or "@interface" in lst and len(package_stack) != 0:

                    SC.Util.class_generic_parameter.clear()
                    SC.Util.method_generic_parameter.clear()

                    class_name = self.Util.get_class_info(line)
                    if (' static ' not in line) and ('$' in class_name) and (' class ' in line):
                        in_nonstatic_nested_class_context = True

                    clazz = self.Class(class_name, package_stack[0].identifier)
                    package_stack[0].classes.append(clazz)
                    clazz_stack.append(clazz)

                    out.write(f"{package_stack[0].identifier}.{clazz_stack[0].identifier}\n")



                # class domain end
                elif '}\n' in line and clazz_stack != []:
                    clazz_stack.clear()
                    in_nonstatic_nested_class_context = False


                # ctor or field or method
                else:
                    if "ctor" in lst and clazz_stack != []:
                        ctor_param_list = SC.Util.get_ctor_info(line.strip())
                        if in_nonstatic_nested_class_context:
                            full_name = f"{package_stack[0].identifier}.{clazz_stack[0].identifier}"
                            outclass_name = full_name.split('$')[0]
                            if ctor_param_list:
                                ctor_param_list = outclass_name + "," + ctor_param_list
                            else:
                                ctor_param_list = outclass_name
                        out.write(
                            f"<{package_stack[0].identifier}.{clazz_stack[0].identifier}: void <init>({ctor_param_list})>\n")

                    elif "field" in lst and clazz_stack != []:
                        result = SC.Util.get_field_info(line.strip())
                        _type, name = result
                        out.write(
                            f"<{package_stack[0].identifier}.{clazz_stack[0].identifier}: {_type} {name}>\n")

                    elif "method" in lst and clazz_stack != []:
                        SC.Util.method_generic_parameter.clear()

                        if len(SC.Util.class_generic_parameter) != 0 and "method @Nullable public <T> T getParcelableExtra(@Nullable String, @NonNull Class<T>);" in line:
                            print(SC.Util.class_generic_parameter)

                        return_type, identifier, parameter_list = SC.Util.get_method_info(line.strip())
                        out.write(
                            f"<{package_stack[0].identifier}.{clazz_stack[0].identifier}: {void_param_handler(return_type)} {identifier}({parameter_list})>\n")

                    elif "enum_constant" in lst and clazz_stack != []:
                        _type, name = SC.Util.get_enum_constant_info(line.strip())
                        out.write(
                            f"<{package_stack[0].identifier}.{clazz_stack[0].identifier}: {_type} {name}>\n")

                    else:
                        raise ValueError("Invalid input file with invalid format: " + line)


def validate_signatures():
    for i in range(28, 34):
        outputpath = f'android-{i}/current.txt.txt'
        with open(outputpath) as r:
            for line in map(str.strip, r):
                try:
                    original = line
                    if line[0] == '<' and line[-1] == '>':
                        line = line[1:-1]  # method or field

                        class_name, line = line.split(':')  # implicitly assert only one colon
                        if '$' in class_name:
                            class_name = class_name.replace('$', '.')
                        if '_' in class_name:
                            class_name = class_name.replace('_', '')
                        assert all(s.isidentifier() for s in class_name.split('.')), 'invalid class name'

                        return_type, line = line[1:].split(' ')  # implicitly assert only one empty space
                        if '$' in return_type:
                            return_type = return_type.replace('$', '.')
                        while return_type.endswith('[]'):
                            return_type = return_type[:-2]
                        assert all(s.isidentifier() for s in return_type.split('.')), 'invalid (return) type'
                        if '(' in line:  # validate method
                            first_left = line.find('(')
                            last_right = line.find(')')
                            name = line[:first_left]
                            assert name.isidentifier() or name == '<init>', 'invalid method name'
                            assert last_right == len(line) - 1, 'invalid parameter parenthesis'

                            parameters = line[first_left + 1:last_right]
                            if parameters:
                                for p in parameters.split(','):
                                    if '$' in p:
                                        p = p.replace('$', '.')
                                    while p.endswith('[]'):
                                        p = p[:-2]
                                    assert all(s.isidentifier() for s in p.split('.')), 'invalid parameter(s)'
                        else:  # validate field
                            assert line.isidentifier(), 'invalid field name'
                    else:
                        class_name = line
                        if '$' in class_name:
                            class_name = class_name.replace('$', '.')
                        if '_' in class_name:
                            class_name = class_name.replace('_', '')
                        assert all(s.isidentifier() for s in class_name.split('.')), 'invalid class name'
                # except ValueError as ve:
                #     if ve.args[0].startswith('too many values to unpack'):
                #         continue
                #     else:
                #         raise
                except:
                    print(f'(api-level {i}) error in: {original}')
                    raise


def validate_quantities():
    for i in range(28, 34):
        inputpath = f'android-{i}/raw/current.txt'
        outputpath = f'android-{i}/current.txt.txt'

        before_class, after_class = 0, 0
        before_ctor, after_ctor = 0, 0
        before_method, after_method = 0, 0
        before_field, after_field = 0, 0
        with open(inputpath) as r:
            for line in map(str.strip, r):
                lst = line.split(" ")
                if ('class' in lst
                        or 'interface' in lst
                        or 'enum' in lst
                        or '@interface' in lst):
                    before_class += 1
                elif 'ctor' in lst:
                    before_ctor += 1
                elif ('field' in lst or
                      'enum_constant' in lst):
                    before_field += 1
                elif 'method' in lst:
                    before_method += 1

        with open(outputpath) as r:
            for line in map(str.strip, r):
                if "<init>" in line:  # ctor
                    after_ctor += 1
                elif '(' in line and ')' in line:  # method
                    after_method += 1
                elif '<' not in line and '>' not in line:  # class_name
                    after_class += 1
                else:  # field or enum_constant
                    after_field += 1

        print()
        assert before_class == after_class, f"android-{i} before_class_num: {before_class}, after_class_num: {after_class}"
        print(f"android-{i} pass class num check: {before_class}")

        assert before_ctor == after_ctor, f"android-{i} before_ctor_num: {before_ctor}, after_ctor_num: {after_ctor}"
        print(f"android-{i} pass ctor num check: {before_ctor}")

        assert before_method == after_method, f"android-{i} before_method_num: {before_method}, after_method_num: {after_method}"
        print(f"android-{i} pass method num check: {before_method}")

        assert before_field == after_field, f"android-{i} before_field_num: {before_field}, after_field_num: {after_field}"
        print(f"android-{i} pass field num check: {before_field}")


if __name__ == '__main__':
    for i in range(28, 34):
        inputpath = f'android-{i}/raw/current.txt'
        outputpath = f'android-{i}/current.txt.txt'
        with open(outputpath, 'w') as w:
            SC(inputpath).convert(w)

            print(f"android-{i} done")
            print(f"android-{i} unique_class: {SC.Util.uni_class}")
            SC.Util.uni_class.clear()

    validate_signatures()

    validate_quantities()
