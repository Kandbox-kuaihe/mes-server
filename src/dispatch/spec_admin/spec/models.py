from typing import List, Optional, Any
from pydantic import Field

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    String,
    BigInteger,
    Integer,
    Boolean,
)
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from sqlalchemy import Column, Integer, CHAR, Text, DateTime
from pydantic import BaseModel, Field, conint
from typing import Optional, List
from dispatch.spec_admin.inspector.models_secondary import spec_inspector_table
from dispatch.spec_admin.inspector.models import InspectorRead
from dispatch.spec_admin.spec.models_secondary import children_spec_table
from dispatch.spec_admin.tolerance.models import ToleranceRead
from dispatch.spec_admin.remark.models import Remark
from dispatch.spec_admin.remark.models_secondary import spec_remark_table

class Spec(Base, TimeStampMixin):
    __tablename__ = "spec"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    mill_id = Column(
        BigInteger,
        ForeignKey("mill.id"),
        nullable=False,
    )
    mill = relationship("Mill", backref="mill_spec")

    spec_code = Column(String(255), nullable=False)
    
    
    test_type_flag = Column(String(6))
    
    test_sub_type = Column(String(6))
    
    
    variation_no = Column(Integer)
    date_created = Column(Integer)
    date_amended = Column(String(6))
    full_name = Column(String(255))
    summary_name = Column(String(255))
    short_name = Column(String(255))
    bmqc_name = Column(String(12))

    dim_f1 = Column(Numeric(precision=20, scale=10))  # 或者使用 Decimal(20, 10)
    dim_f2 = Column(Numeric(precision=20, scale=10))  # 或者使用 Decimal(20, 10)
    dim_f3 = Column(Numeric(precision=20, scale=10))  # 或者使用 Decimal(20, 10)
    dim_f4 = Column(Numeric(precision=20, scale=10))  # 或者使用 Decimal(20, 10)
    dim_b1 = Column(Numeric(precision=20, scale=10))  # 或者使用 Decimal(20, 10)
    dim_b2 = Column(Numeric(precision=20, scale=10))  # 或者使用 Decimal(20, 10)

    end_use = Column(String(5))
    test_freq = Column(String(5))
    inspector_1 = Column(String(5))
    inspector_2 = Column(String(5))
    premise_name = Column(String(6))
    alt_spec_code = Column(String(5), server_default="")
    other_test_1 = Column(String(4))
    other_test_2 = Column(String(4))
    other_test_3 = Column(String(4))
    ultrasonic = Column(String(4))
    man_chk_remark = Column(String(30))
    quality_group = Column(String(2))
    quality_code = Column(String(255))
    cost_code = Column(String(4))
    spec_units = Column(String(1))
    cev_opt = Column(String(1))
    impact_opt = Column(String(1))
    analysis_opt = Column(String(1))
    shelton_code = Column(String(3))
    inspector_3 = Column(String(5))
    inspector_4 = Column(String(5))
    bend_diam = Column(Integer)
    equiv_spec_1 = Column(String(5))
    equiv_spec_2 = Column(String(5))
    equiv_spec_3 = Column(String(5))
    dim_units = Column(String(1))
    rods_roll_type = Column(String(1))
    hsm_qual_code = Column(String(4))
    msm_qual_code = Column(String(4))
    edi_indicator = Column(Integer)
    piling_quality_code = Column(String(4))
    special_qty_cls = Column(String(1))
    test_piece_code = Column(String(1))
    fecc_qual_category = Column(String(4))
    source_type = Column(String(4))
    filler = Column(String(4))

    section_code = Column(String(5))
    eid_req = Column(String(5))
    quality_ind = Column(String(5))
    cert_units = Column(String(5))
    bend_test_dia = Column(String(5))

    type = Column(String(200))
    sub_type = Column(String(5))

    inspector = relationship("Inspector", secondary=spec_inspector_table, back_populates="spec")
    remark = relationship("Remark", secondary=spec_remark_table, back_populates="spec")
    version = Column(Integer, default=1)
    version_status = Column(String(5), default="D")
    release_date = Column(DateTime)
    archive_date = Column(DateTime)
    
    children_specs = relationship("Spec",
                                secondary=children_spec_table,
                                primaryjoin=id == children_spec_table.c.spec_id,
                                secondaryjoin=id == children_spec_table.c.children_spen_id)
    
    stock_test_flag = Column(String(5))
    test_type = Column(String(5))
    test_subtype = Column(String(255))
    tolerance_id = Column(BigInteger, ForeignKey("tolerance.id"), nullable=True)
    tolerance = relationship("Tolerance", backref="tolerance_spec")

    specification_text = Column(Text)
    editors_notes = Column(Text)

    srsm_spec_code = Column(String)

    cd_cust = Column(String)
    cd_cust_type = Column(String)
    tx_cust = Column(String)
    cd_cust_site = Column(String)
    cd_code01 = Column(String)
    cd_code02 = Column(String)
    cd_code03 = Column(String)
    ext_grade_obs = Column(String)

    standard = Column(String)
    thick_from = Column(Numeric(precision=20, scale=10))
    thick_to = Column(Numeric(precision=20, scale=10))

    active_status = Column(String)
    supply = Column(String) #srsm  supply Condit
    rail_status = Column(String) #srsm  Rail Spec Y/N
    deox = Column(String) #srsm  Deox
    prod_ladle = Column(String) #srsm  Prod Ladle

    suspended = Column(Boolean, default=False)
    manual_cert = Column(String(1),default="N")
    



    search_vector = Column(
        TSVectorType(
            "spec_code","short_name","full_name",
            weights={"spec_code": "A","short_name":"B","full_name":"C"},
        )
    )

    __table_args__ = (UniqueConstraint('spec_code', 'version', 'mill_id','alt_spec_code', name='unique_spec_code_version'),)


from dispatch.mill.models import MillRead
class SpecResponse(BaseResponseModel):
    # spec: Optional[SpecRead] = None
    variation_no: Optional[int] = None
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    spec_code: Optional[str] = None
    
    test_type_flag: Optional[str] = None
    test_sub_type: Optional[str] = None
    
    date_created: Optional[int] = None
    date_amended: Optional[str] = None
    full_name: Optional[str] = None
    summary_name: Optional[str] = None
    short_name: Optional[str] = None
    bmqc_name: Optional[str] = None

    dim_f1: Optional[float] = None
    dim_f2: Optional[float] = None
    dim_f3: Optional[float] = None
    dim_f4: Optional[float] = None
    dim_b1: Optional[float] = None
    dim_b2: Optional[float] = None

    end_use: Optional[str] = None
    test_freq: Optional[str] = None
    inspector_1: Optional[str] = None
    inspector_2: Optional[str] = None
    premise_name: Optional[str] = None
    alt_spec_code: Optional[str] = None
    other_test_1: Optional[str] = None
    other_test_2: Optional[str] = None
    other_test_3: Optional[str] = None
    ultrasonic: Optional[str] = None
    man_chk_remark: Optional[str] = None
    quality_group: Optional[str] = None
    quality_code: Optional[str] = None
    cost_code: Optional[str] = None
    spec_units: Optional[str] = None
    cev_opt: Optional[str] = None
    impact_opt: Optional[str] = None
    analysis_opt: Optional[str] = None
    shelton_code: Optional[str] = None
    inspector_3: Optional[str] = None
    inspector_4: Optional[str] = None
    bend_diam: Optional[int] = None
    equiv_spec_1: Optional[str] = None
    equiv_spec_2: Optional[str] = None
    equiv_spec_3: Optional[str] = None
    dim_units: Optional[str] = None
    rods_roll_type: Optional[str] = None
    hsm_qual_code: Optional[str] = None
    msm_qual_code: Optional[str] = None
    edi_indicator: Optional[int] = None
    piling_quality_code: Optional[str] = None
    special_qty_cls: Optional[str] = None
    test_piece_code: Optional[str] = None
    fecc_qual_category: Optional[str] = None
    source_type: Optional[str] = None
    filler: Optional[str] = None

    section_code: Optional[str] = None
    eid_req: Optional[str] = None
    quality_ind: Optional[str] = None
    cert_units: Optional[str] = None
    bend_test_dia: Optional[str] = None

    type: Optional[str] = None
    sub_type: Optional[str] = None

    version: Optional[int] = None
    version_status: Optional[str] = None
    release_date: Optional[datetime] = None
    archive_date: Optional[datetime] = None
    
    #srsm
    cd_cust: Optional[str] = None
    cd_cust_type: Optional[str] = None
    tx_cust: Optional[str] = None
    cd_cust_site: Optional[str] = None
    cd_code01: Optional[str] = None
    cd_code02: Optional[str] = None
    cd_code03: Optional[str] = None
    ext_grade_obs: Optional[str] = None
    

    stock_test_flag: Optional[str] = None
    test_type: Optional[str] = None
    test_subtype: Optional[str] = None
    tolerance_id: Optional[int] = None
    tolerance: Optional[ToleranceRead] = None

    specification_text: Optional[str] = None
    editors_notes: Optional[str] = None

    srsm_spec_code: Optional[str] = None

    standard: Optional[str] = None
    thick_from: Optional[float] = None
    thick_to: Optional[float] = None

    active_status: Optional[str] = None
    supply: Optional[str] = None
    rail_status: Optional[str] = None
    deox: Optional[str] = None
    prod_ladle: Optional[str] = None

    flex_form_data: Optional[dict] = None

    suspended: Optional[bool] = None

    
class SpecCreate(SpecResponse):
    inspector: Optional[List[Any]] = []
    children_specs: Optional[List[Any]] = []
    redio_type: Optional[str] = None


class SpecUpdate(SpecResponse):
    inspector: Optional[List[Any]] = []
    children_specs: Optional[List[Any]] = []


class SpecRead(SpecResponse):
    id: int
    inspector: Optional[List['InspectorRead']] = []
    children_specs: Optional[List['SpecRead']] = []

class SpecReadCode(SpecResponse):
    spec_code: str

class SpecPagination(DispatchBase):
    total: int
    items: List[SpecRead] = []
    itemsPerPage: int
    page: int


class SpecUpdateNew(DispatchBase):
    id: int
    data: dict

class SpecByCode(DispatchBase):
    code: str
    page: int
    itemsPerPage: int

class SpecVersion(DispatchBase):
    id: int

class ChildrenSelect(DispatchBase):
    id: int
    code: str
    name: str
    
class ChildrenSelectRespone(DispatchBase):
    options: Optional[List[ChildrenSelect]] = []