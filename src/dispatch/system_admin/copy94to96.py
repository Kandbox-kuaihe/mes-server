from sqlalchemy import create_engine, MetaData, Table, select, and_
from sqlalchemy.dialects.postgresql import insert

from sqlalchemy.orm import sessionmaker
import json

from dispatch.config import DATABASE_94_HOST, DATABASE_94_PORT, DATABASE_94_NAME, DATABASE_94_USER, \
    DATABASE_94_PASSWORD, DATABASE_96_HOST, DATABASE_96_PORT, DATABASE_96_NAME, DATABASE_96_USER, DATABASE_96_PASSWORD, \
    DEV_DATABASE_SCHEMA

# 源数据库 (94 服务器)
source_config = {
    'host': DATABASE_94_HOST,
    'port': DATABASE_94_PORT,
    'database': DATABASE_94_NAME,
    'user': DATABASE_94_USER,
    'password': DATABASE_94_PASSWORD
}

# 目标数据库 (96 服务器)
target_config = {
    'host': DATABASE_96_HOST,
    'port': DATABASE_96_PORT,
    'database': DATABASE_96_NAME,
    'user': DATABASE_96_USER,
    'password': DATABASE_96_PASSWORD
}

# 创建数据库连接字符串
source_db_url = f"postgresql+psycopg2://{source_config['user']}:{source_config['password']}@{source_config['host']}:{source_config['port']}/{source_config['database']}"
target_db_url = f"postgresql+psycopg2://{target_config['user']}:{target_config['password']}@{target_config['host']}:{target_config['port']}/{target_config['database']}"

# 创建数据库引擎
source_engine = create_engine(source_db_url)
target_engine = create_engine(target_db_url)

# 创建会话
SourceSession = sessionmaker(bind=source_engine)
TargetSession = sessionmaker(bind=target_engine)

def copy_94_to_96(schema_name, table_name):
    source_session = SourceSession()
    target_session = TargetSession()

    try:
        # 读取表的元数据
        metadata = MetaData()
        table = Table(table_name, metadata, schema=schema_name, autoload_with=source_engine)

        # 查询源数据库数据
        query = select(table)
        result = source_session.execute(query)
        
        # 将结果转换为 dict
        rows = [dict(row._mapping) for row in result]

        # 移除 id 字段
        # for row in rows:
        #     if 'id' in row:
        #         del row['id']
        # 处理 dict 类型字段 (转换为 JSON 字符串)
        processed_rows = []
        for row in rows:                
            processed_row = {k: json.dumps(v) if isinstance(v, dict) else v for k, v in row.items()}
            processed_rows.append(processed_row)

        # 插入数据到目标数据库
        target_table = Table(table_name, metadata, schema=schema_name, autoload_with=target_engine)

        if table_name == 'role_menu':

            for row2 in processed_rows:
                # 检查数据是否存在于目标表中
                query_check = select([target_table]).filter_by(menu_id=row2['menu_id'], role_id=row2['role_id'])
                result_check = target_session.execute(query_check).fetchone()

                # 如果数据不存在，则插入
                if result_check is None:
                    insert_stmt = target_table.insert().values(row2)
                    target_session.execute(insert_stmt)
        elif table_name == 'role_menu_button':
            for row3 in processed_rows:
                # 检查数据是否存在于目标表中
                query_check = select([target_table]).filter_by(menu_button_id=row3['menu_button_id'], role_id=row3['role_id'])
                result_check = target_session.execute(query_check).fetchone()

                # 如果数据不存在，则插入
                if result_check is None:
                    insert_stmt = target_table.insert().values(row3)
                    target_session.execute(insert_stmt)
        else:
            insert_stmt = insert(target_table).values(processed_rows).on_conflict_do_nothing()
            target_session.execute(insert_stmt)

        
        
        target_session.commit()

        if table_name in ('role','dispatch_user','menu','menu_button'):
            # 重置序列
            reset_sequence_sql = f"""
                SELECT setval(pg_get_serial_sequence('{schema_name}.{table_name}', 'id'), 
                (SELECT MAX(id) FROM {schema_name}.{table_name}));
            """
            target_session.execute(reset_sequence_sql)
            target_session.commit()

        print(f"成功复制 {len(processed_rows)} 条数据到 {table_name}")

    except Exception as e:
        print(f"发生错误: {e}")
        target_session.rollback()
    finally:
        source_session.close()
        target_session.close()


def copy_table():
    copy_94_to_96(DEV_DATABASE_SCHEMA,'role')

    copy_94_to_96('dispatch_core','dispatch_user')

    copy_94_to_96(DEV_DATABASE_SCHEMA,'menu')
    copy_94_to_96(DEV_DATABASE_SCHEMA,'menu_button')
    copy_94_to_96(DEV_DATABASE_SCHEMA,'role_menu')
    copy_94_to_96(DEV_DATABASE_SCHEMA,'role_menu_button')


if __name__ == "__main__":
    copy_table()