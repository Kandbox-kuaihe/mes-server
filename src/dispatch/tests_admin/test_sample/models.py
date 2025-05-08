from typing import List, Optional

from pydantic import Field
from sqlalchemy import BigInteger, Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.area.models import AreaRead
from dispatch.cast.models import CastRead
from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import BaseResponseModel, DispatchBase, TimeStampMixin
from dispatch.rolling.rolling_list.models import RollingRead
from dispatch.runout_admin.finished_product.models import FinishedProductRead
from dispatch.runout_admin.runout_list.models import RunoutRead
from dispatch.spec_admin.spec.models import SpecRead
from dispatch.spec_admin.inspector.models import InspectorRead
from dispatch.tests_admin.impact_test_card.models import TestImpact, TestImpactRead
from dispatch.tests_admin.tensile_test_card.models import TestTensile, TestTensileRead
from datetime import datetime

class TestSample(Base,TimeStampMixin):
    __tablename__ = 'test_sample'
    
    id = Column(BigInteger, primary_key=True,autoincrement=True)
    test_sample_code = Column(String, nullable=False)
    test_sample_part = Column(String, nullable=True)
    product_name = Column(String, nullable=True) 
    runout_id = Column(BigInteger, ForeignKey('runout.id'), nullable=False)
    runout = relationship("Runout", backref="test_sample_runout")
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False)
    mill = relationship("Mill", backref="mill_TestSample") 
    cast_id = Column(BigInteger, ForeignKey("cast.id"), nullable=True)
    cast = relationship("Cast", backref="cast_test_sample")
    
    
    concast_code = Column(String)  # Optional, hence no 'nullable=True'
    sample_thickness = Column(Numeric(20, 10), nullable=True)
    sample_info = Column(String(60))
    retest = Column(String(1), default=0, nullable=False)
    orientation = Column(String(1), nullable=True)
    standard = Column(String(4), nullable=True)
    inspector_id = Column(BigInteger, ForeignKey("inspector.id"), nullable=True )
    inspector = relationship("Inspector", backref="inspector_test_sample")
    
    spec_details = Column(String, nullable=True)
    # spec_code= Column(String, nullable=True)
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=True, )
    spec = relationship("Spec", backref="spec_test_sample")
    spec_name= Column(String, nullable=True)
    spec_desc= Column(String, nullable=True)
    status= Column(String, nullable=True)

    flange_sample1 = Column(String(1), nullable=True)
    flange_thickness1 = Column(String(5), nullable=True)
    flange_sample2 = Column(String(1), nullable=True)
    flange_thickness2 = Column(String(5), nullable=True)
    web_sample = Column(String(1), nullable=True)
    web_thickness = Column(String(5), nullable=True)

    area_id = Column(BigInteger, ForeignKey('area.id'))
    area = relationship("Area", backref="area_test_sample")
    comment= Column(String, nullable=True)
    reason_code= Column(String, nullable=True)
    source= Column(String, nullable=True)
    size_mm= Column(BigInteger, nullable=True)

    test_sample_no = Column(String, nullable=True)
    rolling_id = Column(BigInteger, ForeignKey('rolling.id'), nullable=True) # It should be nullable=False in the future after rolling problems being solved
    rolling = relationship("Rolling", backref="rolling_test_sample")
    finished_product_id = Column(BigInteger, ForeignKey('finished_product.id'), nullable=True)
    finished_product = relationship("FinishedProduct", backref="finished_product_test_sample")
    cut_code = Column(String)
    ref_code = Column(String)

    product_type_id = Column(BigInteger, ForeignKey("product_type.id"))
    product_type = relationship("ProductType", backref="product_type_test_sample")

    search_vector = Column(
        TSVectorType(
            "test_sample_code",
            weights={"test_sample_code": "A"},
        )
    )


class TestSampleBase(BaseResponseModel):
    runout_id: Optional[int] = None

    test_sample_code: Optional[str] = None
    test_sample_part: Optional[str] = None
    product_name: Optional[str] = None
    mill_id: Optional[int] = None
    cast_id: Optional[int]=None 
    inspector_id: Optional[int] = None
    concast_code: Optional[str] = None
    sample_thickness: Optional[float] = None
    sample_info: Optional[str] = None
    retest: Optional[str] = None
    orientation: Optional[str] = None
    standard: Optional[str] = None
    spec_details: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None

    
    flange_sample1 :  Optional[str] = None
    flange_thickness1 :  Optional[str] = None
    flange_sample2 :  Optional[str] = None
    flange_thickness2 :  Optional[str] = None
    web_sample :  Optional[str] = None
    web_thickness :  Optional[str] = None

    spec_id:  Optional[int]=None 
    spec_name: Optional[str] = None
    spec_desc: Optional[str] = None

    area_id: Optional[int] = None
    comment: Optional[str] = None
    reason_code: Optional[str] = None
    size_mm:  Optional[int] = None

    test_sample_no: Optional[str] = None
    rolling_id: Optional[int] = None
    finished_product_id: Optional[int] = None
    cut_code: Optional[str] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    ref_code: Optional[str] = None


class TestSampleCreate(TestSampleBase):
    id: Optional[int] = None



class TestSampleUpdate(TestSampleBase):
    id: Optional[int] = None


class TestSampleRead(TestSampleBase):


    id: Optional[int] = None
    mill: Optional[MillRead] = None
    area: Optional[AreaRead] = None
    cast: Optional[CastRead] = None 
    spec: Optional[SpecRead] = None
    runout: Optional[RunoutRead] = None 
    inspector: Optional[InspectorRead] = None
    finished_product: Optional[FinishedProductRead]=None
    rolling: Optional[RollingRead] = None
    flange_thickness1: Optional[str] = None
    web_thickness: Optional[str] = None
    impacts: Optional[List[TestImpactRead]] = None
    tensiles: Optional[List[TestTensileRead]] = None



class TestSamplePagination(DispatchBase):
    total: int
    items: List[TestSampleRead] = Field(default_factory=list)
    itemsPerPage: int
    page : int