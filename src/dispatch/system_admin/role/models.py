from typing import Any, List, Optional

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Integer,
    Boolean,
    Table,
    ForeignKey
)
from typing import Optional

from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base 
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel 
from sqlalchemy.orm import relationship
from dispatch.system_admin.menu.models_secondary import role_menu_table,role_menu_button_table
from dispatch.system_admin.auth.models_secondary import role_dispatch_user_table
class Role( Base,TimeStampMixin):

    __tablename__ = 'role' 

    id = Column(BigInteger, primary_key=True,autoincrement=True)
    name = Column(String, nullable=False) #角色名称
    key = Column(String, nullable=False, unique = True) #权限字符
    sort = Column(Integer,default=1) #角色顺序
    status = Column(Boolean, default=True)    #角色状态
    admin = Column(Boolean,default=False)   # 是否为admin
    remark = Column(String)    #备注
    homepage_path = Column(String, default="/")  # 登录后跳转的主页
    # menu = Column(String)   # ManyToManyField  Menu关联菜单
    permission = relationship("MenuButton", secondary=role_menu_button_table, back_populates="role")
    menu = relationship("Menu", secondary=role_menu_table, back_populates="role")
    # permission = Column(String)   #ManyToManyField  MenuButton关联菜单的接口按钮
    dispatch_user = relationship("DispatchUser", secondary=role_dispatch_user_table, back_populates="role")

    search_vector = Column(
        TSVectorType(
            "name",
            "key",
            weights={"name": "A", "key": "B"},
        )
    )

    # __table_args__ = (UniqueConstraint('key', 'id', name='uix_id_role_key'),)




 

class RoleBase(BaseResponseModel):
    name: Optional[str]=""
    key: Optional[str]=""
    sort: Optional[int]=1
    status: Optional[bool]=True 
    admin: Optional[bool]=False 
    remark: Optional[str]="" 
    homepage_path: Optional[str]="/"



class RoleCreate(RoleBase):
    menuPermissions: Optional[Any] = []
    permission: Optional[List[Any]] = []
    menu: Optional[List[Any]] = []
    homepage_id: Optional[int] =None    ## 默认roles页面


class RoleUpdate(RoleBase):
    menuPermissions: Optional[Any] = []
    permission: Optional[List[Any]] = []
    menu: Optional[List[Any]] = []
    homepage_id: Optional[int] =None


class RoleRead(RoleBase,BaseResponseModel):
    id: int
    # menu: Optional[List['MenuButtonRead']] = []
    # permission: Optional[List['MenuRead']] = []

class RolePagination(DispatchBase):
    total: int
    items: List[RoleRead] = []
    itemsPerPage: int
    page : int

class RoleSelect(DispatchBase):
    id: int
    name: str

class RoleSelectRespone(DispatchBase):
    options: Optional[List[RoleSelect]] = []