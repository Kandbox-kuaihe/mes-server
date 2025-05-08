from enum import Enum
from typing import Any, List, Optional

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Integer,
    Boolean,
    ForeignKey,
    Table,
    Enum as SQLEnum,
)
from typing import Optional

from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base 
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel 
from sqlalchemy.orm import relationship

from dispatch.system_admin.menu.models_secondary import role_menu_table,role_menu_button_table



 
class Menu( Base,TimeStampMixin):

    __tablename__ = 'menu' 

    id = Column(BigInteger, primary_key=True,autoincrement=True)
    icon = Column(String(64), nullable=True)  #菜单图标
    name = Column(String(64), nullable=False)   #菜单名称
    title = Column(String(64), nullable=True)   #菜单名称
    sort = Column(Integer,default=1) 
    is_link = Column(Boolean, default=False)     #是否外链
    is_catalog = Column(Boolean,default=False)    #是否目录
    web_path = Column(String(128), nullable=True)  #路由地址
    component = Column(String(128), nullable=True)  #路由地址
    component_name = Column(String(50), nullable=True)  #组件名称
    status = Column(Boolean,default=True)    #菜单状态
    visible = Column(Boolean,default=True)    #侧边栏中是否显示
    desc = Column(String(1000), nullable=True)  

    
    parent_id = Column(Integer, ForeignKey('menu.id') )  #上级菜单
    parent = relationship("Menu",  remote_side=[id] ,back_populates="children")
    
    children = relationship("Menu", back_populates="parent")

    role = relationship("Role", secondary=role_menu_table, back_populates="menu")

    search_vector = Column(
        TSVectorType(
            "name",
            "title",
            "web_path",
            weights={"name": "A", "title": "B","web_path": "C"},
        )
    )

    __table_args__ = (UniqueConstraint('web_path', 'id', name='uix_id_menu_web_path'),)

    def to_dict(self):
            return {
                "id": self.id,
                "name": self.name,
                "parent_id": self.parent_id,
            }

class MenuBase(BaseResponseModel):
    icon: Optional[str]= ""
    name: Optional[str]= ""
    title: Optional[str]= ""
    sort: Optional[int]= 1
    is_link:  Optional[bool]=False 
    is_catalog:  Optional[bool]=False 
    web_path: Optional[str]=""
    component: Optional[str]=""
    component_name: Optional[str]="" 
    status: Optional[bool]=True 
    visible: Optional[bool]=True 
    # role: Optional[List[RoleRead]] = []
    desc: Optional[str]=""

    parent_id: Optional[int] = None
    # children: Optional[list['Menu']] = None



 
class MenuCreate(MenuBase):
    parent_id: Optional[int] = None


class MenuUpdate(MenuBase):
    parent_id: Optional[int] = None


class MenuRead(MenuBase,BaseResponseModel):
    id: int
    parent: Optional[MenuBase] = None
    children: Optional[List[MenuBase]] = []
    

 

class TreeMenuRead(DispatchBase):
    id: Optional[int] = None
    label: str = None
    parent: Optional[int] = None
    children: Optional[List['TreeMenuRead']] = []

 
class TreeSelectMenuRead(DispatchBase):
    id: Optional[int] = None
    title: str = None
    hasChild: Optional[bool] = False
    checkbox: Optional[Any] =  None
    type: Optional[str] =  None
    children: Optional[List['TreeSelectMenuRead']] = []

class TreeSelectMenuResponse(DispatchBase):
    options: Optional[List['TreeSelectMenuRead']] = []

    
class TreeTopMenuRead(DispatchBase): 
    
    options: Optional[List['TreeMenuRead']] = []

class MenuPagination(DispatchBase):
    total: int
    items: List[MenuRead] = []
    itemsPerPage: int
    page : int

class MenuInitRespone(DispatchBase):
    status: str = None



class MenuConfig(DispatchBase):  

    header: Optional[str]= ""
    title: Optional[str]= ""
    group: Optional[str]= ""
    name: Optional[str]= ""
    icon: Optional[str]= ""
    href: Optional[str]= ""
    desc: Optional[str]= ""
    sort: Optional[int]= 1
    visible: Optional[bool]=True 