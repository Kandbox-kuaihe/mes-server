from enum import Enum

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

from sqlalchemy.sql.schema import UniqueConstraint

from dispatch.database import Base 


semi_hold = Table('semi_hold', Base.metadata,
    Column('semi_id', Integer, ForeignKey('semi.id')),
    Column('hold_reason_id', Integer, ForeignKey('semi_hold_reason.id'), nullable=False),
    Column('mill_id', Integer, ForeignKey('mill.id'), nullable=False),
    Column('hold_by', String, nullable=False),
    Column('comment', String),
    PrimaryKeyConstraint('semi_id', 'hold_reason_id')

)
 
