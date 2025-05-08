from typing import List, Optional
from pydantic import  Field

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    String,
    BigInteger,
    Integer,
)
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from sqlalchemy import Column, Integer, CHAR, Text
from pydantic import BaseModel, Field, conint
from typing import Optional, List



# (Base,TimeStampMixin):

from dispatch.spec_admin.spec.models import SpecRead
from dispatch.spec_admin.spprodan_other_element.models import SpprodanOtherElementRead


class Spprodan(Base,TimeStampMixin):

    __tablename__ = 'spprodan'

    id = Column(BigInteger, primary_key=True,autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey("mill.id"), )
    mill = relationship("Mill", backref="mill_Spprodan")
    
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=False, )
    spec = relationship("Spec", backref="spec_spprodan")

    thick_from = Column(Numeric(20, 10), nullable=False)
    thick_to = Column(Numeric(20, 10), nullable=False)
    location = Column(String(1), nullable=False)

    cev_min = Column(Numeric(20, 10))
    cev_max = Column(Numeric(20, 10))
    cev_value = Column(Numeric(20, 10))
    
    main_el_min_val_c = Column(Numeric(20, 10), nullable=False) #Carbon (C)
    main_el_max_val_c = Column(Numeric(20, 10), nullable=False)
    precision_c = Column(Integer)
    main_el_min_val_si = Column(Numeric(20, 10), nullable=False) #Silicon (Si)
    main_el_max_val_si = Column(Numeric(20, 10), nullable=False)
    precision_si = Column(Integer, nullable=True)
    main_el_min_val_mn = Column(Numeric(20, 10), nullable=False) #Manganese (Mn)
    main_el_max_val_mn = Column(Numeric(20, 10), nullable=False)
    precision_mn = Column(Integer, nullable=True)
    main_el_min_val_p = Column(Numeric(20, 10), nullable=False) #Phosphorus (P)
    main_el_max_val_p = Column(Numeric(20, 10), nullable=False)
    precision_p = Column(Integer, nullable=True)
    main_el_min_val_s = Column(Numeric(20, 10), nullable=False) #Sulphur (S)
    main_el_max_val_s = Column(Numeric(20, 10), nullable=False)
    precision_s = Column(Integer, nullable=True)
    main_el_min_val_cr = Column(Numeric(20, 10), nullable=False) #Chromium (Cr)
    main_el_max_val_cr = Column(Numeric(20, 10), nullable=False)
    precision_cr = Column(Integer, nullable=True)
    main_el_min_val_mo = Column(Numeric(20, 10), nullable=False) #Molybdenum (Mo)
    main_el_max_val_mo = Column(Numeric(20, 10), nullable=False)
    precision_mo = Column(Integer, nullable=True)
    main_el_min_val_ni = Column(Numeric(20, 10), nullable=False) #Nickel (Ni)
    main_el_max_val_ni = Column(Numeric(20, 10), nullable=False)
    precision_ni = Column(Integer, nullable=True)
    main_el_min_val_al = Column(Numeric(20, 10), nullable=False) #Aluminium (Al)
    main_el_max_val_al = Column(Numeric(20, 10), nullable=False)
    precision_al = Column(Integer, nullable=True)
    main_el_min_val_b = Column(Numeric(20, 10), nullable=False) #Boron (B)
    main_el_max_val_b = Column(Numeric(20, 10), nullable=False)
    precision_b = Column(Integer, nullable=True)
    main_el_min_val_co = Column(Numeric(20, 10), nullable=False) #Cobalt (Co)
    main_el_max_val_co = Column(Numeric(20, 10), nullable=False)
    precision_co = Column(Integer, nullable=True)
    main_el_min_val_cu = Column(Numeric(20, 10), nullable=False) #Copper (Cu)
    main_el_max_val_cu = Column(Numeric(20, 10), nullable=False)
    precision_cu = Column(Integer, nullable=True)
    main_el_min_val_nb = Column(Numeric(20, 10), nullable=False) #Niobium (Nb)
    main_el_max_val_nb = Column(Numeric(20, 10), nullable=False)
    precision_nb = Column(Integer, nullable=True)
    main_el_min_val_sn = Column(Numeric(20, 10), nullable=False) #Tin (Sn)
    main_el_max_val_sn = Column(Numeric(20, 10), nullable=False)
    precision_sn = Column(Integer, nullable=True)
    main_el_min_val_ti = Column(Numeric(20, 10), nullable=False) #Titanium (Ti)
    main_el_max_val_ti = Column(Numeric(20, 10), nullable=False)
    precision_ti = Column(Integer, nullable=True)
    main_el_min_val_v = Column(Numeric(20, 10), nullable=False) #Vanadium (V)
    main_el_max_val_v = Column(Numeric(20, 10), nullable=False)
    precision_v = Column(Integer, nullable=True)
    main_el_min_val_ca = Column(Numeric(20, 10), nullable=False) #Calium (Ca)
    main_el_max_val_ca = Column(Numeric(20, 10), nullable=False)
    precision_ca = Column(Integer, nullable=True)
    main_el_min_val_n = Column(Numeric(20, 10), nullable=False) #Nitrogen (N)
    main_el_max_val_n = Column(Numeric(20, 10), nullable=False)
    precision_n = Column(Integer, nullable=True)
    main_el_min_val_h = Column(Numeric(20, 10), nullable=False) #Hydrogen (H)
    main_el_max_val_h = Column(Numeric(20, 10), nullable=False)
    precision_h = Column(Integer, nullable=True)
    main_el_min_val_sol_al = Column(Numeric(20, 10), nullable=True) # SOL AL (sol_al)
    main_el_max_val_sol_al = Column(Numeric(20, 10), nullable=True)
    precision_sol_al = Column(Integer, nullable=True)
    main_el_min_val_sp = Column(Numeric(20, 10), nullable=True) #S&P (sp)
    main_el_max_val_sp = Column(Numeric(20, 10), nullable=True)
    precision_sp = Column(Integer, nullable=True)


    main_el_min_val_as = Column(Numeric(20, 10), nullable=True) #AS (as)
    main_el_max_val_as = Column(Numeric(20, 10), nullable=True)
    precision_as = Column(Integer, nullable=True)
    main_el_min_val_bi = Column(Numeric(20, 10), nullable=True) #Bi (bi)
    main_el_max_val_bi = Column(Numeric(20, 10), nullable=True)
    precision_bi = Column(Integer, nullable=True)
    main_el_min_val_ce = Column(Numeric(20, 10), nullable=True) #Ce (ce)
    main_el_max_val_ce = Column(Numeric(20, 10), nullable=True)
    precision_ce = Column(Integer, nullable=True)
    main_el_min_val_o = Column(Numeric(20, 10), nullable=True) #O (o)
    main_el_max_val_o = Column(Numeric(20, 10), nullable=True)
    precision_o = Column(Integer, nullable=True)
    main_el_min_val_pb = Column(Numeric(20, 10), nullable=True) #Pb (pb)
    main_el_max_val_pb = Column(Numeric(20, 10), nullable=True)
    precision_pb = Column(Integer, nullable=True)
    main_el_min_val_sb = Column(Numeric(20, 10), nullable=True) #Sb (sb)
    main_el_max_val_sb = Column(Numeric(20, 10), nullable=True)
    precision_sb = Column(Integer, nullable=True)
    main_el_min_val_w = Column(Numeric(20, 10), nullable=True) #W (w)
    main_el_max_val_w = Column(Numeric(20, 10), nullable=True)
    precision_w = Column(Integer, nullable=True)
    main_el_min_val_zn = Column(Numeric(20, 10), nullable=True) #Zn (zn)
    main_el_max_val_zn = Column(Numeric(20, 10), nullable=True)
    precision_zn = Column(Integer, nullable=True)
    main_el_min_val_zr = Column(Numeric(20, 10), nullable=True) #Zr (zr)
    main_el_max_val_zr = Column(Numeric(20, 10), nullable=True)
    precision_zr = Column(Integer, nullable=True)
    main_el_min_val_te = Column(Numeric(20, 10), nullable=True) #Te (te)
    main_el_max_val_te = Column(Numeric(20, 10), nullable=True)
    precision_te = Column(Integer, nullable=True)
    main_el_min_val_rad = Column(Numeric(20, 10), nullable=True) #Rad (rad)
    main_el_max_val_rad = Column(Numeric(20, 10), nullable=True)
    precision_rad = Column(Integer, nullable=True)
    main_el_min_val_insal = Column(Numeric(20, 10), nullable=True) #Insal (insal)
    main_el_max_val_insal = Column(Numeric(20, 10), nullable=True)
    precision_insal = Column(Integer, nullable=True)
    main_el_min_val_n2 = Column(Numeric(20, 10), nullable=True) #N2 (n2)
    main_el_max_val_n2 = Column(Numeric(20, 10), nullable=True)
    precision_n2 = Column(Integer, nullable=True)
    
    code_1 = Column(String(2), nullable=True)
    other_el_min_val_1 = Column(Numeric(20, 10), nullable=True)
    other_el_max_val_1 = Column(Numeric(20, 10), nullable=True)
    code_2 = Column(String(2), nullable=True)
    other_el_min_val_2 = Column(Numeric(20, 10), nullable=True)
    other_el_max_val_2 = Column(Numeric(20, 10), nullable=True)
    code_3 = Column(String(2), nullable=True)
    other_el_min_val_3 = Column(Numeric(20, 10), nullable=True)
    other_el_max_val_3 = Column(Numeric(20, 10), nullable=True)
    code_4 = Column(String(2), nullable=True)
    other_el_min_val_4 = Column(Numeric(20, 10), nullable=True)
    other_el_max_val_4 = Column(Numeric(20, 10), nullable=True)
    code_5 = Column(String(2), nullable=True)
    other_el_min_val_5 = Column(Numeric(20, 10), nullable=True)
    other_el_max_val_5 = Column(Numeric(20, 10), nullable=True)
    code_6 = Column(String(2), nullable=True)
    other_el_min_val_6 = Column(Numeric(20, 10), nullable=True)
    other_el_max_val_6 = Column(Numeric(20, 10), nullable=True)
    code_7 = Column(String(2), nullable=True)
    other_el_min_val_7 = Column(Numeric(20, 10), nullable=True)
    other_el_max_val_7 = Column(Numeric(20, 10), nullable=True)
    code_8 = Column(String(2), nullable=True)
    other_el_min_val_8 = Column(Numeric(20, 10), nullable=True)
    other_el_max_val_8 = Column(Numeric(20, 10), nullable=True)
    code_9 = Column(String(2), nullable=True)
    other_el_min_val_9 = Column(Numeric(20, 10), nullable=True)
    other_el_max_val_9 = Column(Numeric(20, 10), nullable=True)
    deviation_flag = Column(String(1), nullable=False)
    prod_cev_form = Column(String(1), nullable=False)
    prod_cev_value = Column(Integer, nullable=False)
    filler = Column(String(46), nullable=False)

    __table_args__ = (UniqueConstraint('spec_id', 'thick_from', 'thick_to', name='spprodan_uix_spec_thick_from_to'),)



# BaseResponseModel

class SpprodanResponse(BaseResponseModel):

    spec: Optional[SpecRead] = None
    spec_id:  Optional[int]=None 

    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    thick_from: Optional[float] = None
    thick_to: Optional[float] = None
    location: Optional[str] = None
    
    cev_min: Optional[float] = None
    cev_max: Optional[float] = None
    cev_value: Optional[float] = None
    
    main_el_min_val_c: Optional[float] = None
    main_el_max_val_c: Optional[float] = None
    precision_c: Optional[int] = None
    main_el_min_val_si: Optional[float] = None
    main_el_max_val_si: Optional[float] = None
    precision_si: Optional[int] = None
    main_el_min_val_mn: Optional[float] = None
    main_el_max_val_mn: Optional[float] = None
    precision_mn: Optional[int] = None
    main_el_min_val_p: Optional[float] = None
    main_el_max_val_p: Optional[float] = None
    precision_p: Optional[int] = None
    main_el_min_val_s: Optional[float] = None
    main_el_max_val_s: Optional[float] = None
    precision_s: Optional[int] = None
    main_el_min_val_cr: Optional[float] = None
    main_el_max_val_cr: Optional[float] = None
    precision_cr: Optional[int] = None
    main_el_min_val_mo: Optional[float] = None
    main_el_max_val_mo: Optional[float] = None
    precision_mo: Optional[int] = None
    main_el_min_val_ni: Optional[float] = None
    main_el_max_val_ni: Optional[float] = None
    precision_ni: Optional[int] = None
    main_el_min_val_al: Optional[float] = None
    main_el_max_val_al: Optional[float] = None
    precision_al: Optional[int] = None
    main_el_min_val_b: Optional[float] = None
    main_el_max_val_b: Optional[float] = None
    precision_b: Optional[int] = None
    main_el_min_val_co: Optional[float] = None
    main_el_max_val_co: Optional[float] = None
    precision_co: Optional[int] = None
    main_el_min_val_cu: Optional[float] = None
    main_el_max_val_cu: Optional[float] = None
    precision_cu: Optional[int] = None
    main_el_min_val_nb: Optional[float] = None
    main_el_max_val_nb: Optional[float] = None
    precision_nb: Optional[int] = None
    main_el_min_val_sn: Optional[float] = None
    main_el_max_val_sn: Optional[float] = None
    precision_sn: Optional[int] = None
    main_el_min_val_ti: Optional[float] = None
    main_el_max_val_ti: Optional[float] = None
    precision_ti: Optional[int] = None
    main_el_min_val_v: Optional[float] = None
    main_el_max_val_v: Optional[float] = None
    precision_v: Optional[int] = None
    main_el_min_val_ca: Optional[float] = None
    main_el_max_val_ca: Optional[float] = None
    precision_ca: Optional[int] = None
    main_el_min_val_n: Optional[float] = None
    main_el_max_val_n: Optional[float] = None
    precision_n: Optional[int] = None
    main_el_min_val_h: Optional[float] = None
    main_el_max_val_h: Optional[float] = None
    precision_h: Optional[int] = None
    main_el_min_val_sol_al: Optional[float] = None
    main_el_max_val_sol_al: Optional[float] = None
    precision_sol_al: Optional[int] = None
    main_el_min_val_sp: Optional[float] = None
    main_el_max_val_sp: Optional[float] = None
    precision_sp: Optional[int] = None


    main_el_min_val_as: Optional[float] = None
    main_el_max_val_as: Optional[float] = None
    precision_as: Optional[int] = None
    main_el_min_val_bi: Optional[float] = None
    main_el_max_val_bi: Optional[float] = None
    precision_bi: Optional[int] = None
    main_el_min_val_ce: Optional[float] = None
    main_el_max_val_ce: Optional[float] = None
    precision_ce: Optional[int] = None
    main_el_min_val_o: Optional[float] = None
    main_el_max_val_o: Optional[float] = None
    precision_o: Optional[int] = None
    main_el_min_val_pb: Optional[float] = None
    main_el_max_val_pb: Optional[float] = None
    precision_pb: Optional[int] = None
    main_el_min_val_sb: Optional[float] = None
    main_el_max_val_sb: Optional[float] = None
    precision_sb: Optional[int] = None
    main_el_min_val_w: Optional[float] = None
    main_el_max_val_w: Optional[float] = None
    precision_w: Optional[int] = None
    main_el_min_val_zn: Optional[float] = None
    main_el_max_val_zn: Optional[float] = None
    precision_zn: Optional[int] = None
    main_el_min_val_zr: Optional[float] = None
    main_el_max_val_zr: Optional[float] = None
    precision_zr: Optional[int] = None
    main_el_min_val_te: Optional[float] = None
    main_el_max_val_te: Optional[float] = None
    precision_te: Optional[int] = None
    main_el_min_val_rad: Optional[float] = None
    main_el_max_val_rad: Optional[float] = None
    precision_rad: Optional[int] = None
    main_el_min_val_insal: Optional[float] = None
    main_el_max_val_insal: Optional[float] = None
    precision_insal: Optional[int] = None
    main_el_min_val_n2: Optional[float] = None
    main_el_max_val_n2: Optional[float] = None
    precision_n2: Optional[int] = None
    
    code_1: Optional[str] = None
    other_el_min_val_1: Optional[float] = None
    other_el_max_val_1: Optional[float] = None
    code_2: Optional[str] = None
    other_el_min_val_2: Optional[float] = None
    other_el_max_val_2: Optional[float] = None
    code_3: Optional[str] = None
    other_el_min_val_3: Optional[float] = None
    other_el_max_val_3: Optional[float] = None
    code_4: Optional[str] = None
    other_el_min_val_4: Optional[float] = None
    other_el_max_val_4: Optional[float] = None
    code_5: Optional[str] = None
    other_el_min_val_5: Optional[float] = None
    other_el_max_val_5: Optional[float] = None
    code_6: Optional[str] = None
    other_el_min_val_6: Optional[float] = None
    other_el_max_val_6: Optional[float] = None
    code_7: Optional[str] = None
                                 
    other_el_min_val_7 : Optional[float] = None
    other_el_max_val_7: Optional[float] = None
    code_8 : Optional[str] = None
    other_el_min_val_8: Optional[float] = None
    other_el_max_val_8: Optional[float] = None
    code_9 : Optional[str] = None
    other_el_min_val_9: Optional[float] = None
    other_el_max_val_9 : Optional[float] = None
    deviation_flag: Optional[str] = None
    prod_cev_form: Optional[str] = None
    prod_cev_value : Optional[int] = None
    filler : Optional[str] = None

# Spprodan Response
class SpprodanCreate(SpprodanResponse):
    other_element: List[SpprodanOtherElementRead] = []

class SpprodanUpdate(SpprodanResponse):
    pass

class SpprodanRead(SpprodanResponse):
    id: Optional[int] = None



class SpprodanPagination(DispatchBase):
    total: int
    items: List[SpprodanRead] = []
    itemsPerPage: int
    page: int
    other_element_num: List[int] = []

class SpprodanUpdateNew(DispatchBase):
    id: int
    data: dict


class SpprodanBySpecCode(DispatchBase):
    spec_code: str
    page: int
    itemsPerPage: int


class SpprodanCopyToCode(DispatchBase):
    before_code: str
    after_code: str