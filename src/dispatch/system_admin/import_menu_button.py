import os
import json
from collections import defaultdict

from sqlalchemy.orm.session import Session

from dispatch.database_util.service import get_schema_session
from dispatch.system_admin.menu.models import Menu
from dispatch.system_admin.menu_button.models import MenuButton


def read_menu_button_file():
    cur_path = os.path.abspath(os.path.dirname(__file__))
    with open(f'{cur_path}/../static/menuButtonImport.json', 'r') as file:
        data_list = json.load(file)

    mapping_data = {}
    for i in data_list:
        group_name = i.get("GroupName")
        key_name = f"{i['name']}-{group_name}" if group_name else i['name']
        mapping_data[key_name] = i['MenuButton']
        api = i.get('api')
        if api:
            for btn in i['MenuButton']:
                if not btn.get('api'):
                    btn['api'] = api
    return mapping_data


def import_menu_button(db_session: Session):
    """ 存储菜单对应的所有存在的button列表 
    !!! menuButtonImport.json 里的 name 是 menu.json 里的 title
    """
    menu_button_mapping = defaultdict(list)
    menu_button_data = read_menu_button_file()
    btn_name_menu_titles = db_session.query(MenuButton.name, Menu.title).join(Menu, Menu.id == MenuButton.menu_id).all()
    for btn_menu in btn_name_menu_titles:
        btn_name, menu_title = btn_menu
        menu_button_mapping[menu_title].append(btn_name)
    
    need_created_buttons = []
    for name_group_name, buttons in menu_button_data.items():
        split_res = name_group_name.split("-")
        if len(split_res) == 2:
            name, group_name = split_res
        else:
            name = split_res[0]
            group_name = None

        menu = db_session.query(Menu).filter(Menu.title == name).first()
        """
        统一从menu.json中添加菜单, menuButtonimport.json 只负责管理导入菜单对应按钮
        if not menu:
            parent_id = None
            if group_name:
                # 根据 Menu name 查找父级菜单
                parent_menu = db_session.query(Menu).filter(Menu.name == group_name).first()
                if parent_menu:
                    parent_id = parent_menu.id

            menu = Menu(
                name=name,
                title=name,
                sort=999,
                status=True,
                visible=False,
                parent_id=parent_id
            )
            db_session.add(menu)
            db_session.commit()
        """

        if menu:
            for button in buttons:
                if button["name"] not in menu_button_mapping[name]:
                    need_created_buttons.append(
                        MenuButton(
                            name=button["name"], 
                            value=button["value"], 
                            api=button.get("api", "/api/"), 
                            menu_id=menu.id,
                            remark=button.get("remark", "")
                        )
                    )
                else:
                    # 更新已存在的按钮
                    existing_button = db_session.query(MenuButton).filter(
                        MenuButton.name == button["name"],
                        MenuButton.menu_id == menu.id
                    ).first()
                    if existing_button:
                        existing_button.value = button["value"]
                        existing_button.api = button.get("api", "/api/")
                        remark = button.get("remark", "")
                        if remark:
                            existing_button.remark = remark
                        db_session.add(existing_button)
                        db_session.commit()

    if need_created_buttons:
        db_session.bulk_save_objects(need_created_buttons)
        db_session.commit()


if __name__ == '__main__':
    print(read_menu_button_file())
    from dispatch.common.utils.cli import import_database_models
    import_database_models()
    db_session = get_schema_session(org_code="mes_root")
    import_menu_button(db_session)

