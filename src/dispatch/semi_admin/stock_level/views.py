from fastapi import APIRouter, Depends, Query

from dispatch.semi_admin.semi.models import Semi
from dispatch.runout_admin.finished_product.models import FinishedProduct
from sqlalchemy.orm import Session
from dispatch.database import get_db
from dispatch.database_util.service import common_parameters, apply_model_specific_filters
from .models import StockLevelPagination, StockLevelRead

from typing import List, Optional
from .service import get_bar_type, get_stock

router = APIRouter()


@router.get("/", response_model=StockLevelPagination)
def get_semi_stock(*, db_session: Session = Depends(get_db),
                   common: dict = Depends(common_parameters),
                   area: List[str] = Query([], alias="area_code[]"),
                   id: int = Query(None, alias="cast_code"),
                   bartype: str = Query(None),
                   site: str = Query(None, alias="site"),
                   source: str = Query(None),
                   itemsPerPage: int = Query(10),
                   ):
    return get_stock(db_session=db_session, common=common, area=area, id=id, bartype=bartype, site=site)


@router.get("/bar_type")
def get_bar_types(*, db_session: Session = Depends(get_db)):
    return get_bar_type(db_session)
