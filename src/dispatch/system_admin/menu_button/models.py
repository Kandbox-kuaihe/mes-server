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
from dispatch.system_admin.menu.models import MenuRead
from dispatch.system_admin.role.models import RoleRead
 
class METHOD_CHOICES(int, Enum):
    GET = 0
    POST = 1
    PUT = 2
    DELETE = 3

class MenuButton( Base,TimeStampMixin):

    __tablename__ = 'menu_button' 

    id = Column(BigInteger, primary_key=True,autoincrement=True)
    name = Column(String(64), nullable=False)   #名称
    value = Column(String(64), nullable=False)   #权限值
    api = Column(String(200), nullable=False)   #接口地址 
    method = Column(SQLEnum(METHOD_CHOICES), default=METHOD_CHOICES.GET)   #接口请求方法 
 
    menu_id = Column(BigInteger, ForeignKey("menu.id"), nullable=True, ) #关联菜单
    menu = relationship("Menu", backref="menu_button_to_menu")

    role = relationship("Role", secondary=role_menu_button_table, back_populates="permission")

    remark = Column(String)    #备注
    search_vector = Column(
        TSVectorType(
            "name",
            "api",
            weights={"name": "A", "api": "B"},
        )
    )

    # __table_args__ = (UniqueConstraint('web_path', 'id', name='uix_id_menu_web_path'),)


class MenuButtonBase(BaseResponseModel):
    name: Optional[str]= ""
    value: Optional[str]= ""
    api: Optional[str]= ""
    method: Optional[METHOD_CHOICES]= METHOD_CHOICES.GET
    menu: Optional[MenuRead] = None 
    remark: Optional[str]="" 
    # role: List[RoleRead] = []

class MenuButtonCreate(MenuButtonBase):
    pass


class MenuButtonUpdate(MenuButtonBase):
    pass


class MenuButtonRead(MenuButtonBase,BaseResponseModel):
    id: int


class MenuButtonPagination(DispatchBase):
    total: int
    items: List[MenuButtonRead] = []
    itemsPerPage: int
    page : int
