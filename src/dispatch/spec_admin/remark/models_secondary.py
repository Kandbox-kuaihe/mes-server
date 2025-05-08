from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Table,
    String,
    DateTime,
    JSON,
)
from datetime import datetime

from dispatch.database import Base
from dispatch.models import TimeStampMixin

spec_remark_table = Table('spec_remark', Base.metadata,
                             Column('id', Integer, primary_key=True, autoincrement=True),
                             Column('spec_id', Integer, ForeignKey('spec.id'), nullable=False),
                             Column('remark_id', Integer, ForeignKey('remark.id')),
                             Column('remark_type', String, nullable=False),
                             Column('spec_text_type', String),
                             Column('text', String),

                            # TimeStampMixin columns with creation order
                            Column('updated_by', String),
                            Column('updated_at', DateTime, default=datetime.utcnow),
                            Column('created_at', DateTime, default=datetime.utcnow),
                            Column('created_by', String),
                            Column('is_deleted', Integer, nullable=True, default=0),
                            Column('flex_form_data', JSON, default={})
                             )


