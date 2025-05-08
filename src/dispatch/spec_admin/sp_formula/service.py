from sqlalchemy.sql import and_

from dispatch.spec_admin.sp_formula.models import SpFormula
from dispatch.spec_admin.spmainel_other_element.models import SpmainelOtherElement


def get_predicts(*, db_session, code, spmainel, length=1):
    formula_data = spmainel.flex_form_data["Formula"]

    if any(entry['Name'] == code for entry in formula_data) is not None:
        sp_query = db_session.query(SpFormula).filter(SpFormula.formula_code == code).first()
    return sp_query.tx_formula.ljust(length)[:length] if sp_query else "".ljust(length)[:length]