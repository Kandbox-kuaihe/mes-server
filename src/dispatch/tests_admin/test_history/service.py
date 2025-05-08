from typing import List

from fastapi import HTTPException

from .models import TestHistory, TestHistoryRead
import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from dispatch.system_admin.auth.service import get_current_user
from dispatch.system_admin.auth.models import DispatchUser


def bulk_create_test_history(
    *, db_session, test_history_in: List[dict]
):
   
    if not test_history_in:
        return []

    try:
        db_session.bulk_insert_mappings(
            TestHistory, test_history_in
        )
        db_session.commit()
        return test_history_in
    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def confirm_history(*, db_session, history_in: TestHistoryRead, current_user: DispatchUser = Depends(get_current_user)):
    if not history_in:
            raise HTTPException(status_code=400, detail="History information is required.")
    try:
        # 获取当前时间戳
        confirm_at = datetime.datetime.utcnow()
        history_id = history_in.id
        if not history_id:
            raise HTTPException(status_code=400, detail="History entry must have an 'id'.")
        test_history = db_session.query(TestHistory).filter(TestHistory.id == history_id).first()
        if not test_history:
            raise HTTPException(status_code=404, detail=f"TestHistory with id {history_id} not found.")

        test_history.confirm_by = current_user.email
        test_history.confirm_at = confirm_at

        db_session.commit()
        return test_history
    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=400, detail=str(e))