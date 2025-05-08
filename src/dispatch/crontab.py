from datetime import datetime
import socket

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from dispatch.config import (
    SYNC_ROLLING_INTERVAL,
    SYNC_FINISHED_PRODUCT_INTERVAL,
    INIT_COVERING_TIME,
    SYNC_COH_INTERVAL,
    INIT_PYTEST_TIME,
    IMPORT_ROLLING_FROM_FTP_INTERVAL,
    EXPORT_ROLLING_FTP_INTERVAL,
    DATABASE_NAME,
    ALERTS2TEAMS_INTERVAL,
    ALERTS2TEAMS_LOG_FILES,
)
from dispatch.log import getLogger
logger = getLogger(__name__)
try:
    from dispatch.contrib.script.database_archives.main import run as clean_db_log
    from dispatch.contrib.sync_data.sync_rolling import mysql_to_postgres
    from dispatch.contrib.sync_data.sync_finished_product import mysql_to_postgres as finished_product_sync
    from dispatch.contrib.sync_data.init_covering import init_cover, init_end_use, init_test
    # from dispatch.sync_data.sync_semi import sync_semi
    from dispatch.contrib.sync_data.run_pytest import run_pytest_in_folder
    from dispatch.contrib.sync_data.import_rolling_from_ftp import import_data_from_ftp
    from dispatch.contrib.sync_data.export_rolling_ftp import export_rolling_to_ftp
    from dispatch.contrib.message_admin.message_server.diff_message_report2teams import process_diff_message_report as diff_message_report2teams
    from dispatch.contrib.script.logrotate.rotate_logs import rotate_logs
    from dispatch.contrib.script.srsm_message.rerun_m362 import rerun_m362_job
    from dispatch.contrib.script.srsm_message.rerun_m1001 import rerun_m1001_job
    from scripts.alerts2teams import alerts2teams



    class SchedulerConfig:
        EXECUTORS = {
            "default": ThreadPoolExecutor(15)
        }
        JOB_DEFAULTS = {
            "misfire_grace_time": 10 * 60,  # 允许任务延迟10分钟执行，避免短暂阻塞导致错过任务
            "coalesce": False,  # 不合并多次未执行的任务
            "max_instances": 1  # 同一任务最多并发 1 个实例，避免重复执行
        }

        @classmethod
        def to_dict(cls):
            return {
                "executors": cls.EXECUTORS,
                "job_defaults": cls.JOB_DEFAULTS,
            }

    # background_scheduler = BackgroundScheduler(executors)
    pytest_scheduler = BlockingScheduler(**SchedulerConfig.to_dict())
    blocking_scheduler = BlockingScheduler(**SchedulerConfig.to_dict())
    cover_scheduler = BlockingScheduler()
    semi_end_use_scheduler = BlockingScheduler()

    FINISHED_SYNC_IP = ["10.7.40.95"]
    FINISHED_SYNC_DB = ["mes1024"]

    def get_local_ip():
        """Returns the local IP address of the machine."""
        return socket.gethostbyname(socket.gethostname())

    def init_scheduler():
        init_import_data_from_ftp()
        init_export_rolling_to_ftp()
        init_finished_product_sync()
        init_db_log()
        init_sync_coh()
        init_mysql_to_postgres()
        init_covering_semi_end_use() # cpu consuming
        init_diff_message_report2teams()
        init_logrotate()
        init_rerun_m362_job()
        init_rerun_m1001_job()
        init_alerts2teams()



    def init_finished_product_sync():
        if get_local_ip() in FINISHED_SYNC_IP and DATABASE_NAME in FINISHED_SYNC_DB:
            blocking_scheduler.add_job(
                finished_product_sync,
                'interval',
                seconds=SYNC_FINISHED_PRODUCT_INTERVAL,
                id="finished_product_sync",
                next_run_time=datetime.now()
            )

    def init_mysql_to_postgres():
        blocking_scheduler.add_job(
            mysql_to_postgres,
            'interval',
            seconds=SYNC_ROLLING_INTERVAL,
            id="mysql_to_postgres",
            next_run_time=datetime.now()
        )

    def init_import_data_from_ftp():
        blocking_scheduler.add_job(
            import_data_from_ftp,
            'interval',
            seconds=IMPORT_ROLLING_FROM_FTP_INTERVAL,
            id="import_data_from_ftp",
            next_run_time=datetime.now()
        )

    def init_export_rolling_to_ftp():
        blocking_scheduler.add_job(
            export_rolling_to_ftp,
            'interval',
            seconds=EXPORT_ROLLING_FTP_INTERVAL,
            id="export_rolling_to_ftp",
            next_run_time=datetime.now()
        )


    def init_sync_coh():
        from dispatch.contrib.sync_data.sync_coh import sync_coh
        blocking_scheduler.add_job(
            sync_coh,
            'interval',
            seconds=SYNC_COH_INTERVAL,
            id="sync_coh",
            next_run_time=datetime.now()
        )


    def init_covering_semi_end_use():
        blocking_scheduler.add_job(
            init_cover,
            'cron',
            hour=INIT_COVERING_TIME,
            minute=0,
            second=0,
            id="init_cover",
            executor="default",
            # next_run_time=datetime.now()
        )
        blocking_scheduler.add_job(
            init_test,
            'cron',
            hour=INIT_COVERING_TIME + 1,
            minute=0,
            second=0,
            id="init_test",
            executor="default",
            # next_run_time=datetime.now()
        )
        blocking_scheduler.add_job(
            init_end_use,
            'cron',
            hour=INIT_COVERING_TIME + 1,
            minute=59,
            second=59,
            id="init_end_use",
            executor="default",
            # next_run_time=datetime.now()
        )


    def init_covering():
        cover_scheduler.add_job(
            init_cover, 'cron', hour=INIT_COVERING_TIME, minute=0, second=0, next_run_time=datetime.now()
        )

    def init_semi_end_use():
        semi_end_use_scheduler.add_job(
            init_end_use, 'cron', hour=INIT_COVERING_TIME, minute=59, second=59, next_run_time=datetime.now()
        )

    def init_pytest():
        pytest_scheduler.add_job(
        run_pytest_in_folder,
        'cron',
        hour=INIT_PYTEST_TIME,
        minute=0,
        second=0,
        id="run_pytest_in_folder",
        executor="default",
        next_run_time=datetime.now()
        )

    def init_db_log():
        blocking_scheduler.add_job(
        clean_db_log,
        'cron',
        hour=INIT_PYTEST_TIME+1,
        minute=0,
        second=0,
        id="clean_db_log",
        executor="default",
        next_run_time=datetime.now()
        )

    def init_diff_message_report2teams():
        blocking_scheduler.add_job(
        diff_message_report2teams,
        'cron',
        hour=7,
        minute=30,
        second=0,
        id="diff_message_report2teams",
        executor="default",
        )

    def init_logrotate():
        blocking_scheduler.add_job(
        rotate_logs,
        'cron',
        hour=23,
        minute=59,
        second=0,
        id="logrotate",
        executor="default",
        )

    def init_rerun_m362_job():
        blocking_scheduler.add_job(
        rerun_m362_job,
        'interval',
        minutes=10,
        id="rerun_m362_job",
        next_run_time=datetime.now()
        )

    def init_rerun_m1001_job():
        blocking_scheduler.add_job(
            rerun_m1001_job,
            'interval',
            minutes=10,
            id="rerun_m1001_job",
            next_run_time=datetime.now()
        )

    def init_alerts2teams():
        # Compute hours list based on interval
        hours = ",".join(str(h) for h in range(0, 24, ALERTS2TEAMS_INTERVAL))

        blocking_scheduler.add_job(
            alerts2teams,
            'cron',
            hour=hours,
            minute=0,
            second=0,
            id="alerts2teams",
            executor="default",
            args=[ALERTS2TEAMS_LOG_FILES, ALERTS2TEAMS_INTERVAL],
        )
except ImportError as e:
    logger.warning(f"ImportError: {str(e)}")
    pass


if __name__ == "__main__":
    pass