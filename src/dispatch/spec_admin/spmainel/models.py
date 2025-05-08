from typing import List, Optional
from pydantic import  Field

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    String,
    BigInteger,
    Integer,
    Boolean
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

from dispatch.spec_admin.spec.models import SpecRead
from dispatch.spec_admin.spmainel_other_element.models import SpmainelOtherElementRead


# (Base,TimeStampMixin):

class Spmainel(Base,TimeStampMixin):
    __tablename__ = 'spmainel'
    id = Column(BigInteger, primary_key=True,autoincrement=True)
    spec_id = Column(BigInteger, ForeignKey("spec.id"), nullable=False, )
    spec = relationship("Spec", backref="spec_spmainel")
    mill_id = Column(BigInteger, ForeignKey("mill.id"), nullable=True, )
    mill = relationship("Mill", backref="mill_Spmainel")
    type = Column(String, default="Main", nullable=False) #Type
    is_active = Column(Boolean, default=False)  # job vs absence
    thick_from = Column(Numeric(20, 10), nullable=False) #Thickness From
    thick_to = Column(Numeric(20, 10), nullable=False) #Thickness To
    location = Column(String(1)) #Location
    main_el_min_value_c = Column(Numeric(20, 10), nullable=False) #Carbon (C)
    main_el_max_value_c = Column(Numeric(20, 10), nullable=False)
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
    main_el_min_value_p = Column(Numeric(20, 10), nullable=False) #Phosphorus (P)
    main_el_max_value_p = Column(Numeric(20, 10), nullable=False)
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

    main_el_min_value_sal = Column(Numeric(20, 10)) #SOL AL(sol_al)
    main_el_max_value_sal = Column(Numeric(20, 10))
    anal_ind_sal = Column(String(1))
    opt_ind_sal = Column(String(1))
    uom_sal = Column(String(1))
    precision_sal = Column(Integer)

    main_el_min_value_sp = Column(Numeric(20, 10)) #S&P (sp)
    main_el_max_value_sp = Column(Numeric(20, 10))
    anal_ind_sp = Column(String(1))
    opt_ind_sp = Column(String(1))
    uom_sp = Column(String(1))
    precision_sp = Column(Integer)


    main_el_min_value_as = Column(Numeric(20, 10)) #AS (as)
    main_el_max_value_as = Column(Numeric(20, 10))
    anal_ind_as = Column(String(1))
    opt_ind_as = Column(String(1))
    uom_as = Column(String(1))
    precision_as = Column(Integer)
    main_el_min_value_bi = Column(Numeric(20, 10)) #Bi (bi)
    main_el_max_value_bi = Column(Numeric(20, 10))
    anal_ind_bi = Column(String(1))
    opt_ind_bi = Column(String(1))
    uom_bi = Column(String(1))
    precision_bi = Column(Integer)
    main_el_min_value_ce = Column(Numeric(20, 10)) #Ce (ce)
    main_el_max_value_ce = Column(Numeric(20, 10))
    anal_ind_ce = Column(String(1))
    opt_ind_ce = Column(String(1))
    uom_ce = Column(String(1))
    precision_ce = Column(Integer)
    main_el_min_value_o = Column(Numeric(20, 10)) #O (o)
    main_el_max_value_o = Column(Numeric(20, 10))
    anal_ind_o = Column(String(1))
    opt_ind_o = Column(String(1))
    uom_o = Column(String(1))
    precision_o = Column(Integer)
    main_el_min_value_pb = Column(Numeric(20, 10)) #Pb (pb)
    main_el_max_value_pb = Column(Numeric(20, 10))
    anal_ind_pb = Column(String(1))
    opt_ind_pb = Column(String(1))
    uom_pb = Column(String(1))
    precision_pb = Column(Integer)
    main_el_min_value_sb = Column(Numeric(20, 10)) #Sb (sb)
    main_el_max_value_sb = Column(Numeric(20, 10))
    anal_ind_sb = Column(String(1))
    opt_ind_sb = Column(String(1))
    uom_sb = Column(String(1))
    precision_sb = Column(Integer)
    main_el_min_value_w = Column(Numeric(20, 10)) #W (w)
    main_el_max_value_w = Column(Numeric(20, 10))
    anal_ind_w = Column(String(1))
    opt_ind_w = Column(String(1))
    uom_w = Column(String(1))
    precision_w = Column(Integer)
    main_el_min_value_zn = Column(Numeric(20, 10)) #Zn (zn)
    main_el_max_value_zn = Column(Numeric(20, 10))
    anal_ind_zn = Column(String(1))
    opt_ind_zn = Column(String(1))
    uom_zn = Column(String(1))
    precision_zn = Column(Integer)
    main_el_min_value_zr = Column(Numeric(20, 10)) #Zr (zr)
    main_el_max_value_zr = Column(Numeric(20, 10))
    anal_ind_zr = Column(String(1))
    opt_ind_zr = Column(String(1))
    uom_zr = Column(String(1))
    precision_zr = Column(Integer)
    main_el_min_value_te = Column(Numeric(20, 10)) #Te (te)
    main_el_max_value_te = Column(Numeric(20, 10))
    anal_ind_te = Column(String(1))
    opt_ind_te = Column(String(1))
    uom_te = Column(String(1))
    precision_te = Column(Integer)
    main_el_min_value_rad = Column(Numeric(20, 10)) #Rad (rad)
    main_el_max_value_rad = Column(Numeric(20, 10))
    anal_ind_rad = Column(String(1))
    opt_ind_rad = Column(String(1))
    uom_rad = Column(String(1))
    precision_rad = Column(Integer)
    main_el_min_value_insal = Column(Numeric(20, 10)) #Insal (insal)
    main_el_max_value_insal = Column(Numeric(20, 10))
    anal_ind_insal = Column(String(1))
    opt_ind_insal = Column(String(1))
    uom_insal = Column(String(1))
    precision_insal = Column(Integer)
    main_el_min_value_n2 = Column(Numeric(20, 10)) #N2 (n2)
    main_el_max_value_n2 = Column(Numeric(20, 10))
    anal_ind_n2 = Column(String(1))
    opt_ind_n2 = Column(String(1))
    uom_n2 = Column(String(1))
    precision_n2 = Column(Integer)
    
    c_m_ind = Column(String(4))
    
    
    
    code_1 = Column(String(2))
    other_el_min_value_1 = Column(Numeric(20, 10))
    other_el_max_value_1 = Column(Numeric(20, 10))
    code_2 = Column(String(2))
    other_el_min_value_2 = Column(Numeric(20, 10))
    other_el_max_value_2 = Column(Numeric(20, 10))
    code_3 = Column(String(2))
    other_el_min_value_3 = Column(Numeric(20, 10))
    other_el_max_value_3 = Column(Numeric(20, 10))
    code_4 = Column(String(2))
    other_el_min_value_4 = Column(Numeric(20, 10))
    other_el_max_value_4 = Column(Numeric(20, 10))
    code_5 = Column(String(2))
    other_el_min_value_5 = Column(Numeric(20, 10))
    other_el_max_value_5 = Column(Numeric(20, 10))
    code_6 = Column(String(2))
    other_el_min_value_6 = Column(Numeric(20, 10))
    other_el_max_value_6 = Column(Numeric(20, 10))
    code_7 = Column(String(2))
    other_el_min_value_7 = Column(Numeric(20, 10))
    other_el_max_value_7 = Column(Numeric(20, 10))
    code_8 = Column(String(2))
    other_el_min_value_8 = Column(Numeric(20, 10))
    other_el_max_value_8 = Column(Numeric(20, 10))
    code_9 = Column(String(2))
    other_el_min_value_9 = Column(Numeric(20, 10))
    other_el_max_value_9 = Column(Numeric(20, 10))
    option_flag = Column(String(1))
    other_el_opt_1 = Column(String(1))
    other_el_opt_2 = Column(String(1))
    other_el_opt_3 = Column(String(1))
    other_el_opt_4 = Column(String(1))
    other_el_opt_5 = Column(String(1))
    other_el_opt_6 = Column(String(1))
    other_el_opt_7 = Column(String(1))
    other_el_opt_8 = Column(String(1))
    other_el_opt_9 = Column(String(1))
    filler = Column(String(55))


    __table_args__ = (UniqueConstraint('spec_id', 'thick_from', 'thick_to', 'type', name='spmainel_uix_spec_thick_from_to_type'),)


# BaseResponseModel

class SpMainElResponse(BaseResponseModel):
    # spif_spec_code: Optional[str] = None
    # spif_variation_no: Optional[int] = None
    spec: Optional[SpecRead] = None
    spec_id:  Optional[int]=None 
    mill_id: Optional[int] = None
    mill: Optional[MillRead] = None
    type: Optional[str] = None
    
    is_active: Optional[bool] = None

    thick_from: Optional[float] = None
    thick_to: Optional[float] = None
    location: Optional[str] = None
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
    main_el_min_value_sal: Optional[float] = None
    main_el_max_value_sal: Optional[float] = None
    anal_ind_sal: Optional[str] = None
    opt_ind_sal: Optional[str] = None
    uom_sal: Optional[str] = None
    precision_sal: Optional[int] = None
    main_el_min_value_sp: Optional[float] = None
    main_el_max_value_sp: Optional[float] = None
    anal_ind_sp: Optional[str] = None
    opt_ind_sp: Optional[str] = None
    uom_sp: Optional[str] = None
    precision_sp: Optional[int] = None


    main_el_min_value_as: Optional[float] = None
    main_el_max_value_as: Optional[float] = None
    anal_ind_as: Optional[str] = None
    opt_ind_as: Optional[str] = None
    uom_as: Optional[str] = None
    precision_as: Optional[int] = None
    main_el_min_value_bi: Optional[float] = None
    main_el_max_value_bi: Optional[float] = None
    anal_ind_bi: Optional[str] = None
    opt_ind_bi: Optional[str] = None
    uom_bi: Optional[str] = None
    precision_bi: Optional[int] = None
    main_el_min_value_ce: Optional[float] = None
    main_el_max_value_ce: Optional[float] = None
    anal_ind_ce: Optional[str] = None
    opt_ind_ce: Optional[str] = None
    uom_ce: Optional[str] = None
    precision_ce: Optional[int] = None
    main_el_min_value_o: Optional[float] = None
    main_el_max_value_o: Optional[float] = None
    anal_ind_o: Optional[str] = None
    opt_ind_o: Optional[str] = None
    uom_o: Optional[str] = None
    precision_o: Optional[int] = None
    main_el_min_value_pb: Optional[float] = None
    main_el_max_value_pb: Optional[float] = None
    anal_ind_pb: Optional[str] = None
    opt_ind_pb: Optional[str] = None
    uom_pb: Optional[str] = None
    precision_pb: Optional[int] = None
    main_el_min_value_sb: Optional[float] = None
    main_el_max_value_sb: Optional[float] = None
    anal_ind_sb: Optional[str] = None
    opt_ind_sb: Optional[str] = None
    uom_sb: Optional[str] = None
    precision_sb: Optional[int] = None
    main_el_min_value_w: Optional[float] = None
    main_el_max_value_w: Optional[float] = None
    anal_ind_w: Optional[str] = None
    opt_ind_w: Optional[str] = None
    uom_w: Optional[str] = None
    precision_w: Optional[int] = None
    main_el_min_value_zn: Optional[float] = None
    main_el_max_value_zn: Optional[float] = None
    anal_ind_zn: Optional[str] = None
    opt_ind_zn: Optional[str] = None
    uom_zn: Optional[str] = None
    precision_zn: Optional[int] = None
    main_el_min_value_zr: Optional[float] = None
    main_el_max_value_zr: Optional[float] = None
    anal_ind_zr: Optional[str] = None
    opt_ind_zr: Optional[str] = None
    uom_zr: Optional[str] = None
    precision_zr: Optional[int] = None
    main_el_min_value_te: Optional[float] = None
    main_el_max_value_te: Optional[float] = None
    anal_ind_te: Optional[str] = None
    opt_ind_te: Optional[str] = None
    uom_te: Optional[str] = None
    precision_te: Optional[int] = None
    main_el_min_value_rad: Optional[float] = None
    main_el_max_value_rad: Optional[float] = None
    anal_ind_rad: Optional[str] = None
    opt_ind_rad: Optional[str] = None
    uom_rad: Optional[str] = None
    precision_rad: Optional[int] = None
    main_el_min_value_insal: Optional[float] = None
    main_el_max_value_insal: Optional[float] = None
    anal_ind_insal: Optional[str] = None
    opt_ind_insal: Optional[str] = None
    uom_insal: Optional[str] = None
    precision_insal: Optional[int] = None
    main_el_min_value_n2: Optional[float] = None
    main_el_max_value_n2: Optional[float] = None
    anal_ind_n2: Optional[str] = None
    opt_ind_n2: Optional[str] = None
    uom_n2: Optional[str] = None
    precision_n2: Optional[int] = None
    
    c_m_ind: Optional[str] = None
    code_1: Optional[str] = None
    other_el_min_value_1: Optional[float] = None
    other_el_max_value_1: Optional[float] = None
    code_2: Optional[str] = None
    other_el_min_value_2: Optional[float] = None
    other_el_max_value_2: Optional[float] = None
    code_3: Optional[str] = None
    other_el_min_value_3: Optional[float] = None
    other_el_max_value_3: Optional[float] = None
    code_4: Optional[str] = None
    other_el_min_value_4: Optional[float] = None
    other_el_max_value_4: Optional[float] = None
    code_5: Optional[str] = None
    other_el_min_value_5: Optional[float] = None
    other_el_max_value_5: Optional[float] = None
    code_6: Optional[str] = None
    other_el_min_value_6: Optional[float] = None
    other_el_max_value_6: Optional[float] = None
    code_7: Optional[str] = None
    other_el_min_value_7: Optional[float] = None
    other_el_max_value_7: Optional[float] = None
    code_8: Optional[str] = None
    other_el_min_value_8: Optional[float] = None
    other_el_max_value_8: Optional[float] = None
    code_9: Optional[str] = None
    other_el_min_value_9: Optional[float] = None
    other_el_max_value_9: Optional[float] = None
    option_flag: Optional[str] = None
    other_el_opt_1: Optional[str] = None
    other_el_opt_2: Optional[str] = None
    other_el_opt_3: Optional[str] = None
    other_el_opt_4: Optional[str] = None
    other_el_opt_5: Optional[str] = None
    other_el_opt_6: Optional[str] = None
    other_el_opt_7: Optional[str] = None
    other_el_opt_8: Optional[str] = None
    other_el_opt_9: Optional[str] = None
    filler: Optional[str] = None

    flex_form_data: Optional[dict] = None


# SpecMainEl Response
class SpMainElCreate(SpMainElResponse):
    other_element: List[SpmainelOtherElementRead] = []

class SpMainElUpdate(SpMainElResponse):
    pass

class SpMainElRead(SpMainElResponse):
    id: int  

class SpMainElPagination(DispatchBase):
    total: int
    items: List[SpMainElRead] = []
    itemsPerPage: int
    page: int
    other_element_num: List[int] = []


class SpMainElUpdateNew(DispatchBase):
    id: int
    data: dict


class SpMainElBySpecCode(DispatchBase):
    spec_code: str
    page: int
    itemsPerPage: int

class SpMainElCopyToCode(DispatchBase):
    before_code: str
    after_code: str