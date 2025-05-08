from enum import Enum

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Integer,
    Boolean,
    ForeignKey,
    Table,
    PrimaryKeyConstraint,
    insert
)

from sqlalchemy.sql.schema import UniqueConstraint

from dispatch.database import Base

finished_product_load = Table('fp_load', Base.metadata,
                              Column('finished_product_id', Integer, ForeignKey('finished_product.id')),
                              Column('finished_product_load_id', Integer, ForeignKey('load.id')),
                              # Column('mill_id', Integer, ForeignKey('mill.id')),
                              # Column('hold_by', String),
                              # Column('comment', String),

                             PrimaryKeyConstraint('finished_product_id', 'finished_product_load_id'),

                              )