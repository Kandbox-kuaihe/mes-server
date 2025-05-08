import logging

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from dispatch.common.utils.read_menu_js import get_menu
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.menu_button.models import MenuButtonCreate, MenuButton
from dispatch.system_admin.menu.models import (
    Menu,
    MenuCreate,
    MenuUpdate,
    MenuInitRespone,
)
from dispatch.system_admin.role.models import Role
from dispatch.system_admin.role import service as role_service
from dispatch.system_admin.menu.service import create, update, get_by_name
from dispatch.org.service import get
from dispatch.system_admin.menu_button import service as menu_button_service
from dispatch.system_admin.menu.models_secondary import role_menu_table, role_menu_button_table
from dispatch.system_admin.import_menu_button import import_menu_button
from dispatch.org import setting_utils


from dispatch.log import getLogger
logger = getLogger(__name__)

def with_exception_handling(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Function {func.__name__} failed: {e}")
            return MenuInitRespone(status=f"{func.__name__} failed, caused: {e}")
    return wrapper


class InitMenuButtonSettings:

    @staticmethod
    @with_exception_handling
    def _init_menu(db_session: Session):
        data_list = get_menu()
        for row in data_list:
            try: 
                first_data = get_by_name(db_session=db_session, name=row["name"])
            except Exception as e:
                logger.error(f"Parent menu name: {row['name']}, error: {e}.")
                raise Exception(f"There is more than one record of the parent menu: {row['name']} in the database.")

            if first_data is None:
                first_data = create(db_session=db_session, Menu_in=MenuCreate(**row))
            for second_menu in row["children"]:
                second_menu['parent_id'] = first_data.id
                second_menu_icon = second_menu.get("icon")
                second_menu_desc = second_menu.get("desc")
                try: 
                    second_menu_data = get_by_name(db_session=db_session, name=second_menu["name"])
                except Exception as e:
                    logger.error(f"Children menu name: {second_menu['name']}, title: {second_menu['title']}, error: {e}.")
                    raise Exception(f"There is more than one record of the children menu: {second_menu['name']} in the database.")

                if second_menu_data is None:
                    second_menu_data = create(db_session=db_session, Menu_in=MenuCreate(**second_menu))
                else:
                    second_menu_data.icon = second_menu_icon
                    second_menu_data.desc = second_menu_desc
                    Menu_in = MenuUpdate(**second_menu_data.__dict__)
                    second_menu_data = update(db_session=db_session, Menu=second_menu_data, Menu_in=Menu_in)
                second_menu_button_list = [i.name for i in second_menu_data.menu_button_to_menu ]
                for menu_button in second_menu["menu_button"]:
                    if menu_button['name']  in second_menu_button_list:
                        continue
                    menu_button['menu'] = second_menu_data
                    menu_button_service.create(db_session=db_session, MenuButton_in=MenuButtonCreate(**menu_button))

        return MenuInitRespone(status="Init menu success.")
    
    @staticmethod
    @with_exception_handling
    def _init_menu_role_button(db_session: Session):
        """
        Create  role_menu_table role_menu_button_table
        """

        role = db_session.query(Role).filter(Role.name == 'sys').first()
        menus = db_session.query(Menu).all()
        buttons = db_session.query(MenuButton).all()

        role_menu = []
        menu_button = []
        for menu in menus:
            is_menu = (
                db_session.query(role_menu_table)
                .filter(
                    role_menu_table.c.menu_id == menu.id,
                    role_menu_table.c.role_id == role.id,
                )
                .first()
            )
            if not is_menu:
                role_menu.append({
                    "menu_id": menu.id,
                    "role_id": role.id
                })

        for button in buttons:
            is_button = (
                db_session.query(role_menu_button_table)
                .filter(
                    role_menu_button_table.c.menu_button_id == button.id,
                    role_menu_button_table.c.role_id == role.id,
                )
                .first()
            )
            if not is_button:
                menu_button.append({
                    "menu_button_id": button.id,
                    "role_id": role.id
                })
        if len(role_menu)>0:
            db_session.execute(role_menu_table.insert(), role_menu)
        if len(menu_button)>0:
            db_session.execute(role_menu_button_table.insert(), menu_button)
        db_session.commit()

        return MenuInitRespone(status="Init menu role button success.")
    
    @staticmethod
    @with_exception_handling
    def _init_settings(db_session: Session, current_user: DispatchUser):
        org = get(db_session=db_session, org_id=current_user.org_id, org_code=None)
        if not org:
            raise ValueError("This user organization is not found.")

        org.org_setting = setting_utils.read_setting_json() # ["default_job_flex_form_data"]
        flag_modified(org, "org_setting")
        db_session.add(org)
        db_session.commit()
        
        return MenuInitRespone(status="Init settings success.")
    

    @staticmethod
    @with_exception_handling
    def _import_menu_button(db_session: Session):
        import_menu_button(db_session)
        return MenuInitRespone(status="Import menu button success.")


    @staticmethod
    def init_menu_button_settings(db_session: Session, current_user: DispatchUser):
        """
        初始化菜单,按钮,数据字典
        :param db_session:
        :return:
        """

        res_init_menu = InitMenuButtonSettings._init_menu(db_session)
        res_import_button = InitMenuButtonSettings._import_menu_button(db_session)
        
        res_init_role_button = InitMenuButtonSettings._init_menu_role_button(db_session)
        res_init_settings = InitMenuButtonSettings._init_settings(db_session, current_user)

        return MenuInitRespone(
            status=f"{res_import_button.status} {res_init_menu.status} {res_init_role_button.status} {res_init_settings.status}"
        )
        