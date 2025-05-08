import json
import os
import re
from copy import copy


def read_menu_file():
    # 读取JavaScript文件
    cur_path = os.path.abspath(os.path.dirname(__file__))
    with open(f'{cur_path}/../../static/menu.json', 'r') as file:
    # with open('/home/zhuojiacheng/data/mes_data/mes_web/src/dispatch/static/menu.json', 'r') as file:
        js_content = file.read()

    data_list = json.loads(js_content)

    return data_list


def read_menu_button_file():
    # 读取JavaScript文件
    cur_path = os.path.abspath(os.path.dirname(__file__))
    with open(f'{cur_path}/../../static/menuButton.json', 'r') as file:
        js_content = file.read()

    data_list = json.loads(js_content)
    mapping_data = {}
    for i in data_list:
        mapping_data[i['name']] = i['MenuButton']
        api  = i.get('api')
        if api:
            for btn in i['MenuButton']:
                if not btn.get('api'):
                    btn['api'] = api
    return mapping_data


first_menu_template =  {
        "name": "",
        "title": "",
        "icon": "",
        "sort": 1,
        "is_link": False,
        "is_catalog": True,
        "web_path": "",
        "component": "",
        "component_name": "",
        "status": True,
        "visible": True,
        "desc": "",
        "children": [],
        "menu_button": []
}

sec_menu_template =  {
                "name": "",
                "title": "",
                "icon": "",
                "sort": 0,
                "is_link": False,
                "is_catalog": False,
                "web_path": "",
                "component": "",
                "component_name": "",
                "status": True,
                "visible": True,
                "desc": "",
                "menu_button": []
            }


def get_menu_button(api, menuButtonList):
    button = []
    if api == 'menus':
        button.append({
                        "name": "menuButton",
                        "value": "menuButton",
                        "api": "/api/v1/"+api+"/",
                        "method": 1,
                        "remark": "",
                    })
    
    if api == 'roles':
        button.append({
                        "name": "PermissionButton",
                        "value": "PermissionButton",
                        "api": "/api/v1/"+api+"/",
                        "method": 1,
                        "remark": "",
                    })
    if menuButtonList:
        new_button = []
        for i in button:
            i['api'] =  i.get('api') or "/api/v1/"+api+"/"
            new_button.append(i)
        return new_button +  button
    else:
        return[
                {
                    "name": "Search",
                    "value": "Search",
                    "api": "/api/v1/"+api+"/",
                    "method": 0,
                    "remark": "",
                },
                {
                    "name": "Detail",
                    "value": "Detail",
                    "api": "/api/v1/"+api+"/{id}/",
                    "method": 0,
                    "remark": "",
                },
                {
                    "name": "Create",
                    "value": "Create",
                    "api": "/api/v1/"+api+"/",
                    "method": 1,
                    "remark": "",
                },
                {
                    "name": "Update",
                    "value": "Update",
                    "api": "/api/v1/"+api+"/{id}/",
                    "method": 2,
                    "remark": "",
                },
                {
                    "name": "Delete",
                    "value": "Delete",
                    "api": "/api/v1/"+api+"/{id}/",
                    "method": 3 ,
                    "remark": "",
                }
            ] +button



def get_first_menu(row,index):

    return {
        "name": row['header'],
        "title": row.get("title",''),
        "icon": "",
        "sort": index,
        "is_link": False,
        "is_catalog": True,
        "web_path": "",
        "component": "",
        "component_name": "",
        "status": True,
        "visible": True,
        "desc": row.get('desc',''),
        "children": [],
        "menu_button": []
}

def get_second_menu(row,index,menuButton):
    component = row.get("href","").replace("/","")
    return {
                "name": row['name'],
                "title": row.get("title",''),
                "icon": row.get('icon','mdi-clock-time-three-outline'),
                "sort": index,
                "is_link": False,
                "is_catalog": False,
                "web_path": row.get("href",""),
                "component": "",
                "component_name": component,
                "status": True,
                "visible": True,
                "desc": row.get('desc',''),
                "menu_button": get_menu_button(component,menuButton.get( row['name'],[]))
            }

def split_and_capitalize(s):
    # 将字符串分割成单词列表，假设单词由驼峰命名法连接
    words = []
    new_word = ''
    for char in s:
        if char.isupper():
            if new_word:
                words.append(new_word)
            new_word = char  # 开始一个新单词
        else:
            new_word += char  # 将字符添加到当前单词
    if new_word:  # 添加最后一个单词
        words.append(new_word)

    # 将单词首字母大写，并用空格连接
    capitalized_words = [word.capitalize() for word in words]
    return ' '.join(capitalized_words)

def get_menu():
    data_list = read_menu_file()
    menuButton= read_menu_button_file()
    data = []
    index = 1
    for row in data_list :
        try:
            pass
            if not row.get('header'):
                continue
            if "name" not in row:
                row['name'] = row.get('header')
            data.append(get_first_menu(row,index))
            index += 1
        except Exception as e:
            print(row)
            print(e)

    new_data = []
    for first_menu in data:
        index = 1
        for row in data_list :
            if  row.get('header'):
                    continue
            if first_menu['name'] == row['group']:
                # row['name'] = split_and_capitalize(row['name'])
                first_menu['children'].append(get_second_menu(row,index,menuButton))
                index +=1

        new_data.append(first_menu)

    return new_data

if __name__ == '__main__': 
    print(get_menu())