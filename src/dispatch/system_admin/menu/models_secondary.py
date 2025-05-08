from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Integer,
    Boolean,
    ForeignKey,
    Table,
    PrimaryKeyConstraint
)
from typing import Optional

from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base 
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel 
from sqlalchemy.orm import relationship




role_menu_table = Table('role_menu', Base.metadata,
    Column('menu_id', Integer, ForeignKey('menu.id')),
    Column('role_id', Integer, ForeignKey('role.id')),
    PrimaryKeyConstraint('menu_id', 'role_id')
)
 

role_menu_button_table = Table('role_menu_button', Base.metadata,
    Column('menu_button_id', Integer, ForeignKey('menu_button.id')),
    Column('role_id', Integer, ForeignKey('role.id')),
    PrimaryKeyConstraint('menu_button_id', 'role_id')
)
 