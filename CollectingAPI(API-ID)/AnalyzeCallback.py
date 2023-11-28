# -*- coding: utf-8 -*-
import re


def select_method_name(listener):
    if listener == 'addTextChangedListener':
        return 'afterTextChanged'
    if listener == 'setOnClickListener':
        return 'onClick'
    if listener == 'setOnTouchListener':
        return 'onTouch'
    if listener == 'setOnLongClickListener':
        return 'onLongClick'
    if listener == 'setOnDragListener':
        return 'onDrag'
    # ......


def analyse_click(listener, source_code, class_name):
    add_class_name = class_name[1:-1]
    source_code_lines = source_code.split('\n')
    name_id_list = []
    name_class_list = []
    name_id_class_list = []
    new1_list = []
    new2_list = []
    for line in source_code_lines:
        if 'findViewById' in line:
            parts = line.split('=')
            if len(parts) > 0:
                t = parts[0]
                parts1 = t.split(' ')
                for i in parts1[::-1]:
                    if i != '':
                        view_name = i
                        break
            temp = re.findall(r'findViewById[(](.+?)[)]', line)
            if len(temp) > 0:
                view_id = temp[0]
            else:
                view_id = ''
            name_id_list.append({'view_name': view_name, 'view_id': view_id})
        if listener in line:
            parts = line.split('.' + listener)
            if len(parts) > 0:
                t = parts[0]
                parts1 = t.split(' ')
                for i in parts1[::-1]:
                    if i != '':
                        clicked_view_name = i
                        break
            temp = re.findall(r'[(]new[ ](.+?)[(]', line)
            if len(temp) > 0:
                clicked_class_name = temp[0]
            else:
                clicked_class_name = ''
            name_class_list.append({'clicked_view_name': clicked_view_name, 'clicked_class_name': clicked_class_name})
        if listener in line and 'new ' not in line:
            parts = line.split('.' + listener)
            clicked_view_name = ''
            if len(parts) > 0:
                t = parts[0]
                parts1 = t.split(' ')
                for i in parts1[::-1]:
                    if i != '':
                        clicked_view_name = i
                        break
            temp = re.findall(listener + '[(](.+?)[)]', line)
            if len(temp) > 0:
                clicked_field_name = temp[0]
            else:
                clicked_field_name = ''
            if clicked_field_name != '' and clicked_view_name != '':
                new1_list.append({'clicked_view_name': clicked_view_name, 'clicked_field_name': clicked_field_name})
        if '= new' in line:
            parts = line.split(' = new')
            clicked_field_name = ''
            new_view_class = ''
            if parts > 0:
                t = parts[0]
                parts1 = t.split(' ')
                for i in parts1[::-1]:
                    if i != '':
                        clicked_field_name = i
                        break
                    else:
                        clicked_field_name = ''
            temp = re.findall(r'=[ ]new[ ](.+?)[(]', line)
            if len(temp) > 0:
                new_view_class = temp[0]
            else:
                new_view_class = ''
            if new_view_class != '' and clicked_field_name != '':
                new2_list.append({'clicked_field_name': clicked_field_name, 'new_view_class': new_view_class})
    new3_list = []
    for i in new1_list:
        if i['clicked_field_name'] == 'this':
            new3_list.append({'clicked_view_name': i['clicked_view_name'], 'new_view_class': add_class_name})

    for i in new1_list:
        for j in new2_list:
            if i['clicked_field_name'] == j['clicked_field_name'] and i['clicked_field_name'] != '':
                new3_list.append({'clicked_view_name': i['clicked_view_name'], 'new_view_class': j['new_view_class']})

    for i in name_id_list:
        temp_i = {'method_name': 'onClick', 'name': i['view_name'], 'id': i['view_id'], 'class': ''}
        temp_i['method_name'] = select_method_name(listener)
        flag = 0
        for j in name_class_list:
            if i['view_name'] == j['clicked_view_name']:
                flag = 1
                temp_i['class'] = j['clicked_class_name']
                continue
        if temp_i['class'] == '':
            for z in new3_list:
                if temp_i['name'] == z['clicked_view_name']:
                    flag = 1
                    temp_i['class'] = z['new_view_class']
                    continue
        if flag == 1:
            name_id_class_list.append(temp_i)
    return name_id_class_list