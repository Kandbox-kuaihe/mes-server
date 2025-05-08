from dispatch.tests_admin.test_msg_impact.models import TestMsgImpact, TestMsgImpactCreate


def create(*, db_session, test_msg_impact_in: TestMsgImpactCreate) -> TestMsgImpact:
    created = TestMsgImpact(**test_msg_impact_in.model_dump())
    db_session.add(created)
    db_session.commit()
    return created


def get_by_testing_machine(*, db_session, testing_machine: str) -> TestMsgImpact:
    return db_session.query(TestMsgImpact).filter(TestMsgImpact.testing_machine == testing_machine).one_or_none()
