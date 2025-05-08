from typing import List, Optional, Union

from pydantic import BaseModel, Field
from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    String,
    BigInteger,
    Integer,
    DateTime
)

from typing import Optional

from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.cast.models import CastRead
from dispatch.database import Base
from dispatch.mill.models import MillRead
from dispatch.models import TimeStampMixin, DispatchBase, BaseResponseModel

from sqlalchemy.orm import relationship

from dispatch.product_type.models import ProductTypeRead
from dispatch.runout_admin.runout_list.models import RunoutRead
from dispatch.spec_admin.inspector.models import InspectorRead
from dispatch.tests_admin.tensile_test_card.models import TestTensileRead, TestTensileUpdate, TestTensileCreate
from dispatch.tests_admin.test_sample.models import TestSampleRead
from dispatch.spec_admin.spec.models import SpecRead
from dispatch.rolling.rolling_list.models import RollingRead

from dispatch.tests_admin.test_chemial.models import TestChemialRead, TestChemialCreate, TestChemialUpdate
from dispatch.tests_admin.impact_test_card.models import TestImpactRead, TestImpactCreate, TestImpactUpdate
from dispatch.tests_admin.bend_test_card.models import TestBendRead, TestBendCreate, TestBendUpdate
from dispatch.tests_admin.hardness_test_card.models import TestHardnessRead, TestHardnessCreate, TestHardnessUpdate
from dispatch.tests_admin.sulphur_test_card.models import TestSulphurRead, TestSulphurCreate, TestSulphurUpdate
from dispatch.tests_admin.cleanness_test_card.models import TestCleannessRead, TestCleannessCreate, TestCleannessUpdate
from dispatch.tests_admin.product_hydrogen_test_card.models import TestHydrogenRead, TestHydrogenCreate, \
    TestHydrogenUpdate
from dispatch.tests_admin.decarburisation_test_card.models import TestDecarburisationRead, TestDecarburisationCreate, \
    TestDecarburisationUpdate
from dispatch.tests_admin.product_analysis_card.models import TestProductAnalysisRead, TestProductAnalysisCreate, \
    TestProductAnalysisUpdate
from dispatch.tests_admin.resistivity_test_card.models import TestResistivityRead, TestResistivityCreate, \
    TestResistivityUpdate
from dispatch.tests_admin.conductivity_test_card.models import TestConductivityRead, TestConductivityCreate
from dispatch.tests_admin.microstructure_test_card.models import TestMicrostructureRead, TestMicrostructureCreate


class Test(Base, TimeStampMixin):
    __tablename__ = 'test'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    mill_id = Column(BigInteger, ForeignKey('mill.id'), nullable=False)
    mill = relationship("Mill", foreign_keys=[mill_id])
    test_code = Column(String, nullable=False)
    ref_code = Column(String)
    mf_test_code = Column(String)

    piece_sub_id = Column(String)
    temp_value = Column(String)

    test_sample_id = Column(BigInteger, ForeignKey('test_sample.id'), nullable=True)
    test_sample = relationship("TestSample", foreign_keys=[test_sample_id])

    runout_id = Column(BigInteger, ForeignKey('runout.id'), nullable=True) # It should be nullable=False in the future after rolling problems being solved
    runout = relationship("Runout", backref="runout_test")

    rolling_code = Column(String, nullable=True) # It should be nullable=False in the future after rolling problems being solved
    rolling_id = Column(BigInteger, ForeignKey('rolling.id'), nullable=True)
    rolling = relationship("Rolling", backref="rolling_test")

    spec_code = Column(String, nullable=True)  # It has to be nullable=True. Because TBM has multi specs in one test, so specs would be saved in flex_form_data
    spec_id = Column(BigInteger, ForeignKey('spec.id'), nullable=True) # It has to be nullable=True. Because TBM has multi specs in one test, so specs would be saved in flex_form_data
    spec = relationship("Spec", backref="spec_test")

    # standard = Column(String, nullable=True)
    check_digit_0 = Column(Integer, nullable=True)
    check_digit_1 = Column(Integer, nullable=True)
    check_digit_2 = Column(Integer, nullable=True)
    cast_id = Column(BigInteger, ForeignKey('cast.id'), nullable=True)
    cast = relationship("Cast", foreign_keys=[cast_id])
    cast_code = Column(String, nullable=True)
    
    semi_id = Column(BigInteger, ForeignKey('semi.id'), nullable=True)
    semi = relationship("Semi", foreign_keys=[semi_id])

    product_type_id = Column(BigInteger, ForeignKey('product_type.id'))
    product_type = relationship("ProductType", backref="product_type_test")

    inspector_id_1 = Column(BigInteger, ForeignKey('inspector.id'), nullable=True)
    inspector_id_2 = Column(BigInteger, ForeignKey('inspector.id'), nullable=True)
    inspector_id_3 = Column(BigInteger, ForeignKey('inspector.id'), nullable=True)
    inspector_id_4 = Column(BigInteger, ForeignKey('inspector.id'), nullable=True)

    inspector_1 = relationship("Inspector", foreign_keys=[inspector_id_1])
    inspector_2 = relationship("Inspector", foreign_keys=[inspector_id_2])
    inspector_3 = relationship("Inspector", foreign_keys=[inspector_id_3])
    inspector_4 = relationship("Inspector", foreign_keys=[inspector_id_4])


    type = Column(String, nullable=False)
    status = Column(String)  # test, waiting, tested, deleted
    print_status = Column(String, default='Not Printed', nullable=False)  # 'Printed', 'Not Printed'

    tensile = Column(Integer, default=0, nullable=False)
    bend = Column(Integer, default=0, nullable=False)
    impact = Column(Integer, default=0, nullable=False)
    hardness = Column(Integer, default=0, nullable=False)

    resistivity = Column(Integer, default=0, nullable=False)
    cleanness = Column(Integer, default=0, nullable=False)
    decarburisation = Column(Integer, default=0, nullable=False)
    sulphur = Column(Integer, default=0, nullable=False)
    hydrogen = Column(Integer, default=0, nullable=False)
    prodan = Column(Integer, default=0, nullable=False)
    conductivity = Column(Integer, default=0, nullable=True)

    piece_sub_id = Column(String)
    temp_value = Column(String)
    sample_thickness = Column(String)

    # 更新人名的首字母
    update_name = Column(String)
    # 更新原因
    update_reason = Column(String)

    tester_initials = Column(String)
    comment = Column(String)

    pass_status = Column(String)


    micro_structure = Column(Integer, default=0)

   

    tensile_object = relationship("TestTensile", uselist=False,
                                  primaryjoin="and_(Test.id == TestTensile.test_id, Test.type == 'tensile')",
                                  lazy="select")
    bend_object = relationship("TestBend", uselist=False,
                               primaryjoin="and_(Test.id == TestBend.test_id, Test.type == 'bend')",
                               lazy="select")
    impact_object = relationship("TestImpact", uselist=False,
                                 primaryjoin="and_(Test.id == TestImpact.test_id, Test.type == 'impact')",
                                 lazy="select")
    hardness_object = relationship("TestHardness", uselist=False,
                                   primaryjoin="and_(Test.id == TestHardness.test_id, Test.type == 'hardness')",
                                   lazy="select")
    cleanness_object = relationship("TestCleanness", uselist=False,
                                    primaryjoin="and_(Test.id == TestCleanness.test_id, Test.type == 'cleanness')",
                                    lazy="select")
    decarburisation_object = relationship("TestDecarburisation", uselist=False,
                                          primaryjoin="and_(Test.id == TestDecarburisation.test_id, Test.type == 'decarburisation')",
                                          lazy="select")
    sulphur_object = relationship("TestSulphur", uselist=False,
                                  primaryjoin="and_(Test.id == TestSulphur.test_id, Test.type == 'sulphur')",
                                  lazy="select")
    hydrogen_object = relationship("TestHydrogen", uselist=False,
                                   primaryjoin="and_(Test.id == TestHydrogen.test_id, Test.type == 'hydrogen')",
                                   lazy="select")
    resistivity_object = relationship("TestResistivity", uselist=False,
                                      primaryjoin="and_(Test.id == TestResistivity.test_id, Test.type == 'resistivity')",
                                      lazy="select")
    prodan_object = relationship("TestProdan", uselist=False,
                                 primaryjoin="and_(Test.id == TestProdan.test_id, Test.type == 'prodan')",
                                 lazy="select")
    conductivity_object = relationship("TestConductivity", uselist=False,
                                      primaryjoin="and_(Test.id == TestConductivity.test_id, Test.type == 'conductivity')",
                                      lazy="select")
    microstructure_object = relationship("TestMicrostructure", uselist=False,
                                 primaryjoin="and_(Test.id == TestMicrostructure.test_id, Test.type == 'microstructure')",
                                 lazy="select")

    test_job_id = Column(BigInteger, ForeignKey('test_job.id'), nullable=True)
    test_job = relationship("TestJob", backref="test_job_test")

    search_vector = Column(
        TSVectorType(
            "test_code",
            weights={"test_code": "A"},
        )
    )

    # __table_args__ = (
    #     UniqueConstraint('test_code', name='unique_key_test_code'),
    # )


class TestBase(BaseResponseModel):
    id: Optional[int] = None
    test_code: Optional[str] = None
    mf_test_code: Optional[str] = None
    mill_id: Optional[int] = None
    ref_code: Optional[str] = None
    runout_id: Optional[int] = None
    rolling_id: Optional[int] = None
    test_sample_id: Optional[int] = None
    spec_id: Optional[int] = None
    # standard: Optional[str] = None
    check_digit_0: Optional[int] = None
    check_digit_1: Optional[int] = None
    check_digit_2: Optional[int] = None
    cast_id: Optional[int] = None

    cast_code: Optional[str] = None
    inspector_id_1: Optional[int] = None
    inspector_id_2: Optional[int] = None
    inspector_id_3: Optional[int] = None
    inspector_id_4: Optional[int] = None

    semi_id: Optional[int] = None
    
    product_type_id: Optional[int] = None

    piece_sub_id : Optional[str] = None
    temp_value : Optional[str] = None

    rolling_code: Optional[str] = None
    spec_code: Optional[str] = None

    type: Optional[str] = None
    print_status: Optional[str] = None
    status: Optional[str] = None
    tensile: Optional[int] = None
    bend: Optional[int] = None
    impact: Optional[int] = None
    hardness: Optional[int] = None

    resistivity: Optional[int] = None
    cleanness: Optional[int] = None
    decarburisation: Optional[int] = None
    sulphur: Optional[int] = None
    hydrogen: Optional[int] = None
    prodan: Optional[int] = None
    micro_structure: Optional[int] = None
    conductivity: Optional[int] = None
    rolling: Optional[RollingRead] = None
    test_sample: Optional[TestSampleRead] = None

    piece_sub_id : Optional[str] = None
    temp_value : Optional[str] = None
    sample_thickness : Optional[str] = None
    update_name: Optional[str] = None
    update_reason: Optional[str] = None
    tester_initials: Optional[str] = None
    comment: Optional[str] = None
    pass_status: Optional[str] = None

    tensile_object: Optional[TestTensileRead] = None
    bend_object: Optional[TestBendRead] = None
    impact_object: Optional[TestImpactRead] = None
    hardness_object: Optional[TestHardnessRead] = None
    cleanness_object: Optional[TestCleannessRead] = None
    decarburisation_object: Optional[TestDecarburisationRead] = None
    sulphur_object: Optional[TestSulphurRead] = None
    hydrogen_object: Optional[TestHydrogenRead] = None
    prodan_object: Optional[TestProductAnalysisRead] = None
    resistivity_object: Optional[TestResistivityRead] = None
    conductivity_object: Optional[TestConductivityRead] = None
    microstructure_object: Optional[TestMicrostructureRead] = None

    test_job_id: Optional[int] = None


class TestCreate(TestBase):
    cast_id: Optional[int] = None
    pass


class TestUpdate(TestBase):
    pass


class TestRead(TestBase, BaseResponseModel):
    id: Optional[int] = None
    runout: Optional[RunoutRead] = None
    rolling: Optional[RollingRead] = None
    test_sample: Optional[TestSampleRead] = None
    spec: Optional[SpecRead] = None
    product_type: Optional[ProductTypeRead] = None
    inspector_1: Optional[InspectorRead] = None
    inspector_2: Optional[InspectorRead] = None
    inspector_3: Optional[InspectorRead] = None
    inspector_4: Optional[InspectorRead] = None
    mill: Optional[MillRead] = None
    cast: Optional[CastRead] = None

class TestPagination(DispatchBase):
    total: int
    items: List[TestRead] = []
    itemsPerPage: int
    page: int


class TestPrintStatus(BaseResponseModel):
    id: Optional[int] = None
    test_code: Optional[str] = None
    type: Optional[str] = None


class TestBulkUpdatePrintStatus(BaseModel):
    ids: Optional[List[int]] = None


class TestNewCreate(TestBase):
    
    sub_test_in: Optional[Union[
        TestTensileCreate, TestImpactCreate, TestBendCreate, TestHardnessCreate, TestSulphurCreate, TestCleannessCreate, TestHydrogenCreate, TestDecarburisationCreate, TestResistivityCreate, TestProductAnalysisCreate]] = None


class TestNewRead(TestBase):
    runout: Optional[RunoutRead] = None
    rolling: Optional[RollingRead] = None
    test_sample: Optional[TestSampleRead] = None
    spec: Optional[SpecRead] = None
    product_type: Optional[ProductTypeRead] = None
    inspector_1: Optional[InspectorRead] = None
    inspector_2: Optional[InspectorRead] = None
    inspector_3: Optional[InspectorRead] = None
    inspector_4: Optional[InspectorRead] = None
    mill: Optional[MillRead] = None
    sub_test_in: Optional[Union[
        TestTensileRead, TestImpactRead, TestBendRead, TestHardnessRead, TestSulphurRead, TestCleannessRead, TestHydrogenRead, TestDecarburisationRead, TestResistivityRead, TestProductAnalysisRead]] = None
    test_sample_code: Optional[str] = None
    runout_code:Optional[str] = None

class TestNewUpdate(TestBase):
    sub_test_in: Optional[Union[
        TestTensileUpdate, TestImpactUpdate, TestBendUpdate, TestHardnessUpdate, TestSulphurUpdate, TestCleannessUpdate, TestHydrogenUpdate, TestDecarburisationUpdate, TestResistivityUpdate, TestProductAnalysisUpdate]] = None
