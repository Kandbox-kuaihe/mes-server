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

finished_product_load_cut_sequence_plan = Table(
    'fp_load_csp', Base.metadata,
    Column('finished_product_load_id', Integer, ForeignKey('load.id')),
    Column('cut_sequence_plan_id', Integer, ForeignKey('cut_sequence_plan.id')),
    PrimaryKeyConstraint('finished_product_load_id', 'cut_sequence_plan_id'),
)
