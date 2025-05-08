from datetime import datetime
from typing import List, Optional,Dict

from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, Integer, String, event, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declared_attr
from dispatch import config
from sqlalchemy.dialects.postgresql import UUID

# SQLAlchemy models...
class TimeStampMixin(object):
    """ Timestamping mixin"""

    updated_by = Column(String)
    updated_by._creation_order = 9999
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_at._creation_order = 9998

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at._creation_order = 9997
    created_by = Column(String)
    created_by._creation_order = 9996

    is_deleted = Column(Integer, nullable=True,default=0) 
    is_deleted._creation_order = 9995

    flex_form_data = Column(
        JSON, default={}
    )
    flex_form_data._creation_order = 9994

    # @staticmethod
    # def _updated_at(mapper, connection, target):
    #     target.updated_at = datetime.utcnow()

    # @classmethod
    # def __declare_last__(cls):
    #     event.listen(cls, "before_update", cls._updated_at)


class EventMixin(TimeStampMixin):
    """ Contact mixin"""
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    source = Column(String)
    description = Column(String)
    details = Column(String)
    flex_form_data = Column(JSON, default={})



class ResourceMixin(TimeStampMixin):
    """Resource mixin."""

    resource_type = Column(String)
    resource_id = Column(String)
    weblink = Column(String)

    @declared_attr
    def job_code(cls):  # noqa
        return Column(String, ForeignKey("job.code"))


# Pydantic models...
class DispatchBase(BaseModel):
    class Config:
        # orm_mode = True
        from_attributes = True
        validate_assignment = True
        arbitrary_types_allowed = True
        # arbitrary_types_allowed = True

        # 延迟构建 https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.defer_build
        defer_build = True


class ContactBase(DispatchBase):
    email: str
    name: Optional[str] = None
    is_active: Optional[bool] = True
    is_external: Optional[bool] = False
    company: Optional[str] = None
    contact_type: Optional[str] = None
    notes: Optional[str] = None
    owner: Optional[str] = None


class PluginOptionModel(DispatchBase):
    pass


# self referential models
class TermNested(DispatchBase):
    id: Optional[int]
    text: str
    # disabling this for now as recursive models break swagger api gen
    # definitions: Optional[List["DefinitionNested"]] = []


class DefinitionNested(DispatchBase):
    id: Optional[int]
    text: str
    terms: Optional[List["TermNested"]] = []


class ServiceNested(DispatchBase):
    pass


class WorkerNested(DispatchBase):
    pass


class TeamNested(DispatchBase):
    pass


class TermReadNested(DispatchBase):
    id: int
    text: str


class DefinitionReadNested(DispatchBase):
    id: int
    text: str


class ServiceReadNested(DispatchBase):
    name: Optional[str] = None
    external_id: Optional[str] = None
    is_active: Optional[bool] = None
    type: Optional[str] = None


class WorkerReadNested(ContactBase):
    id: int
    title: Optional[str] = None
    weblink: Optional[str]
    title: Optional[str]


class TeamReadNested(ContactBase):
    pass


class PolicyReadNested(DispatchBase):
    pass


class BaseResponseModel(DispatchBase):
    updated_at: Optional[datetime] = None

    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    is_deleted: Optional[int] = 0
    flex_form_data: Optional[Dict] = {}

class BaseResponseNoExtraModel(DispatchBase):
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
