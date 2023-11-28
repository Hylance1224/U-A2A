# -*- coding: utf-8 -*-
import os
import uiautomator2 as u2
from androguard.core.bytecodes.apk import APK
import time
import random
import re
import xlrd
import GetFeatures
import RecordVideo
import threading
import AnalyzeNode
import BasicOperation
import ChangeState


global global_num
global global_depth
global global_operated_components
global global_total_operate_static_node
global global_static_nodes


def transfer_node_into_tag(node):
    text = GetFeatures.get_feature(node)
    return node.getAttribute('resource-id') + node.getAttribute('class') + text


def transfer_text_into_tags(file):
    nodes = AnalyzeNode.get_all_interactive_nodes(file, static_ids)
    tags = []
    for node in nodes:
        tag = transfer_node_into_tag(node)
        tags.append(tag)
    return tags


def infer_page_similar(file1, file2):
    tags1 = transfer_text_into_tags(file1)
    tags2 = transfer_text_into_tags(file2)
    if len(tags1) != len(tags2):
        return False
    else:
        for i in range(len(tags1)):
            if tags1[i] != tags2[i]:
                return False
    return True


def get_node_location(node):
    bounds = node.getAttribute('bounds')
    x_t = re.findall('\[(.+?),', bounds)
    x1 = float(x_t[0])
    x2 = float(x_t[1])
    x_coordinate = (x2 + x1)/2
    y_t = re.findall(',(.+?)\]', bounds)
    y1 = float(y_t[0])
    y2 = float(y_t[1])
    y_coordinate = (y2 + y1) / 2
    return (x1, y1, x2, y2)


def store_page_file():
    global global_num
    global global_depth
    global_num = global_num + 1
    global_depth = global_depth + 1
    image = global_d.screenshot(format='raw')
    ss = str(global_num)
    open(path + ss + ".jpg", "wb").write(image)
    text = global_d.dump_hierarchy()
    with open(path + ss + ".dom", "w", encoding='utf-8') as f:
        f.write(text)
    return path + ss + ".dom"


def is_operated(node):
    tag = transfer_node_into_tag(node)
    for c in global_operated_components:
        if tag == c:
            return True
    return False


def is_clickable(node):
    if node.getAttribute('clickable') == 'true':
        return True
    else:
        return False


def weight_choice(list, weight):
    new_list = []
    for i in range(len(list)):
        for j in range(weight[i]):
            new_list.append(list[i])
    return random.choice(new_list)


def is_new_occur_component(target_node):
    target_text = AnalyzeNode.get_text(target_node)
    target_id = AnalyzeNode.get_id_text(target_node)
    target_bounds = target_node.getAttribute('bounds')
    if global_num == 1:
        return True

    p = path + str(global_num - 1) + ".dom"
    interactive_nodes = AnalyzeNode.get_all_interactive_nodes(p, static_ids)
    for node in interactive_nodes:
        id_text = AnalyzeNode.get_id_text(node)
        text = AnalyzeNode.get_text(node)
        if target_text != '' or target_id != '':
            if target_id == id_text and target_text == text:
                return False
        else:
            bounds = node.getAttribute('bounds')
            if target_bounds == bounds:
                return False
    return True


def filter_components(operable_nodes):
    ids = []
    clear_nodes = []
    for node in operable_nodes:
        id = AnalyzeNode.get_id_text(node)
        if id == '':
            clear_nodes.append(node)
        elif id != '' and id not in ids:
            clear_nodes.append(node)
            ids.append(id)
    return clear_nodes


def sort_components(operable_nodes):
    priority = []
    for node in operable_nodes:
        if not is_operated(node):
            if AnalyzeNode.get_id_text(node) in static_ids:
                priority.append(60)
            if is_new_occur_component(node):
                priority.append(60)
            if is_clickable(node):
                priority.append(10)
            else:
                priority.append(7)
        else:
            if is_clickable(node):
                priority.append(3)
            elif AnalyzeNode.get_id_text(node) in static_ids:
                priority.append(2)
            else:
                priority.append(2)
    return priority


def choose_next_node(file, package_name):
    nodes = AnalyzeNode.get_all_interactive_nodes(file, static_ids)
    app_nodes = []
    for n in nodes:
        if n.getAttribute('package')==package_name:
            app_nodes.append(n)
    if len(nodes) == 0:
        return 'blank'
    elif len(nodes) > 0 and len(app_nodes) == 0:
        return 'jump'
    filter_nodes = filter_components(app_nodes)
    if len(filter_nodes) == 0:
        return 'jump'
    weight = sort_components(filter_nodes)
    next_node = weight_choice(filter_nodes, weight)
    return next_node


def operate_node(node):
    global global_total_operate_static_node
    global global_static_nodes
    id_text = AnalyzeNode.get_id_text(node)
    if id_text in static_ids:
        global_total_operate_static_node = global_total_operate_static_node + 1
        if id_text not in global_static_nodes:
            global_static_nodes.append(id_text)
    global global_operated_components
    tag = transfer_node_into_tag(node)
    if not is_operated(node):
        global_operated_components.append(tag)
    operations = []
    if node.getAttribute('clickable') == 'true':
        operations.append('click')
    elif node.getAttribute('long-clickable') == 'true':
        operations.append('long-click')
    elif node.getAttribute('scrollable') == 'true':
        operations.append('scoll')
    else:
        operations.append('click')
    operation = random.choice(operations)
    x1, y1, x2, y2 = get_node_location(node)
    x = (x1 + x2) / 2
    y = (y1 + y2) / 2

    if operation == 'click':
        global_d.click(x, y)
    elif operation == 'long-click':
        global_d.long_click(x, y)
    elif operation == 'scoll':
        if (x2-x1) > (y2-y1):
            global_d.swipe((x1+y2)/2, (y1+y2)/2, x1, (y1+y2)/2)
        else:
            global_d.swipe((x1 + y2) / 2, (y1 + y2) / 2, x1, (y1 + y2) / 2)
    store_animation_attribute(node, operation)


def store_animation_attribute(node, action):
    ss = str(global_num)
    f = open(path + ss + "attribute.txt", "w", encoding='utf-8')  # 设置文件对象
    text = AnalyzeNode.get_text(node)
    content_des = AnalyzeNode.get_content_des(node)
    sibling_text = AnalyzeNode.get_sibling_text(node)
    inner_text = AnalyzeNode.get_inner_text(node)
    id_text = AnalyzeNode.get_id(node)
    f.write('action:')
    f.write(action)
    f.write('\n')
    f.write('text:')
    f.write(text)
    f.write('\n')
    f.write('content-description:')
    f.write(content_des)
    f.write('\n')
    f.write('inner text:')
    f.write(inner_text)
    f.write('\n')
    f.write('sibling text:')
    f.write(sibling_text)
    f.write('\n')
    f.write('id:')
    f.write(id_text)
    f.write('\n')
    f.close()


def store_animation():
    ss = str(global_num)
    animation_path = path + ss
    RecordVideo.record_video(animation_path)


def store_screenshots():
    ss = str(global_num)
    animation_path = path + ss
    RecordVideo.record_screenshots(global_d, animation_path)


def get_static_id(app_num, static_id_path):
    p = static_id_path + str(app_num)+'look.xlsx'
    if not os.path.exists(p):
        return None
    file = xlrd.open_workbook(p)
    table = file.sheet_by_name('Sheet1')
    nrows = table.nrows
    static_ids = []
    for i in range(1, nrows):
        static_id = table.row(i)[6].value
        if static_id != '':
            static_ids.append(static_id)
    return static_ids


def check_and_change_state(package_name):
    global global_depth
    package_now, activity = BasicOperation.get_package_and_activity(global_d, package_name)
    if package_now != package_name:
        BasicOperation.stop_other_app(global_d, package_name)
        global_d.app_start(package_name)
        time.sleep(10)
    if ChangeState.need_restart(global_num, store_path, global_d):
        BasicOperation.stop_app(global_d)
        time.sleep(2)
        global_d.app_start(package_name)
        global_depth = 0
        time.sleep(10)
    if ChangeState.need_stop(global_num, store_path):
        return 'stop'
    return 'no_stop'


def store_operate(node, path, activity):
    ss = str(global_num)
    f = open(path + ss + "operate.txt", "w", encoding='utf-8')
    if is_operated(node):
        f.write('True')
    else:
        f.write('False')
    f.write('\n')
    f.write(node.getAttribute('class'))
    f.write('\n')
    f.write(node.getAttribute('text'))
    f.write('\n')
    f.write(node.getAttribute('content-desc'))
    f.write('\n')
    f.write(GetFeatures.get_sibling_text(node))
    f.write('\n')
    f.write(GetFeatures.get_child_content(node))
    f.write('\n')
    f.write(node.getAttribute('resource-id'))
    f.write('\n')
    f.write(activity)
    f.close()


def store_blank_operate(path, activity):
    ss = str(global_num)
    f = open(path + ss + "operate.txt", "w", encoding='utf-8')
    f.write('blank')
    f.write('\n')
    f.write('\n')
    f.write('\n')
    f.write('\n')
    f.write('\n')
    f.write('\n')
    f.write('\n')
    f.write(activity)
    f.close()


def traverse(package_name, store_path):
    global_d.app_start(package_name)
    global global_depth
    global path
    global_depth = 0
    path = store_path
    time.sleep(10)
    while(1):
        time.sleep(3)
        if check_and_change_state(package_name) == 'stop':
            break
        # 存储当前页面
        package_now, activity = BasicOperation.get_package_and_activity(global_d, package_name)
        file = store_page_file()

        node = choose_next_node(file, package_name)
        if node == 'blank':
            store_blank_operate(store_path, activity)
            global_d.click(100, 100)
        elif node == 'jump':
            store_blank_operate(store_path, activity)
            time.sleep(10)
        else:
            store_operate(node, store_path, activity)
            threads = []
            threads.append(threading.Thread(target=store_animation))
            threads.append(threading.Thread(target=operate_node, args=(node,)))

            for t in threads:
                t.start()
                time.sleep(0.5)


def get_package_name_from_file(path, number):
    file = xlrd.open_workbook(path + '/apk.xlsx')
    table = file.sheet_by_name('Sheet1')
    nrows = table.nrows
    ids = []
    for i in range(0, nrows):
        id = table.row(i)[0].value
        ids.append({'num': i + 1, 'id': id})

    for i in ids:
        if i['num'] == number:
            return i['id']


if __name__ == "__main__":
    global global_operated_components
    global global_num
    global global_total_operate_static_node
    global global_static_nodes
    global_d = u2.connect("127.0.0.1:7555")
    p = 'G:/apk/apk_photo'
    static_id_path = 'G:/apk/apk_photo/API/'
    for i in range(773, 800):
        print(i)
        static_ids = get_static_id(i, static_id_path)
        if static_ids is None:
            continue
        # print(static_ids)
        apk_path = p + '/' + str(i) + '.apk'
        package_name = get_package_name_from_file(p, i)
        print(package_name)
        try:
            global_d.app_install(apk_path)
        except:
            continue
        global_operated_components = []
        global_static_nodes = []
        global_num = 0
        global_total_operate_static_node = 0
        store_path = 'G:/output_animation/photo/' + str(i) + '/'
        os.makedirs(store_path)
        traverse(package_name, store_path)
        BasicOperation.stop_app(global_d)
        global_d.press("home")
        try:
            global_d.app_uninstall(package_name)
        except:
            pass



