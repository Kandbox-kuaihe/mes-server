import logging
import os

import pandas as pd
from io import BytesIO
from fastapi import APIRouter
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from sqlalchemy import  and_
from .models import Cast, CastUpdate, CastCreate

from dispatch.cast_spec import service as cast_spec_service
from sqlalchemy import select
from dispatch.semi_admin.semi.models import Semi


logging.basicConfig(level=logging.INFO)

from dispatch.log import getLogger
log = getLogger(__name__)
router = APIRouter()



def get(*, db_session, id: int) -> Optional[Cast]:
    """Returns an cast given an cast id."""
    return db_session.query(Cast).filter(Cast.id == id).first()


def get_by_code(*, db_session, code: str) -> Optional[Cast]:
    """Returns an cast given an cast code address."""
    if not code: return
    return db_session.query(Cast).filter(Cast.cast_code == code).first()

def get_by_bos_cast_code(*, db_session, code: str) -> Optional[Cast]:
    """Returns an cast given an cast code address."""
    if not code: return
    return db_session.query(Cast).filter(Cast.bos_cast_code == code).first()

def get_default_cast(*, db_session ) -> Optional[Cast]:
    """Returns an cast given an cast code address."""
    return db_session.query(Cast).first()


def get_all(*, db_session) -> List[Optional[Cast]]:
    """Returns all casts."""
    return db_session.query(Cast)


def get_by_mill(*, db_session, mill_id) -> List[Optional[Cast]]:
    """Returns all casts."""
    return db_session.query(Cast).filter(Cast.mill_id == mill_id).all()


def message_create(*, db_session, **kwargs) -> Cast:
    cast_in = CastCreate(**kwargs)
    contact = create(db_session=db_session, cast_in=cast_in)
    return contact


def create(*, db_session, cast_in: CastCreate) -> Cast:
    """Creates an cast."""
    cast = get_by_code(db_session=db_session,code=cast_in.cast_code)

    if cast:
        raise HTTPException(status_code=400, detail="The cast with this code already exists.")

    contact = Cast(**cast_in.dict(exclude={"flex_form_data", "mill"})
                    )

    if not contact.long_cast_code:
        contact.long_cast_code = contact.cast_code
    contact.created_at = datetime.now(timezone.utc)

    db_session.add(contact)
    db_session.commit()
    try:
        from dispatch.contrib.cover.get_spec_service.utils import batch_insert
        result = batch_insert(db_session=db_session, cast=contact)
        log.info(f"push cast spec success {result}")
    except:
        log.warning(f"push cast spec fail {contact.id}")
    return contact

def update(
    *,
    db_session,
    cast: Cast,
    cast_in: CastUpdate,
) -> Cast:

    update_data = cast_in.dict(
        exclude={"flex_form_data", "mill", "quality"},
    )
    for field, field_value in update_data.items():
        setattr(cast, field, field_value)

    cast.flex_form_data = cast_in.flex_form_data
    cast.updated_at = datetime.now(timezone.utc)
    cast.updated_by = cast_in.updated_by
    db_session.add(cast)
    db_session.commit()

    try:
        from dispatch.contrib.cover.get_spec_service.utils import batch_insert
        cast_spec_service.delete_by_cast_id(db_session=db_session, cast_id=cast.id)
        result = batch_insert(db_session=db_session, cast=cast)
        log.info(f"push cast spec success {result}")
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except:
        log.warning(f"push cast spec fail {cast.id}")
    return cast

def import_file(db_session: Session, files: List[UploadFile], current_user):
    """
    处理上传的两个 Excel 文件并插入或更新数据库中的数据。
    
    :param db_session: 数据库会话
    :param files: 上传的 Excel 文件列表
    :param current_user: 当前用户，用于操作记录
    :return: 处理结果（成功的个数和更新的个数）
    """
    
    # 确保传入了两个文件
    if len(files) != 2:
        raise HTTPException(status_code=400, detail="Exactly two Excel files are required.")
    # 读取文件内容
    try:
        df1 = pd.read_excel(BytesIO(files[0].file.read()), header=None, skiprows=4)
        df2 = pd.read_excel(BytesIO(files[1].file.read()), header=None, skiprows=4)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading files: {str(e)}")

    try:
        if df1.iloc[0, 20] == 'C':  # 检查 df1 中第20列的值是否为 'C'
            df1, df2 = df2, df1
        elif df2.iloc[0, 20] == 'C':  # 检查 df2 中第20列的值是否为 'C'
            df1, df2 = df1, df2
        else:
            raise HTTPException(status_code=400, detail="Check file format")
    except IndexError:
        raise HTTPException(status_code=400, detail="Check file format")

    # 清理数据：确保 cast_code 列为字符串类型，去除多余的 `.0` 后缀
    df1[4] = df1[4].astype(str).str.replace(r'\.0$', '', regex=True)
    df2[3] = df2[3].astype(str).str.replace(r'\.0$', '', regex=True)

    
    # 获取当前时间
    current_time = datetime.utcnow()

    # 获取数据库中 cast 表的字段

    success_sum = 0  # 记录成功插入的数量
    repeat_sum = 0   # 记录更新的数量
    create_or_update_codes = []

    # 遍历 df1 数据
    for i, row1 in df1.iterrows():
        cast_code = row1.iloc[4]  # 获取 df1 中的 cast_code 列
        if cast_code == "nan":
            continue

        # 查找对应的 df2 行
        row2 = df2[df2.iloc[:, 3] == cast_code]  # 假设 df2 的 cast_code 在第4列
        
        if not row2.empty:
            data_to_insert = {}
            try:
                data_to_insert['quality_code'] = str(row2.iloc[0, 15])[:-2].zfill(4)  # 处理 quality_code
            except IndexError:
                pass  # 处理缺失的字段

            # 处理 df2 中的 U 到 AU 列，转换为 ch_ 字段
            for col in range(20, 47):  # U 列是 20，AU 列是 46
                if isinstance(row2.iloc[0, col], str):
                    field_name = 'ch_' + row2.iloc[0, col].lower()  # 转换为 ch_ 字段

                    # 将字段添加到数据字典中
                    data_to_insert[field_name] = row1.iloc[col - 6]  # df1 中的 O 到 AO 列作为数据源

            # 添加 created_by, updated_by, created_at, updated_at 字段
            data_to_insert['created_by'] = current_user.email
            data_to_insert['updated_by'] = current_user.email
            data_to_insert['created_at'] = current_time
            data_to_insert['updated_at'] = current_time
            # 检查 cast_code 是否已经存在
            existing_cast = db_session.query(Cast).filter(Cast.cast_code == cast_code).first()
            create_or_update_codes.append(cast_code)
            
            if existing_cast:
                # 如果存在，更新数据
                for key, value in data_to_insert.items():
                    setattr(existing_cast, key, value)  # 更新现有的字段
                db_session.commit()
                repeat_sum += 1  # 更新计数
                # try:
                #     result = get_spec_list(db_session=db_session, cast_id=existing_cast.id)
                #     log.info(f"push cast spec success {result}")
                # except:
                #     log.warning(f"push cast spec fail {existing_cast.id}")
            else:
                # 如果不存在，插入新数据
                new_cast = Cast(**data_to_insert, cast_code=cast_code)
                db_session.add(new_cast)
                db_session.commit()
                success_sum += 1  # 插入成功计数
                # try:
                #     result = get_spec_list(db_session=db_session, cast_id=new_cast.id)
                #     log.info(f"push cast spec success {result}")
                # except:
                #     log.warning(f"push cast spec fail {new_cast.id}")

    # 返回成功插入的个数和更新的个数
    return {
        "success_sum": success_sum,
        "repeat_sum": repeat_sum,
        "create_or_update_codes": create_or_update_codes
    }


def part_update(
    *,
    db_session,
    cast: Cast,
    cast_in: CastUpdate,
) -> Cast:

    update_data = cast_in.dict(
        exclude={"flex_form_data", "mill"},
    )
    for field, field_value in update_data.items():
        if field_value:
            setattr(cast, field, field_value)

    cast.flex_form_data = cast_in.flex_form_data
    db_session.add(cast)
    db_session.commit()
    return cast


def delete(*, db_session, id: int):
    cast = db_session.query(Cast).filter(Cast.id == id).one_or_none()
    
    if cast:
        cast.is_deleted = 1
    db_session.add(cast)
    db_session.commit()

    return cast


def get_codes(*, db_session):
    codes = []
    result = db_session.query(Cast.cast_code).all()
    if not result:
        return codes
    for i in result:
        codes.append(i[0])
    return codes

def get_by_code_m(db_session, code: str, mill_id: int):
    return db_session.query(Cast).filter(and_(Cast.cast_code == code, Cast.mill_id == mill_id)).first()


def get_by_code_all(db_session, code: str):
    return db_session.query(Cast).filter(Cast.cast_code == code).all()


def update_authorize_date(*, db_session, cast_id: int):
    cast = db_session.query(Cast).filter(Cast.id == cast_id).one_or_none()
    if cast:
        cast.authorize_date = datetime.now(timezone.utc)
    db_session.add(cast)
    db_session.commit()
    return cast

def auto_generate_code(db_session)-> int:
    generate_code_result = db_session.execute(select(Cast.generate_code).order_by(Cast.generate_code.desc())).scalars().first()
    result = db_session.execute(select(Cast.cast_code).filter(Cast.generate_code == generate_code_result)).scalars().all()
    existing_codes = set(result)
    for new_code in range(10000, 60001):
        if str(new_code) not in existing_codes:
            return new_code, generate_code_result

    if generate_code_result is not None:
        generate_code_result += 1
        new_code= 10000
        return  new_code, generate_code_result



def get_cast_by_semi_load(*, db_session, semi_load_ids: List[int]):
    casts = {}
    for semi_load_id in semi_load_ids:
        semi = db_session.query(Semi).filter(Semi.semi_load_id==int(semi_load_id)).first()
        if semi:
            casts[semi.cast.id] = semi.cast

    return list(casts.values())


def export_to_excel(*, db_session, data_list):
    """
    将 Cast 数据导出到 Excel 文件。

    :param db_session: 数据库会话
    :param data_list: 查询到的 Cast 数据列表
    :return: 生成的 Excel 文件路径
    """
    # 定义需要导出的字段
    export_fields = [
        "id", "mill_id", "generate_code", "cast_code", "bos_cast_code", "quality_code", "cast_suffix",
        "ch_c", "ch_si", "ch_mn", "ch_p", "ch_s", "ch_s_p", "ch_cr", "ch_mo", "ch_ni", "ch_al", "ch_b",
        "ch_co", "ch_cu", "ch_nb", "ch_sn", "ch_ti", "ch_v", "ch_ca", "ch_n", "ch_o", "ch_h", "ch_solal",
        "ch_as", "ch_bi", "ch_ce", "ch_pb", "ch_sb", "ch_w", "ch_zn", "ch_zr", "ch_te", "ch_rad", "ch_insal",
        "ch_n2", "ch_sal", "authorize_date", "quality_id", "long_cast_code"
    ]

    # 转换数据为字典列表
    data = []
    for item in data_list:
        row = {field: getattr(item, field) for field in export_fields}
        data.append(row)
    # 创建 DataFrame
    df = pd.DataFrame(data)

    # 格式化日期字段
    if "authorize_date" in df.columns:
        df["authorize_date"] = df["authorize_date"].apply(
            lambda x: x.strftime("%Y-%m-%d %H:%M:%S.%f") if pd.notna(x) else None
        )

    # 生成文件名和路径
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # file_name = f"cast_export_{timestamp}.xlsx"
    file_name = f"cast_export_{timestamp}.csv"
    file_path = os.path.join("/tmp", file_name)  # 假设文件存储在 /tmp 目录下

    # 导出到 Excel
    try:
        # df.to_excel(file_path, index=False)
        df.to_csv(file_path, index=False)
    except Exception as e:
        raise RuntimeError(f"Failed to export Excel file: {str(e)}")

    return file_path

def import_dict_to_db_new(rows: list[dict], db_session, curr_user: str):
    """
    根据 export_to_excel 导出的字段格式，导入 Cast 数据。
    """
    # 定义需要处理的字段映射，与 export_to_excel 的字段保持一致
    field_mapping = {
        "id": "id",
        "mill_id": "mill_id",
        "generate_code": "generate_code",
        "cast_code": "cast_code",
        "bos_cast_code": "bos_cast_code",
        "quality_code": "quality_code",
        "cast_suffix": "cast_suffix",
        "ch_c": "ch_c",
        "ch_si": "ch_si",
        "ch_mn": "ch_mn",
        "ch_p": "ch_p",
        "ch_s": "ch_s",
        "ch_s_p": "ch_s_p",
        "ch_cr": "ch_cr",
        "ch_mo": "ch_mo",
        "ch_ni": "ch_ni",
        "ch_al": "ch_al",
        "ch_b": "ch_b",
        "ch_co": "ch_co",
        "ch_cu": "ch_cu",
        "ch_nb": "ch_nb",
        "ch_sn": "ch_sn",
        "ch_ti": "ch_ti",
        "ch_v": "ch_v",
        "ch_ca": "ch_ca",
        "ch_n": "ch_n",
        "ch_o": "ch_o",
        "ch_h": "ch_h",
        "ch_solal": "ch_solal",
        "ch_as": "ch_as",
        "ch_bi": "ch_bi",
        "ch_ce": "ch_ce",
        "ch_pb": "ch_pb",
        "ch_sb": "ch_sb",
        "ch_w": "ch_w",
        "ch_zn": "ch_zn",
        "ch_zr": "ch_zr",
        "ch_te": "ch_te",
        "ch_rad": "ch_rad",
        "ch_insal": "ch_insal",
        "ch_n2": "ch_n2",
        "ch_sal": "ch_sal",
        "authorize_date": "authorize_date",
        "quality_id": "quality_id",
        "long_cast_code": "long_cast_code",
        "created_at": "created_at",
        "updated_at": "updated_at"
    }

    def preprocess_row(row):
        """
        预处理每一行数据，确保字段值符合数据库字段类型要求。
        """
        for key, value in row.items():
            # 将空字符串或无效值替换为 None
            if value == "" or value is None:
                row[key] = None
            # 对特定字段进行类型转换
            elif key in {"mill_id", "generate_code", "quality_id"}:  # 数值类型字段
                try:
                    row[key] = int(value) if value else None
                except ValueError:
                    row[key] = None
            elif key in {"authorize_date", "created_at", "updated_at"}:  # 日期类型字段
                try:
                    row[key] = datetime.strptime(value, "%Y-%m-%d %H:%M:%S") if value else None
                except ValueError:
                    row[key] = None
        return row

    # 遍历每一行数据并进行预处理
    processed_rows = [preprocess_row(row) for row in rows]

    # 更新或插入数据
    add_cnt, update_cnt = 0, 0
    for row in processed_rows:
        # 检查是否存在记录
        existing_cast = db_session.query(Cast).filter(Cast.id == row["id"]).first()
        if existing_cast:
            # 更新现有记录
            for field, value in row.items():
                if field in field_mapping:
                    setattr(existing_cast, field_mapping[field], value)
            existing_cast.updated_by = curr_user
            existing_cast.updated_at = datetime.now()
            update_cnt += 1
        else:
            # 插入新记录
            cast = Cast(
                **{field_mapping[field]: value for field, value in row.items() if field in field_mapping},
                created_by=curr_user,
                updated_by=curr_user,
            )
            db_session.add(cast)
            add_cnt += 1

    db_session.commit()
    return add_cnt, update_cnt

