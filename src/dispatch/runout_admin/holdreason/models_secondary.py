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


finished_product_hold = Table('finished_product_hold', Base.metadata,
    Column('finished_product_id', Integer, ForeignKey('finished_product.id'), nullable=False),
    Column('hold_reason_id', Integer, ForeignKey('hold_reason.id'), nullable=False),
    Column('mill_id', Integer, ForeignKey('mill.id'), nullable=False),
    Column('hold_by', String, nullable=False),
    Column('comment', String),
    PrimaryKeyConstraint('finished_product_id', 'hold_reason_id')

)
 
