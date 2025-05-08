
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Table,
    PrimaryKeyConstraint
)


from dispatch.database import Base 




role_dispatch_user_table = Table('role_user', Base.metadata,
    Column('dispatch_user_id', Integer, ForeignKey('dispatch_core.dispatch_user.id')),
    Column('role_id', Integer, ForeignKey('role.id')),
    PrimaryKeyConstraint('dispatch_user_id', 'role_id')
)
 

user_mill_table = Table('user_mill', Base.metadata,
    Column('mill_id', Integer, ForeignKey('mill.id')),
    Column('dispatch_user_id', Integer, ForeignKey('dispatch_core.dispatch_user.id')),
    PrimaryKeyConstraint('mill_id', 'dispatch_user_id')
)

 