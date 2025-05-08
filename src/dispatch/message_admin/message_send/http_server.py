import datetime

import aiohttp
import asyncio

from dispatch.config import DEFAULT_EMAIL, DEFAULT_PWD
from dispatch.message_admin.message_send.db import MessageLogDB

import aiohttp
import asyncio


class AsyncHttpClient:
    def __init__(self):
        self.session = None
        self.token = None  # 用于存储 token

    async def _init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def _close_session(self):
        if self.session:
            await self.session.close()

    async def close_session(self):
        await self._close_session()

    async def _send_request(self, method, url, params=None, data=None, json=None, headers=None, cookies=None):

        await self._init_session()

        # 如果有 token，则将 token 加入请求头
        if self.token:
            if headers is None:
                headers = {}
            headers['Authorization'] = f'Bearer {self.token}'

        async with self.session.request(method, url, params=params, data=data, json=json, headers=headers,
                                        cookies=cookies) as response:

            # 如果响应状态为 204，无内容（如 DELETE 请求），返回 None
            if response.status == 204:
                return True, None
            if response.status == 200:
                # 返回 JSON 格式的响应内容
                return await response.json()
            if response.status == 400:
                content = await response.content.read()
                print(f"HTTP 请求失败，400 错误: {content.decode('utf-8')}")
            else:
                content = await response.content.read()

                print(f"HTTP 请求失败: {response}")
            return False, response.status, json, content.decode('utf-8')

    async def get(self, url, params=None, headers=None, cookies=None):
        return await self._send_request('GET', url, params=params, headers=headers, cookies=cookies)

    async def post(self, url, data=None, json=None, headers=None, cookies=None):
        return await self._send_request('POST', url, data=data, json=json, headers=headers, cookies=cookies)

    async def put(self, url, data=None, json=None, headers=None, cookies=None):
        return await self._send_request('PUT', url, data=data, json=json, headers=headers, cookies=cookies)

    async def delete(self, url, params=None, headers=None, cookies=None):
        return await self._send_request('DELETE', url, params=params, headers=headers, cookies=cookies)

    async def login(self, login_url, username, password):
        """登录并获取 token"""
        data = {
            'email': username,
            'password': password
        }

        login_response = await self.post(login_url, json=data)
        data = login_response.get('data', [])
        if login_response and 'token' in data:
            self.token = data['token']  # 假设 token 保存在响应的 'token' 字段中
            return self.token
        else:
            print("Login failed, no token received.")
            return None

    async def batch_post(self, url, data_list, headers=None, cookies=None, sequential=True):
        """批量发送 POST 请求，支持按顺序或并发执行"""
        from dispatch.enums import FilePath
        success_count = 0
        failure_count = 0
        error_log_filename = fr"{FilePath.RESEND_MESSAGE_LOGS_PATH.value}send_message_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        responses = []

        if sequential:
            # 按顺序执行
            for data in data_list:
                response = await self.post(url, json=data, headers=headers, cookies=cookies)  # 逐个执行
                responses.append(response)
                if isinstance(response, tuple):
                    status = response[0]
                    status_code = response[1]
                    response_data = response[2]
                    response_reason = response[3]
                    if status:
                        success_count += 1
                    else:
                        failure_count += 1
                        with open(error_log_filename, 'a', encoding='utf-8') as f:
                            f.write(f"Status Code: {status_code} >>>>>>> Request Reason: {response_reason}\n")
                            f.write(f"Response Data: {response_data}\n\n")  # 两行换行
                else:
                    success_count += 1
        else:
            # 并发执行
            tasks = [self.post(url, json=data, headers=headers, cookies=cookies) for data in data_list]
            responses = await asyncio.gather(*tasks)

            for response in responses:
                if isinstance(response, tuple):
                    status = response[0]
                    status_code = response[1]
                    response_data = response[2]
                    response_reason = response[3]
                    if status:
                        success_count += 1
                    else:
                        failure_count += 1
                        with open(error_log_filename, 'a', encoding='utf-8') as f:
                            f.write(f"Status Code: {status_code} >>>>>>> Request Reason: {response_reason}\n")
                            f.write(f"Response Data: {response_data}\n\n")  # 两行换行
                else:
                    success_count += 1

        # 输出统计结果
        print(f"成功发送的请求数: {success_count}")
        print(f"失败的请求数: {failure_count}")
        return responses, success_count, failure_count





class SendMessage:
    def __init__(self):
        self.mb = MessageLogDB()
        self.client = AsyncHttpClient()
        self.url_7xxx = 'http://localhost:8000/api/v1/message_server/push_message/pc_7xxx/repeat'
        self.url_srsm = 'http://localhost:8000/api/v1/message_server/push_message/repeat'
        self.login_url = 'http://localhost:8000/api/v1/auth/login'

    def get_date_7xxx(self, message_id: int, from_time=None, to_time=None):
        result_list = self.mb.query_7xxx_message(message_id, from_time, to_time)
        return result_list

    def get_date_srsm(self, message_id: int, from_time=None, to_time=None):
        result_list = self.mb.query_srsm_message(message_id, from_time, to_time)
        return result_list

    async def resend_7xxx(self, data: list, sequential=True, is_delete_logs=True):
        token = await self.client.login(login_url=self.login_url, username=DEFAULT_EMAIL,
                                        password=DEFAULT_PWD)
        response, success_count, failure_count = await self.client.batch_post(url=self.url_7xxx, data_list=data,
                                                                              sequential=sequential)
        self.close()
        return success_count, failure_count

    async def resend_srsm(self, data: list, sequential=True):
        token = await self.client.login(login_url=self.login_url, username=DEFAULT_EMAIL,
                                        password=DEFAULT_PWD)

        response, success_count, failure_count = await self.client.batch_post(url=self.url_srsm, data_list=data,
                                                                              sequential=sequential)
        self.close()
        return success_count, failure_count

    def delete_logs(self, message_id: int, from_time=None, to_time=None):
        return self.mb.delete_repeat_message_logs(message_id=message_id, from_time=from_time, to_time=to_time)

    def close(self):
        self.client.close_session()


async def main(message_id: int, from_time=None, to_time=None, sequential=True):
    client = AsyncHttpClient()
    message = SendMessage()
    if message_id in [7001, 7104, 7108, 7118]:
        data = message.get_date_7xxx(message_id=message_id, from_time=from_time, to_time=to_time)
        success_count, failure_count = await message.resend_7xxx(data=data, sequential=sequential)
    else:
        data = message.get_date_srsm(message_id=message_id, from_time=from_time, to_time=to_time)
        success_count, failure_count = await message.resend_srsm(data=data, sequential=sequential)
    await client.close_session()
    message.delete_logs(message_id=message_id)

if __name__ == '__main__':
    MESSAGE_ID = 2
    FROM_TIME = '2025-03-01'
    TO_TIME = '2025-04-09'
    asyncio.run(main(message_id=MESSAGE_ID, from_time=FROM_TIME, to_time=TO_TIME))
