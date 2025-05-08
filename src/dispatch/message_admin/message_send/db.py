import json
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dispatch.config import DB_PARAMS_DICT


class MessageLogDB:
    def __init__(self, host=None, port=None, user=None, password=None, database=None):
        self.postgres_config = {
            'host': host or DB_PARAMS_DICT["host"],
            'port': port or DB_PARAMS_DICT["port"],
            'user': user or DB_PARAMS_DICT["user"],
            'password': password or DB_PARAMS_DICT["password"],
            'database': database or DB_PARAMS_DICT["dbname"]
        }

        self.postgres_url = f"postgresql://{self.postgres_config['user']}:{self.postgres_config['password']}@{self.postgres_config['host']}:{self.postgres_config['port']}/{self.postgres_config['database']}"
        self.engine = create_engine(self.postgres_url)
        self.session = sessionmaker(bind=self.engine)()
        self.schema = "dispatch_organization_mes_root"

    from datetime import datetime

    def query_7xxx_message(self, message_id: int, from_time=None, to_time=None, message_source: str = 'message_json'):
        # 如果 from_time 或 to_time 为 None，默认设置为当前日期
        if from_time is None:
            from_time = datetime.today().date()  # 设置默认值为今天
        if to_time is None:
            to_time = datetime.today().date()  # 设置默认值为今天
        print(from_time, to_time)
        # 执行 SQL 查询
        result = self.session.execute(
            f"""
            SELECT {message_source}
            FROM {self.schema}.message_log 
            WHERE message_json IS NOT NULL 
            AND created_at::date >= '{from_time}'::date
            AND created_at::date <= '{to_time}'::date
            AND message_id = {message_id}
            """
        )
        result_list = [json.loads(i[0]) for i in result.fetchall()]
        return result_list

    def query_srsm_message(self, message_id: int, from_time=None, to_time=None, message_source: str = 'msg'):
        # 如果 from_time 或 to_time 为 None，默认设置为当前日期
        if from_time is None:
            from_time = datetime.today().date()  # 设置默认值为今天
        if to_time is None:
            to_time = datetime.today().date()  # 设置默认值为今天
        print(from_time, to_time)
        # 执行 SQL 查询
        result = self.session.execute(
            f"""
            SELECT message_id, \"type\", {message_source}
            FROM {self.schema}.message_log 
            WHERE message_json IS NOT NULL 
            AND created_at::date >= '{from_time}'::date
            AND created_at::date <= '{to_time}'::date
            AND message_id = {message_id}
            AND repeat_flag = 0
            """
        )
        result_list = [{"id": i[0],
                        "type": i[1],
                        "msg": i[2]
                        } for i in result.fetchall()]
        return result_list

    def query_all_message_id(self):
        result = self.session.execute(F"SELECT DISTINCT message_id FROM {self.schema}.message_log ")
        result_list = [int(i[0]) for i in result.fetchall()]
        return result_list


    def delete_repeat_message_logs(self, message_id: int, from_time=None, to_time=None):
        if from_time is None:
            from_time = datetime.today().date()  # 设置默认值为今天
        if to_time is None:
            to_time = datetime.today().date()  # 设置默认值为今天

        result = self.session.execute(
            f"""
            DELETE FROM {self.schema}.message_log 
            WHERE message_id = {message_id}
            AND created_at::date >= '{from_time}'::date
            AND created_at::date <= '{to_time}'::date
            AND repeat_flag = 1
            """
        )

        self.session.commit()
        return True


if __name__ == '__main__':
    mb = MessageLogDB()

    # one = mb.query_7xxx_message(message_id=7104, from_time='2025-04-01', to_time='2025-04-03')[0]
    # print(type(json.loads(one)))

    print(mb.query_all_message_id())
