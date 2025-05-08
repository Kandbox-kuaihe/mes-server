
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Table,
    PrimaryKeyConstraint
)

from dispatch.database import Base 



spec_inspector_table = Table('spec_inspector', Base.metadata,
    Column('spec_id', Integer, ForeignKey('spec.id')),
    Column('inspector_id', Integer, ForeignKey('inspector.id')),
    PrimaryKeyConstraint('spec_id','inspector_id'),
)
 


 