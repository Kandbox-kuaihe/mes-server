import psycopg2
from dispatch.config import DB_PARAMS_DICT
import pandas as pd
from dispatch.config import DATABASE_CREDENTIALS,DATABASE_PORT,DATABASE_NAME,DATABASE_HOSTNAME
# ,ROOT_DIR,DEV_DATABASE_SCHEMA
username, password = str(DATABASE_CREDENTIALS).split(":")

# 配置数据库连接参数
db_params = {
    'dbname': DATABASE_NAME,
    'user': username,
    'password': password,
    'host': DATABASE_HOSTNAME,
    'port': DATABASE_PORT
}

def pandas_to_pg(sql_query):
    # 建立数据库连接
    conn = psycopg2.connect(**db_params)
    #    创建游标
    cur = conn.cursor()
    with conn.cursor() as cur:
        cur.execute(sql_query)
        conn.commit()




conn = psycopg2.connect(**DB_PARAMS_DICT)


def pandas_to_pg(sql_query: str):
    """pandas 执行sql 语句

    Args:
        sql_query (_type_): 要执行的sql语句
    """
    # 建立数据库连接
    #    创建游标
    cur = conn.cursor()
    with conn.cursor() as cur:
        cur.execute(sql_query)
        conn.commit()


def get_pandas_df_from_sql(query: str, mapping: dict = None) -> pd.DataFrame:
    df = pd.read_sql_query(query, conn)
    df.columns = df.columns.str.replace(' ', '')
    if mapping:
        df = df[list(mapping.keys())]
        # df = df.drop_duplicates(subset=list(mapping.keys()))
    return df


def get_pandas_df_from_excle(file_path: str, header: int = 0, skiprows: list = None, delete_Unnamed: bool = True,
                             sheet_name: str = None, nrows: int = None) -> pd.DataFrame:
    """

    Args:
        file_path (str): _description_
        header (int, optional): _description_. Defaults to 0.
        skiprows (list, optional): [1]  要跳过 哪几行. Defaults to None.
        delete_Unnamed (bool, optional): 是否要删除Unnamed 开头的列 . Defaults to True.
    Returns:
        pd.DataFrame: _description_
    """
    # 要看这个 xlsx 文件 第一列对应的列名
    # cast_file_name = f'{config.ROOT_DIR}/src/dispatch/spec_admin/spec/runout_spec_service/import_corvering/TTTENSIL.xlsx'

    if sheet_name:
        df = pd.read_excel(file_path, header=header, skiprows=skiprows, sheet_name=sheet_name, nrows=nrows)
    else:
        df = pd.read_excel(file_path, header=header, skiprows=skiprows, nrows=nrows)
    # 去除没有列名的列
    # 假设df是已经读取数据后的DataFrame ， 将标记好的字段读取为 df ， 然后入库
    if delete_Unnamed:
        columns_to_drop = [col for col in df.columns if col.startswith("Unnamed:")]
        df = df.drop(columns=columns_to_drop)

    # 如果列名有 空格 ，删除
    df.columns = df.columns.str.replace(' ', '')
    return df


def get_pandas_df_from_csv(file_path: str, header: int = 0, skiprows: list = None, delete_Unnamed: bool = True,
                          sheet_name: str = None, nrows: int = None) -> pd.DataFrame:
    """
    从CSV文件中读取数据并进行处理

    Args:
        file_path (str): CSV文件路径
        header (int, optional): 指定作为列名的行号. Defaults to 0.
        skiprows (list, optional): 要跳过的行号列表. Defaults to None.
        delete_Unnamed (bool, optional): 是否删除以Unnamed开头的列. Defaults to True.
        sheet_name (str, optional): CSV文件没有sheet概念，此参数在这里无实际作用，保留以保持接口一致性. Defaults to None.
        nrows (int, optional): 读取的行数. Defaults to None.
    Returns:
        pd.DataFrame: 处理后的DataFrame
    """
    df = pd.read_csv(file_path, header=header, skiprows=skiprows, nrows=nrows)
    if delete_Unnamed:
        columns_to_drop = [col for col in df.columns if col.startswith("Unnamed:")]
        df = df.drop(columns=columns_to_drop)
    df.columns = df.columns.str.replace(' ', '')
    return df