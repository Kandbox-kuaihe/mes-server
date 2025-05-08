import logging
import colorlog  # 新增依赖
from dispatch.config import config
from uvicorn.config import LOGGING_CONFIG

LOG_LEVEL = config("LOG_LEVEL", default=logging.INFO)
# Console colours
DEBUG_COLOUR = config("DEBUG_COLOUR", default="cyan")
INFO_COLOUR = config("INFO_COLOUR", default="green")
WARNING_COLOUR = config("WARNING_COLOUR", default="yellow")
ERROR_COLOUR = config("ERROR_COLOUR", default="red")
CRITICAL_COLOUR = config("CRITICAL_COLOUR", default="red,bg_white")

module_levels = {
    "dispatch.main": logging.INFO,
    "easydispatch_cli": logging.WARNING,
}

def configure_logging():
    # 定义带颜色的日志格式
    LOGFORMAT = (
        "%(log_color)s[%(asctime)s][%(pathname)s(%(lineno)d)] %(levelname)s: %(message)s"
    )
    DATEFMT = "%Y-%m-%d %H:%M:%S"

    # 使用 colorlog 的 ColoredFormatter
    formatter = colorlog.ColoredFormatter(
        LOGFORMAT,
        datefmt=DATEFMT,
        reset=True,
        log_colors={
            "DEBUG": DEBUG_COLOUR,
            "INFO": INFO_COLOUR,
            "WARNING": WARNING_COLOUR,
            "ERROR": ERROR_COLOUR,
            "CRITICAL": CRITICAL_COLOUR,
        },
    )

    # 强制清除并重新配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    
    # 清除所有现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加新的 StreamHandler 并应用颜色格式
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    # 配置 uvicorn 相关日志器（保留原始颜色）
    uv_loggers = ["uvicorn", "uvicorn.access", "uvicorn.error"]
    for name in uv_loggers:
        uv_logger = logging.getLogger(name)
        #uv_logger.handlers = []
        # 注释掉以下行以保留 uvicorn 默认颜色
        uv_handler = logging.StreamHandler()
        uv_handler.setFormatter(formatter)
        uv_logger.addHandler(uv_handler)
        uv_logger.propagate = False  # 避免传播到根日志器

    # 配置模块级日志器
    for module, level in module_levels.items():
        module_logger = logging.getLogger(module)
        module_logger.setLevel(level)
        # 清除现有处理器
        module_logger.handlers = []
        # 添加新处理器
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        module_logger.addHandler(handler)
        module_logger.propagate = False

    # 确保所有未配置的日志器使用根配置
    logging.basicConfig(level=LOG_LEVEL, handlers=[])

def getLogger(name=None):
    return logging.getLogger(name)

def getLog(name=None):
    return logging.getLogger(name)

# Apply configuration (call once at program startup)
configure_logging()

### How to use???
# from dispatch.log import getLog
# log = getLog(__name__)
