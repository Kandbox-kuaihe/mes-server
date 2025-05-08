import json
from enum import Enum

import redis
from datetime import datetime
import logging
import os
import base64
import itertools
import importlib.metadata
from starlette.datastructures import Secret

from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings
log = logging.getLogger(__name__)

# Kandbox config
basedir = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR =os.path.abspath(os.path.join(basedir, "../.."))


env_file = os.path.join(ROOT_DIR, "dev.env")

config = Config(env_file=env_file)


LOG_LEVEL = config("LOG_LEVEL", default=logging.INFO)
LOG_FILE = config("LOG_FILE", default="dispatch_all.log")



module_levels = {
    "dispatch.main": logging.INFO,
    "easydispatch_cli":logging.WARNING,
    "covering":logging.DEBUG,
}

DEBUG = False
DISPATCH_UI_URL = config("DISPATCH_UI_URL", default="http://localhost:8000")



# authentication
DISPATCH_AUTHENTICATION_PROVIDER_SLUG = config(
    "DISPATCH_AUTHENTICATION_PROVIDER_SLUG", default="dispatch-auth-provider-basic"
)

LOCAL_ENCRYPT_KEY = config("LOCAL_ENCRYPT_KEY", default="010101")

DISPATCH_JWT_SECRET = config("DISPATCH_JWT_SECRET", default="secret")
DISPATCH_JWT_ALG = config("DISPATCH_JWT_ALG", default="HS256")
# Seconds, 8640000/60/60/24 == 100 days.
DISPATCH_JWT_EXP = config("DISPATCH_JWT_EXP", default=8640000)

if DISPATCH_AUTHENTICATION_PROVIDER_SLUG == "dispatch-auth-provider-basic":
    if not DISPATCH_JWT_SECRET:
        log.warning("No JWT secret specified, this is required if you are using basic authentication.")

DISPATCH_AUTHENTICATION_DEFAULT_USER = config(
    "DISPATCH_AUTHENTICATION_DEFAULT_USER", default="dispatch@example.com"
)

DISPATCH_AUTHENTICATION_PROVIDER_PKCE_JWKS = config(
    "DISPATCH_AUTHENTICATION_PROVIDER_PKCE_JWKS", default=None
)

if DISPATCH_AUTHENTICATION_PROVIDER_SLUG == "dispatch-auth-provider-pkce":
    if not DISPATCH_AUTHENTICATION_PROVIDER_PKCE_JWKS:
        log.warning(
            "No PKCE JWKS url provided, this is required if you are using PKCE authentication."
        )






METRIC_PROVIDERS = config("METRIC_PROVIDERS", cast=CommaSeparatedStrings, default="")


# database
DATABASE_HOSTNAME = config("DATABASE_HOSTNAME", default="localhost")
DATABASE_CREDENTIALS = config("DATABASE_CREDENTIALS", cast=Secret, default="")
DATABASE_NAME = config("DATABASE_NAME", default="")
DATABASE_ARCHIVE_NAME = config("DATABASE_ARCHIVE_NAME", default="")
DATABASE_PORT = config("DATABASE_PORT", default="5432")
SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DATABASE_CREDENTIALS}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}"

SQLALCHEMY_DATABASE_ARCHIVE_URI = f"postgresql+psycopg2://{DATABASE_CREDENTIALS}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_ARCHIVE_NAME}"


# mysql config
MYSQL_DATABASE_HOSTNAME = config("MYSQL_DATABASE_HOSTNAME", default="localhost")
MYSQL_DATABASE_CREDENTIALS = config("MYSQL_DATABASE_CREDENTIALS", cast=Secret, default="")
MYSQL_DATABASE_PORT = config("MYSQL_DATABASE_PORT", default=3306)
MYSQL_DATABASE_NAME = config("MYSQL_DATABASE_NAME", default="")


# Incident Cost Configuration


# kafka

REDIS_KEY_TEMPLATE_LOGIN_EXPIRE = "exp:{{{}}}:{}"
REDIS_KEY_TEMPLATE_USER = "user:email:{}"
REDIS_KEY_TEMPLATE_USER_PERMISSION = "permission:email:{}"
# redis
REDIS_HOST = config("REDIS_HOST", default="127.0.0.1")
REDIS_PORT = config("REDIS_PORT", default="6379")
REDIS_PASSWORD = config("REDIS_PASSWORD", default=None)

REDIS_DB =  config("REDIS_DB", default=0)

DISPATCH_VERSION = "1.0.20250403" #importlib.metadata.version('mes-web')

from uvicorn.config import LOGGING_CONFIG
LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelprefix)s %(message)s"
print(datetime.now(),f"Database_Config: Current redis: REDIS_HOST = {(REDIS_HOST,REDIS_PORT)}, REDIS_DB = {REDIS_DB}. Current postgres: DATABASE = {(DATABASE_HOSTNAME,DATABASE_PORT)}, DATABASE_NAME = {DATABASE_NAME}, DISPATCH_VERSION = {DISPATCH_VERSION}  ")

if REDIS_PASSWORD == "":
    redis_pool = redis.ConnectionPool(
        host=REDIS_HOST, port=REDIS_PORT, password=None, decode_responses=True,db=REDIS_DB
    )
else:
    redis_pool = redis.ConnectionPool(
        host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True,db=REDIS_DB
    )

# redis_pool = redis.ConnectionPool(host='10.0.0.1', port=6379, db=0)

ALLOWED_MAXIMUM_MINUTES = config("ALLOWED_MAXIMUM_MINUTES", cast=int, default=120)
NEGATIVE_MIN_VALUE = 1e20

# 是否允许注册
ENABLE_REGISTER = config("ENABLE_REGISTER", default="yes")


KANDBOX_DATE_FORMAT = "%Y%m%d"
KANDBOX_DAY_FORMAT_ISO = "%Y-%m-%d"
# datetime.strptime('2019-07-01',"%Y-%m-%d")

KANDBOX_DATETIME_FORMAT_WITH_MS = "%Y-%m-%d %H:%M:%S.%f"  # For postgres as well

ALEMBIC_ARCHIVE_REVISION_PATH = config(
    "ALEMBIC_ARCHIVE_REVISION_PATH",
    default=f"{os.path.dirname(os.path.realpath(__file__))}/database_util/revisions/archive",
)
ALEMBIC_TENANT_REVISION_PATH = config(
    "ALEMBIC_TENANT_REVISION_PATH",
    default=f"{os.path.dirname(os.path.realpath(__file__))}/database_util/revisions/tenant",
)

ALEMBIC_CORE_REVISION_PATH = config(
    "ALEMBIC_TENANT_REVISION_PATH",
    default=f"{os.path.dirname(os.path.realpath(__file__))}/database_util/revisions/core",
)

ALEMBIC_BASE_PATH = config(
    "ALEMBIC_BASE_PATH",
    default=f"{os.path.dirname(os.path.realpath(__file__))}/database_util/",
)



ALEMBIC_INI_PATH = config(
    "ALEMBIC_INI_PATH", default=f"{os.path.dirname(os.path.realpath(__file__))}/alembic.ini",
)
ALEMBIC_MULTI_TENANT_MIGRATION_PATH = config(
    "ALEMBIC_MULTI_TENANT_MIGRATION_PATH",
    default=f"{os.path.dirname(os.path.realpath(__file__))}/database_util/revisions/multi-tenant-migration.sql",
)


BASE_ENV = config("BASE_ENV", default="")


DEFAULT_ORG_MAX_NBR_JOBS = config("DEFAULT_ORG_MAX_NBR_JOBS", cast=int, default=1600)
DEFAULT_ORG_MAX_NBR_WORKERS = config("DEFAULT_ORG_MAX_NBR_WORKERS", cast=int, default=66)
DEFAULT_ORG_MAX_NBR_TEAMS = config("DEFAULT_ORG_MAX_NBR_TEAMS", cast=int, default=5)
DEFAULT_TEAM_TIMEZONE = config("DEFAULT_TEAM_TIMEZONE",  default="Europe/London") # # "Asia/Dubai",







PLANNER_TEMPLATE_DICT = {

}




SEPERATOR_TOP_1 = '|'

# SEPERATOR_TOP_2 and 3 are used only in assigned_jobs to seperate flex form fields
SEPERATOR_TOP_2 = '+'
SEPERATOR_TOP_3 = '='

SEPERATOR_FLEX_0 = ';' # used in flex form data.
SEPERATOR_FLEX_1 = ':'
SEPERATOR_FLEX_2 = ',' #only 3rd level , to avoid spanish , as peroid.

# SEPERATOR_SLOT_CODE = '_'
SEPERATOR_JOB_CODE = '-' # This should avoid numbers. Code should be alphabetic


LIMS_URL=config("LIMS_URL",  default="") # # "Asia/Dubai",

MYSQL_CONFIG = {
    "drivername": config("DRIVER_NAME", default="mysql+pymysql"),
    "host": config("MYSQL_HOST", default=""),
    "port": config("MYSQL_PORT", cast=int, default=3306),
    "username": config("MYSQL_USERNAME", default=""),
    "password": config("MYSQL_PASSWORD", default=""),
    "database": config("MYSQL_DATABASE", default="")
}
# Sync rolling from srsm interval: seconds
SYNC_ROLLING_INTERVAL = config("SYNC_ROLLING_INTERVAL", default=60 * 60, cast=int)
SYNC_FINISHED_PRODUCT_INTERVAL = config("SYNC_FINISHED_PRODUCT_INTERVAL", default=24 * 60 * 60, cast=int)
# FTP import rolling to mes
IMPORT_ROLLING_FROM_FTP_INTERVAL = config("IMPORT_ROLLING_FROM_FTP_INTERVAL", default=5 * 60, cast=int)
# FTP export rolling to mes
EXPORT_ROLLING_FTP_INTERVAL = config("EXPORT_ROLLING_FTP_INTERVAL", default=30 * 60, cast=int)

SYNC_COH_INTERVAL = config("SYNC_COH_INTERVAL", default=60 * 60, cast=int)
SYNC_SEMI_INTERVAL = config("SYNC_SEMI_INTERVAL", default=60 * 60 * 4, cast=int)

# init covering
INIT_COVERING_TIME = config("INIT_COVERING_TIME", default=1, cast=int)
MILL_ID = config("MILL_ID", default=410)
# init pytest
INIT_PYTEST_TIME = config("INIT_PYTEST_TIME", default=2, cast=int)

# FTP config
FTP_CONFIG = {
    "TBM": {
        "mes_ftp": { # 我们的94 ftp，给他们上传的，上传的目录是：/greenwood，文件名是：ROLLPROG.TXT。我们需要从这里下载，然后上传到数据库
            "host": config("MES_FTP_HOST", default=""),
            "port": config("MES_FTP_PORT", cast=int, default=21),
            "username": config("MES_FTP_USERNAME", default=""),
            "password": config("MES_FTP_PASSWORD", default=""),
            "filename": config("MES_FTP_DOWNLOAD_FILENAME", default="")
        },
        "pcc_ftp": { # 他们的ftp，给我们上传的。我们生成的文件，上传到他们的ftp。
            "host": config("FTP_HOST", default=""),
            "port": config("FTP_PORT", cast=int, default=21),
            "username": config("FTP_USERNAME", default=""),
            "password": config("FTP_PASSWORD", default=""),
            "filename": config("FTP_UPLOAD_FILENAME", default=""),
            "rollrep_filename": config("FTP_UPLOAD_ROLLREP_FILENAME", default=""),
            "gty91f2_filename": config("FTP_UPLOAD_GTY91F2_FILENAME", default="")
        }
    }
}


# 以下部分是 dev 环境的配置信息， 上线发布，不需要携带

DB_USERNAME, DB_PASSWORD = str(DATABASE_CREDENTIALS).split(":")

# 配置数据库连接参数
DB_PARAMS_DICT = {
    'dbname': DATABASE_NAME,
    'user': DB_USERNAME,
    'password': DB_PASSWORD,
    'host': DATABASE_HOSTNAME,
    'port': DATABASE_PORT
}
# 导入 这个schema 下的 spec 相关数据  
DEV_DATABASE_SCHEMA=config("DEV_DATABASE_SCHEMA",  default="")

#  IBM mq 配置
#  DEV LIMS ENV
# 获取 MQ_ON_OFF 环境变量，默认值为 False
mq_read_on_off = config("MQ_READ_ON_OFF", default=False, cast=bool)
mq_read_queue_name = config('MQ_READ_QUEUE_NAME', default='')
mq_write_on_off = config("MQ_WRITE_ON_OFF", default=False, cast=bool)
mq_write_queue_name = config('MQ_WRITE_QUEUE_NAME', default='')

#mq_on_off = True
# 动态生成默认配置
MQ_LIMIS_ENDPOINTS_READ_CONFIG = config("MQ_LIMIS_ENDPOINTS_READ_CONFIG",  default='{}')
MQ_LIMIS_ENDPOINTS_WRITE_CONFIG = config("MQ_LIMIS_ENDPOINTS_WRITE_CONFIG",  default='{}')
MQ_LIMIS_ENDPOINTS_READ = json.loads(MQ_LIMIS_ENDPOINTS_READ_CONFIG) 
MQ_LIMIS_ENDPOINTS_WRITE = json.loads(MQ_LIMIS_ENDPOINTS_WRITE_CONFIG)

# load auto plan 吨位设置
LOAD_AUTO_PLAN_TONNAGE = config("LOAD_AUTO_PLAN_TONNAGE", default=12)

CAST_GENERATED_CODE = config("CAST_GENERATED_CODE", default=19)




# 消息转发到不同服务器的相关配置
ENABLE_MESSAGE_FORWARD = config("ENABLE_MESSAGE_FORWARD", cast=bool, default=False)  # 是否启用消息转发
IGNORE_MESSAGES_LOCAL = set([ item.strip() for item in config("IGNORE_MESSAGES_LOCAL", default="").split(',') if item.strip()])
# 转发消息的地址
FORWARD_URLS = set([ item.strip() for item in config("FORWARD_URLS", default="").split(',') if item.strip()])

# 允许发送消息的host列表
ALLOWED_SEND_MESSAGES_HOSTS = set(
    [
        item.strip() for item in config("ALLOWED_SEND_MESSAGES_HOSTS", default="").split(',')
        if item.strip()
    ]
)


HOLD_AGED_BAR_MONTH = config("HOLD_AGED_BAR_MONTH", default=12)

ADVICE_SEQUENCE_NAME = config("ADVICE_SEQUENCE_NAME", default="advice_id_seq")
FINISHED_PRODUCT_LOAD_SEQUENCE_NAME = config("FINISHED_PRODUCT_LOAD_SEQUENCE_NAME", default="load_id_seq")

TEAMS_WEB_HOOK_URL = config("TEAMS_WEB_HOOK_URL", default='')

LOGROTATE_BIN = config("LOGROTATE_BIN", default="")
ALERTS2TEAMS_INTERVAL = config("ALERTS2TEAMS_INTERVAL", default=3, cast=int)
ALERTS2TEAMS_LOG_FILES = config("ALERT_LOG_FILES", default=[])

DEFAULT_DOMAIN = config("DEFAULT_DOMAIN", default="")
DEFAULT_EMAIL = config("DEFAULT_EMAIL", default="")
DEFAULT_PWD  = config("DEFAULT_PWD", default="")

CLI_USERNAME = config("CLI_USERNAME", default="")
CLI_PASSWORD = config("CLI_PASSWORD", default="")

UTILS_EMAIL  = config("UTILS_EMAIL", default="")
UTILS_PWD  = config("UTILS_PWD", default="")

MESSAGE_URL_IS_SERVICE_CENTER_TRUE_START  = config("MESSAGE_URL_IS_SERVICE_CENTER_TRUE_START", default="")
MESSAGE_URL_IS_SERVICE_CENTER_TRUE_END  = config("MESSAGE_URL_IS_SERVICE_CENTER_TRUE_END", default="")
MESSAGE_URL_IS_SERVICE_CENTER_FALSE_START  = config("MESSAGE_URL_IS_SERVICE_CENTER_FALSE_START", default="")
MESSAGE_URL_IS_SERVICE_CENTER_FALSE_END  = config("MESSAGE_URL_IS_SERVICE_CENTER_FALSE_END", default="")

class MILLEnum(int,Enum):
    MILL1 =  1
    MILL410 = 410
    MILL5=  5
    MILL2 = 2
    MILL_UNKNOWN = 999999999
    # MILL6 =410


dict_code = {
    410: MILLEnum.MILL410,
    1: MILLEnum.MILL1,
    5: MILLEnum.MILL5,
    2: MILLEnum.MILL2,
    # 6: MILLEnum.MILL6
}
def get_mill_ops(mill_id):
    # 根据不同code获取不同的id
    return dict_code.get(mill_id, None)

ODOO_HOST = config("ODOO_HOST", default="")
ODOO_DB = config("ODOO_DB", default="")
ODOO_USERNAME = config("ODOO_USERNAME", default="")
ODOO_PASSWORD = config("ODOO_PASSWORD", default="")