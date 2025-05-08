
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Table,
    PrimaryKeyConstraint

)

from dispatch.database import Base 



children_spec_table = Table('children_spec_table', Base.metadata,
    Column('spec_id', Integer, ForeignKey('spec.id')),
    Column('children_spen_id', Integer, ForeignKey('spec.id')),
    PrimaryKeyConstraint('spec_id', 'children_spen_id')
)
 


 