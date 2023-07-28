import os.path as ospath
from os import listdir, walk, makedirs


possible_list = ["call_APIs", "call_external_APIs", "call_reflect_APIs"]
possible_data_set = ["fdroid_result", "gplay_result", "malware_result"]







def mkdir_in_current_dir(dir_name):
    walk(ospath.abspath(__file__))
    if not ospath.exists(dir_name):
        makedirs(dir_name)


def is_obfuscator(api):
    def name_checking(name):
        if "$" in name:
            name = name.split("$")
            for i in name:
                if name_checking(i):
                    return True
            return False
        else:
            return len(name) <= 2

    param = api.split("->")[1]

    for i in api.split("->")[0].split("."):
        if name_checking(i):
            return True

    if "(" in param and ")" in param:
        name = param.split("(")[0].split(".")
        for i in name:
            if name_checking(i):
                return True
        param_list = param.split("(")[1].split(")")[0].split(",")
        for name in param_list:
            for i in name.split("."):
                if name_checking(i):
                    return True
    else:
        return name_checking(param)



def formalize_reflect_api(api: str):
    assert "->" in api and "(" not in api and ")" not in api
    return 'L' + api.replace("->", ";->").replace(".", "/").replace("$", "/")



def rm_param_lst(api):
    return api.split("(")[0]



def _get_pkg_name(x):
    return x.split('->')[0]

def sort_api_set(api_set: set) -> list:
    api_list = list(api_set)
    api_list = [line + '\n' for line in api_list]
    api_list = list(dict.fromkeys(api_list))
    api_list.sort(key=_get_pkg_name)
    return api_list



def stat_tmp_list_appendix(tmp_stat_list, filter_api_with_obfuscator=False):
    api_with_obfuscator = set()

    data_set_name = tmp_stat_list.split('_')[0]

    txt_list = [ospath.join(tmp_stat_list, file) for file in listdir(
        tmp_stat_list) if file.endswith('.txt')]

    merged_csv_field = {line.strip() for line in open(
        ospath.join(ospath.dirname(ospath.abspath(__file__)),
                     f"merged_api_list/field-CSV.txt"),
        'r')}

    merged_jar_field = {line.strip() for line in open(
        ospath.join(ospath.dirname(ospath.abspath(__file__)),
                     f"merged_api_list/field-JAR.txt"),
        'r')}

    merged_txt_field = {line.strip() for line in open(
        ospath.join(ospath.dirname(ospath.abspath(__file__)),
                     f"merged_api_list/field-TXT.txt"),
        'r')}
    merged_xml_field = {line.strip() for line in open(
        ospath.join(ospath.dirname(ospath.abspath(__file__)),
                     f"merged_api_list/field-XML.txt"),
        'r')}

    merged_csv_method = {line.strip() for line in open(
        ospath.join(ospath.dirname(ospath.abspath(__file__)),
                     f"merged_api_list/method-CSV.txt"),
        'r')}

    merged_jar_method = {line.strip() for line in open(
        ospath.join(ospath.dirname(ospath.abspath(__file__)),
                     f"merged_api_list/method-JAR.txt"),
        'r')}

    merged_txt_method = {line.strip() for line in open(
        ospath.join(ospath.dirname(ospath.abspath(__file__)),
                     f"merged_api_list/method-TXT.txt"),
        'r')}
    merged_xml_method = {line.strip() for line in open(
        ospath.join(ospath.dirname(ospath.abspath(__file__)),
                     f"merged_api_list/method-XML.txt"),
        'r')}

    only_in_csv_field = merged_csv_field - \
        merged_jar_field - merged_txt_field - merged_xml_field

    only_in_jar_field = merged_jar_field - \
        merged_csv_field - merged_txt_field - merged_xml_field

    only_in_txt_field = merged_txt_field - \
        merged_csv_field - merged_jar_field - merged_xml_field

    only_in_xml_field = merged_xml_field - \
        merged_csv_field - merged_jar_field - merged_txt_field

    only_in_csv_method = merged_csv_method - \
        merged_jar_method - merged_txt_method - merged_xml_method

    only_in_jar_method = merged_jar_method - \
        merged_csv_method - merged_txt_method - merged_xml_method

    only_in_txt_method = merged_txt_method - \
        merged_csv_method - merged_jar_method - merged_xml_method

    only_in_xml_method = merged_xml_method - \
        merged_csv_method - merged_jar_method - merged_txt_method

    # The only here is not true
    merged_csv_api = {rm_param_lst(api) for api in (
        merged_csv_method | merged_csv_field)}
    merged_jar_api = {rm_param_lst(api) for api in (
        merged_jar_method | merged_jar_field)}
    merged_txt_api = {rm_param_lst(api) for api in (
        merged_txt_method | merged_txt_field)}
    merged_xml_api = {rm_param_lst(api) for api in (
        merged_xml_method | merged_xml_field)}

    only_in_csv_api = merged_csv_api - merged_jar_api -\
        merged_txt_api - merged_xml_api

    only_in_jar_api = merged_jar_api - merged_csv_api -\
        merged_txt_api - merged_xml_api

    only_in_txt_api = merged_txt_api - merged_csv_api -\
        merged_jar_api - merged_xml_api

    only_in_xml_api = merged_xml_api - merged_csv_api -\
        merged_jar_api - merged_txt_api

    shared_field = merged_csv_field & merged_jar_field & merged_txt_field & merged_xml_field

    shared_method = merged_csv_method & merged_jar_method & merged_txt_method & merged_xml_method

    shared_api = merged_csv_api & merged_jar_api & merged_txt_api & merged_xml_api

    all_field = merged_csv_field | merged_jar_field | merged_txt_field | merged_xml_field

    all_method = merged_csv_method | merged_jar_method | merged_txt_method | merged_xml_method

    all_api = merged_csv_api | merged_jar_api | merged_txt_api | merged_xml_api

    call_field = set()
    call_method = set()
    only_in_csv_field_num = set()
    only_in_jar_field_num = set()
    only_in_txt_field_num = set()
    only_in_xml_field_num = set()
    only_in_csv_method_num = set()
    only_in_jar_method_num = set()
    only_in_txt_method_num = set()
    only_in_xml_method_num = set()
    in_shared_method_num = set()
    in_shared_field_num = set()
    androidx_or_support_field_num = set()
    androidx_or_support_method_num = set()

    # only for reflect api (api form without parameter list)
    is_reflect_api_list = False
    call_api = set()  # stat for reflect api
    in_all_api_num = set()
    in_shared_api_num = set()
    androidx_or_support_api_num = set()
    only_in_csv_api_num = set()
    only_in_jar_api_num = set()
    only_in_txt_api_num = set()
    only_in_xml_api_num = set()

    for api_txt in txt_list:
        assert api_txt.endswith('.txt'), 'Invalid file: ' + api_txt

        with open(api_txt, 'r') as FILE:

            for line in FILE:

                line = line.strip()

                # "call_external_APIs"
                if possible_list[1] in api_txt:
                    if filter_api_with_obfuscator and is_obfuscator(line):
                        api_with_obfuscator.add(line)
                        continue

                if line.endswith(";"):  # reflect api
                    line = line[:-1]
                    is_reflect_api_list = True

                    if line.startswith("androidx.") or line.startswith("android.support."):
                        androidx_or_support_api_num.add(line)

                    call_api.add(line)

                    if line in only_in_csv_api:
                        only_in_csv_api_num.add(line)
                    elif line in only_in_jar_api:
                        only_in_jar_api_num.add(line)
                    elif line in only_in_txt_api:
                        only_in_txt_api_num.add(line)
                    elif line in only_in_xml_api:
                        only_in_xml_api_num.add(line)

                    if line in shared_api:
                        in_shared_api_num.add(line)
                    if line in all_api:
                        in_all_api_num.add(line)

                else:
                    # method
                    if "(" in line and ")" in line:
                        if line.startswith("androidx.") or line.startswith("android.support."):
                            androidx_or_support_method_num.add(line)

                        call_method.add(line)
                        if line in only_in_csv_method:
                            only_in_csv_method_num.add(line)
                        elif line in only_in_jar_method:
                            only_in_jar_method_num.add(line)
                        elif line in only_in_txt_method:
                            only_in_txt_method_num.add(line)
                        elif line in only_in_xml_method:
                            only_in_xml_method_num.add(line)

                        if line in shared_method:
                            in_shared_method_num.add(line)

                    # field
                    else:

                        if line.startswith("androidx.") or line.startswith("android.support."):
                            androidx_or_support_field_num.add(line)

                        call_field.add(line)
                        if line in only_in_csv_field:
                            only_in_csv_field_num.add(line)
                        elif line in only_in_jar_field:
                            only_in_jar_field_num.add(line)
                        elif line in only_in_txt_field:
                            only_in_txt_field_num.add(line)
                        elif line in only_in_xml_field:
                            only_in_xml_field_num.add(line)

                        if line in shared_field:
                            in_shared_field_num.add(line)

    miss_method = call_method - all_method
    miss_field = call_field - all_field
    miss_api = call_api - all_api

    prefix = "direct" if possible_list[0] in api_txt else "extra" if possible_list[1] in api_txt else "reflect"
    mkdir_in_current_dir(f"{prefix}-{data_set_name}")

    # ["call_APIs", "call_external_APIs"]
    if not is_reflect_api_list:
        with open(
                ospath.join(f"{prefix}-{data_set_name}",
                             f"{prefix}-{data_set_name}-only-csv-method.txt"),
                'w') as csv_only_method:
            csv_only_method.writelines(
                sort_api_set(only_in_csv_method_num))

        with open(
                ospath.join(f"{prefix}-{data_set_name}",
                             f"{prefix}-{data_set_name}-only-jar-method.txt"),
                'w') as jar_only_method:
            jar_only_method.writelines(
                sort_api_set(only_in_jar_method_num))

        with open(
                ospath.join(f"{prefix}-{data_set_name}",
                             f"{prefix}-{data_set_name}-only-txt-method.txt"),
                'w') as txt_only_method:
            txt_only_method.writelines(
                sort_api_set(only_in_txt_method_num))

        with open(
                ospath.join(f"{prefix}-{data_set_name}",
                             f"{prefix}-{data_set_name}-only-xml-method.txt"),
                'w') as xml_only_method:
            xml_only_method.writelines(
                sort_api_set(only_in_xml_method_num))

        with open(
                ospath.join(f"{prefix}-{data_set_name}",
                             f"{prefix}-{data_set_name}-shared-method.txt"),
                'w') as shared_method_list:
            shared_method_list.writelines(
                sort_api_set(in_shared_method_num))

        with open(
                ospath.join(f"{prefix}-{data_set_name}",
                             f"{prefix}-{data_set_name}-only-csv-field.txt"),
                'w') as csv_only_field:
            csv_only_field.writelines(
                sort_api_set(only_in_csv_field_num))

        with open(
                ospath.join(f"{prefix}-{data_set_name}",
                             f"{prefix}-{data_set_name}-only-jar-field.txt"),
                'w') as jar_only_field:
            jar_only_field.writelines(
                sort_api_set(only_in_jar_field_num))

        with open(
                ospath.join(f"{prefix}-{data_set_name}",
                             f"{prefix}-{data_set_name}-only-txt-field.txt"),
                'w') as txt_only_field:
            txt_only_field.writelines(
                sort_api_set(only_in_txt_field_num))

        with open(
                ospath.join(f"{prefix}-{data_set_name}",
                             f"{prefix}-{data_set_name}-only-xml-field.txt"),
                'w') as xml_only_field:
            xml_only_field.writelines(
                sort_api_set(only_in_xml_field_num))

        with open(
                ospath.join(f"{prefix}-{data_set_name}",
                             f"{prefix}-{data_set_name}-shared-field.txt"),
                'w') as shared_field_list:
            shared_field_list.writelines(
                sort_api_set(in_shared_field_num))

        # ["call_APIs", "call_external_APIs"]
        if possible_list[0] in api_txt or possible_list[1] in api_txt:

            # ouput missed field in call_external_APIs without obfuscator
            if filter_api_with_obfuscator and possible_list[1] in api_txt:

                with open(
                        ospath.join(f"{prefix}-{data_set_name}",
                                     f"{prefix}-{data_set_name}-non-AAL-field-without-obfuscator.txt"),
                        'w') as non_AAL_field_list:
                    non_AAL_field_list.writelines(sort_api_set(miss_field))

                with open(
                        ospath.join(f"{prefix}-{data_set_name}",
                                     f"{prefix}-{data_set_name}-non-AAL-method-without-obfuscator.txt"),
                        'w') as non_AAL_method_list:
                    non_AAL_method_list.writelines(
                        sort_api_set(miss_method))

                with open(
                        ospath.join(f"{prefix}-{data_set_name}",
                                     f"{prefix}-{data_set_name}-total-field-without-obfuscator.txt"),
                        'w') as total_field_list:
                    total_field_list.writelines(
                        sort_api_set(call_field))

                with open(
                        ospath.join(f"{prefix}-{data_set_name}",
                                     f"{prefix}-{data_set_name}-total-method-without-obfuscator.txt"),
                        'w') as total_method_list:
                    total_method_list.writelines(
                        sort_api_set(call_method))

                with open(
                        ospath.join(f"{prefix}-{data_set_name}",
                                     f"{prefix}-{data_set_name}-androidx-or-support-field-without-obfuscator.txt"),
                        'w') as androidx_or_support_field_list:
                    androidx_or_support_field_list.writelines(
                        sort_api_set(androidx_or_support_field_num))

                with open(
                        ospath.join(f"{prefix}-{data_set_name}",
                                     f"{prefix}-{data_set_name}-androidx-or-support-method-without-obfuscator.txt"),
                        'w') as androidx_or_support_method_list:
                    androidx_or_support_method_list.writelines(
                        sort_api_set(androidx_or_support_method_num))

            # ouput missed field
            else:
                with open(
                        ospath.join(f"{prefix}-{data_set_name}",
                                     f"{prefix}-{data_set_name}-non-AAL-field.txt"),
                        'w') as non_AAL_field_list:
                    non_AAL_field_list.writelines(sort_api_set(miss_field))

                with open(
                        ospath.join(f"{prefix}-{data_set_name}",
                                     f"{prefix}-{data_set_name}-non-AAL-method.txt"),
                        'w') as non_AAL_field_list:
                    non_AAL_field_list.writelines(sort_api_set(miss_method))

                with open(
                        ospath.join(f"{prefix}-{data_set_name}",
                                     f"{prefix}-{data_set_name}-total-field.txt"),
                        'w') as total_field_list:
                    total_field_list.writelines(
                        sort_api_set(call_field))

                with open(
                        ospath.join(f"{prefix}-{data_set_name}",
                                     f"{prefix}-{data_set_name}-total-method.txt"),
                        'w') as total_method_list:
                    total_method_list.writelines(
                        sort_api_set(call_method))

                with open(
                        ospath.join(f"{prefix}-{data_set_name}",
                                     f"{prefix}-{data_set_name}-androidx-or-support-field.txt"),
                        'w') as androidx_or_support_field_list:
                    androidx_or_support_field_list.writelines(
                        sort_api_set(androidx_or_support_field_num))

                with open(
                        ospath.join(f"{prefix}-{data_set_name}",
                                     f"{prefix}-{data_set_name}-androidx-or-support-method.txt"),
                        'w') as androidx_or_support_method_list:
                    androidx_or_support_method_list.writelines(
                        sort_api_set(androidx_or_support_method_num))

        draw_latex_appendix_table1(
            data_set_name,
            f"{len(listdir(tmp_stat_list)):,}",
            f"{len(only_in_jar_field_num):,}/{len(only_in_jar_field):,}",
            f"{len(only_in_xml_field_num):,}/{len(only_in_xml_field):,}",
            f"{len(only_in_txt_field_num):,}/{len(only_in_txt_field):,}",
            f"{len(only_in_csv_field_num):,}/{len(only_in_csv_field):,}",
            f"{len(in_shared_field_num):,}/{len(shared_field):,}",
            f"{len(miss_field):,}",
            f"{len(call_field):,}",
            f"{len(androidx_or_support_field_num):,}",
            f"{len(only_in_jar_method_num):,}/{len(only_in_jar_method):,}",
            f"{len(only_in_xml_method_num):,}/{len(only_in_xml_method):,}",
            f"{len(only_in_txt_method_num):,}/{len(only_in_txt_method):,}",
            f"{len(only_in_csv_method_num):,}/{len(only_in_csv_method):,}",
            f"{len(in_shared_method_num):,}/{len(shared_method):,}",
            f"{len(miss_method):,}",
            f"{len(call_method):,}",
            f"{len(androidx_or_support_method_num):,}",
        )

    # ["call_reflect_APIs"]
    else:
        with open(
                ospath.join(f"{prefix}-{data_set_name}",
                             f"{prefix}-{data_set_name}-only-csv-api.txt"),
                'w') as csv_only_api:
            csv_only_api.writelines(
                sort_api_set({formalize_reflect_api(api) for api in only_in_csv_api_num}))

        with open(
                ospath.join(f"{prefix}-{data_set_name}",
                             f"{prefix}-{data_set_name}-only-jar-api.txt"),
                'w') as jar_only_api:
            jar_only_api.writelines(
                sort_api_set({formalize_reflect_api(api) for api in only_in_jar_api_num}))

        with open(
                ospath.join(f"{prefix}-{data_set_name}",
                             f"{prefix}-{data_set_name}-only-txt-api.txt"),
                'w') as txt_only_api:
            txt_only_api.writelines(
                sort_api_set({formalize_reflect_api(api) for api in only_in_txt_api_num}))

        with open(
                ospath.join(f"{prefix}-{data_set_name}",
                             f"{prefix}-{data_set_name}-only-xml-api.txt"),
                'w') as xml_only_api:
            xml_only_api.writelines(
                sort_api_set({formalize_reflect_api(api) for api in only_in_xml_api_num}))

        with open(
                ospath.join(f"{prefix}-{data_set_name}",
                             f"{prefix}-{data_set_name}-shared-api.txt"),
                'w') as shared_api_list:
            shared_api_list.writelines(
                sort_api_set({formalize_reflect_api(api) for api in in_shared_api_num}))

        with open(
                ospath.join(f"{prefix}-{data_set_name}",
                             f"{prefix}-{data_set_name}-total-api.txt"),
                'w') as total_api_list:
            total_api_list.writelines(
                sort_api_set({formalize_reflect_api(api) for api in call_api}))

        with open(
                ospath.join(f"{prefix}-{data_set_name}",
                             f"{prefix}-{data_set_name}-non-AAL-api.txt"),
                'w') as api_list:
            api_list.writelines(sort_api_set(
                {formalize_reflect_api(api) for api in miss_api}))

        with open(
                ospath.join(f"{prefix}-{data_set_name}",
                             f"{prefix}-{data_set_name}-androidx-or-support-api.txt"),
                'w') as androidx_or_support_api_list:
            androidx_or_support_api_list.writelines(
                sort_api_set({formalize_reflect_api(api) for api in androidx_or_support_api_num}))

        draw_latex_appendix_table2(
            data_set_name,
            f"{len(listdir(tmp_stat_list)):,}",
            f"{len(only_in_jar_api_num):,}/{len(only_in_jar_api):,}",
            f"{len(only_in_xml_api_num):,}/{len(only_in_xml_api):,}",
            f"{len(only_in_txt_api_num):,}/{len(only_in_txt_api):,}",
            f"{len(only_in_csv_api_num):,}/{len(only_in_csv_api):,}",
            f"{len(in_shared_api_num):,}/{len(shared_api):,}",
            f"{len(miss_api):,}",
            f"{len(call_api):,}",
            f"{len(androidx_or_support_api_num):,}",
        )


def stat_tmp_list_body(data_set, filter_api_with_obfuscator=False):
    data_set_name = data_set.split('_')[0]

    direct_call_api_dir = data_set_name + f"_{possible_list[0]}"
    extra_call_api_dir = data_set_name + f"_{possible_list[1]}"
    reflect_call_api_dir = data_set_name + f"_{possible_list[2]}"

    direct_call_api_txt_list = [ospath.join(direct_call_api_dir, file) for file in
                                listdir(direct_call_api_dir) if file.endswith('.txt')]

    extra_call_api_txt_list = [ospath.join(extra_call_api_dir, file) for file in
                               listdir(extra_call_api_dir) if file.endswith('.txt')]

    reflect_call_api_txt_list = [ospath.join(reflect_call_api_dir, file) for file in
                                 listdir(reflect_call_api_dir) if file.endswith('.txt')]

    direct_call_api = set()
    extra_call_api = set()
    reflect_call_api = set()

    for api_txt in direct_call_api_txt_list:
        with open(api_txt, 'r') as FILE:
            for line in FILE:
                line = line.strip()
                direct_call_api.add(line)

    for api_txt in extra_call_api_txt_list:
        with open(api_txt, 'r') as FILE:
            for line in FILE:
                line = line.strip()
                if filter_api_with_obfuscator and is_obfuscator(line):
                    continue
                extra_call_api.add(line)

    for api_txt in reflect_call_api_txt_list:
        with open(api_txt, 'r') as FILE:
            for line in FILE:
                line = line.strip()
                reflect_call_api.add(line)

    dataset = 'F-Droid' if data_set_name == 'fdroid' else 'Google Play' if data_set_name == 'gplay' else 'Malware'

    draw_latex_body_table(
        dataset,
        f"{len(listdir(direct_call_api_dir)):,}",   # as direct call are used by all, simplified logic!!!
        f"{len(direct_call_api):,}",
        f"{len(listdir(direct_call_api_dir)):,}",
        f"{len(extra_call_api):,}",
        f"{len(listdir(extra_call_api_dir)):,}",
        f"{len(reflect_call_api):,}",
        f"{len(listdir(reflect_call_api_dir)):,}"
    )





def _dummy(x):
    return "-" if x == "0/0" else x

def draw_latex_appendix_table1(dataset,
                               apk_num,
                               jar_only_field,
                               xml_only_field,
                               txt_only_field,
                               csv_only_field,
                               shared_field,
                               miss_field,
                               call_field,
                               androidx_or_support_field,
                               jar_only_method,
                               xml_only_method,
                               txt_only_method,
                               csv_only_method,
                               shared_method,
                               miss_method,
                               call_method,
                               androidx_or_support_method):
    print(
        f"{dataset} & {apk_num} & {_dummy(jar_only_field)} & {_dummy(xml_only_field)} & {_dummy(txt_only_field)} & {csv_only_field} & {shared_field} & {miss_field} & {call_field} & {androidx_or_support_field} & {_dummy(jar_only_method)} & {_dummy(xml_only_method)} & {_dummy(txt_only_method)} & {csv_only_method} & {shared_method} & {miss_method} & {call_method} & {androidx_or_support_method}\\\\")

def draw_latex_appendix_table2(dataset,
                               apk_num,
                               jar_only_api,
                               xml_only_api,
                               txt_only_api,
                               csv_only_api,
                               shared_api,
                               miss_api,
                               call_api,
                               androidx_or_support_api):
    print(
        f"{dataset} & {apk_num} & {_dummy(jar_only_api)} & {_dummy(xml_only_api)} & {_dummy(txt_only_api)} & {csv_only_api} & {shared_api} & {miss_api} & {call_api} & {androidx_or_support_api}\\\\")





def draw_latex_body_table(dataset,
                          apk_num,
                          direct_call_api_num,
                          direct_call_apk_num,
                          extra_call_api_num,
                          extra_call_apk_num,
                          reflect_api_num,
                          reflect_apk_num):
    print(
        f"{dataset} & {apk_num} & {direct_call_api_num} & {direct_call_apk_num} & {extra_call_api_num} & {extra_call_apk_num} & {reflect_api_num} & {reflect_apk_num} \\\\")





def general_stat_for_body():
    print(
        f"------------------------ Table for body ---------------------------")
    for data_set in possible_data_set:
        stat_tmp_list_body(data_set, False)
    print(f"-----------------------------------------------------------------")


def _get_tmp_dict_name(data_set, key):
    return data_set.split('_')[0] + '_' + key

def general_stat_for_appendix(contain_obfuscate):
    for key in possible_list:
        print(
            f"---------------------Table for appendix: {key} (contain obfuscate={contain_obfuscate})------------------------")
        for data_set in possible_data_set:
            stat_tmp_list_appendix(_get_tmp_dict_name(
                data_set, key), not contain_obfuscate)
        print(f"---------------------------------------------------------------------")



if __name__ == '__main__':
    general_stat_for_body()

    # general_stat_for_appendix(contain_obfuscate=True)
    # general_stat_for_appendix(contain_obfuscate=False)
