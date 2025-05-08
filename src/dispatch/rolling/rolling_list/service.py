import csv
import re
from tempfile import NamedTemporaryFile
from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from sqlalchemy import or_, text
from sqlalchemy.sql import and_, desc
import pandas as pd
from datetime import datetime, timedelta
from copy import copy

from dispatch.mill.models import Mill
from dispatch.product_size.models import ProductSize
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.product_category.service import get_by_code as product_category_get_by_code
from dispatch.product_class.service import get_by_code as product_class_get_by_code
from dispatch.product_category.service import get as product_category_get_by_id
from dispatch.product_class.service import get as product_class_get_by_id
from dispatch.runout_admin.runout_list.service import get_by_rolling_id as get_runout_list_by_rolling_id
from dispatch.runout_admin.runout_list.service import get_runout_code_min, get_runout_code_max
from dispatch.product_class.models import ProductClass
from dispatch.product_category.models import ProductCategory
from .models import Rolling, RollingCreate, RollingUpdate
import logging, openpyxl
from sqlalchemy import func

from dispatch.order_admin.order_item.models import OrderItem

from dispatch.log import getLogger
from ...config import get_mill_ops, MILLEnum, DEV_DATABASE_SCHEMA

log = getLogger(__name__)


def get(*, db_session, id: int) -> Optional[Rolling]:
    res = db_session.query(Rolling).filter(Rolling.id == id).one_or_none()
    category_result = product_category_get_by_id(db_session=db_session, id=res.product_category_id)
    if category_result:
        res.product_category_code = category_result.code
    else:
        res.product_category_code = None

    class_result = product_class_get_by_id(db_session=db_session, id=res.product_class_id)
    if class_result:
        res.product_class_code = class_result.code
    else:
        res.product_class_code = None
    return res

def get_by_code(*, db_session, code: str, mill_id: int) -> Optional[Rolling]:
    return db_session.query(Rolling).filter(Rolling.rolling_code == code, Rolling.mill_id == mill_id).first()

def get_by_id(*, db_session, id: int) -> Optional[Rolling]:
    return db_session.query(Rolling).filter(Rolling.id == id).one_or_none()

def get_latest_20(*, db_session) -> List[Rolling]:
    return db_session.query(Rolling).order_by(Rolling.id.desc()).limit(20).all()

def get_by_number_of_rollings(*, db_session, number_of_rollings,mill_id) -> List[Rolling]:
    return  db_session.query(Rolling).filter(
                Rolling.rolling_status.notin_(["Closed", "Completed"]),  # Exclude "Closed" and "Completed"
                Rolling.programmed_start_date > datetime.utcnow(),# Start date must be greater than the current date
                Rolling.mill_id == mill_id  
            ).order_by(Rolling.programmed_start_date.asc()).limit(number_of_rollings).all()  # Order by ascending start date.limit(20)  # Limit to 20 results

def get_by_openstatus_limit_40(*, db_session, mill_id) -> List[Rolling]:
    return  db_session.query(Rolling).filter(
                Rolling.rolling_status.notin_(["Closed", "Completed"]),  # Exclude "Closed" and "Completed"
                Rolling.programmed_start_date > datetime.utcnow(),  # Start date must be greater than the current date
                Rolling.mill_id == mill_id
            ).order_by(Rolling.programmed_start_date.asc()).limit(40).all()  # Order by ascending start date.limit(20)  # Limit to 40 results

def get_by_shot_code(*, db_session, code: str) -> Optional[Rolling]:
    return db_session.query(Rolling).filter(Rolling.short_code == code).one_or_none()

def get_by_product_type_id(*, db_session, product_type_id: int):
    """
    Returns a rolling entry given a product_type_id.
    """
    return db_session.query(Rolling).filter(Rolling.product_type_id == product_type_id).one_or_none()


def get_by_rolling_code_mill(*, db_session, rolling_code: str, mill_id: int) -> Optional[Rolling]:
    return db_session.query(Rolling).filter(
        and_(Rolling.rolling_code == rolling_code, Rolling.mill_id == mill_id)
    ).order_by(Rolling.id.desc()).first()

def get_by_product_type_short_code(*, db_session, product_type_code:str , short_code: str) -> Optional[Rolling]:
    return db_session.query(Rolling).filter(
        and_(Rolling.rolling_code.like(f"{product_type_code}%"), Rolling.short_code == short_code)
    ).one_or_none()



def get_or_create_by_code(*, db_session, rolling_in) -> Rolling:
    if rolling_in.id:
        q = db_session.query(Rolling).filter(
            Rolling.id == rolling_in.id)
    else:
        # return None
        raise Exception("The Rolling.id can not be None.")

    instance = q.first()

    if instance:
        return instance

    return create(db_session=db_session, rolling_in=rolling_in)


def get_all(*, db_session) -> List[Optional[Rolling]]:
    return db_session.query(Rolling)


def get_mill_all(*, db_session, current_user) -> List[Optional[Rolling]]:
    model = Rolling
    query = db_session.query(model)

    # 应用模型特定的过滤逻辑
    if current_user.current_mill_id != -1 and "mill_id" in model._sa_class_manager.keys():
        query = query.filter(or_(model.mill_id == current_user.current_mill_id,
                                 model.mill_id == None))

    # 如果有模型特定的过滤器，应用它们
    model_map = {
        # Mill: [restricted_mill_filter], 
    }

    filters = model_map.get(model, [])
    for f in filters:
        query = f(query, current_user, current_user.role)

    # 返回经过所有过滤器的查询结果
    return query.all()


def create(*, db_session, rolling_in: RollingCreate) -> Rolling:
    rolling = Rolling(**rolling_in.dict(exclude={"mill", "product_category", "product_class", "product_type", "product_category_code", "product_class_code"}))
    db_session.add(rolling)
    db_session.commit()
    return rolling


def new_create_rolling(*, db_session, rolling_in: RollingCreate) -> Rolling:
    # product_category_code = rolling_in.product_category_code
    # product_class_code = rolling_in.product_class_code

    # # 获取对应的 product_class 和 product_category
    # result_pclass = product_class_get_by_code(db_session=db_session, code=product_class_code)
    # result_pcategory = product_category_get_by_code(db_session=db_session, code=product_category_code)

    # 设置外键 ID
    # rolling_in.product_category_id = result_pcategory.id
    # rolling_in.product_class_id = result_pclass.id

    mill=None
    product_size = None
    if rolling_in.mill_id:
        mill = db_session.query(Mill).filter(Mill.id == rolling_in.mill_id).first()
        rolling_in.mill_code = mill.code
    if rolling_in.product_size_id:
        product_size = db_session.query(ProductSize).filter(ProductSize.id == rolling_in.product_size_id).first()
    # 创建 Rolling 实例时排除不需要的字段
    rolling = Rolling(**rolling_in.dict(exclude={"product_category_code", "product_class_code","mill","product_size","product_size_code"}),mill=mill,product_size=product_size)
    db_session.add(rolling)
    db_session.commit()
    return rolling


def create_all(*, db_session,
               rolling_in: List[RollingCreate]) -> List[Rolling]:
    rolling = [Rolling(id=d.id) for d in rolling_in]
    db_session.bulk_save_insert(rolling)
    db_session.commit()
    db_session.refresh()
    return rolling


def update(*, db_session, rolling: Rolling,
           rolling_in: RollingUpdate) -> Rolling:
    mill= None
    product_size = None
    # product_category_code = rolling_in.product_category_code
    # product_class_code = rolling_in.product_class_code

    # 获取对应的 product_class 和 product_category
    # result_pclass = product_class_get_by_code(db_session=db_session, code=product_class_code)
    # result_pcategory = product_category_get_by_code(db_session=db_session, code=product_category_code)

    if rolling_in.mill_code:
        mill = db_session.query(Mill).filter(Mill.code == rolling_in.mill_code).first()
    if rolling_in.product_size_id:
        product_size = db_session.query(ProductSize).filter(ProductSize.id == rolling_in.product_size_id).first()

    # 设置外键 ID
    # rolling_in.product_category_id = result_pcategory.id
    # rolling_in.product_class_id = result_pclass.id
    rolling_in.mill_id = mill.id if mill else None
    

    update_data = rolling_in.model_dump(
        exclude={"mill_code","mill","product_size"},
    )

    for key, value in update_data.items():
        setattr(rolling, key, value)
    db_session.add(rolling)
    db_session.commit()
    return rolling


def update_status(*, db_session, rolling: Rolling, rolling_in: RollingUpdate) -> Rolling:
    for key, value in rolling_in.dict(exclude={}).items():
        setattr(rolling, key, value)
    db_session.commit()
    return rolling


def delete(*, db_session, id: int):
    rolling = db_session.query(Rolling).filter(
        Rolling.id == id).first()
    orderItem = db_session.query(OrderItem).filter(
        OrderItem.rolling_id == id).all()
    if not orderItem:
        db_session.delete(rolling)
        db_session.commit()
        return
    else:
        raise HTTPException(status_code=400, detail="The rolling has orderItem, can not delete.")


def import_file(*, db_session, file, current_user:DispatchUser) -> Rolling:
    wb = openpyxl.load_workbook(file.file, data_only=True)
    ws = wb.active

    success_sum = 0
    repeat_sum = 0
    max_id = db_session.query(func.max(Rolling.id)).scalar()
    temp_max_id = max_id
    create_dict = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[2] is None:
            continue
        # 拆分section字段
        section = row[2].strip().split(' ')
        dim1 = section[0]
        dim2 = section[1]
        start_date = row[10] if row[10] else None

        # 拼接rolling_code 字段
        rolling_code = '-'.join([row[3], dim1, dim2, row[1]])
        create_dict.append({
            # 'mill_code': row[1],
            'rolling_seq': row[0],
            'rolling_code': rolling_code,
            'rolling_dim1': dim1,
            'rolling_dim2': dim2,
            'short_code': row[1],
            'product_type': row[3],
            'semi_size': row[7],
            'comment': row[9],
            'rolling_status': "Open",
            'rolling_rate': row[14],
            'std_time_75_pct': row[15],
            'rolling_time_total': row[16],
            'programmed_start_date': row[10],
            'duration_minutes': row[12],
            'programmed_tonnage': row[4],
            'week_number': row[19],
            'year': start_date.year if start_date else None,
            'created_by': current_user.email,
            'updated_by': current_user.email
        })
    print("create_dict", create_dict)
    add_list = []
    if len(create_dict) >= 1:
        for cd in create_dict:
            # 判断是否已存在
            rolling_data = db_session.query(Rolling).filter(Rolling.rolling_code == cd.get('rolling_code')).first()
            if rolling_data:
                repeat_sum += 1
                rolling_data.rolling_seq = cd.get('rolling_seq')
                rolling_data.semi_size = cd.get('semi_size')
                rolling_data.rolling_status = cd.get('rolling_status')
                rolling_data.comment = cd.get('comment')
                rolling_data.rolling_rate = cd.get('rolling_rate')
                rolling_data.std_time_75_pct = cd.get('std_time_75_pct')
                rolling_data.rolling_time_total = cd.get('rolling_time_total')
                rolling_data.programmed_start_date = cd.get('programmed_start_date')
                rolling_data.duration_minutes = cd.get('duration_minutes')
                rolling_data.programmed_tonnage = cd.get('programmed_tonnage')
                rolling_data.week_number = cd.get('week_number')
                rolling_data.updated_by = cd.get('updated_by')
                rolling_data.year = cd.get('year')
            else:
                # 由于客户说 import 功能报错，故临时指定id
                # temp_max_id += 1
                # cd['id'] = temp_max_id

                # product_class = db_session.query(ProductClass).filter(ProductClass.code == cd.get('product_type')).first()
                # if product_class:
                #     cd['product_class_id'] = product_class.id

                # product_category = db_session.query(ProductCategory).filter(ProductCategory.dim1 == cd.get('rolling_dim1'),
                #                                                             ProductCategory.dim2 == cd.get('rolling_dim2')).first()
                # if product_category:
                #     cd['product_category_id'] = product_category.id

                mill = db_session.query(Mill).filter(Mill.id == current_user.current_mill_id).first()


                product_size_code = "-".join([cd.get('product_type'), cd.get('rolling_dim1'), cd.get('rolling_dim2')])
                product_size = db_session.query(ProductSize).filter(ProductSize.code == product_size_code, ProductSize.mill_id == mill.id).first()
                if product_size:
                    cd['product_size_id'] = product_size.id
                
                if mill:
                    cd['mill'] = mill
                    cd['mill_code'] = mill.code

                add_list.append(Rolling(**cd))

    if len(add_list) > 0:
        success_sum = len(add_list)
        db_session.add_all(add_list)
        
        amend_rolling_attach(db_session=db_session)
    db_session.commit()
    return {
        "success_sum": success_sum,
        "repeat_sum": repeat_sum
    }


def import_csv_file(*, db_session, file, current_user):
    created_num = 0
    updated_num = 0
    created_list = []
    curr_mill_id = current_user.current_mill_id
    curr_mill_code = current_user.current_mill_code
    data = []
    # 匹配浮点型字符串
    pattern = r'^[-+]?\d*\.?\d+$'
    with open(file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=' ', skipinitialspace=True)
        for row in reader:
            # 过滤掉空字符串元素
            row = list(filter(None, row))
            # 提取前9个元素
            first_nine = row[:9]
            # 第10个元素是duration hours，但是可能为空
            ten = row[9]
            if ten.isdigit() or bool(re.match(pattern, ten)):
                ten = float(ten)
                is_existed_hours = True
            else:
                ten = 0
                is_existed_hours = False

            # 提取后三个元素
            last_three = row[-3:]
            # 合并中间的元素为 status
            middle_combined = " ".join(row[10:-3]) if is_existed_hours else " ".join(row[9:-3])
            new_row = first_nine + [ten] + [middle_combined] + last_three
            data.append(new_row)

    for row in data:
        rolling_seq = row[0] if row[0] else 0
        short_code = row[1]
        rolling_dim1 = row[2]
        rolling_dim2 = row[3]
        product_type = row[4]
        tonnage = row[5] if row[5] else 0
        planned_week_ending = row[6]
        # duration = row[7]
        semi_size = row[8]
        duration = row[9]
        comment = row[10]
        if all([row[12], row[11]]):
            programmed_start_time = datetime.strptime(f"{row[12]} {row[11]}", "%d/%m/%y %H:%M:%S")
        else:
            programmed_start_time = None

        year = programmed_start_time.year if programmed_start_time else None
        week_number = programmed_start_time.isocalendar()[1] if programmed_start_time else None
        rolling_code = "-".join([product_type, rolling_dim1, rolling_dim2, short_code])

        rolling_obj: Rolling | None = db_session.query(Rolling).filter(
            and_(
                Rolling.rolling_code == rolling_code,
                Rolling.mill_id == curr_mill_id
            )
        ).order_by(desc(Rolling.id)).first()

        if rolling_obj:
            orig_seq = rolling_obj.rolling_seq
            orig_tonnage = rolling_obj.programmed_tonnage
            orig_semi_size = rolling_obj.semi_size
            orig_duration = rolling_obj.duration_minutes
            orig_rolling_time_total = rolling_obj.rolling_time_total
            orig_comment = rolling_obj.comment

            rolling_obj.rolling_seq = int(float(rolling_seq))
            rolling_obj.programmed_tonnage = float(tonnage)
            rolling_obj.semi_size = semi_size
            rolling_obj.week_number = week_number
            rolling_obj.comment = comment
            rolling_obj.mill_code = curr_mill_code
            rolling_obj.duration_minutes = int(float(duration) * 60) if duration else orig_duration
            rolling_obj.rolling_time_total = duration if duration else orig_rolling_time_total
            rolling_obj.updated_at = datetime.now()
            db_session.add(rolling_obj)
            updated_num += 1
            log.info(
                f"""Update rolling: {rolling_obj.id}:{rolling_code}, rolling_seq: {orig_seq} -> {rolling_seq}, 
                programmed_tonnage: {orig_tonnage} -> {tonnage}, semi_size: {orig_semi_size} -> {semi_size}, 
                duration_minutes: {orig_duration} -> {rolling_obj.duration_minutes}, 
                rolling_time_total: {orig_rolling_time_total} -> {rolling_obj.rolling_time_total}, 
                comment: {orig_comment} -> {rolling_obj.comment}"""
            )
        else:
            rolling_info = {
                "rolling_seq": int(float(rolling_seq)),
                "rolling_code": rolling_code,
                "rolling_dim1": rolling_dim1,
                "rolling_dim2": rolling_dim2,
                "short_code": short_code,
                "product_type": product_type,
                "programmed_tonnage": float(tonnage),
                "semi_size": semi_size,
                "rolling_status": "Open",
                "programmed_start_date": programmed_start_time,
                "week_number": week_number,
                "year": str(year),
                "created_at": datetime.now(),
                "created_by": current_user.email,
                "updated_at": datetime.now(),
                "updated_by": current_user.email,
                "mill_id": curr_mill_id,
                "mill_code": curr_mill_code,
                "duration_minutes": int(float(duration) * 60) if duration else 0,
                "rolling_time_total": duration if duration else 0
            }
            # product_class = db_session.query(ProductClass).filter(
            #     and_(ProductClass.code == product_type, ProductClass.mill_id == curr_mill_id)
            # ).first()
            # product_category_code = "-".join([rolling_dim1.strip(), rolling_dim2.strip()])
            # product_category = db_session.query(ProductCategory).filter(
            #     and_(ProductCategory.code == product_category_code,
            #          ProductCategory.mill_id == curr_mill_id
            #     )
            # ).first()
            # if product_class:
            #     rolling_info["product_class_id"] = product_class.id

            # if product_category:
            #     rolling_info["product_category_id"] = product_category.id

            product_size_code = "-".join([product_type, rolling_dim1.strip(), rolling_dim2.strip()])
            product_size = db_session.query(ProductSize).filter(ProductSize.code == product_size_code, ProductSize.mill_id == curr_mill_id).first()
            if product_size:
                rolling_info['product_size_id'] = product_size.id
            
            created_list.append(Rolling(**rolling_info))
    
    if created_list:
        created_num = len(created_list)
        db_session.add_all(created_list)
    
    db_session.commit()
    log.info(f"Import rolling from FTP file, created_num: {created_num}, updated_num: {updated_num}")
    return {"created_num": created_num, "updated_num": updated_num}


def amend_rolling_attach(db_session):
    result = db_session.execute(text(f"""update
        {DEV_DATABASE_SCHEMA}.order_item oi
        set
            rolling_id = (
                select
                    r.id
                from
                    {DEV_DATABASE_SCHEMA}.rolling r
                where
                    oi.product_code = r.product_type
                    and oi.product_dim1 = r.rolling_dim1
                    and oi.product_dim2 = r.rolling_dim2
                    and oi.rolling_code = r.short_code
                    and oi.plant_id = r.mill_id
            )
        where oi.rolling_id is null"""))
    db_session.commit()

    return result


def get_codes(*, db_session):
    codes = []
    result = db_session.query(Rolling.rolling_code).all()
    if not result:
        return codes
    for i in result:
        codes.append(i[0])
    return codes


def get_rolling_ids_by_code(*, db_session, q: str) -> List[int]:
    return db_session.query(Rolling.id).filter(Rolling.rolling_code.contains(q)).all()


def get_rolling_id_codes(*, db_session, code: str):
    rolling_id_codes = db_session.query(Rolling.id, Rolling.rolling_code).filter(Rolling.rolling_code.contains(code)).all()
    return rolling_id_codes


def export_to_csv(data_list: List[Rolling]):
    data = []
    for item in data_list:
        rolling_info_list = item.rolling_code.split('-')
        if len(rolling_info_list) < 3:
            continue

        roll_ni = rolling_info_list[3] if len(rolling_info_list) > 3 else ''
        serial_size = f' {rolling_info_list[1]} {rolling_info_list[2]}'
        product = rolling_info_list[0]

        # 获取 programmed start date 当前周周一
        # week_number = item.programmed_start_date.isocalendar()[1]
        # monday = datetime.strptime(f'{item.programmed_start_date.year}-W{week_number}-1', '%G-W%V-%u')
        # 计算该周周六的日期作为 planned week ending，在周一的基础上加上 5 天
        # sunday = monday + timedelta(days=5)
        
        data.append({
            "SEQ": item.rolling_seq,
            "ROLL NI": roll_ni,
            "SERIAL SIZE": serial_size,
            "PRODUCT": product,
            "TONNAGE": item.programmed_tonnage,
            "PLANNED WEEK ENDING": None,
            "DURATION": round(item.duration_minutes / 60, 1) if item.duration_minutes else None,
            "SEMI SIZE": item.semi_size,
            "STATUS": item.rolling_status,
            "START TIME": item.programmed_start_date.strftime("%H:%M:%S") if item.programmed_start_date else None,
            "START DATE": item.programmed_start_date.strftime("%d/%m/%Y") if item.programmed_start_date else None,
            "COMMENT": item.comment
        })

    columns = [
        "SEQ", "ROLL NI", "SERIAL SIZE", "PRODUCT", "TONNAGE", "PLANNED WEEK ENDING", "DURATION", "SEMI SIZE",
        "STATUS", "START TIME", "START DATE", "COMMENT"
    ]
    df = pd.DataFrame(data, columns=columns)
    with NamedTemporaryFile(mode="w+", suffix=".csv", delete=False) as temp_csv:
        tmp_file_path = temp_csv.name
        # 保存 Excel 文件到指定路径
        df.to_csv(tmp_file_path, index=False)
    
    return tmp_file_path


def export_to_excel(db_session, data_list):
    # 获取数据
    data = []

    for item in data_list:
        rolling_info_list = item.rolling_code.split('-')
        if len(rolling_info_list) < 3:
            continue
        roll_no = rolling_info_list[3] if len(rolling_info_list) > 3 else ''
        section = f' {rolling_info_list[1]} {rolling_info_list[2]}'
        pc = rolling_info_list[0]

        tonnes = db_session.query(func.SUM(OrderItem.tonnage)).filter(OrderItem.rolling_id == item.id).scalar()

        data.append({
            "Sequence": item.rolling_seq,
            "Roll No": roll_no,
            "Section": section,
            "PC": pc,
            "Tonnes": tonnes,
            "Day": item.programmed_start_date.strftime('%a') if item.programmed_start_date else None,
            "Start Time": item.programmed_start_date.strftime('%H:%M') if item.programmed_start_date else None,
            "Semi Size": item.semi_size,
            "Roll Change Hours": None,
            "Comments": item.rolling_status,
            "Hours": item.programmed_start_date,  
            "Date": item.programmed_start_date.strftime('%Y-%m-%d') if item.programmed_start_date else None,
            "Cumulative Minutes": None,  
            "Minutes": item.duration_minutes,
            "Rolling Rate": item.rolling_rate,
            "Std Time 75 Pct": item.std_time_75_pct,
            "Roll Time Total": item.rolling_time_total,
            "Rolling": f'{pc} {section}',
            "Find Day": None,  
            "Week No": item.week_number,
            "Week Ending": None,
            "Programmed Total Tons": item.programmed_tonnage,
        })

    # 定义 Excel 的列
    columns = [
        "Sequence", "Roll No", "Section", "PC", "Tonnes", "Day", "Start Time", "Semi Size", 
        "Roll Change Hours", "Comments", "Hours", "Date", "Cumulative Minutes", "Minutes",
        "Rolling Rate", "Std Time 75 Pct", "Roll Time Total", "Rolling", "Find Day", 
        "Week No", "Week Ending", "Programmed Total Tons",
    ]
    
    # 创建 DataFrame
    df = pd.DataFrame(data, columns=columns)
    file_name = f"rolling_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    tmp_file_path = f"/tmp/{file_name}"  # 指定临时文件的保存路径
    
    # 保存 Excel 文件到指定路径
    df.to_csv(tmp_file_path, index=False)

    return tmp_file_path


def get_id_by_code(*, db_session, rolling_code: str):
    return db_session.query(Rolling.id).filter(Rolling.rolling_code == rolling_code).scalar()

def get_rolling_start_and_end_date(*, db_session, rolling_id: int):
    ls = []
    runout_list = get_runout_list_by_rolling_id(db_session=db_session, rolling_id=rolling_id)
    rolling_start_date = min([runout.created_at for runout in runout_list]) if runout_list else None
    runout_from = get_runout_code_min(db_session=db_session, rolling_id=rolling_id)
    rolling_end_date = max([runout.created_at for runout in runout_list]) if runout_list else None
    runout_to = get_runout_code_max(db_session=db_session, rolling_id=rolling_id)
    ls.append((rolling_start_date, runout_from, rolling_end_date, runout_to))
    return ls[0] if ls else (None, None, None, None)

# def get_by_first_product_type_code(*, db_session, product_type_code: str, dim3: str) -> Optional[Rolling]:
#     return db_session.query(Rolling).filter(
#         Rolling.rolling_code.like(f"{product_type_code.strip()}-%"),
#         Rolling.rolling_dim3 == dim3
#     ).first()

def get_by_first_rolling_by_product_size_code(*, db_session, product_size_code: str) -> Optional[Rolling]:
    return db_session.query(Rolling).filter(Rolling.rolling_code.like(f"{product_size_code.strip()}-%"),get_mill_ops(Rolling.mill_id) == MILLEnum.MILL1).first()

def order_item_kg_rolling_id(db_session, rolling_id):
    if rolling_id:
        kg = db_session.query(func.sum(OrderItem.tonnage)).filter(OrderItem.rolling_id == rolling_id).scalar()
        return kg or 0
    return 0