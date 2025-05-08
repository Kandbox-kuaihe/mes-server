import secrets
import string
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, List, Optional
from uuid import uuid4

import bcrypt
from jose import jwt
from pydantic import Field, ValidationInfo, field_validator
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer
from sqlalchemy import LargeBinary as Binary
from sqlalchemy import PrimaryKeyConstraint, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.config import DISPATCH_JWT_ALG, DISPATCH_JWT_EXP, DISPATCH_JWT_SECRET
from dispatch.database import Base
from dispatch.models import BaseResponseModel, DispatchBase, TimeStampMixin

# from dispatch.team.models import TeamRead
from dispatch.org.enums import UserRoles
from dispatch.system_admin.auth.models_secondary import role_dispatch_user_table, user_mill_table
from dispatch.system_admin.menu.models import MenuBase, MenuConfig
from dispatch.system_admin.menu_button.models import MenuButtonRead
from dispatch.system_admin.role.models import RoleRead

# from dispatch.mill.models import MillRead

def generate_password():
    """Generates a resonable password if none is provided."""
    alphanumeric = string.ascii_letters + string.digits
    while True:
        password = "".join(secrets.choice(alphanumeric) for i in range(10))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password) >= 3
        ):
            break
    return password


def hash_password(password: str):
    """Generates a hashed version of the provided password."""
    pw = bytes(password, "utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt)



dispatch_user_managed_teams = Table(
    "dispatch_user_managed_teams",
    Base.metadata,
    # Column("team_id", Integer, ForeignKey("team.id")),
    Column("user_id", Integer, ForeignKey("dispatch_core.dispatch_user.id")),
    Column("user_role", String, default=UserRoles.PLANNER),
    PrimaryKeyConstraint( "user_id"),
)


class DispatchUser(Base, TimeStampMixin):

    __table_args__ = {"schema": "dispatch_core"}
    id = Column(BigInteger, primary_key=True,autoincrement=True)
    email = Column(String, unique=True)
    password = Column(Binary, nullable=False)
    # role = Column(String, nullable=False, default=UserRoles.WORKER)
    
    role = relationship("Role", secondary=role_dispatch_user_table, back_populates="dispatch_user")
    is_org_owner = Column(Boolean, nullable=True, default=False)
    org_id = Column(Integer, nullable=False, default=-1)
    org_code = Column(String, nullable=False, default="-1")
    is_team_owner = Column(Boolean, nullable=True, default=False)
    # team_code = Column(String, nullable=True, default="t1")
    default_team_id = Column(Integer, default=-1)
    # https://avatars1.githubusercontent.com/u/5224736?s=400&u=c9dd310fdfea18388a409197a3f5f4f6b64af46e&v=4
    thumbnail_photo_url = Column(String, default="")
    full_name = Column(String)

    is_team_worker = Column(Boolean, nullable=True, default=False)
    is_active = Column(Boolean, default=False)  # job vs absence

    current_mill_id = Column(Integer, default=-1)
    current_mill_code = Column(String, nullable=True, default="")
    current_menu_path = Column(String, nullable=True, default="/")
    mill = relationship("Mill", secondary=user_mill_table, back_populates="dispatch_user")

    show_bottom_note = Column(Boolean, default=True)

    # managed_teams = relationship(
    #     "Team",
    #     secondary=dispatch_user_managed_teams,
    #     backref="dispatch_user_managed_teams_rel",
    # )

    search_vector = Column(
        TSVectorType(
            "email",
            "full_name",
            weights={"email": "A", "full_name": "B"},
        )
    )

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    def generate_token(self, duration_seconds):
        session_id = str(uuid4())
        now = datetime.now()

        # 直接使用 Unix 时间戳计算
        exp_timestamp = int(now.timestamp()) + int(duration_seconds)

        data = {
            "exp": exp_timestamp,  # 使用 Unix 时间戳，避免 datetime 计算问题
            "email": self.email,
            "org_code": self.org_code,
            "org_id": self.org_id,
            "role": [i.name for i in self.role],
            "default_team_id": self.default_team_id,
            "current_mill_id": self.current_mill_id,
            "session_id": session_id,
        }
        return jwt.encode(data, DISPATCH_JWT_SECRET, algorithm=DISPATCH_JWT_ALG)
    
    def generate_token_for_job(self, duration_seconds, job_code):
        today = date.today()
        now = datetime(year=today.year, month=today.month, day=today.day)

        # 直接使用 Unix 时间戳计算
        exp_timestamp = int(now.timestamp()) + int(duration_seconds)

        data = {
            "exp": exp_timestamp,  # 这里存储 Unix 时间戳
            "email": self.email,
            "org_code": self.org_code,
            "org_id": self.org_id,
            "job_code": job_code,
        }

        return jwt.encode(data, DISPATCH_JWT_SECRET, algorithm=DISPATCH_JWT_ALG)

    @property
    def token(self):
        return self.generate_token(duration_seconds=DISPATCH_JWT_EXP)

    def principals(self):
        return [f"user:{self.email}", f"role:{[i.name for i in self.role]}"]


class UserBase(BaseResponseModel):
    email: str = Field(
        default=None,
        title="username or email",
        description="The username to login. Though name is email, it may not be email format.",
    )
    is_active: bool = False

    @field_validator("email")
    def email_required(cls, v:str, info: ValidationInfo) -> str:
        if not v:
            raise ValueError("Must not be empty string and must be a email")
        return v


class UserLogin(UserBase):
    password: str

    @field_validator("password")
    def password_required(cls, v:str, info: ValidationInfo) -> str:
        if not v:
            raise ValueError("Must not be empty string")
        return v


class UserRegister(UserLogin):
    id: Optional[int] = None
    password: Optional[str] 
    role: Optional[List[int]] = []
    mill: Optional[List[int]] = []
    org_id: int = None
    org_code: str = None
    en_code: Optional[str]=None

    # managed_teams: Optional[List[TeamRead]] = []
    is_active: bool = False
    is_org_owner: bool = False
    is_team_owner: bool = False
    is_team_worker: bool = False
    default_team_id: Optional[int] = None
    current_mill_id: Optional[int] = None
    current_mill_code: Optional[str] = None
    current_menu_path: Optional[str] = "/"
    full_name:  Optional[str] = None
    import_sample_data: str = "no_data"
    planner_code: str = "single_planner"

    show_bottom_note: Optional[bool] = True
    """
    org_code: Optional[str]
    is_org_owner: Optional[bool]
    """

    @field_validator("password", mode="before")
    def password_required(cls, v:str, info: ValidationInfo) -> str:
        # we generate a password for those that don't have one
        password = v or generate_password()
        return hash_password(password)


class UserLoginResponse(BaseResponseModel):
    token: Optional[str]
    is_first_login: int = 0
    instance_id: str = None
    org_id:int = 0
    role: Optional[List[RoleRead]] = []
    org_code:Optional[str] = None
    default_team_id:Optional[int] = None
    current_mill_id:Optional[int] = None
    current_mill_code: Optional[str] = None
    current_menu_path: Optional[str] = "/"
    userToken:Optional[str] = None

    


class UserRead(UserBase):
    id: int
    org_id: int
    org_code: str
    default_team_id: Optional[int] = None
    current_mill_id: Optional[int] = None
    current_mill_code: Optional[str] = None
    current_menu_path: Optional[str] = "/"
    is_org_owner: bool
    is_team_owner: bool
    thumbnail_photo_url: Optional[str]
    full_name: Optional[str]
    role: Optional[List['RoleRead']] = []
    show_bottom_note: Optional[bool] = True
    # mill: Optional[List['MillRead']] = []
    # managed_teams: Optional[List[TeamRead]] = []


# class UserReadInternal(UserRead):
#     managed_team_ids: List[int] = []
#     # password: Optional[str]
#     # token


class UserUpdate(DispatchBase):

    id: int
    role: Optional[List[int]] = []
    mill: Optional[List[int]] = []
    default_team_id: int = None
    current_mill_id: Optional[int] = None
    current_mill_code: Optional[str] = None
    current_menu_path: Optional[str] = "/"
    email: Optional[str] = None
    password: Optional[str] = None
    old_password: Optional[str] = None
    # managed_teams: Optional[List[TeamRead]] = []
    is_active: bool = False
    org_id: Optional[int] = None
    org_code: Optional[str] = None
    show_bottom_note: Optional[bool] = True

    def password_required(cls, v):
        # we generate a password for those that don't have one
        password = v or generate_password()
        return hash_password(password)


class UserRegisterResponse(DispatchBase):
    email: str
    org_code: str
    default_team_id: int
    current_mill_id: int
    current_mill_code: Optional[str] = None
    is_org_owner: bool
    role: Optional[List[RoleRead]] = []


class UserPagination(DispatchBase):
    total: int
    items: List[UserRead] = []


class DispatchUserOrganization(Base, TimeStampMixin):
    __table_args__ = {"schema": "dispatch_core"}
    dispatch_user_id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, primary_key=True)
    role = Column(String, default=UserRoles.WORKER)
    team_id = Column(Integer)
    worker_code =Column(String)


class LoginRespones(DispatchBase):
   status:int

   message:str='succeed'
   data:Optional[UserLoginResponse]=None
   result:str='success' 


class MenuButtonPermission(DispatchBase):
    id: Optional[int]=None,
    name: Optional[str]="",
    path:  Optional[str]="",
    component_name:  Optional[str]="",
    permission:  Optional[str]="",
    remark:  Optional[str]="",

class UserPermissionRead(DispatchBase): 
    permission: Optional[List[MenuButtonPermission]] = []
    menu: Optional[List[MenuConfig]] = []

class UserPassWordUpdate(DispatchBase):

    id: int
    password: Optional[str] = None
    old_password: Optional[str] = None

    def password_required(cls, v):
        # we generate a password for those that don't have one
        password = v or generate_password()
        return hash_password(password)

 