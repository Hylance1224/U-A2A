# -*- coding: utf-8 -*-
import os
import re
import xlsxwriter


def analyze_string_xml(path):
    files = os.listdir(path)
    name_content = []
    for file in files:
        f = open(path + "/" + file)
        content = ""
        lines = f.readlines()
        for line in lines:
            if '/>' in line:
                pass
            else:
                content = content + line
        content = content.replace('\n', ' ')
        if "<string name" in content and "</string>" in content:
            pat = re.compile(r'<string name="(.*?)">')
            string_name = pat.findall(content)
            string_content = re.findall(r'">(.*?)</string>', content)
            for i in range(len(string_name)):
                name_content.append({'string_name':string_name[i],'text':string_content[i]})
    return name_content


def analyze_public_xml(path):
    files = os.listdir(path)
    id_name_list = []
    for file in files:
        f = open(path + "/" + file)
        lines = f.readlines()
        for line in lines:
            if "name=" in line and "id=" in line and 'type="id"' in line:
                pat = re.compile(r'name="(.*?)"')
                name_re = pat.findall(line)
                id_re = re.findall(r'id="(.*?)"', line)
                if len(name_re) > 0:
                    id_name = name_re[0]
                else:
                    id_name = ''
                if len(id_re) > 0:
                    id = id_re[0]
                else:
                    id = ''
                if '0x' in id:
                    id_string = id.replace('0x','')
                    dec_id = int(id_string, 16)
                    dec_id = str(dec_id)
                else:
                    dec_id = ''
                id_name_list.append({'id': dec_id, 'id_name': id_name})
    return id_name_list


def analyze_line(line, line_num, space_num, file, string_list, id_list):
    line_layout_list = []
    type_re = re.findall(r'<(.+?)[ ]android:', line)
    if len(type_re) > 0:
        type = type_re[0]
    else:
        type = ''
    string_name_re = re.findall(r'android:text="@string/(.+?)"', line)
    if len(string_name_re) > 0:
        string_name = string_name_re[0]
    else:
        string_name = ''
    id_re = re.findall(r'android:id="@id/(.+?)"', line)
    id = ''
    if len(id_re) > 0:
        id_name = id_re[0]
        for i in id_list:
            if i['id_name'] == id_name:
                id = i['id']
    else:
        id_name = ''
    text_re = re.findall(r'android:text="(.+?)"', line)
    if len(text_re) > 0 and string_name == '':
        text = text_re[0]
    else:
        text = ''
    contentDescription_name_re = re.findall(r'android:contentDescription="@string/(.+?)"', line)
    if len(contentDescription_name_re) > 0:
        contentDescription_name = contentDescription_name_re[0]
    else:
        contentDescription_name = ''
    contentDescription_re = re.findall(r'android:contentDescription="(.+?)"', line)
    if len(contentDescription_re) > 0 and contentDescription_name == '':
        contentDescription = contentDescription_re[0]
    else:
        contentDescription = ''
    hint_name_re = re.findall(r'android:hint="@string/(.+?)"', line)
    if len(hint_name_re) > 0:
        hint_name = hint_name_re[0]
    else:
        hint_name = ''
    hint_re = re.findall(r'android:hint="(.+?)"', line)
    if len(hint_re) > 0 and hint_name == '':
        hint = hint_re[0]
    else:
        hint = ''
    if id_name != '' or text != '' or contentDescription != '' or hint != '':
        line_layout_list.append(
            {'type': type, 'file': file, 'id_name': id_name, 'id':id, 'string_name': string_name, 'text': text,
             'contentDescription_name': contentDescription_name,
             'contentDescription': contentDescription, 'hint_name': hint_name,
             'hint': hint, 'line_num': line_num, 'space_num': space_num})
    for line_layout in line_layout_list:
        for string in string_list:
            if string['string_name'] == line_layout['string_name']:
                line_layout['text'] = string['text']
            if string['string_name'] == line_layout['contentDescription_name']:
                line_layout['contentDescription'] = string['text']
            if string['string_name'] == line_layout['hint_name']:
                line_layout['hint'] = string['text']
    return line_layout_list


def get_blank_space(line):
    space_num = 0
    for i in line:
        if i == ' ':
            space_num = space_num + 1
        else:
            break
    return space_num


def analyze_layout(path):
    files = os.listdir(path + 'layout')
    string_list = analyze_string_xml(path + 'values')
    id_list = analyze_public_xml(path + 'values')
    file_idName_stringName = []
    for file in files:
        layout_list = []
        f = open(path + "layout/" + file)
        lines = f.readlines()
        line_num = 1
        for line in lines:
            line_num = line_num + 1
            space_num = get_blank_space(line)
            layout_list.extend(analyze_line(line, line_num, space_num, file, string_list, id_list))
        for i in range(len(layout_list)):
            if i >= 1:
                layout_pre = layout_list[i - 1]
            else:
                layout_pre = -1
            if i <= len(layout_list) - 2:
                layout_next =  layout_list[i + 1]
            else:
                layout_next = -1
            layout = layout_list[i]
            layout['pre'] = ''
            layout['next'] = ''
            if layout_pre != -1:
                if layout_pre['line_num'] == layout['line_num'] - 1:
                    if layout_pre['space_num'] == layout['space_num']:
                        if layout_pre['text'] != '':
                            layout['pre'] = layout_pre['text']
            if layout_next != -1:
                if layout_next['line_num'] == layout['line_num'] + 1:
                    if layout_next['space_num'] == layout['space_num']:
                        if layout_next['text'] != '':
                            layout['next'] = layout_next['text']
        file_idName_stringName.extend(layout_list)
    return file_idName_stringName


def get_id_map(path):
    stringName_text_list = analyze_string_xml(path=path + 'values')
    id_idName_list = analyze_public_xml(path=path + 'values')
    file_idName_stringName_list = analyze_layout(path=path + "layout")
    for file_idName_stringName in file_idName_stringName_list:
        file_idName_stringName['id'] = ''
        file_idName_stringName['text'] = ''
        for stringName_text in stringName_text_list:
            if stringName_text['string_name'] == file_idName_stringName['string_name']:
                file_idName_stringName['text'] = stringName_text['text']
            if stringName_text['string_name'] == file_idName_stringName['contentDescription_name']:
                file_idName_stringName['contentDescription'] = stringName_text['text']
            if stringName_text['string_name'] == file_idName_stringName['hint_name']:
                file_idName_stringName['hint'] = stringName_text['text']
        for id_idName in id_idName_list:
            if id_idName['id_name'] == file_idName_stringName['id_name']:
                if '0x' in id_idName['id']:
                    id_string = id_idName['id'].replace('0x','')
                    dec_id = int(id_string, 16)
                    dec_id = str(dec_id)
                else:
                    dec_id = ''
                file_idName_stringName['id'] = dec_id

    return file_idName_stringName_list


def write_xml(clicked_obj_list):
    dst_wb = xlsxwriter.Workbook('dst.xlsx')
    worksheet = dst_wb.add_worksheet()
    i = 0
    for clicked_obj in clicked_obj_list:
        worksheet.write(i, 0, clicked_obj['id'])
        worksheet.write(i, 1, clicked_obj['class'])
        if clicked_obj['ui_obj'] != []:
            worksheet.write(i, 5, clicked_obj['ui_obj']['text'])
            worksheet.write(i, 6, clicked_obj['ui_obj']['contentDescription'])
            worksheet.write(i, 7, clicked_obj['ui_obj']['hint'])
            worksheet.write(i, 8, clicked_obj['ui_obj']['id_name'])
            worksheet.write(i, 9, clicked_obj['ui_obj']['id'])
        if len(clicked_obj['api_list']) == 0:
            i = i + 1
        else:
            for api in clicked_obj['api_list']:
                worksheet.write(i, 3, api['class_name'])
                worksheet.write(i, 4, api['name'])
                i = i + 1
    dst_wb.close()


if __name__ == "__main__":
    uis = analyze_layout('E:/Python project/disassembler-study/example-APP/googlephoto/apk/res/')
    for ui in uis:
        print (ui)







