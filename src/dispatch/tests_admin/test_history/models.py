import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import Field
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Index, Date
)

from dispatch.database import Base
from dispatch.models import BaseResponseModel, DispatchBase, TimeStampMixin

class TestHistory(Base, TimeStampMixin):
    __tablename__ = "test_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(String, default=uuid.uuid4, nullable=False)
    test_id = Column(BigInteger, ForeignKey("test.id"), nullable=False)
    test_type = Column(String, nullable=False)
    action_type = Column(String, nullable=False)

    update_name = Column(String)
    update_reason = Column(String)

    testing_machine = Column(String)  # card 中的值
    # section = Column(String) #重复
    section_size_code = Column(String)  # test添加 product type
    semi_id = Column(BigInteger)  #semi id 改为 semi
    kgm = Column(Numeric(20, 10)) # product type 带出来，改为 kgm
    # max = Column(Numeric(20, 10))  
    # result = Column(String)
    susp = Column(String) # tensile 尽量全名
    confirm_by = Column(String)
    confirm_at = Column(DateTime)

    # ---Impact---
    temp_c = Column(Numeric(20, 10))
    temp_f = Column(Numeric(20, 10))
    temp_units = Column(String)
    energy_1_j = Column(Numeric(20, 10))
    energy_2_j = Column(Numeric(20, 10))
    energy_3_j = Column(Numeric(20, 10))
    energy_average_j = Column(Numeric(20, 10))
    energy_1_f = Column(Numeric(20, 10))
    energy_2_f = Column(Numeric(20, 10))
    energy_3_f = Column(Numeric(20, 10))
    energy_average_f = Column(Numeric(20, 10))
    shear_1 = Column(Numeric(20, 10))
    shear_2 = Column(Numeric(20, 10))
    shear_3 = Column(Numeric(20, 10))
    shear_average = Column(Numeric(20, 10))
    impact_units = Column(String)
    energy_units = Column(String)
    r1_temp_c = Column(Numeric(20, 10))
    r1_temp_f = Column(Numeric(20, 10))
    r1_energy_1_j = Column(Numeric(20, 10))
    r1_energy_2_j = Column(Numeric(20, 10))
    r1_energy_3_j = Column(Numeric(20, 10))
    r1_energy_average_j = Column(Numeric(20, 10))
    r1_energy_1_f = Column(Numeric(20, 10))
    r1_energy_2_f = Column(Numeric(20, 10))
    r1_energy_3_f = Column(Numeric(20, 10))
    r1_energy_average_f = Column(Numeric(20, 10))
    r1_shear_1 = Column(Numeric(20, 10))
    r1_shear_2 = Column(Numeric(20, 10))
    r1_shear_3 = Column(Numeric(20, 10))
    r1_shear_average = Column(Numeric(20, 10))
    r1_temp_units = Column(String)
    r1_impact_units = Column(String)
    r1_energy_units = Column(String)


    # ---bend---
    heat_treated_by = Column(String)
    tested_by = Column(String)
    result_1 = Column(String)
    result_2 = Column(String)

    # ---cleanness---
    type = Column(String)
    k_number = Column(Numeric(20, 10))
    k_value = Column(Numeric(20, 10))

    # ---hardness---
    bhn_min_max = Column(String)
    ball_size_mm = Column(Numeric(20, 10))  
    load_kg = Column(Numeric(20, 10))
    hardness_1 = Column(Numeric(20, 10))
    hardness_2 = Column(Numeric(20, 10))
    hardness_3 = Column(Numeric(20, 10))
    hardness_4 = Column(Numeric(20, 10))
    hardness_5 = Column(Numeric(20, 10))
    hardness_av = Column(Numeric(20, 10))

    # ---decarburisation---
    decarburisation_min = Column(Numeric(20, 10))
    decarburisation_max = Column(Numeric(20, 10))
    decarburisation = Column(Numeric(20, 10))

    # ---hydrogen---
    spec_test = Column(String)
    rail_grade = Column(String)
    max_test = Column(Numeric(20, 10))


    # ---resistivity---
    max_resistivity = Column(Numeric(20, 10))
    temperature = Column(Numeric(20, 10))
    temp = Column(Numeric(20, 10))
    distance = Column(Numeric(20, 10))
    volt = Column(Numeric(20, 10))
    current = Column(Numeric(20, 10))
    resistivity = Column(Numeric(20, 10))
    humidity = Column(Numeric(20, 10))

    # ---sulphur---
    sulphur_rail_grade = Column(Numeric(20, 10))

    # ---tensile---
    tested_thickness = Column(Numeric(20, 10))
    tested_width = Column(Numeric(20, 10))
    tested_diameter = Column(Numeric(20, 10))
    yield_tt0_5 = Column(Numeric(20, 10))
    yield_high = Column(Numeric(20, 10))
    yield_rp0_2 = Column(Numeric(20, 10))
    yield_low = Column(Numeric(20, 10))
    elongation_code = Column(String)
    elongation_a565 = Column(Numeric(20, 10))
    elongation_a200 = Column(Numeric(20, 10))
    elongation_a50 = Column(Numeric(20, 10))
    elongation_8 = Column(Numeric(20, 10))
    elongation_2 = Column(Numeric(20, 10))
    elongation_a80 = Column(Numeric(20, 10))
    r1_tested_thickness = Column(Numeric(20, 10))
    r1_tested_width = Column(Numeric(20, 10))
    r1_tested_diameter = Column(Numeric(20, 10))
    r1_yield_tt0_5 = Column(Numeric(20, 10))
    r1_yield_high = Column(Numeric(20, 10))
    r1_yield_rp0_2 = Column(Numeric(20, 10))
    r1_yield_low = Column(Numeric(20, 10))
    r1_elongation_code = Column(String)
    r1_elongation_a565 = Column(Numeric(20, 10))
    r1_elongation_a200 = Column(Numeric(20, 10))
    r1_elongation_a50 = Column(Numeric(20, 10))
    r1_elongation_8 = Column(Numeric(20, 10))
    r1_elongation_2 = Column(Numeric(20, 10))
    r1_elongation_a80 = Column(Numeric(20, 10))
    r2_tested_thickness = Column(Numeric(20, 10))
    r2_tested_width = Column(Numeric(20, 10))
    r2_tested_diameter = Column(Numeric(20, 10))
    r2_yield_tt0_5 = Column(Numeric(20, 10))
    r2_yield_high = Column(Numeric(20, 10))
    r2_yield_rp0_2 = Column(Numeric(20, 10))
    r2_yield_low = Column(Numeric(20, 10))
    r2_elongation_code = Column(String)
    r2_elongation_a565 = Column(Numeric(20, 10))
    r2_elongation_a200 = Column(Numeric(20, 10))
    r2_elongation_a50 = Column(Numeric(20, 10))
    r2_elongation_8 = Column(Numeric(20, 10))
    r2_elongation_2 = Column(Numeric(20, 10))
    r2_elongation_a80 = Column(Numeric(20, 10))
    tensile_uts_mpa = Column(Numeric(20, 10))
    r1_tensile_uts_mpa = Column(Numeric(20, 10))
    r2_tensile_uts_mpa = Column(Numeric(20, 10))


    # ---prodan---
    result_c = Column(Numeric(20, 10))
    result_si = Column(Numeric(20, 10))
    result_mn = Column(Numeric(20, 10))
    result_p = Column(Numeric(20, 10))
    result_s = Column(Numeric(20, 10))
    result_cr = Column(Numeric(20, 10))
    result_mo = Column(Numeric(20, 10))
    result_ni = Column(Numeric(20, 10))
    result_al = Column(Numeric(20, 10))
    result_b = Column(Numeric(20, 10))
    result_co = Column(Numeric(20, 10))
    result_cu = Column(Numeric(20, 10))
    result_nb = Column(Numeric(20, 10))
    result_sn = Column(Numeric(20, 10))
    result_ti = Column(Numeric(20, 10))
    result_v = Column(Numeric(20, 10))
    result_ca = Column(Numeric(20, 10))
    result_n2 = Column(Numeric(20, 10))
    result_o = Column(Numeric(20, 10))
    result_h = Column(Numeric(20, 10))
    result_sal = Column(Numeric(20, 10))
    result_as = Column(Numeric(20, 10))
    result_bi = Column(Numeric(20, 10))
    result_ce = Column(Numeric(20, 10))
    result_pb = Column(Numeric(20, 10))
    result_sb = Column(Numeric(20, 10))
    result_w = Column(Numeric(20, 10))
    result_zn = Column(Numeric(20, 10))
    result_zr = Column(Numeric(20, 10))


class TestHistoryBase(BaseResponseModel):
    uuid: Optional[str]

    test_id: Optional[int]
    test_type: Optional[str]
    action_type: Optional[str]

    testing_machine: Optional[str]
    section_size_code: Optional[str]
    semi_id: Optional[int]
    kgm: Optional[float]

    susp: Optional[str]
    update_name: Optional[str] = None
    update_reason: Optional[str] = None
    confirm_by: Optional[str] = None
    confirm_at: Optional[datetime] = None

    # ---Impact---
    temp_c: Optional[float]
    temp_f: Optional[float]
    temp_units: Optional[str]
    energy_1_j: Optional[float]
    energy_2_j: Optional[float]
    energy_3_j: Optional[float]
    energy_average_j: Optional[float]
    energy_1_f: Optional[float]
    energy_2_f: Optional[float]
    energy_3_f: Optional[float]
    energy_average_f: Optional[float]
    shear_1: Optional[float]
    shear_2: Optional[float]
    shear_3: Optional[float]
    shear_average: Optional[float]
    impact_units: Optional[str]
    energy_units: Optional[str]
    r1_temp_c: Optional[float]
    r1_temp_f: Optional[float]
    r1_energy_1_j: Optional[float]
    r1_energy_2_j: Optional[float]
    r1_energy_3_j: Optional[float]
    r1_energy_average_j: Optional[float]
    r1_energy_1_f: Optional[float]
    r1_energy_2_f: Optional[float]
    r1_energy_3_f: Optional[float]
    r1_energy_average_f: Optional[float]
    r1_shear_1: Optional[float]
    r1_shear_2: Optional[float]
    r1_shear_3: Optional[float]
    r1_shear_average: Optional[float]
    r1_temp_units: Optional[str]
    r1_impact_units: Optional[str]
    r1_energy_units: Optional[str]


    # ---bend---
    heat_treated_by: Optional[str]
    tested_by: Optional[str]
    result_1: Optional[str]
    result_2: Optional[str]

    # ---cleanness---
    type: Optional[str]
    k_number: Optional[float]
    k_value: Optional[float]

    # ---hardness---
    bhn_min_max: Optional[str]
    ball_size_mm: Optional[float]
    load_kg: Optional[float]
    hardness_1: Optional[float]
    hardness_2: Optional[float]
    hardness_3: Optional[float]
    hardness_4: Optional[float]
    hardness_5: Optional[float]
    hardness_av: Optional[float]

    # ---decarburisation---
    decarburisation_min: Optional[float]
    decarburisation_max: Optional[float]
    decarburisation: Optional[float]

    # ---hydrogen---
    spec_test: Optional[str]
    rail_grade: Optional[str]
    max_test: Optional[float]


    # ---resistivity---
    max_resistivity: Optional[float]
    temperature: Optional[float]
    temp: Optional[float]
    distance: Optional[float]
    volt: Optional[float]
    current: Optional[float]
    resistivity: Optional[float]
    humidity: Optional[float]

    # ---sulphur---
    sulphur_rail_grade: Optional[float]

    # ---tensile---
    tested_thickness: Optional[float]
    tested_width: Optional[float]
    tested_diameter: Optional[float]
    yield_tt0_5: Optional[float]
    yield_high: Optional[float]
    yield_rp0_2: Optional[float]
    yield_low: Optional[float]
    elongation_code: Optional[str]
    elongation_a565: Optional[float]
    elongation_a200: Optional[float]
    elongation_a50: Optional[float]
    elongation_8: Optional[float]
    elongation_2: Optional[float]
    elongation_a80: Optional[float]
    r1_tested_thickness: Optional[float]
    r1_tested_width: Optional[float]
    r1_tested_diameter: Optional[float]
    r1_yield_tt0_5: Optional[float]
    r1_yield_high: Optional[float]
    r1_yield_rp0_2: Optional[float]
    r1_yield_low: Optional[float]
    r1_elongation_code: Optional[str]
    r1_elongation_a565: Optional[float]
    r1_elongation_a200: Optional[float]
    r1_elongation_a50: Optional[float]
    r1_elongation_8: Optional[float]
    r1_elongation_2: Optional[float]
    r1_elongation_a80: Optional[float]
    r2_tested_thickness: Optional[float]
    r2_tested_width: Optional[float]
    r2_tested_diameter: Optional[float]
    r2_yield_tt0_5: Optional[float]
    r2_yield_high: Optional[float]
    r2_yield_rp0_2: Optional[float]
    r2_yield_low: Optional[float]
    r2_elongation_code: Optional[str]
    r2_elongation_a565: Optional[float]
    r2_elongation_a200: Optional[float]
    r2_elongation_a50: Optional[float]
    r2_elongation_8: Optional[float]
    r2_elongation_2: Optional[float]
    r2_elongation_a80: Optional[float]
    tensile_uts_mpa: Optional[float]
    r1_tensile_uts_mpa: Optional[float]
    r2_tensile_uts_mpa: Optional[float]

    # ---prodan---
    result_c: Optional[float]
    result_si: Optional[float]
    result_mn: Optional[float]
    result_p: Optional[float]
    result_s: Optional[float]
    result_cr: Optional[float]
    result_mo: Optional[float]
    result_ni: Optional[float]
    result_al: Optional[float]
    result_b: Optional[float]
    result_co: Optional[float]
    result_cu: Optional[float]
    result_nb: Optional[float]
    result_sn: Optional[float]
    result_ti: Optional[float]
    result_v: Optional[float]
    result_ca: Optional[float]
    result_n2: Optional[float]
    result_o: Optional[float]
    result_h: Optional[float]
    result_sal: Optional[float]
    result_as: Optional[float]
    result_bi: Optional[float]
    result_ce: Optional[float]
    result_pb: Optional[float]
    result_sb: Optional[float]
    result_w: Optional[float]
    result_zn: Optional[float]
    result_zr: Optional[float]


class TestHistoryCreate(TestHistoryBase):
    pass


class TestHistoryRead(TestHistoryBase):
    id: int


class TestHistoryPagination(DispatchBase):
    total: int
    items: List[TestHistoryRead] = Field(default_factory=list)


class TestHistoryTypeEnum(str, Enum):

    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"


class TestHistoryObjectEnum(Enum):

    impact_object = {"temp_c","temp_f","temp_units","energy_1_j","energy_2_j","energy_3_j","energy_average_j","energy_1_f","energy_2_f",
                    "energy_3_f","energy_average_f","shear_1","shear_2","shear_3","shear_average","impact_units","energy_units","r1_temp_c",
                    "r1_temp_f","r1_energy_1_j","r1_energy_2_j","r1_energy_3_j","r1_energy_average_j","r1_energy_1_f","r1_energy_2_f","r1_energy_3_f","r1_energy_average_f",
                    "r1_shear_1","r1_shear_2","r1_shear_3","r1_shear_average","r1_temp_units","r1_impact_units","r1_energy_units","testing_machine"
                    }
    bend_object = {"heat_treated_by","tested_by","result_1","result_2"}
    cleanness_object = {"type","k_number","k_value","testing_machine"}
    hardness_object = {"bhn_min_max","ball_size_mm","load_kg","hardness_1","hardness_2","hardness_3","hardness_4","hardness_5","hardness_av","testing_machine"}
    decarburisation_object = {"decarburisation_min","decarburisation_max","decarburisation","testing_machine"}
    hydrogen_object = {"spec_test","rail_grade","max_test","testing_machine"} 
    resistivity_object = {"max_resistivity","temperature","temp","distance","volt","current","resistivity","humidity"}
    sulphur_object = {"sulphur_rail_grade","testing_machine"}
    tensile_object = {"tested_thickness","tested_width","tested_diameter","yield_tt0_5","yield_high","yield_rp0_2","yield_low","elongation_code",
                      "elongation_a565","elongation_a200","elongation_a50","elongation_8","elongation_2","elongation_a80","r1_tested_thickness","r1_tested_width",
                      "r1_tested_diameter","r1_yield_tt0_5","r1_yield_high","r1_yield_rp0_2","r1_yield_low","r1_elongation_code","r1_elongation_a565",
                      "r1_elongation_a200","r1_elongation_a50","r1_elongation_8","r1_elongation_2","r1_elongation_a80","r2_tested_thickness","r2_tested_width",
                      "r2_tested_diameter","r2_yield_tt0_5","r2_yield_high","r2_yield_rp0_2","r2_yield_low","r2_elongation_code","r2_elongation_a565","r2_elongation_a200",
                      "r2_elongation_a50","r2_elongation_8","r2_elongation_2","r2_elongation_a80","tensile_uts_mpa","r1_tensile_uts_mpa","r2_tensile_uts_mpa","testing_machine",
                      "susp"
                    }
    
    prodan_object = {"result_c","result_si","result_mn","result_p","result_s","result_cr","result_mo","result_ni","result_al","result_b","result_co",
                     "result_cu","result_nb","result_sn","result_ti","result_v","result_ca","result_n2","result_o","result_h","result_sal","result_as",
                     "result_bi","result_ce","result_pb","result_sb","result_w","result_zn","result_zr"
                    }
