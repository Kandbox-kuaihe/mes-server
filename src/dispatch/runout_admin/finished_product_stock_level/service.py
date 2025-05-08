from dispatch.runout_admin.finished_product.models import FinishedProduct
from sqlalchemy.orm import Session
from dispatch.database import get_class_by_tablename
from sqlalchemy import func, desc
from sqlalchemy_filters import apply_pagination
from dispatch.database_util.service import apply_model_specific_filters
from dispatch.cast.models import Cast
from dispatch.area.models import Area
from dispatch.site.models import Site
from .models import StockLevelPagination, StockLevelRead


def get_bar_type(db_session: Session):
    bar_type = []
    finished_types = db_session.query(FinishedProduct.type).distinct().all()
    if finished_types:
        bar_type.extend([item[0] for item in finished_types])

    return bar_type


def get_stock(db_session: Session,
              common: dict,
              area: list,
              bartype: str,
              site: str):
    query = db_session.query(
        FinishedProduct.area_id,
        Area.code.label('area_code'),  # 选取关联表 Area 的 code 字段并命名为 area_code
        Site.code.label('site_code'),  # 选取关联表 Site 的 code 字段并命名为 site_code
        func.sum(FinishedProduct.quantity).label('quantity'),
        func.sum(FinishedProduct.length_mm).label('length_mm'),
        func.sum(FinishedProduct.defect_quantity).label('defect_quantity'),
        func.sum(FinishedProduct.estimated_weight_kg).label('weight'),
        func.array_agg(FinishedProduct.type).label('finished_prouduct_types'),  # 获取 finished_product_type 字段的数组
        func.max(FinishedProduct.created_at).label('latest_created_at'),
        func.count(FinishedProduct.id).label('no_of_finished_product'),
        (func.sum(FinishedProduct.estimated_weight_kg) / func.sum(FinishedProduct.quantity)).label('weight_per_bloom')  # 新增字段 weight_per_bloom
    ).join(
        Area, FinishedProduct.area_id == Area.id  # 连接 Area 表
    ).join(
        Site, Area.site_id == Site.id  # 连接 Site 表
    ).filter(
        FinishedProduct.is_deleted != 1
    )
    # 添加过滤条件
    if area:
        query = query.filter(Area.code.in_(area))
    if site:
        query = query.filter(Site.code == site)
    if bartype:
        # 假设 finished_product_type 包含 bartype 中的某个值
        query = query.filter(FinishedProduct.type.in_(bartype.split(',')))
    default_date = '1900-01-01'
    query = query.group_by(
        FinishedProduct.area_id,
        Area.code,
        Site.code
    ).order_by(
        desc(func.coalesce(func.max(FinishedProduct.created_at), default_date))
    )
    model_cls = get_class_by_tablename("FinishedProduct")
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
        if row.finished_prouduct_types:
            unique_non_empty_finished_product_types = set(filter(None, row.finished_prouduct_types))
            bartype = ', '.join(unique_non_empty_finished_product_types)
        else:
            bartype = None
        stock_level_read = StockLevelRead(
            area_code=row.area_code,
            site_code=row.site_code,
            no_of_finished_product=row.no_of_finished_product,
            quantity=row.quantity,
            weight=row.weight,
            bartype=bartype,
            defect_blms=row.defect_quantity,
            good_blms=row.quantity - row.defect_quantity if row.defect_quantity is not None else row.quantity,
            length_mm=row.length_mm,
            weight_per_bloom=row.weight_per_bloom,
        )
        stock_level_read_items.append(stock_level_read)
    return StockLevelPagination(
        total=pagination.total_results,
        items=stock_level_read_items,
        itemsPerPage=pagination.page_size,
        page=pagination.page_number
    )
