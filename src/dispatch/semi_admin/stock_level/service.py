from dispatch.semi_admin.semi.models import Semi
from dispatch.runout_admin.finished_product.models import FinishedProduct
from sqlalchemy.orm import Session
from dispatch.database import Base, engine, get_class_by_tablename
from sqlalchemy import func, desc, cast, Integer
from sqlalchemy_filters import apply_filters, apply_pagination
from dispatch.database_util.service import apply_model_specific_filters
from dispatch.cast.models import Cast
from dispatch.area.models import Area
from dispatch.site.models import Site
from .models import StockLevelPagination, StockLevelRead

def get_bar_type(db_session: Session):
    bar_type = []

    # 获取 semi 表中的 distinct semi_type
    semi_types = db_session.query(Semi.semi_type).distinct().all()
    if semi_types:
        bar_type.extend([item[0] for item in semi_types])
    return bar_type


def get_stock(db_session: Session,
              common: dict,
              area: list,
              id: int,
              bartype: str,
              site: str):
    query = db_session.query(
        Semi.cast_id,
        Cast.cast_code.label('cast_code'),  # 选取关联表 Cast 的 code 字段并命名为 cast_code
        Semi.area_id,
        Semi.dim1,
        Semi.dim2,
        Semi.quality_code,
        Area.code.label('area_code'),  # 选取关联表 Area 的 code 字段并命名为 area_code
        Site.code.label('site_code'),  # 选取关联表 Site 的 code 字段并命名为 site_code
        func.sum(Semi.quantity).label('quantity'),
        func.sum(Semi.length_mm).label('length_mm'),
        func.sum(Semi.defect_quantity).label('defect_quantity'),
        func.sum(Semi.scrap_quantity).label('scrap_quantity'),
        func.sum(Semi.estimated_weight_kg).label('weight'),
        func.array_agg(Semi.semi_type).label('semi_types'),  # 获取 semi_type 字段的数组
        func.max(Semi.created_at).label('latest_created_at'),
        func.concat(cast(Semi.dim1, Integer), 'x', cast(Semi.dim2, Integer)).label('semi_size'),  # 获取 dim1 和 dim2 并命名为 semi_size
        (func.sum(Semi.estimated_weight_kg) / func.sum(Semi.quantity)).label('weight_per_bloom')  # 新增字段 weight_per_bloom
    ).join(
        Cast, Semi.cast_id == Cast.id  # 连接 Cast 表
    ).join(
        Area, Semi.area_id == Area.id  # 连接 Area 表
    ).join(
        Site, Area.site_id == Site.id  # 连接 Site 表
    ).filter(
        Semi.is_deleted != 1
    )
    # 添加过滤条件
    if area:
        query = query.filter(Area.code.in_(area))
    if site:
        query = query.filter(Site.code == site)
    if id:
        query = query.filter(Semi.cast_id == id)
    if bartype:
        # 假设 semi_type 包含 bartype 中的某个值
        query = query.filter(Semi.semi_type.in_(bartype.split(',')))
    default_date = '1900-01-01'
    query = query.group_by(
        Semi.quality_code,
        Semi.cast_id,
        Cast.cast_code,
        Semi.area_id,
        Area.code,
        Site.code,
        Semi.dim1,
        Semi.dim2,
    ).order_by(
        desc(func.coalesce(func.max(Semi.created_at), default_date))
    )
    model_cls = get_class_by_tablename("Semi")
    query = apply_model_specific_filters(model_cls, query, common["current_user"], common["role"], db_session, common["fields"], common["values"])

    try:
        query, pagination = apply_pagination(query, page_number=common["page"], page_size=common["items_per_page"])
    except Exception as e:
        return StockLevelPagination(
            total=0,
            items=[],
            itemsPerPage=common["items_per_page"],
            page=common["page"]
        )
    results = query.all()

    stock_level_read_items = []
    for row in results:
        if row.semi_types:
            unique_non_empty_semi_types = set(filter(None, row.semi_types))
            bartype = ', '.join(unique_non_empty_semi_types)
        else:
            bartype = None
        scrap_quantity = row.scrap_quantity if row.scrap_quantity is not None else 0
        stock_level_read = StockLevelRead(
            area_code=row.area_code,
            site_code=row.site_code,
            quantity=row.quantity,
            weight=row.weight,
            bartype=bartype,
            defect_blms=row.defect_quantity,
            good_blms=row.quantity - scrap_quantity,
            cast_code=row.cast_code,
            quality_code=row.quality_code,
            semi_size=row.semi_size,
            length_mm=row.length_mm,
            weight_per_bloom=row.weight_per_bloom
        )
        stock_level_read_items.append(stock_level_read)
    return StockLevelPagination(
        total=pagination.total_results,
        items=stock_level_read_items,
        itemsPerPage=pagination.page_size,
        page=pagination.page_number
    )