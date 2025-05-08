
import logging
from dispatch.common.utils.read_menu_js import get_menu

from dispatch.org.enums import UserRoles
from dispatch.system_admin.menu.models import MenuCreate
from dispatch.system_admin.menu_button.models import MenuButton, MenuButtonCreate
from dispatch.system_admin.role import  service as role_service
from dispatch.system_admin.menu import  service as menu_service
from dispatch.system_admin.auth import  service as auth_service

from dispatch.system_admin.menu_button import service as menu_button_service
from dispatch.system_admin.role.models import RoleCreate

from dispatch.log import getLogger
log = getLogger(__name__)


def init_menu_role(org_db_session,user_email):

    # intialize menu
    permission_data = []
    menu_data = []
    try:
        data_list = get_menu()
        for row in data_list:
            first_data = menu_service.get_by_name(db_session=org_db_session, name=row["name"])
            if first_data is None:
                first_data = menu_service.create(db_session=org_db_session, Menu_in=MenuCreate(**row))
            menu_data.append(first_data)
            for second_menu in row["children"]:
                second_menu['parent_id'] = first_data.id
                second_menu_data = menu_service.get_by_name(db_session=org_db_session, name=second_menu["name"])
                if second_menu_data is None:
                    second_menu_data = menu_service.create(db_session=org_db_session, Menu_in=MenuCreate(**second_menu))
                
                menu_data.append(second_menu_data)
                second_menu_button_list = [i.name for i in second_menu_data.menu_button_to_menu ]
                for menu_button in second_menu["menu_button"]:
                    if menu_button['name']  in second_menu_button_list:
                        existing_button = org_db_session.query(MenuButton).filter(
                            MenuButton.menu_id == second_menu_data.id,
                            MenuButton.name == menu_button['name']
                        ).first()
                        existing_button.remark = menu_button.get('remark')
                        existing_button.api = menu_button.get('api')
                        org_db_session.add(existing_button)
                    else:
                        menu_button['menu'] = second_menu_data
                        menu_button_data = menu_button_service.create(db_session=org_db_session, MenuButton_in=MenuButtonCreate(**menu_button))
                    
                    permission_data.append(menu_button_data)

    except Exception as e:
        log.error(f'An exception occurred,{e}')

    
    # 创建一个初始化的角色
    try:
        # UserRoles()
        Role_in = RoleCreate(
                            name = UserRoles.SYSTEM, 
                            key = UserRoles.SYSTEM,
                            sort =1,
                            status = True,
                            admin = True,
                            remark = "System role",
                            menuPermissions= [],
                            permission= permission_data,
                            menu= menu_data,
                            homepage_id = 1
                        )
        role_data = role_service.create(db_session=org_db_session,Role_in=Role_in)
        if user_email:
            user_data = auth_service.get_by_email(db_session=org_db_session,email=user_email)
        else:
            user_data = auth_service.get_by_default_org_code(db_session=org_db_session)
        if user_data:
            user_data.role.append(role_data)
            org_db_session.add(user_data)
            org_db_session.commit()
            org_db_session.refresh(role_data)

    except Exception as e:
        log.error(f'An exception occurred,{e}')
    finally:
        org_db_session.close()