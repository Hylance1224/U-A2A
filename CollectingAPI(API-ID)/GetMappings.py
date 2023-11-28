# -*- coding: utf-8 -*-
from androguard.misc import AnalyzeAPK
from androguard.core.bytecodes import apk
from androguard.core.bytecodes import dvm
from androguard.core.analysis import analysis
from androguard.core.analysis.analysis import ExternalMethod
from androguard.decompiler.decompiler import DecompilerDAD
import xlsxwriter
import re
import sys
import AnalyzeXML
import AnalyzeCallback
import sys
import pickle
import os
reload(sys)
sys.setdefaultencoding('utf8')


def get_androguard_obj(apkfile):
    a = apk.APK(apkfile)
    d = dvm.DalvikVMFormat(a.get_dex())
    dx = analysis.Analysis(d)
    return a, d, dx


def get_androguard_obj_1(apkfile):
    a, d, dx = AnalyzeAPK(apkfile)
    return a, d, dx


def get_field_value(field_name):
    temp = field_name.split('.')
    field_name = ''
    field_class = ''
    if len(temp) > 0:
        field_name = temp[-1]
        field_name = field_name
        field_class = 'L' + temp[0]
        for i in range(1, len(temp) - 1):
            field_class = field_class + '/' + temp[i]
        field_class = field_class + ';'
    if field_class != '' and field_name != '':
        for dex in d:
            clas = dex.get_class(field_class)
            if clas is not None:
                fields = clas.get_fields()
                for field in fields:
                    if field is not None:
                        if field.get_name() == field_name:
                            value = field.get_init_value().get_value()
                            str_value = str(value)
                            return str_value
    return ''


def get_click_id_class_list(a, d, dx):
    decompiler = DecompilerDAD(d, dx)
    name_id_class_list = []
    for clas in dx.get_classes():
        vm_class = clas.get_vm_class()
        try:
            class_source_code = decompiler.get_source_class(vm_class)
        except:  # external class
            class_source_code = ''
        name_id_class_list.extend(
            AnalyzeCallback.analyse_click(listener='setOnClickListener', source_code=class_source_code,
                                          class_name=vm_class.get_name()))
        name_id_class_list.extend(
            AnalyzeCallback.analyse_click(listener='addTextChangedListener', source_code=class_source_code,
                                          class_name=vm_class.get_name()))
        name_id_class_list.extend(
            AnalyzeCallback.analyse_click(listener='setOnTouchListener', source_code=class_source_code,
                                          class_name=vm_class.get_name()))
        name_id_class_list.extend(
            AnalyzeCallback.analyse_click(listener='setOnLongClickListener', source_code=class_source_code,
                                          class_name=vm_class.get_name()))
        name_id_class_list.extend(
            AnalyzeCallback.analyse_click(listener='setOnDragListener', source_code=class_source_code,
                                          class_name=vm_class.get_name()))
        # ......
    for name_id_class in name_id_class_list:
        if not name_id_class['id'].isdigit():
            field_value = get_field_value(name_id_class['id'])
            if field_value != '':
                name_id_class['id'] = field_value
    return name_id_class_list


def get_call(a, d, dx):
    call_list = []
    for method in dx.get_methods():
        orig_method = method.get_method()
        for other_class, callee, offset in method.get_xref_to():
            call_list.append({'orig_method': orig_method, 'callee': callee})
    return call_list


def find_method(a, d, dx, full_class_name, method_name):
    temp = full_class_name.split('$')
    class_name = 'L' + temp[0]
    full_class_name = full_class_name.replace('.', '/')
    full_class_name = 'L'+ full_class_name + ';'
    classes = dx.find_classes(name=class_name)
    for i in classes:
        if i.name == full_class_name:
            methods = i.get_methods()
            for method in methods:
                if method.name == method_name:
                    return method
    return 0


def find_called_api(dx, method):
    analyzed_method = {'extended_method':[], 'preparing_method':[], 'API':[]}
    analyzed_method['preparing_method'].append(method)
    extend_method(dx, analyzed_method)
    api_list = []
    for api in analyzed_method['API']:
        api_list.append({'class_name': api.get_class_name(), 'name':api.get_name()})
    return api_list


def extend_method(dx, analyzed_method):
    for method in analyzed_method['preparing_method']:
        encoded_method = method.get_method()
        if encoded_method in analyzed_method['extended_method']:
            pass
        else:
            analyzed_method['extended_method'].append(encoded_method)
            for other_class, called_method, offset in method.get_xref_to():  # called_method, EncodedMethod
                if isinstance(called_method, ExternalMethod):
                    analyzed_method['API'].append(called_method)
                else:
                    finded_called_methods = dx.find_methods(classname=called_method.get_class_name(), methodname=called_method.get_name())
                    for i in finded_called_methods: # find_call_methods, MethodClassAnalysis
                        if i.get_method() == called_method:
                            analyzed_method['preparing_method'].append(i)
                            extend_method(dx, analyzed_method)


def get_clicked_id_api(a, d, dx, id_text_map, dir):
    clicked_id_class_list = get_click_id_class_list(a, d, dx)
    for clicked_id_class in clicked_id_class_list:
        if clicked_id_class['class'] != '':
            on_click_method = find_method(a, d, dx, clicked_id_class['class'], clicked_id_class['method_name'])
            clicked_id_class['method'] = on_click_method
        else:
            clicked_id_class['method'] = 0
    for clicked_id_method in clicked_id_class_list:
        api_list = []
        if clicked_id_method['method'] != 0:
            api_list = find_called_api(dx, clicked_id_method['method'])
        clicked_id_method['api_list'] = api_list
    for clicked_obj in clicked_id_class_list:
        clicked_obj['ui_obj'] = []
        for id_text in id_text_map:
            if clicked_obj['id'] == id_text['id']:
                clicked_obj['ui_obj'] = id_text
    write_xml(clicked_id_class_list, dir)
    return


def write_xml(clicked_obj_list, dir):
    i = 0
    dst_wb = xlsxwriter.Workbook(path +dir + '.xlsx')
    worksheet = dst_wb.add_worksheet()
    for clicked_obj in clicked_obj_list:
        if len(clicked_obj['api_list']) == 0:
            continue
        worksheet.write(i, 0, clicked_obj['id'])
        if clicked_obj['ui_obj'] != []:
            worksheet.write(i, 5, clicked_obj['ui_obj']['text'])
            worksheet.write(i, 6, clicked_obj['ui_obj']['contentDescription'])
            worksheet.write(i, 7, clicked_obj['ui_obj']['hint'])
            # ......
            worksheet.write(i, 8, clicked_obj['ui_obj']['pre'])
            worksheet.write(i, 9, clicked_obj['ui_obj']['next'])
            worksheet.write(i, 10, clicked_obj['ui_obj']['id_name'])
            worksheet.write(i, 11, clicked_obj['ui_obj']['id'])
        if len(clicked_obj['api_list']) == 0:
            i = i + 1
        else:
            for api in clicked_obj['api_list']:
                worksheet.write(i, 2, api['class_name'])
                worksheet.write(i, 3, api['name'])
                i = i + 1
    dst_wb.close()


path = 'F:/apk/'
resPath = 'F:/apk/res/'

if __name__ == '__main__':
    apk_name = 'test.apk'
    id_text_map = AnalyzeAPK.analyze_layout(resPath)
    a, d, dx = get_androguard_obj_1(path + apk_name + '.apk')
    get_clicked_id_api(a, d, dx, id_text_map, apk_name)











