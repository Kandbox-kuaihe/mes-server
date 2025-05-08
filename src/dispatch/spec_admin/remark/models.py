from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import DispatchBase, TimeStampMixin
from dispatch.spec_admin.remark.models_secondary import spec_remark_table

# from dispatch.spec_admin.spec.models import SpecRead


class Remark(Base, TimeStampMixin):
    """
    Model for remarks.
    """
    

    id = Column(Integer, primary_key=True, autoincrement=True)
    mill_id = Column(Integer, ForeignKey('mill.id'), nullable=False)  # Assuming 'mill' is the referenced table
    mill = relationship("Mill", foreign_keys=[mill_id])

    code = Column(String, nullable=False)
    type = Column(String, nullable=True)
    group = Column(String, nullable=True)
    name = Column(String, nullable=True)
    desc = Column(String, nullable=True)
    spec = relationship("Spec", secondary=spec_remark_table, back_populates="remark")

    __table_args__ = (
        UniqueConstraint('code', 'group', name='unique_key_remark_code_group'),
    )

    search_vector = Column(
        TSVectorType(
            "code",
            "type",
            "name",
            weights={"code": "A", "type": "B", "name": "C"},
        )
    )


# Pydantic models...

class RemarkBase(DispatchBase):
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    code: Optional[str] = None
    type: Optional[str] = None
    group: Optional[str] = None
    name: Optional[str] = None
    desc: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RemarkCreate(RemarkBase):
    updated_by: Optional[str] = None
    mill_id: Optional[int] = None

class RemarkUpdate(RemarkBase):
    updated_by: Optional[str] = None
    mill_id: Optional[int] = None


class RemarkRead(RemarkBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class RemarkPagination(DispatchBase):
    total: int
    items: List[RemarkRead] = []
    itemsPerPage: int
    page: int


class SpecRemarkBase(DispatchBase):
    spec_id: Optional[int] = None
    remark_id: Optional[int] = None
    remark: Optional[RemarkRead] = None
    spec: Optional[Any] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SpecRemarkRead(SpecRemarkBase):
    pass

class SpecRemarkCreate(SpecRemarkBase):
    spec_id: int
    remark_id: int


class EditorNotesCreate(SpecRemarkBase):
    spec_id: Optional[int] = None
    remark_id: Optional[int] = None
    text: Optional[str] = None
    remark_type: str = "e"


class EditorNotesRead(EditorNotesCreate):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SpecTextCreate(SpecRemarkBase):
    spec_id: Optional[int] = None
    remark_id: Optional[int] = None
    text: Optional[str] = None
    spec_text_type: Optional[str] = None
    remark_type: str = "s"


class SpecTextRead(SpecTextCreate):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None