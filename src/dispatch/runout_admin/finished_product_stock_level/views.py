from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from dispatch.database import get_db
from dispatch.database_util.service import common_parameters
from .models import StockLevelPagination

from typing import List
from .service import get_bar_type, get_stock

router = APIRouter()


@router.get("/", response_model=StockLevelPagination)
def get_finished_stock(*, db_session: Session = Depends(get_db),
                   common: dict = Depends(common_parameters),
                   area: List[str] = Query([], alias="area_code[]"),
                   id: int = Query(None, alias="cast_code"),
                   bartype: str = Query(None),
                   site: str = Query(None, alias="site"),
                   source: str = Query(None),
                   itemsPerPage: int = Query(10),
                   ):
    return get_stock(db_session=db_session, common=common, area=area, bartype=bartype, site=site)


@router.get("/bar_type")
def get_bar_types(*, db_session: Session = Depends(get_db)):
    return get_bar_type(db_session)
