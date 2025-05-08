from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from dispatch.config import DEV_DATABASE_SCHEMA
from dispatch.database import get_db
from dispatch.system_admin.auth.models import DispatchUser
from dispatch.system_admin.auth.service import get_current_user
from dispatch.database_util.service import common_parameters, search_filter_sort_paginate
from dispatch.product_type.models import ProductTypeCreate, ProductTypeRead, ProductTypeUpdate, ProductTypePagination, \
    ProductType
from dispatch.product_type.service import create_product_type, get_product_types, get_product_type, delete_product_type, update_product_type, create_product_type_by_mill_code, get_dim3, get_codes,get_id_by_code
from dispatch.semi_admin.semi_size.service import get_size_id_by_code,get_by_width_thick
from dispatch.product_class.service import get_by_code_SRSM as get_class_by_code
from dispatch.product_category.service import get_by_code_SRSM as get_category_by_code
from sqlalchemy import cast, String, Integer
import pandas as pd
import os 
router = APIRouter()


@router.post(path="/create")
def product_create(product_in: ProductTypeCreate, db: Session = Depends(get_db)):
    try:
        ob = create_product_type_by_mill_code(db=db, product_data=product_in)
        return {"message": "插入成功", "product_type": ob}
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"外键约束错误: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"错误: {str(e)}")


@router.delete(path="/delete/{id}")
def product_delete(id: int, db: Session = Depends(get_db)):
    print(id)
    product = get_product_type(db, id)
    if not product:
        raise HTTPException(status_code=400, detail="This product_id does not exist")

    # 使用上下文管理器处理事务
    try:
        delete_product_type(db, id)
        db.commit()  # 提交事务
        return f"删除成功: product_id: {id}"
    except Exception as e:
        db.rollback()  # 回滚事务
        print(e)
        raise HTTPException(status_code=400, detail=f"Failed to delete product: {str(e)}")


@router.put("/update/{product_type_id}")
def product_update(
    product_type_id: int,
    product_data: ProductTypeUpdate,
    db: Session = Depends(get_db),
    current_user: DispatchUser = Depends(get_current_user),  # 获取当前用户
):
    # 检查是否存在
    product_type = get_product_type(db, product_type_id)
    if not product_type:
        raise HTTPException(status_code=400, detail="ProductType not found")

    # 设置 updated_by 字段为当前用户的邮箱
    product_data.updated_by = current_user.email

    # 调用 service 层更新数据
    updated_product_type = update_product_type(db, product_type_id, product_data)

    if updated_product_type:
        return f"更新成功: product_id: {product_type_id}"

    raise HTTPException(status_code=400, detail="Failed to update ProductType")
    



@router.get(path="/list")
def product_list(db: Session = Depends(get_db)):
    result_temp = get_product_types(db=db)
    print(result_temp)
    return get_product_types(db=db)


@router.get("/", response_model=ProductTypePagination)
def get_product_list(*, common: dict = Depends(common_parameters), db: Session = Depends(get_db),
                     product_class: str = None, dims: str = None, product_category: str = None):
    query = db.query(ProductType)
    if product_class:
        query = query.filter(ProductType.code.like(f'{product_class}%'))
    if product_category:
        query = query.filter(ProductType.code.like(f'%{product_category}%'))

    query_str = common.get("query_str")
    if query_str:
        query = query.filter(ProductType.code.like(f'%{query_str}%'))
        common["query_str"] = ''

    if dims:
        # Order Items 页面dim3筛选
        if common.get('query_str'):
            search_pattern = f"%{common['query_str']}%"
            query = query.filter(
                cast(cast(ProductType.dim3, Integer), String).like(search_pattern))
            del common['query_str']
    common['query'] = query
    return search_filter_sort_paginate(model="ProductType", **common)


@router.get('/get/dim3')
def get_product_dim3(db: Session = Depends(get_db)):
    result_temp = get_dim3(db=db)
    return result_temp



@router.get(path="/hello")
def hello():
    return "Hello World!"


@router.get("/codes")
def get_code(db_session: Session = Depends(get_db)):
    # print(id)
    ls = get_codes(db_session=db_session)
    return ls





@router.get("/create_sql")
def create_sql(db_session: Session = Depends(get_db)):
# 读取 Excel 文件
    excel_file = pd.ExcelFile('./SRSM-Semi-Size.xlsx')

    # 获取所有表名
    sheet_name = excel_file.sheet_names

    df = excel_file.parse('SRSM Semi Size_MB01 screen in M', header=0)

    product_class_inserts=[]
    product_class_groups = df.groupby(['PROD_ID'])
    for (prod_id,), group in product_class_groups:
        product_class_code = prod_id[:2]
        insert_values = f"('{product_class_code}', 1)"
        product_class_inserts.append(insert_values)

    product_class_values_str = ', '.join(product_class_inserts)
    bulk_product_class_insert_sql = f"INSERT INTO product_type (code,  mill_id) VALUES {product_class_values_str}  ON CONFLICT (code,mill_id) DO NOTHING ;"


    #生成 product_type表的插入语句
    # product_type_inserts=[]
    # product_type_groups = df.groupby(['PROD_ID', 'WGT'])
    # for (prod_id, wgt), group in product_type_groups:
    #     prod_id = prod_id.replace(' ', '-')
    #     prod_id = prod_id[:2] + '-' + prod_id[2:]
    #     product_type_code = f"{prod_id}-{wgt}"
    #     insert_values = f"('{product_type_code}', 1)"
    #     product_type_inserts.append(insert_values)

    # product_type_values_str = ', '.join(product_type_inserts)
    # bulk_product_type_insert_sql = f"INSERT INTO product_type (code,  mill_id) VALUES {product_type_values_str}  ON CONFLICT (code) DO NOTHING ;"


    # 生成 semi_size 表的插入语句
    semi_size_inserts = []
    semi_size_groups = df.groupby(['WIDTH', 'THICK'])
    for (width, thick), group in semi_size_groups:
        code = f"{width}-{thick}"
        semi_size_insert =  f"({code}, {width}, {thick}, 1)"
        semi_size_inserts.append(semi_size_insert)

    semi_size_values_str = ', '.join(semi_size_inserts)    
    bulk_semi_size_insert_sql = f"INSERT INTO {DEV_DATABASE_SCHEMA}.semi_size (code, width_mm, thick_mm, mill_id) VALUES {semi_size_values_str}ON CONFLICT (code) DO NOTHING;"



    # 生成 semi_size_detail 表的插入语句
    semi_size_detail_inserts = []
    semi_size_detail_groups = df.groupby(['WIDTH', 'THICK', 'LENGTH', 'WEIGHT'])
    for (width, thick, length, weight), group in semi_size_detail_groups:
        semi_size_code = f"{width}-{thick}"
        semi_size_id=get_size_id_by_code(db_session,semi_size_code)
        min_length = group['MIN LTH'].iloc[0]
        max_length = group['MAX LTH'].iloc[0]

        insert_values = f"({semi_size_id}, {length}, {weight}, {min_length}, {max_length}, 1)"
        semi_size_detail_inserts.append(insert_values)

    values_str = ', '.join(semi_size_detail_inserts)
    bulk_semi_size_detail_insert_sql = f"INSERT INTO {DEV_DATABASE_SCHEMA}.semi_size_detail (semi_size_id, length_mm, standard_weight_t, min_length_mm, max_length_mm, mill_id) VALUES {values_str}"



    # 生成 alternative_semi_size 表的插入语句，
    alt_semi_size_inserts = []
    product_type_inserts=[]
    alt_semi_size_groups = df.groupby(['PROD_ID', 'WGT', 'WIDTH', 'THICK', 'LENGTH', 'WEIGHT', 'OPT'])
    for (prod_id, wgt, width, thick, length, weight, rank_seq), group in alt_semi_size_groups:
        semi_size_code = f"{width}-{thick}"
        semi_size_id=get_size_id_by_code(db_session,semi_size_code)
        prod_id = prod_id.replace(' ', '-')
        prod_id = prod_id[:2] + '-' + prod_id[2:]
        product_type_code = f"{prod_id}-{wgt}"
        product_type_id = get_id_by_code(db_session,product_type_code)
        
        insert_values = f"({product_type_id}, {width}, {thick}, {length}, {weight}, {rank_seq}, 1, {semi_size_id})"
        alt_semi_size_inserts.append(insert_values)

    alt_values_str = ', '.join(alt_semi_size_inserts)
    bulk_alt_insert_sql = f"INSERT INTO {DEV_DATABASE_SCHEMA}.alternative_semi_size (product_type_id, semi_width, thickness, opt_length, weight, rank_seq, mill_id, semi_size_id) VALUES {alt_values_str};"
    
    protype_groups = df.groupby(['PROD_ID', 'WGT'])
    for (prod_id, wgt), group in protype_groups:

        prod_id = prod_id.replace(' ', '-')
        prod_id = prod_id[:2] + '-' + prod_id[2:]
        product_type_code = f"{prod_id}-{wgt}"

        insert_values_product_type = f"('{product_type_code}',{wgt},1)"
        product_type_inserts.append(insert_values_product_type)
    protype_values_str = ', '.join(product_type_inserts)
    bulk_protype_insert_sql = f"INSERT INTO {DEV_DATABASE_SCHEMA}.product_type (code, dim3 ,mill_id) VALUES {protype_values_str} ON CONFLICT (code) DO NOTHING;"

    return bulk_product_class_insert_sql

@router.get("/create_sql_TY43")
def create_sql(db_session: Session = Depends(get_db)):
    # 读取 Excel 文件
    excel_file = pd.ExcelFile('./TY43-04-03-25.xlsx')

    # 解析指定工作表
    df = excel_file.parse('TY43', header=0)

    # 生成 alternative_semi_size 表的插入语句
    alt_semi_size_inserts = []

    for index, row in df.iterrows():
        # 从行中获取所需的值
        type = row.get('SECT_TYPE')
        dim1 = row.get('DIM1')
        dim2 = row.get('DIM2')
        weight = row.get('SECT_WGT')
        width = row.get('WIDTH')
        thick = row.get('THICK')
        length = row.get('OPT_LTH')  # 假设存在 LENGTH 列，如果不存在会返回 None
        min_length = row.get('MIN_LTH')
        max_length = row.get('MAX_LTH')
        source = row.get('SOURCE')
        rank_seq = row.get('ALT')

        dim1 = str(dim1).lstrip('0')
        dim2 = str(dim2).lstrip('0')

        semi_size = get_by_width_thick(db_session=db_session, width=width, thick=thick)
        semi_size_id = semi_size.id if semi_size else None
        print(width) 

        product_type_code = f"{type}-{dim1}-{dim2}-{weight}"
        product_type_id = get_id_by_code(db_session, product_type_code)

        insert_values = f"({product_type_id}, {width}, {thick}, {length}, {rank_seq}, 410, {semi_size_id},{min_length},{max_length},{source})"
        alt_semi_size_inserts.append(insert_values)

    alt_values_str = ', '.join(alt_semi_size_inserts)
    bulk_alt_insert_sql = f"INSERT INTO {DEV_DATABASE_SCHEMA}.alternative_semi_size (product_type_id, semi_width, thickness, opt_length, rank_seq, mill_id, semi_size_id,min_length,max_length,source) VALUES {alt_values_str};"

    return bulk_alt_insert_sql



@router.get("/create_sql_type")
def create_sql(db_session: Session = Depends(get_db)):
    # 读取 Excel 文件
    current_dir = os.getcwd()
    # 构建 Excel 文件的完整路径
    excel_file_path = os.path.join(current_dir, 'SRSM-Product-File.xlsx')
    # 读取 Excel 文件
    print(excel_file_path)
    excel_file = pd.ExcelFile(excel_file_path)

    # 解析指定工作表
    df = excel_file.parse('T51003A2', header=0)

    # 生成 alternative_semi_size 表的插入语句
    product_type_inserts = []

    for index, row in df.iterrows():
        # 从行中获取所需的值
        type = row.get('SHAPE')
        dim1 = row.get('DIM1')
        dim2 = row.get('DIM2')
        weight = row.get('WT_METRE')
        if weight is not None:
            try:
                # 将字符串转换为浮点数
                weight = float(weight)
                # 除以 100
                result = weight / 100
                # 判断是否能被整除
                if result.is_integer():
                    # 如果能被整除，转换为整数
                    dim3 = int(result)
                else:
                    # 不能被整除，保留两位小数
                    dim3 = round(result, 2)
            except ValueError:
                print("输入的值不是有效的数字。")
        else:
            print("字典中没有 'WT_METRE' 键。")
        flange_thickness_str = row.get('THICK')
        if flange_thickness_str is not None:
            try:
                # 将字符串转换为数字
                flange_thickness = float(flange_thickness_str)
                # 除以 10
                flange_thickness = flange_thickness / 10
                if flange_thickness.is_integer():
                    # 如果能被整除，转换为整数
                    flange_thickness = int(result)
            except ValueError:
                print("输入的值不是有效的数字。")
        else:
            print("字典中没有 'THICK' 键。")
        web_thickness = row.get('WEB_TH')

        product_class = get_class_by_code(db_session=db_session, code=type)
        if not product_class:
            print("product_class not found",type)
        class_id = product_class.id if product_class else None

        product_category_code= f"{dim1}-{dim2}"
        product_category = get_category_by_code(db_session=db_session, code=product_category_code)
        if not product_category:
            print("product_category not found",product_category_code)
        product_category_id = product_category.id if product_category else None

        product_type_code = f"{type}-{dim1}-{dim2}-{dim3}"


        insert_values = f"(1, '{product_type_code}', {dim1}, {dim2}, {dim3}, {flange_thickness}, {web_thickness}, {class_id}, {product_category_id})"
        product_type_inserts.append(insert_values)

    alt_values_str = ', '.join(product_type_inserts)
    bulk_alt_insert_sql = f"INSERT INTO {DEV_DATABASE_SCHEMA}.product_type (mill_id, code, dim1, dim2, dim3, flange_thickness, web_thickness ,product_class_id, product_category_id) VALUES {alt_values_str} ON CONFLICT (code,mill_id) DO NOTHING;"

    return bulk_alt_insert_sql

@router.get("/get_product_type_dim3/{id}")
def get_product_type_dim3(id: int, db_session: Session = Depends(get_db)):
    product_type = get_product_type(db_session, id)
    if product_type:
        return product_type.dim3
    else:
        return None