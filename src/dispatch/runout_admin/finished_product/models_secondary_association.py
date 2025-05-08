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

finished_product_association = Table('finished_product_association', Base.metadata,
                              Column('finished_product_id', Integer, ForeignKey('finished_product.id')),
                              Column('finished_product_association_id', Integer, ForeignKey('finished_product.id')),


                              PrimaryKeyConstraint('finished_product_id', 'finished_product_association_id')

                              )

