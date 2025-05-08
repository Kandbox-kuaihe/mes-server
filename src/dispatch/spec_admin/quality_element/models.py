from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey,Numeric
from sqlalchemy.orm import relationship
from typing import List, Optional
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel
from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel
from dispatch.spec_admin.quality.models import QualityRead
from dispatch.spec_admin.quality_other_element.models import QualityOtherElementRead
from pydantic import Field
class QualityElement(Base, TimeStampMixin):
    __tablename__ = 'quality_element'

    id = Column(Integer, primary_key=True)
    quality_id = Column(Integer, ForeignKey('quality.id'), nullable=False)
    quality = relationship("Quality", backref="quality_element_quality")
    type = Column(String, nullable=False)
    code = Column(String)
    is_active = Column(Boolean, nullable=False)
    thick_from = Column(Integer)
    thick_to = Column(Integer)
    location = Column(String(1))
    main_el_min_value_c = Column(Numeric(20, 10), default=0, nullable=False) #Carbon (C)
    main_el_max_value_c = Column(Numeric(20, 10), default=0, nullable=False)
    anal_ind_c = Column(String(1))
    opt_ind_c = Column(String(1))
    uom_c = Column(String(1))
    precision_c = Column(Integer)
    main_el_min_value_si = Column(Numeric(20, 10)) #Silicon (Si)
    main_el_max_value_si = Column(Numeric(20, 10))
    anal_ind_si = Column(String(1))
    opt_ind_si = Column(String(1))
    uom_si = Column(String(1))
    precision_si = Column(Integer)
    main_el_min_value_mn = Column(Numeric(20, 10)) #Manganese (Mn)
    main_el_max_value_mn = Column(Numeric(20, 10))
    anal_ind_mn = Column(String(1))
    opt_ind_mn = Column(String(1))
    uom_mn = Column(String(1))
    precision_mn = Column(Integer)
    main_el_min_value_p = Column(Numeric(20, 10)) #Phosphorus (P)
    main_el_max_value_p = Column(Numeric(20, 10))
    anal_ind_p = Column(String(1))
    opt_ind_p = Column(String(1))
    uom_p = Column(String(1))
    precision_p = Column(Integer)
    main_el_min_value_s = Column(Numeric(20, 10)) #Sulphur (S)
    main_el_max_value_s = Column(Numeric(20, 10))
    anal_ind_s = Column(String(1))
    opt_ind_s = Column(String(1))
    uom_s = Column(String(1))
    precision_s = Column(Integer)
    main_el_min_value_cr = Column(Numeric(20, 10)) #Chromium (Cr)
    main_el_max_value_cr = Column(Numeric(20, 10))
    anal_ind_cr = Column(String(1))
    opt_ind_cr = Column(String(1))
    uom_cr = Column(String(1))
    precision_cr = Column(Integer)
    main_el_min_value_mo = Column(Numeric(20, 10)) #Molybdenum (Mo)
    main_el_max_value_mo = Column(Numeric(20, 10))
    anal_ind_mo = Column(String(1))
    opt_ind_mo = Column(String(1))
    uom_mo = Column(String(1))
    precision_mo = Column(Integer)
    main_el_min_value_ni = Column(Numeric(20, 10)) #Nickel (Ni)
    main_el_max_value_ni = Column(Numeric(20, 10))
    anal_ind_ni = Column(String(1))
    opt_ind_ni = Column(String(1))
    uom_ni = Column(String(1))
    precision_ni = Column(Integer)
    main_el_min_value_al = Column(Numeric(20, 10)) #Aluminium (Al)
    main_el_max_value_al = Column(Numeric(20, 10))
    anal_ind_al = Column(String(1))
    opt_ind_al = Column(String(1))
    uom_al = Column(String(1))
    precision_al = Column(Integer)
    main_el_min_value_b = Column(Numeric(20, 10)) #Boron (B)
    main_el_max_value_b = Column(Numeric(20, 10))
    anal_ind_b = Column(String(1))
    opt_ind_b = Column(String(1))
    uom_b = Column(String(1))
    precision_b = Column(Integer)
    main_el_min_value_co = Column(Numeric(20, 10)) #Cobalt (Co)
    main_el_max_value_co = Column(Numeric(20, 10))
    anal_ind_co = Column(String(1))
    opt_ind_co = Column(String(1))
    uom_co = Column(String(1))
    precision_co = Column(Integer)
    main_el_min_value_cu = Column(Numeric(20, 10)) #Copper (Cu)
    main_el_max_value_cu = Column(Numeric(20, 10))
    anal_ind_cu = Column(String(1))
    opt_ind_cu = Column(String(1))
    uom_cu = Column(String(1))
    precision_cu = Column(Integer)
    main_el_min_value_nb = Column(Numeric(20, 10)) #Niobium (Nb)
    main_el_max_value_nb = Column(Numeric(20, 10))
    anal_ind_nb = Column(String(1))
    opt_ind_nb = Column(String(1))
    uom_nb = Column(String(1))
    precision_nb = Column(Integer)
    main_el_min_value_sn = Column(Numeric(20, 10)) #Tin (Sn)
    main_el_max_value_sn = Column(Numeric(20, 10))
    anal_ind_sn = Column(String(1))
    opt_ind_sn = Column(String(1))
    uom_sn = Column(String(1))
    precision_sn = Column(Integer)
    main_el_min_value_ti = Column(Numeric(20, 10)) #Titanium (Ti)
    main_el_max_value_ti = Column(Numeric(20, 10))
    anal_ind_ti = Column(String(1))
    opt_ind_ti = Column(String(1))
    uom_ti = Column(String(1))
    precision_ti = Column(Integer)
    main_el_min_value_v = Column(Numeric(20, 10)) #Vanadium (V)
    main_el_max_value_v = Column(Numeric(20, 10))
    anal_ind_v = Column(String(1))
    opt_ind_v = Column(String(1))
    uom_v = Column(String(1))
    precision_v = Column(Integer)
    main_el_min_value_ca = Column(Numeric(20, 10)) #Calium (Ca)
    main_el_max_value_ca = Column(Numeric(20, 10))
    anal_ind_ca = Column(String(1))
    opt_ind_ca = Column(String(1))
    uom_ca = Column(String(1))
    precision_ca = Column(Integer)
    main_el_min_value_n = Column(Numeric(20, 10)) #Nitrogen (N)
    main_el_max_value_n = Column(Numeric(20, 10))
    anal_ind_n = Column(String(1))
    opt_ind_n = Column(String(1))
    uom_n = Column(String(1))
    precision_n = Column(Integer)
    main_el_min_value_h = Column(Numeric(20, 10)) #Hydrogen (H)
    main_el_max_value_h = Column(Numeric(20, 10))
    anal_ind_h = Column(String(1))
    opt_ind_h = Column(String(1))
    uom_h = Column(String(1))
    precision_h = Column(Integer)
    main_el_min_value_sol_al = Column(Numeric(20, 10)) #SOL AL(sol_al)
    main_el_max_value_sol_al = Column(Numeric(20, 10))
    anal_ind_sol_al = Column(String(1))
    opt_ind_sol_al = Column(String(1))
    uom_sol_al = Column(String(1))
    precision_sol_al = Column(Integer)
    main_el_min_value_sp = Column(Numeric(20, 10)) #S&P (sp)
    main_el_max_value_sp = Column(Numeric(20, 10))
    anal_ind_sp = Column(String(1))
    opt_ind_sp = Column(String(1))
    uom_sp = Column(String(1))
    precision_sp = Column(Integer)
    
    

class QualityElementResponse(BaseResponseModel):
    id : Optional[int] = None
    code: Optional[str] = None
    quality_id : Optional[int] = None
    type : Optional[str] = None
    is_active : Optional[bool] = None
    thick_from : Optional[int] = None
    thick_to : Optional[int] = None
    location : Optional[str] = None
    main_el_min_value_c: Optional[float] = None
    main_el_max_value_c: Optional[float] = None
    anal_ind_c: Optional[str] = None
    opt_ind_c: Optional[str] = None
    uom_c: Optional[str] = None
    precision_c: Optional[int] = None
    main_el_min_value_si: Optional[float] = None
    main_el_max_value_si: Optional[float] = None
    anal_ind_si: Optional[str] = None
    opt_ind_si: Optional[str] = None
    uom_si: Optional[str] = None
    precision_si: Optional[int] = None
    main_el_min_value_mn: Optional[float] = None
    main_el_max_value_mn: Optional[float] = None
    anal_ind_mn: Optional[str] = None
    opt_ind_mn: Optional[str] = None
    uom_mn: Optional[str] = None
    precision_mn: Optional[int] = None
    main_el_min_value_p: Optional[float] = None
    main_el_max_value_p: Optional[float] = None
    anal_ind_p: Optional[str] = None
    opt_ind_p: Optional[str] = None
    uom_p: Optional[str] = None
    precision_p: Optional[int] = None
    main_el_min_value_s: Optional[float] = None
    main_el_max_value_s: Optional[float] = None
    anal_ind_s: Optional[str] = None
    opt_ind_s: Optional[str] = None
    uom_s: Optional[str] = None
    precision_s: Optional[int] = None

    main_el_min_value_cr: Optional[float] = None
    main_el_max_value_cr: Optional[float] = None
    anal_ind_cr: Optional[str] = None
    opt_ind_cr: Optional[str] = None
    uom_cr: Optional[str] = None
    precision_cr: Optional[int] = None
    main_el_min_value_mo: Optional[float] = None
    main_el_max_value_mo: Optional[float] = None
    anal_ind_mo: Optional[str] = None
    opt_ind_mo: Optional[str] = None
    uom_mo: Optional[str] = None
    precision_mo: Optional[int] = None
    main_el_min_value_ni: Optional[float] = None
    main_el_max_value_ni: Optional[float] = None
    anal_ind_ni: Optional[str] = None
    opt_ind_ni: Optional[str] = None
    uom_ni: Optional[str] = None
    precision_ni: Optional[int] = None
    main_el_min_value_al: Optional[float] = None
    main_el_max_value_al: Optional[float] = None
    anal_ind_al: Optional[str] = None
    opt_ind_al: Optional[str] = None
    uom_al: Optional[str] = None
    precision_al: Optional[int] = None
    main_el_min_value_b: Optional[float] = None
    main_el_max_value_b: Optional[float] = None
    anal_ind_b: Optional[str] = None
    opt_ind_b: Optional[str] = None
    uom_b: Optional[str] = None
    precision_b: Optional[int] = None
    main_el_min_value_co: Optional[float] = None
    main_el_max_value_co: Optional[float] = None
    anal_ind_co: Optional[str] = None
    opt_ind_co: Optional[str] = None
    uom_co: Optional[str] = None
    precision_co: Optional[int] = None
    main_el_min_value_cu: Optional[float] = None
    main_el_max_value_cu: Optional[float] = None
    anal_ind_cu: Optional[str] = None
    opt_ind_cu: Optional[str] = None
    uom_cu: Optional[str] = None
    precision_cu: Optional[int] = None
    main_el_min_value_nb: Optional[float] = None
    main_el_max_value_nb: Optional[float] = None
    anal_ind_nb: Optional[str] = None
    opt_ind_nb: Optional[str] = None
    uom_nb: Optional[str] = None
    precision_nb: Optional[int] = None
    main_el_min_value_sn: Optional[float] = None
    main_el_max_value_sn: Optional[float] = None
    anal_ind_sn: Optional[str] = None
    opt_ind_sn: Optional[str] = None
    uom_sn: Optional[str] = None
    precision_sn: Optional[int] = None
    main_el_min_value_ti: Optional[float] = None
    main_el_max_value_ti: Optional[float] = None
    anal_ind_ti: Optional[str] = None
    opt_ind_ti: Optional[str] = None
    uom_ti: Optional[str] = None
    precision_ti: Optional[int] = None
    main_el_min_value_v: Optional[float] = None
    main_el_max_value_v: Optional[float] = None
    anal_ind_v: Optional[str] = None
    opt_ind_v: Optional[str] = None
    uom_v: Optional[str] = None
    precision_v: Optional[int] = None
    main_el_min_value_ca: Optional[float] = None
    main_el_max_value_ca: Optional[float] = None
    anal_ind_ca: Optional[str] = None
    opt_ind_ca: Optional[str] = None
    uom_ca: Optional[str] = None
    precision_ca: Optional[int] = None
    main_el_min_value_n: Optional[float] = None
    main_el_max_value_n: Optional[float] = None
    anal_ind_n: Optional[str] = None
    opt_ind_n: Optional[str] = None
    uom_n: Optional[str] = None
    precision_n: Optional[int] = None
    main_el_min_value_h: Optional[float] = None
    main_el_max_value_h: Optional[float] = None
    anal_ind_h: Optional[str] = None
    opt_ind_h: Optional[str] = None
    uom_h: Optional[str] = None
    precision_h: Optional[int] = None
    main_el_min_value_sol_al: Optional[float] = None
    main_el_max_value_sol_al: Optional[float] = None
    anal_ind_sol_al: Optional[str] = None
    opt_ind_sol_al: Optional[str] = None
    uom_sol_al: Optional[str] = None
    precision_sol_al: Optional[int] = None
    main_el_min_value_sp: Optional[float] = None
    main_el_max_value_sp: Optional[float] = None
    anal_ind_sp: Optional[str] = None
    opt_ind_sp: Optional[str] = None
    uom_sp: Optional[str] = None
    precision_sp: Optional[int] = None
    quality_other_element: Optional[List[QualityOtherElementRead]] = []



class QualityElementUpdate(QualityElementResponse):
    pass

class QualityElementRead(QualityElementResponse):
    quality: Optional[QualityRead] = None
    
class QualityElementCreate(QualityElementResponse):
    pass
    
    
    
class QualityElementPagination(DispatchBase):
    total: int
    items: List[QualityElementRead] = []
    itemsPerPage: int
    page: int
