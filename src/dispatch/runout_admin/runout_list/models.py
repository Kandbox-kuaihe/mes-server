from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    String,
    BigInteger,
    Integer,
    DateTime
)

from typing import  Optional

from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel,BaseResponseNoExtraModel

from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from dispatch.product_type.models import ProductTypeRead
from dispatch.rolling.rolling_list.models import RollingRead
from dispatch.semi_admin.semi.models import SemiRead
from dispatch.cast.models import CastRead


class Runout(Base,TimeStampMixin):
    __tablename__ = 'runout'

    id = Column(BigInteger, primary_key=True,autoincrement=True)
    rolling_id = Column(BigInteger, ForeignKey('rolling.id'), nullable=True) # It should be nullable=False
    rolling = relationship("Rolling", backref="rolling_runout")
    
    runout_code = Column(String, nullable=False)
    runout_desc = Column(String)
    product_code = Column(String)
    furnace_sequence_number = Column(String)

    semi_id = Column(BigInteger, ForeignKey('semi.id'))
    semi = relationship("Semi", backref="semi_runout")
    
    cast_id = Column(BigInteger, ForeignKey("cast.id"), nullable=True, )
    cast = relationship("Cast", backref="cast_runout")
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=False, )
    mill = relationship("Mill", backref="mill_Runout")    
    
    concast_code = Column(String)
    cold_length_mm = Column(Numeric(20, 10))
    quality_code = Column(String)
    shift_code = Column(String)
    nose_crop_length_mm = Column(Numeric(20, 10))
    tail_crop_length_mm = Column(Numeric(20, 10))
    cutting_loss_length_mm = Column(Numeric(20, 10))
    scrap_number = Column(Numeric(20, 10))
    scrap_detail = Column(String)
    scrap_defect_reason_code = Column(String)
    scrap_length_mm = Column(Numeric(20, 10))
    runout_cutting_date = Column(DateTime)
    cut_count = Column(Integer)
    
    runout_length = Column(Numeric(20, 10))
    runout_weight = Column(Numeric(20, 10))
    rolling_code = Column(String)
    semi_code = Column(String)

    nominal_f1 = Column(Numeric(precision=20, scale=10))
    actual_f1 = Column(Numeric(precision=20, scale=10))
    nominal_f2 = Column(Numeric(precision=20, scale=10))
    actual_f2 = Column(Numeric(precision=20, scale=10))
    nominal_f3 = Column(Numeric(precision=20, scale=10))
    actual_f3 = Column(Numeric(precision=20, scale=10))
    nominal_f4 = Column(Numeric(precision=20, scale=10))
    actual_f4 = Column(Numeric(precision=20, scale=10))
    nominal_fh1 = Column(Numeric(precision=20, scale=10))
    actual_fh1 = Column(Numeric(precision=20, scale=10))
    nominal_fh2 = Column(Numeric(precision=20, scale=10))
    actual_fh2 = Column(Numeric(precision=20, scale=10))
    nominal_fh3 = Column(Numeric(precision=20, scale=10))
    actual_fh3 = Column(Numeric(precision=20, scale=10))
    nominal_fh4 = Column(Numeric(precision=20, scale=10))
    actual_fh4 = Column(Numeric(precision=20, scale=10))
    nominal_b1 = Column(Numeric(precision=20, scale=10))
    actual_b1 = Column(Numeric(precision=20, scale=10))
    nominal_b2 = Column(Numeric(precision=20, scale=10))
    actual_b2 = Column(Numeric(precision=20, scale=10))
    nominal_d = Column(Numeric(precision=20, scale=10))
    actual_d = Column(Numeric(precision=20, scale=10))
    nominal_weight = Column(Numeric(precision=20, scale=10))
    calculated_weight = Column(Numeric(precision=20, scale=10))
    difference = Column(Numeric(precision=20, scale=10))
    off_centre_web = Column(Numeric(precision=20, scale=10))
    flange_variation = Column(Numeric(precision=20, scale=10))
    information_to_banks = Column(String)

    product_type_id = Column(BigInteger, ForeignKey("product_type.id"), nullable=True, )
    product_type = relationship("ProductType", backref="product_type_runout")

    actual_web_thick = Column(Numeric(precision=20, scale=10))
    actual_web_thick_1 = Column(Numeric(precision=20, scale=10))
    actual_web_thick_2 = Column(Numeric(precision=20, scale=10))
    actual_web_thick_3 = Column(Numeric(precision=20, scale=10))
    sample_position = Column(String)   ## N=Nose, M=mid, T=tail
    weight_error_kgm = Column(Numeric(precision=20, scale=10))
    source = Column(String)      ## source (runout), values 0 = MANUAL, 1 = AUTOMATIC
    tol_hold = Column(String)    ## tol_hold (runout), values 1 or 2 not passed so bars need holding, 0 = passed 
    tol_table = Column(String)
    tolnumber = Column(String)
    auto_end_use_flag = Column(String)

    search_vector = Column(
        TSVectorType(
            "runout_code",
            "product_code",
            weights={"runout_code": "A", "product_code": "B"},
        )
    )

    __table_args__ = (
        UniqueConstraint('runout_code', name='unique_key_runout_code'),
    )


class RunoutBase(BaseResponseNoExtraModel):
    rolling_id: Optional[int] = None
    runout_code: Optional[str] = None
    runout_desc: Optional[str] = None
    product_code: Optional[str] = None
    furnace_sequence_number: Optional[str] = None
    semi_id: Optional[int] = None
    cast_id: Optional[int]=None 
    concast_code: Optional[str] = None
    cold_length_mm: Optional[float] = None
    quality_code: Optional[str] = None
    shift_code: Optional[str] = None
    nose_crop_length_mm: Optional[float] = None
    tail_crop_length_mm: Optional[float] = None
    cutting_loss_length_mm: Optional[float] = None
    scrap_number: Optional[float] = None
    scrap_detail: Optional[str] = None
    scrap_defect_reason_code: Optional[str] = None
    scrap_length_mm: Optional[float] = None
    runout_cutting_date: Optional[datetime] = None
    cut_count: Optional[int] = None
    
    runout_length: Optional[float] = None
    runout_weight: Optional[float] = None 
    rolling_code: Optional[str] = None
    semi_code: Optional[str] = None 
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None

    nominal_f1: Optional[float] = None
    actual_f1: Optional[float] = None
    nominal_f2: Optional[float] = None
    actual_f2: Optional[float] = None
    nominal_f3: Optional[float] = None
    actual_f3: Optional[float] = None
    nominal_f4: Optional[float] = None
    actual_f4: Optional[float] = None
    nominal_fh1: Optional[float] = None
    actual_fh1: Optional[float] = None
    nominal_fh2: Optional[float] = None
    actual_fh2: Optional[float] = None
    nominal_fh3: Optional[float] = None
    actual_fh3: Optional[float] = None
    nominal_fh4: Optional[float] = None
    actual_fh4: Optional[float] = None
    nominal_b1: Optional[float] = None
    actual_b1: Optional[float] = None
    nominal_b2: Optional[float] = None
    actual_b2: Optional[float] = None
    nominal_d: Optional[float] = None
    actual_d: Optional[float] = None
    nominal_weight: Optional[float] = None
    calculated_weight: Optional[float] = None
    difference: Optional[float] = None
    off_centre_web: Optional[float] = None
    flange_variation: Optional[float] = None
    information_to_banks: Optional[str] = None

    product_type_id: Optional[int] = None

    actual_web_thick : Optional[float] = None
    actual_web_thick_1 : Optional[float] = None
    actual_web_thick_2 : Optional[float] = None
    actual_web_thick_3 : Optional[float] = None
    sample_position : Optional[str] = None 
    weight_error_kgm : Optional[float] = None
    source : Optional[str] = None  
    tol_hold : Optional[str] = None    
    tol_table: Optional[str] = None
    tolnumber : Optional[str] = None
    auto_end_use_flag :Optional[str] = None

class RunoutCreate(RunoutBase,BaseResponseModel):
    pass


class RunoutUpdate(RunoutBase,BaseResponseModel):
    pass


class RunoutRead(RunoutBase):
    id: int
    semi: Optional[SemiRead] = None
    rolling: Optional[RollingRead] = None
    cast: Optional[CastRead] = None
    product_type: Optional[ProductTypeRead] = None


class RunoutPagination(DispatchBase):
    total: int
    items: List[RunoutRead] = []
    itemsPerPage: int
    page : int