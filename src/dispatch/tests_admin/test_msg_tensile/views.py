from dispatch.database import get_db
from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user

from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from .service import trigger_m362

router = APIRouter()

@router.post("/send_to_pcc_m362/{test_id}")
def send_to_pcc_m362(
    *,
    db_session: Session = Depends(get_db),
    test_id: int,
    current_user: DispatchUser = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):

    trigger_m362(db_session=db_session, test_id=test_id, background_tasks=background_tasks, current_mill_code=current_user.current_mill_code)
    return {"status": "ok"}