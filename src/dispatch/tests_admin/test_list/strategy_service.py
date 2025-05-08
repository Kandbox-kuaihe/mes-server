from abc import ABC, abstractmethod
from .models import Test, TestCreate, TestUpdate, TestRead, TestPagination, TestNewCreate, TestNewRead, TestNewUpdate
from dispatch.tests_admin.cleanness_test_card.models import TestCleannessCreate, TestCleannessUpdate, TestCleannessRead, \
    TestCleanness
from dispatch.tests_admin.bend_test_card.models import TestBendCreate, TestBendUpdate, TestBendRead, TestBend
from dispatch.tests_admin.decarburisation_test_card.models import TestDecarburizationCreate, TestDecarburizationUpdate, \
    TestDecarburizationRead, TestDecarburization
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



################## 整合后的Test Service ##################

class TestService:
    # 入口类
    def __init__(self, test_type: str):
        # 通过工厂生产具体策略
        self.strategy = StrategyFactory.get_strategy(test_type)
        self.sub_data_create_type = StrategyFactory.get_create_type(test_type)
        self.sub_data_update_type = StrategyFactory.get_update_type(test_type)
        # 自适应包装对象
        self.sub_data_object_type = StrategyFactory.get_object_type(test_type)
        self.sub_data_read_type = StrategyFactory.get_read_type(test_type)

    def create(self, db_session, test_in: TestNewCreate):
        # 动态获取子测试类型
        if not self.sub_data_create_type:
            raise ValueError(f"Unsupported test type: {test_in.test_type}")
        # 自动实例化 sub_test_in 方便后续返回
        sub_test_in = self.sub_data_create_type(**test_in.sub_test_in.model_dump())
        # 调用
        sub_test_created = self.strategy.test_create(db_session=db_session, sub_test_in=sub_test_in)
        # 每次创建 sub_test都会创建一个test 把刚刚创建好的sub test id 给test
        setattr(test_in, test_in.test_type, sub_test_created.id)
        test_created = Test(**test_in.model_dump(exclude={"sub_test_in", "test_type"}))
        db_session.add(test_created)
        db_session.commit()
        # print(type(sub_test_created))
        return TestNewRead(sub_test_in=sub_test_created)

    def update(self, db_session, test: Test, test_in: TestNewUpdate):
        update_data = test_in.model_dump(exclude={"sub_test_in", "test_type"})
        for field, field_value in update_data.items():
            setattr(test, field, field_value)
        db_session.add(test)
        db_session.commit()
        # test 及其 test子类型被创建后， 只能update test 不能修改子类型
        return TestNewRead(**update_data, sub_test_in=self.sub_data_update_type(**test_in.sub_test_in.model_dump()))

    def delete(self, *, db_session, test: Test, test_in: TestNewUpdate):
        # 先删除 子test   包装成对应的对象传参
        # print(test_in)
        sub_test_in = self.sub_data_update_type(**test_in.sub_test_in.model_dump())
        self.strategy.test_delete(db_session=db_session,
                                  sub_test_in=sub_test_in)
        # 再删除 test
        test.is_deleted = 1
        db_session.add(test)
        db_session.commit()
        return TestNewRead(**test_in.model_dump(exclude={"sub_test_in", "test_type"}),
                           sub_test_in=self.sub_data_object_type(**sub_test_in.model_dump()))


class CURDBaseStrategy(ABC):
    """
    [cleanness, sulphur, hardness, tensile, decarburization, bend, hydrogen, impact]
    """

    @abstractmethod
    def test_create(self, db_session, sub_test_in):
        pass

    def test_delete(self, db_session, sub_test_in):
        pass

    # @abstractmethod
    # def test_update(self, db_session, test, test_in):
    #     pass
    #
    # @abstractmethod
    # def test_read(self, db_session):
    #     pass


class ConcreteTestCleannessStrategy(CURDBaseStrategy):

    @classmethod
    def test_create(cls, db_session, sub_test_in):
        return cleanness_service.create(db_session=db_session, TestCleanness_in=sub_test_in)

    @classmethod
    def test_delete(cls, db_session, sub_test_in):
        return cleanness_service.delete(db_session=db_session, TestCleanness_id=sub_test_in.id)


class ConcreteTestSulphurStrategy(CURDBaseStrategy):
    @classmethod
    def test_create(cls, db_session, sub_test_in):
        return sulphur_service.create(db_session=db_session, TestSulphur_in=sub_test_in)

    @classmethod
    def test_delete(cls, db_session, sub_test_in):
        return sulphur_service.delete(db_session=db_session, TestSulphur_id=sub_test_in.id)


class ConcreteTestHardnessStrategy(CURDBaseStrategy):
    @classmethod
    def test_create(cls, db_session, sub_test_in):
        return hardness_service.create(db_session=db_session, TestHardness_in=sub_test_in)

    @classmethod
    def test_delete(cls, db_session, sub_test_in):
        return hardness_service.delete(db_session=db_session, TestHardness_id=sub_test_in.id)


class StrategyFactory:
    """
    工厂生产策略
    """
    strategy_map = {
        "cleanness": ConcreteTestCleannessStrategy,
        "sulphur": ConcreteTestSulphurStrategy,
        # "hardness": ConcreteTestHardnessStrategy,
        # "tensile": ConcreteTestTensileStrategy,
        # "decarburization": ConcreteTestDecarburizationStrategy,
        # "bend": ConcreteTestBendStrategy,
        # "hydrogen": ConcreteTestHydrogenStrategy,
        # "impact": ConcreteTestImpactStrategy,
    }

    # 定义类型映射
    create_type_map = {
        "cleanness": TestCleannessCreate,
        "sulphur": TestSulphurCreate,
        "hardness": TestHardnessCreate,
        "tensile": TestTensileCreate,
        "decarburization": TestDecarburizationCreate,
        "bend": TestBendCreate,
        "hydrogen": TestHydrogenCreate,
        "impact": TestImpactCreate,
    }

    update_type_map = {
        "cleanness": TestCleannessUpdate,
        "sulphur": TestSulphurUpdate,
        "hardness": TestHardnessUpdate,
        "tensile": TestTensileUpdate,
        "decarburization": TestDecarburizationUpdate,
        "bend": TestBendUpdate,
        "hydrogen": TestHydrogenUpdate,
        "impact": TestImpactUpdate,
    }

    read_type_map = {
        "cleanness": TestCleannessRead,
        "sulphur": TestSulphurRead,
        "hardness": TestHardnessRead,
        "tensile": TestTensileRead,
        "decarburization": TestDecarburizationRead,
        "bend": TestBendRead,
        "hydrogen": TestHydrogenRead,
        "impact": TestImpactRead,
    }

    object_type_map = {
        "cleanness": TestCleanness,
        "sulphur": TestSulphur,
        "hardness": TestHardness,
        "tensile": TestTensile,
        "decarburization": TestDecarburization,
        "bend": TestBend,
        "hydrogen": TestHydrogen,
        "impact": TestImpact,
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
