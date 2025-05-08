from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.database import get_db

from .models import (
    BundleMatrixRead,
    AutoPlanGet,
)

from .service import (
    get_by_auto_plan,
)

router = APIRouter()

@router.get("/by_auto_plan", response_model=BundleMatrixRead)
def get_type(
        db_session: Annotated[Session, Depends(get_db)],
        auto_plan_get_in: Annotated[AutoPlanGet, Query()],
):
    matrix = get_by_auto_plan(db_session=db_session, auto_plan_get=auto_plan_get_in)

    if not matrix:
        raise HTTPException(status_code=400, detail=f"The matrix does not exist.")

    return matrix