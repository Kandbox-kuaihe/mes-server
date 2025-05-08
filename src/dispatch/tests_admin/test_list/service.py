from datetime import datetime, timedelta
from typing import List, Optional, Final
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import func, current_user
from fastapi import HTTPException
from abc import ABC, abstractmethod
from .models import Test, TestCreate, TestUpdate, TestRead, TestPagination, TestNewCreate, TestNewRead, TestNewUpdate, \
    TestPrintStatus
from dispatch.tests_admin.cleanness_test_card.models import TestCleannessCreate, TestCleannessUpdate, TestCleannessRead, \
    TestCleanness
from dispatch.tests_admin.bend_test_card.models import TestBendCreate, TestBendUpdate, TestBendRead, TestBend
from dispatch.tests_admin.decarburisation_test_card.models import TestDecarburisationCreate, TestDecarburisationUpdate, \
    TestDecarburisationRead, TestDecarburisation
from dispatch.tests_admin.hardness_test_card.models import TestHardnessCreate, TestHardnessUpdate, TestHardnessRead, \
    TestHardness
from dispatch.tests_admin.impact_test_card.models import TestImpactCreate, TestImpactUpdate, TestImpactRead, TestImpact
from dispatch.tests_admin.product_hydrogen_test_card.models import TestHydrogenCreate, TestHydrogenUpdate, \
    TestHydrogenRead, TestHydrogen
from dispatch.tests_admin.sulphur_test_card.models import TestSulphurCreate, TestSulphurUpdate, TestSulphurRead, \
    TestSulphur
from dispatch.tests_admin.tensile_test_card.models import TestTensileCreate, TestTensileUpdate, TestTensileRead, \
    TestTensile
from dispatch.tests_admin.cleanness_test_card import service as cleanness_service
from dispatch.tests_admin.decarburisation_test_card import service as decarburisation_service
from dispatch.tests_admin.product_hydrogen_test_card import service as product_hydrogen_test_card_service
from dispatch.tests_admin.bend_test_card import service as bend_service
from dispatch.tests_admin.hardness_test_card import service as hardness_service
from dispatch.tests_admin.impact_test_card import service as impact_service
from dispatch.tests_admin.sulphur_test_card import service as sulphur_service
from dispatch.tests_admin.tensile_test_card import service as tensile_service
from dispatch.tests_admin.resistivity_test_card import service as resistivity_service
from dispatch.tests_admin.product_analysis_card import service as product_analysis_service
from dispatch.tests_admin.test_history.models import TestHistoryObjectEnum,TestHistoryTypeEnum
from dispatch.tests_admin.test_history.service import bulk_create_test_history
from ..product_analysis_card.models import TestProductAnalysisCreate, TestProductAnalysisUpdate, \
    TestProductAnalysisRead, TestProdan
from ..resistivity_test_card.models import TestResistivityCreate, TestResistivityUpdate, TestResistivityRead, \
    TestResistivity
from dispatch.tests_admin.microstructure_test_card.models import TestMicrostructure
from typing import Annotated
from annotated_types import MaxLen, MinLen
from sqlalchemy import and_, desc
from dispatch.tests_admin.test_history import service as test_history_service
from dispatch.log import getLog
from ...config import MILLEnum, get_mill_ops
from ...spec_admin.sp_other_test.models import SpOtherTest
from ...spec_admin.spimpact.models import Spimpact

log = getLog(__name__)

def get(*, db_session, id: int) -> Optional[Test]:
    return db_session.get(Test, id)


def get_by_code(*, db_session, code: str) -> Optional[Test]:
    stmt = select(Test).where(Test.test_code == code)
    return db_session.scalar(stmt)

def get_by_ref_code_rolling_cast(*, db_session, ref_code, rolling_id, cast_id):
    stmt = select(Test).where(
        Test.ref_code == ref_code,
        Test.rolling_id == rolling_id,
        Test.cast_id == cast_id
    ).order_by(Test.created_at.desc())
    row = db_session.scalar(stmt)

    return row

def get_by_mf_test_code(*, db_session, mf_test_code: str, type: str):
    stmt = select(Test).where(
        Test.mf_test_code == mf_test_code,
        Test.type == type
    ).order_by(Test.created_at.desc())
    row = db_session.scalar(stmt)

    return row

def get_by_runout_id(*, db_session, runout_id: int) -> Optional[Test]:
    return db_session.query(Test).filter(Test.runout_id == runout_id).all()


def get_max_code_test_obj(*, db_session, test_type: str, test_id: int, mill_id: int):
    strategy = StrategyFactory.get_object_type(test_type)
    max_test_type_obj = db_session.query(strategy).filter(
        strategy.mill_id == mill_id, strategy.code != None
    ).order_by(desc(strategy.code)).first()
    return max_test_type_obj

def get_max_code_test_obj_new(*, db_session, test_type: str, mill_id: int):
    strategy = StrategyFactory.get_object_type(test_type)
    if test_type == 'decarburisation':
        strategy.mill_id = 1
    max_test_type_obj = db_session.query(strategy).filter(
        strategy.mill_id == mill_id, strategy.code != None
    ).order_by(desc(strategy.code)).first()
    return max_test_type_obj


def create(*, db_session, test_in: TestCreate) -> Test:
    created = Test(**test_in.model_dump(exclude={"sub_test_in", "test_sample", "spec", "rolling", "runout", "cast"}))
    db_session.add(created)
    db_session.commit()
    return created


def create_dict(*, db_session, test_in) -> Test:
    test_service = TestService(test_in['type'])
    created = TestNewCreate(**test_in)
    created = test_service.create(db_session=db_session, test_in=created)
    return created


def find_max_test_code(db_session: Session, mill_id: int):
    max_id = db_session.query(func.max(Test.id)).filter(Test.mill_id == mill_id).scalar()
    if not max_id:
        max_id = 1
    return str(max_id).zfill(6)


def update(
        *,
        db_session,
        test: Test,
        test_in: TestUpdate,
) -> Test:
    update_data = test_in.model_dump()
    for field, field_value in update_data.items():
        setattr(test, field, field_value)

    db_session.add(test)
    db_session.commit()
    return test


def delete(*, db_session, test: Test, test_id: int):
    test.is_deleted = 1

    db_session.commit()


from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional

def get_filter_print_status(db_session: Session, mill_id: int, from_time: Optional[str] = None, to_time: Optional[str] = None, print_status: Optional[str] = None):
    print_status = print_status if print_status else 'Not Printed',
    # 默认查询前一天的数据
    if not from_time or not to_time:
        yesterday = datetime.now().date() - timedelta(days=1)
        from_time = yesterday
        to_time = yesterday

    else:
        try:
            from_time = datetime.strptime(from_time, "%Y-%m-%d").date()
            to_time = datetime.strptime(to_time, "%Y-%m-%d").date()
        except HTTPException:
            raise HTTPException(status_code=400, detail="Invalid date format. Please use YYYY-MM-DD.")

    return db_session.query(Test).with_entities(
        Test.id,
        Test.test_code,
        Test.type
    ).filter(and_(
        Test.mill_id == mill_id,
        Test.print_status == print_status,
        func.date(Test.created_at) >= from_time,  # 大于等于起始日期
        func.date(Test.created_at) <= to_time  # 小于等于结束日期
    )).all()


def bulk_update_print_status(db_session: Session, test_list: list):
    db_session.bulk_update_mappings(Test, test_list)
    db_session.commit()



################## 整合后的Test Service ##################

class TestService:
    # 入口类
    def __init__(self, test_type: str = None):
        if test_type:
            self.test_type = test_type
            # 通过工厂生产具体策略
            self.strategy = StrategyFactory.get_strategy(test_type)
            self.sub_data_create_type = StrategyFactory.get_create_type(test_type)
            self.sub_data_update_type = StrategyFactory.get_update_type(test_type)
            # 自适应包装对象
            self.sub_data_object_type = StrategyFactory.get_object_type(test_type)
            self.sub_data_read_type = StrategyFactory.get_read_type(test_type)

    def create(self, db_session, test_in: TestNewCreate) -> Test:
        # 动态获取子测试类型
        if not self.sub_data_create_type:
            raise HTTPException(status_code=400, detail=f"Unsupported test type: {test_in.type}")
        # if db_session.query(Test).filter_by(test_code=test_in.test_code).first():
        #     raise HTTPException(status_code=400, detail=f"Key (test_code)=({test_in.test_code}) already exists.")
        setattr(test_in, test_in.type, 1)
        test_created = Test(**test_in.model_dump(exclude={"sub_test_in", "test_sample", "spec", "rolling", "runout", "cast", "inspector_1", "inspector_2", "inspector_3", "inspector_4"}))
        # 设置test 中的  sub test 为 1

        db_session.add(test_created)
        db_session.flush()

        test_in.sub_test_in.mill_id = test_in.mill_id
        test_in.sub_test_in.test_id = test_created.id
        try:
            # log.warning(f"code: {test_created.test_code}, test_standard: {str(test_created.spec.standard).zfill(2)}")
            if get_mill_ops(test_in.mill_id) == MILLEnum.MILL1 and test_in.type in ['tensile', 'bend', 'impact']:
                test_in.sub_test_in.check_digit_1 = calculate_check_digit(
                    test_code=test_created.test_code,
                    test_standard=str(test_created.spec.standard).zfill(2),
                    retest_ind="0"
                )
                # log.warning("=========2========")
                test_in.sub_test_in.check_digit_2 = calculate_check_digit(
                    test_code=test_created.test_code,
                    test_standard=str(test_created.spec.standard).zfill(2),
                    retest_ind="1"
                )
                test_in.sub_test_in.check_digit_3 = calculate_check_digit(
                    test_code=test_created.test_code,
                    test_standard=str(test_created.spec.standard).zfill(2),
                    retest_ind="2"
                )
            else:
                test_in.sub_test_in.check_digit_1 = calculate_check_digit(
                    test_code=test_created.test_code,
                    test_standard=str(test_created.spec.standard).zfill(2),
                    retest_ind="0"
                )
        except Exception as e:
            log.error(f"test service create: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        # 自动实例化 sub_test_in 方便后续返回
        sub_test_in = self.sub_data_create_type(**test_in.sub_test_in.model_dump())
        # 调用
        sub_test_created = self.strategy.test_create(db_session=db_session, sub_test_in=sub_test_in)
        db_session.commit()
        test = db_session.query(Test).filter_by(id=test_created.id).first()
        test.sub_test_in = sub_test_created

        his = {
            "action_type": TestHistoryTypeEnum.CREATE,
            "test_type":test.type,
            "test_id": test.id,
            "created_by": test.created_by,
            "section_size_code": test.product_type.code if test.product_type else None,
            "kgm": test.product_type.dim3 if test.product_type else None,
        }
        enum_value = TestHistoryObjectEnum[f"{test.type}_object"].value
        if enum_value:
            test_object = getattr(test, f"{test.type}_object")
            for item in enum_value:
                if f"{test.type}_object" == 'sulphur_object' and item == 'sulphur_rail_grade':
                    his[f"{test.type}_rail_grade"] = getattr(test_object, "rail_grade")
                    continue
                his[item] = getattr(test_object, item)

        bulk_create_test_history(db_session=db_session, test_history_in=[his])
        return test

    def update(self, db_session, test: Test, test_in: TestNewUpdate) -> TestNewRead:
        temp_test_in = test_in
        update_data = test_in.model_dump(
            exclude={"cast", "sub_test_in", "test_sample", "spec", "rolling", "runout", f"{test.type}_object", "conductivity_object", "microstructure_object"})
        for field, field_value in update_data.items():
            setattr(test, field, field_value)
        db_session.add(test)
        db_session.commit()

        sub_test_in = db_session.query(self.sub_data_object_type).filter_by(id=test_in.sub_test_in.id).first()
        update_sub_test_in = self.sub_data_update_type(**temp_test_in.sub_test_in.model_dump())

        sub_test_in = self.strategy.test_update(db_session=db_session, sub_test_in=sub_test_in, update_sub_test_in=update_sub_test_in)
        test.sub_test_in = sub_test_in
        
        his = {
            "action_type": TestHistoryTypeEnum.MODIFY,
            "update_name": test.update_name,
            "update_reason": test.update_reason,
            "test_type": test.type,
            "test_id": test.id,
            "updated_by": test.updated_by,
            "section_size_code": test.product_type.code if test.product_type else None,
            "kgm": test.product_type.dim3 if test.product_type else None,
        }
        enum_value = TestHistoryObjectEnum[f"{test.type}_object"].value
        if enum_value:
            # test_object = getattr(test, f"{test.type}_object")
            for item in enum_value:
                if f"{test.type}_object" == 'sulphur_object' and item == 'sulphur_rail_grade':
                    his[f"{test.type}_rail_grade"] = getattr(sub_test_in, "rail_grade")
                    continue
                his[item] = getattr(sub_test_in, item)

        bulk_create_test_history(db_session=db_session, test_history_in=[his])

        return test

    def delete(self, *, db_session, test: Test) -> TestNewRead:
        # 先删除 子test   包装成对应的对象传参
        sub_test_in = getattr(test, f"{test.type}_object")
        if sub_test_in is not None:
            raise HTTPException(status_code=400, detail="The test contains test data and cannot be deleted.")
        if sub_test_in:
            self.strategy.test_delete(db_session=db_session,
                                      sub_test_in_id=sub_test_in.id)
        # 再删除 test
        test.is_deleted = 1
        db_session.add(test)
        db_session.commit()
        # test.sub_test_in = sub_test_in

        his = {
            "action_type": TestHistoryTypeEnum.DELETE,
            "test_type":test.type,
            "test_id": test.id,
            "updated_by": test.updated_by,
            "section_size_code": test.product_type.code if test.product_type else None,
            "kgm": test.product_type.dim3 if test.product_type else None,
        }
        # enum_value = TestHistoryObjectEnum[test.type + '_object'].value
        # if enum_value:
        #     for item in enum_value:
        #         if f"{test.type}_object" == 'sulphur_object' and item == 'sulphur_rail_grade':
        #             his[f"{test.type}_rail_grade"] = getattr(sub_test_in, "rail_grade")
        #             continue
        #         his[item] = getattr(sub_test_in, item)

        bulk_create_test_history(db_session=db_session, test_history_in=[his])
        return test

    def read(self, *, db_session, test: TestRead) -> TestNewRead:
        # 获取子test对象
        test_id = test.id
        sub_test_in = getattr(test, f"{self.test_type}_object")
        if not sub_test_in:
            raise HTTPException(status_code=400, detail=f"The test must be associated with a test_type, but key (test_object)=({self.test_type}) does not exist.")
        test = db_session.query(Test).filter_by(id=test_id).first()
        test.sub_test_in = db_session.query(self.sub_data_object_type).filter_by(id=sub_test_in.id).first()
        if test.cast:
            test.cast_code = test.cast.cast_code
        if test.test_sample:
            test.test_sample_code = test.test_sample.test_sample_code
        if test.runout:
            test.runout_code = test.runout.runout_code
        if test.rolling:
            test.rolling_code = test.rolling.rolling_code
        return test
    
def update_then_get_test_status_by_tensile(db_session, runout, test_sample, piece_sub_id: str,sample_thickness):
    if not runout or not piece_sub_id: return
    test = db_session.query(Test).filter(and_(Test.runout_id == runout.id, Test.piece_sub_id == piece_sub_id, Test.type == 'tensile', Test.sample_thickness == str(float(sample_thickness)))).first()
    if test:
        test.status = 'T'
        test.update_by = 'MES'
        test.updated_at = datetime.now()
    else:
        spec = test_sample.spec
        test = Test(runout_id=runout.id,
                                test_code=runout.runout_code + "-" + str(1),
                                piece_sub_id = piece_sub_id,
                                test_sample_id=test_sample.id,
                                rolling_id=test_sample.rolling_id,
                                rolling_code=runout.rolling_code,
                                spec_code=spec.spec_code if spec else None,
                                spec_id=spec.id if spec else None,
                                type='tensile',
                                status="T",
                                sample_thickness=str(float(sample_thickness)),
                                cast_id= test_sample.cast_id,
                                cast_code = test_sample.concast_code,
                                created_by="MES",
                                created_at=datetime.now(),
                                mill_id= MILLEnum.MILL410,
                                tensile=1,
                                impact=0,
                                product_type_id=runout.product_type_id
                                )
        log.warning(f'Test does not exist, and created one {test} from test tensile')
        db_session.add(test)
    db_session.commit()
    return test

def update_then_get_test_status_by_impact(db_session, runout, temp_value: str, test_sample, piece_sub_id: str):
    if not runout : return
    test = db_session.query(Test).filter(and_(Test.runout_id == runout.id, Test.piece_sub_id == piece_sub_id, Test.temp_value == str(int(temp_value or '0')), Test.type == 'impact')).first()
    if test:
        test.status = 'T'
        test.update_by = 'MES'
        test.updated_at = datetime.now()
    else:
        spec = test_sample.spec
        test = Test(runout_id=runout.id,
                                test_code=runout.runout_code + "-" + str(1),
                                piece_sub_id = piece_sub_id,
                                test_sample_id=test_sample.id,
                                rolling_id=test_sample.rolling_id,
                                rolling_code=runout.rolling_code,
                                spec_code=spec.spec_code if spec else None,
                                spec_id=spec.id if spec else None,
                                type='impact',
                                status="T",
                                cast_id= test_sample.cast_id,
                                cast_code = test_sample.concast_code,
                                created_by="MES",
                                created_at=datetime.now(),
                                updated_by="MES",
                                updated_at=datetime.now(),
                                mill_id= MILLEnum.MILL410,
                                tensile=0,
                                impact=1,
                                temp_value=str(int(temp_value or '0')),
                                product_type_id=runout.product_type_id
                                )
        log.warning(f'Test does not exist, and created one {test} from test impact')
        db_session.add(test)
    db_session.commit()
    return test
class CURDBaseStrategy(ABC):
    """
    [cleanness, sulphur, hardness, tensile, decarburisation, bend, hydrogen, impact]
    """

    @abstractmethod
    def test_create(self, db_session, sub_test_in):
        pass

    def test_delete(self, db_session, sub_test_in_id):
        pass

    @abstractmethod
    def test_update(self, db_session, sub_test_in, update_sub_test_in):
        pass
    #
    # @abstractmethod
    # def test_read(self, db_session):
    #     pass


class ConcreteTestCleannessStrategy(CURDBaseStrategy):

    @classmethod
    def test_create(cls, db_session, sub_test_in):
        return cleanness_service.create(db_session=db_session, TestCleanness_in=sub_test_in)

    @classmethod
    def test_delete(cls, db_session, sub_test_in_id):
        return cleanness_service.delete(db_session=db_session, TestCleanness_id=sub_test_in_id)

    @classmethod
    def test_update(cls, db_session, sub_test_in, update_sub_test_in):
        return cleanness_service.update(db_session=db_session, TestCleanness=sub_test_in, TestCleanness_in=update_sub_test_in)



class ConcreteTestSulphurStrategy(CURDBaseStrategy):
    @classmethod
    def test_create(cls, db_session, sub_test_in):
        return sulphur_service.create(db_session=db_session, TestSulphur_in=sub_test_in)

    @classmethod
    def test_delete(cls, db_session, sub_test_in_id):
        return sulphur_service.delete(db_session=db_session, TestSulphur_id=sub_test_in_id)

    @classmethod
    def test_update(cls, db_session, sub_test_in, update_sub_test_in):
        return sulphur_service.update(db_session=db_session, TestSulphur=sub_test_in, TestSulphur_in=update_sub_test_in)


class ConcreteTestHardnessStrategy(CURDBaseStrategy):
    @classmethod
    def test_create(cls, db_session, sub_test_in):
        return hardness_service.create(db_session=db_session, TestHardness_in=sub_test_in)

    @classmethod
    def test_delete(cls, db_session, sub_test_in_id):
        return hardness_service.delete(db_session=db_session, TestHardness_id=sub_test_in_id)

    @classmethod
    def test_update(cls, db_session, sub_test_in, update_sub_test_in):
        return hardness_service.update(db_session=db_session, TestHardness=sub_test_in, TestHardness_in=update_sub_test_in)

class ConcreteTestBendStrategy(CURDBaseStrategy):
    @classmethod
    def test_create(cls, db_session, sub_test_in):
        return bend_service.create(db_session=db_session, bend_test_card_in=sub_test_in)

    @classmethod
    def test_delete(cls, db_session, sub_test_in_id):
        return bend_service.delete(db_session=db_session, id=sub_test_in_id)

    @classmethod
    def test_update(cls, db_session, sub_test_in, update_sub_test_in):
        return bend_service.update(db_session=db_session, bend_test_card=sub_test_in, bend_test_card_in=update_sub_test_in)



class ConcreteTestImpactStrategy(CURDBaseStrategy):
    @classmethod
    def test_create(cls, db_session, sub_test_in):
        return impact_service.create(db_session=db_session, TestImpact_in=sub_test_in)

    @classmethod
    def test_delete(cls, db_session, sub_test_in_id):
        return impact_service.delete(db_session=db_session, TestImpact_id=sub_test_in_id)

    @classmethod
    def test_update(cls, db_session, sub_test_in, update_sub_test_in):
        return impact_service.update(db_session=db_session, TestImpact=sub_test_in, TestImpact_in=update_sub_test_in)

class ConcreteTestTensileStrategy(CURDBaseStrategy):
    @classmethod
    def test_create(cls, db_session, sub_test_in):
        return tensile_service.create(db_session=db_session, TestTensile_in=sub_test_in)

    @classmethod
    def test_delete(cls, db_session, sub_test_in_id):
        return tensile_service.delete(db_session=db_session, TestTensile_id=sub_test_in_id)

    @classmethod
    def test_update(cls, db_session, sub_test_in, update_sub_test_in):
        return tensile_service.update(db_session=db_session, TestTensile=sub_test_in, TestTensile_in=update_sub_test_in)

class ConcreteTestHydrogenStrategy(CURDBaseStrategy):
    @classmethod
    def test_create(cls, db_session, sub_test_in):
        return product_hydrogen_test_card_service.create(db_session=db_session, product_hydrogen_test_card_in=sub_test_in)

    @classmethod
    def test_delete(cls, db_session, sub_test_in_id):
        return product_hydrogen_test_card_service.delete(db_session=db_session, id=sub_test_in_id)

    @classmethod
    def test_update(cls, db_session, sub_test_in, update_sub_test_in):
        return product_hydrogen_test_card_service.update(db_session=db_session, product_hydrogen_test_card=sub_test_in, product_hydrogen_test_card_in=update_sub_test_in)

class ConcreteTestDecarburisationStrategy(CURDBaseStrategy):
    @classmethod
    def test_create(cls, db_session, sub_test_in):
        return decarburisation_service.create(db_session=db_session, decarburisation_test_card_in=sub_test_in)

    @classmethod
    def test_delete(cls, db_session, sub_test_in_id):
        return decarburisation_service.delete(db_session=db_session, id=sub_test_in_id)

    @classmethod
    def test_update(cls, db_session, sub_test_in, update_sub_test_in):
        return decarburisation_service.update(db_session=db_session, decarburisation_test_card=sub_test_in, decarburisation_test_card_in=update_sub_test_in)

class ConcreteTestResistivityStrategy(CURDBaseStrategy):
    @classmethod
    def test_create(cls, db_session, sub_test_in):
        return resistivity_service.create(db_session=db_session, resistivity_test_card_in=sub_test_in)

    @classmethod
    def test_delete(cls, db_session, sub_test_in_id):
        return resistivity_service.delete(db_session=db_session, id=sub_test_in_id)

    @classmethod
    def test_update(cls, db_session, sub_test_in, update_sub_test_in):
        return resistivity_service.update(db_session=db_session, resistivity_test_card=sub_test_in, resistivity_test_card_in=update_sub_test_in)

class ConcreteTestProductAnalysisStrategy(CURDBaseStrategy):
    @classmethod
    def test_create(cls, db_session, sub_test_in):
        return product_analysis_service.create(db_session=db_session, test_prodan_in=sub_test_in)

    @classmethod
    def test_delete(cls, db_session, sub_test_in_id):
        return product_analysis_service.delete(db_session=db_session, test_prodan_id=sub_test_in_id)

    @classmethod
    def test_update(cls, db_session, sub_test_in, update_sub_test_in):
        return product_analysis_service.update(db_session=db_session, test_prodan=sub_test_in, test_prodan_in=update_sub_test_in)


class StrategyFactory:
    """
    工厂生产策略
    """
    strategy_map = {
        "cleanness": ConcreteTestCleannessStrategy,
        "sulphur": ConcreteTestSulphurStrategy,
        "hardness": ConcreteTestHardnessStrategy,
        "tensile": ConcreteTestTensileStrategy,
        "decarburisation": ConcreteTestDecarburisationStrategy,
        "bend": ConcreteTestBendStrategy,
        "hydrogen": ConcreteTestHydrogenStrategy,
        "impact": ConcreteTestImpactStrategy,
        "resistivity": ConcreteTestResistivityStrategy,
        "prodan": ConcreteTestProductAnalysisStrategy,
    }

    # 定义类型映射
    create_type_map = {
        "cleanness": TestCleannessCreate,
        "sulphur": TestSulphurCreate,
        "hardness": TestHardnessCreate,
        "tensile": TestTensileCreate,
        "decarburisation": TestDecarburisationCreate,
        "bend": TestBendCreate,
        "hydrogen": TestHydrogenCreate,
        "impact": TestImpactCreate,
        "resistivity": TestResistivityCreate,
        "prodan": TestProductAnalysisCreate,
    }

    update_type_map = {
        "cleanness": TestCleannessUpdate,
        "sulphur": TestSulphurUpdate,
        "hardness": TestHardnessUpdate,
        "tensile": TestTensileUpdate,
        "decarburisation": TestDecarburisationUpdate,
        "bend": TestBendUpdate,
        "hydrogen": TestHydrogenUpdate,
        "impact": TestImpactUpdate,
        "resistivity": TestResistivityUpdate,
        "prodan": TestProductAnalysisUpdate,
    }

    read_type_map = {
        "cleanness": TestCleannessRead,
        "sulphur": TestSulphurRead,
        "hardness": TestHardnessRead,
        "tensile": TestTensileRead,
        "decarburisation": TestDecarburisationRead,
        "bend": TestBendRead,
        "hydrogen": TestHydrogenRead,
        "impact": TestImpactRead,
        "resistivity": TestResistivityRead,
        "prodan": TestProductAnalysisRead,
    }

    object_type_map = {
        "cleanness": TestCleanness,
        "sulphur": TestSulphur,
        "hardness": TestHardness,
        "tensile": TestTensile,
        "decarburisation": TestDecarburisation,
        "bend": TestBend,
        "hydrogen": TestHydrogen,
        "impact": TestImpact,
        "resistivity": TestResistivity,
        "prodan": TestProdan,
        "micro_structure": TestMicrostructure
    }

    @staticmethod
    def get_strategy(test_type: str):
        strategy = StrategyFactory.strategy_map.get(test_type)
        if not strategy:
            raise ValueError(f"Error test type: {test_type}")
        return strategy

    @staticmethod
    def get_object_type(type: str):
        strategy = StrategyFactory.object_type_map.get(type)
        if not strategy:
            raise ValueError(f"Error test type: {type}")
        return strategy

    @staticmethod
    def get_create_type(type: str):
        strategy = StrategyFactory.create_type_map.get(type)
        if not strategy:
            raise ValueError(f"Error test type: {type}")
        return strategy

    @staticmethod
    def get_update_type(type: str):
        strategy = StrategyFactory.update_type_map.get(type)
        if not strategy:
            raise ValueError(f"Error test type: {type}")
        return strategy

    @staticmethod
    def get_read_type(type: str):
        strategy = StrategyFactory.read_type_map.get(type)
        if not strategy:
            raise ValueError(f"Error test type: {type}")
        return strategy


def calculate_check_digit(
        test_code: Annotated[str, MaxLen(6), MinLen(6)],
        test_standard: Annotated[str, MaxLen(2), MinLen(2)],
        retest_ind: Annotated[str, MaxLen(1), MinLen(1)],
        check_digit: Annotated[str, MaxLen(1), MinLen(1)] = 0,
) -> int:

    # 定义权重因子
    SET_1_WEIGHT_FACTOR: Final = "09100708040603050200"
    SET_2_WEIGHT_FACTOR: Final = "10030204050708060900"

    # 拼接完整字符串（校验位初始设为0）
    full_sign_code = f"{test_code}{test_standard}{retest_ind}{check_digit}"
    # log.error(full_sign_code)
    def calculate_sum(weight_str: str) -> int:
        """计算加权和"""
        total = 0
        for i in range(10):
            # 获取当前位的数字和权重
            digit = int(full_sign_code[i])
            weight = int(weight_str[i * 2: i * 2 + 2])
            total += digit * weight
        return total

    # 第一轮计算（使用Set1）
    sum1 = calculate_sum(SET_1_WEIGHT_FACTOR)
    rem1 = sum1 % 11
    check_digit = 11 - rem1 if rem1 != 0 else 0

    # 处理需要Set2的情况（当11 - rem1 == 10时）
    if check_digit == 10:
        # 第二轮计算（使用Set2）
        sum2 = calculate_sum(SET_2_WEIGHT_FACTOR)
        rem2 = sum2 % 11
        check_digit = 11 - rem2 if rem2 != 0 else 0

    return check_digit



def impact_spec_temp(db_session: Session, spec_id, flange_thickness):
    if flange_thickness and spec_id:
        result = db_session.query(Spimpact).filter(and_(
            Spimpact.spec_id == spec_id,
            Spimpact.thick_from <= flange_thickness,
            Spimpact.thick_to >= flange_thickness
        )).first()
        return {
            "value": result.temp_value_1,
            "temp_units": result.temp_units
        }
    return {}
    # if spec_id and not flange_thickness:
    #     result = db_session.query(SpOtherTest).filter(and_(
    #         SpOtherTest.spec_id == spec_id,
    #         SpOtherTest.cd_vari == "REST1VAL"
    #     )).first()
    #     return {
    #         "max": result.vl_max,
    #         "rail_grade": 260
    #     }