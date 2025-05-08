import multiprocessing
import uvicorn
import logging
import time
from dispatch.config import DEBUG

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
from dispatch.log import getLogger
logger = getLogger(__name__)

def main():
    try:
        overall_start_time = time.time()
        startup_phases = {}
        
        # 记录配置准备时间
        config_start = time.time()
        cpu_count = multiprocessing.cpu_count()
        workers = cpu_count * 2 + 1 if not DEBUG else 1
        
        # Uvicorn配置
        config = uvicorn.Config(
            "dispatch.main:app",
            host="0.0.0.0",
            port=8000,
            workers=workers if not DEBUG else 1,
            loop="uvloop",
            limit_concurrency=1000,
            limit_max_requests=10000,
            timeout_keep_alive=30,
            access_log=False,
            reload=DEBUG,
            reload_dirs=["src/dispatch"],
            log_level="info",
            proxy_headers=True,
            forwarded_allow_ips="*",
        )
        startup_phases['config_preparation'] = time.time() - config_start
        
        # 记录服务器初始化时间
        server_init_start = time.time()
        server = uvicorn.Server(config)
        startup_phases['server_initialization'] = time.time() - server_init_start
        
        # 打印启动阶段耗时统计
        logger.info("Startup phases breakdown:")
        for phase, duration in startup_phases.items():
            logger.info(f"  - {phase}: {duration:.2f} seconds")
            
        logger.info(f"Starting server with {workers} workers (DEBUG={DEBUG})")
        logger.info(f"Total preparation time: {time.time() - overall_start_time:.2f} seconds")
        
        # 运行服务器
        server.run()
        
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise

if __name__ == "__main__":
    main()
