from sqlalchemy import select

from .models import (
    BundleMatrix,
    BundleMatrixRead,
    AutoPlanGet,
)

def get_by_auto_plan(*, db_session, auto_plan_get: AutoPlanGet) -> BundleMatrixRead | None:
    stmt = select(BundleMatrix).where(
        BundleMatrix.cust_no == auto_plan_get.cust_no,
        BundleMatrix.add_no == auto_plan_get.add_no,
        BundleMatrix.roll_ref == auto_plan_get.roll_ref,
        BundleMatrix.kg_per_metre == auto_plan_get.kg_per_metre,
        BundleMatrix.max_bar_length == auto_plan_get.max_bar_length,
        BundleMatrix.spec_no == auto_plan_get.spec_no,
    )
    bundle_matrix = db_session.scalar(stmt)

    return bundle_matrix


def get_num_bars(*, db_session, bundle_maxtrix_info: dict):
    bundle_maxtrix_obj = db_session.query(BundleMatrix).filter(
        BundleMatrix.form == bundle_maxtrix_info.get("form"),
        BundleMatrix.size == bundle_maxtrix_info.get("size"),
        BundleMatrix.kg_per_metre == bundle_maxtrix_info.get("kg_per_metre"),
        BundleMatrix.max_bar_length == bundle_maxtrix_info.get("max_bar_length")
    ).first()
    return bundle_maxtrix_obj.num_bars if bundle_maxtrix_obj else 0
