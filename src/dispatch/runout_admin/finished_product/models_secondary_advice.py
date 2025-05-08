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

finished_product_advice = Table('finished_product_advice', Base.metadata,
                              Column('finished_product_id', Integer, ForeignKey('finished_product.id')),
                              Column('advice_id', Integer, ForeignKey('advice.id')),
                              # Column('mill_id', Integer, ForeignKey('mill.id')),
                              # Column('hold_by', String),
                              # Column('comment', String),

                              PrimaryKeyConstraint('finished_product_id', 'advice_id')


                              )

