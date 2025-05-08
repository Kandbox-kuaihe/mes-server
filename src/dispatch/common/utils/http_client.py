

import json
import pickle
import requests
import logging

from dispatch.config import LIMS_URL



from dispatch.log import getLogger
logger = getLogger(__name__)

class HandleHttp:
   

    def __init__(self,url = None):
        self.apiDomain = url if url else LIMS_URL

    def common_http_request(self, requestType, requestUrl=None, headers=None, requestData=None, resultType="dict"):
        """
        发送http请求
        :param interface_url: 接口地址
        :param headerdata: 请求头文件
        :param interface_parm: 接口请求参数
        :param request_type: 请求类型,不区分大小写,GET POST
        :return: 字典形式结果
        """
        # if requestUrl is not None:
        http_url = self.set_http_url(requestUrl)
        # if headers is not None:
        http_head = self.set_http_head(headers)

        if requestData:
            http_body = self.set_http_body(requestData)
        else:
            http_body = {}
        # try:
        if requestType.lower() == 'get':
            result = self.__http_get(http_url,
                                     http_head,
                                     http_body)
            logger.debug('用例请求URL:%s\n'
                         '用例请求头：%s\n'
                         '用例请求参数：%s\n'
                         % (http_url, http_head, http_body))

        elif requestType.lower() == 'post':
            result = self.__http_post(http_url,
                                      http_head,
                                      http_body)
            logger.debug('用例请求URL:%s\n'
                         '用例请求头：%s\n'
                         '用例请求参数：%s\n'
                         % (http_url, http_head, http_body))

        elif requestType.lower() == 'put':
            result = self.__http_put(http_url,
                                     http_head,
                                     http_body)
            logger.debug('用例请求URL:%s\n'
                         '用例请求头：%s\n'
                         '用例请求参数：%s\n'
                         % (http_url, http_head, http_body))
        else:
            logger.error('请求类型错误') 

        if resultType == "dict":
            # try:
            #     return pickle.dumps(json.loads(result))
            # except Exception :
            #     return pickle.dumps(result)
            return json.loads(result)
        else:
            return json.dumps(result,ensure_ascii=False)


    def __http_get(self, interface_url, headerdata, interface_param):
        """

        :param interface_url: 接口地址
        :param headerdata: 请求头文件
        :param interface_param: 接口请求参数
        :return: 字典形式结果
        """
        try:
            if interface_url != '':
                requrl = interface_url

                response = requests.get(url=requrl,
                                        headers=headerdata,
                                        verify=False,
                                        timeout=40,
                                        params=interface_param
                                        )
                if response.status_code == 200:
                    response_time = response.elapsed.microseconds / 1000  # 发起请求和响应到达的时间,单位ms
                    result = response.text
                else:
                    result = json.dumps({'接口返回状态': response.status_code,"reason":response.reason}, ensure_ascii=False)
                    logger.error(result)
            elif interface_url == '':
                result = json.dumps({'接口地址参数为空': ''}, ensure_ascii=False)
                logger.error(result)
            else:
                result = json.dumps({'接口地址错误': ''}, ensure_ascii=False)
                logger.error(result)
        except Exception as e:
            result = json.dumps({'未知错误': str(e)}, ensure_ascii=False)
            logger.error(result)
        return result
    
    def __http_post(self, interface_url, headerdata, interface_param):
        """

        :param interface_url: 接口地址
        :param headerdata: 请求头文件
        :param interface_param: 接口请求参数
        :return: 字典形式结果
        """
        # print("headers", type(headerdata))
        # print("interface_param", type(interface_param))
        try:
            if interface_url != '':
                if 'application/x-www-form-urlencoded' in headerdata.get('Content-Type'):
                    response = requests.post(url=interface_url,
                                             headers=headerdata,  # 字典
                                             data=interface_param,  # 字典
                                             verify=False,
                                             timeout=40)

                if 'application/json' in headerdata.get('Content-Type'):
                    response = requests.post(url=interface_url,
                                             headers=headerdata,  # 字典
                                             json=interface_param,  # 字典
                                             verify=False,
                                             timeout=40)

                if 'multipart/form-data' in headerdata.get('Content-Type'):
                    # files = {'file': open('upload.txt', 'rb')}
                    response = requests.post(url=interface_url,
                                             headers=headerdata,  # 字典
                                             files=interface_param,  # 字典
                                             verify=False,
                                             timeout=40)

                if response.status_code == 200:
                    response_time = response.elapsed.microseconds / 1000  # 发起请求和响应到达的时间,单位ms
                    logger.debug('接口返回结果：%s' % response.text)
                    result = response.text
                else :
                    result = json.dumps({'接口返回状态:': response.status_code,"reason":response.reason}, ensure_ascii=False)
                    logger.error(result)
            elif interface_url == '':
                result = json.dumps({'接口地址参数为空': ''}, ensure_ascii=False)
                logger.error(result)
            else:
                result = json.dumps({'接口地址错误': ''}, ensure_ascii=False)
                logger.error(result)
        except Exception as e:
            result = json.dumps({'未知错误': str(e)}, ensure_ascii=False)
            logger.error(result)
        return result

    def __http_put(self, interface_url, headerdata, interface_param):
        """
        
        :param interface_url: 请求URL
        :param headerdata: 请求头参数
        :param interface_param: 请求体参数
        :return: 
        """
        try:
            if 'application/x-www-form-urlencoded' in headerdata.get('Content-Type'):
                interface_param = interface_param
            elif 'application/json' in headerdata.get('Content-Type'):
                interface_param = json.dumps(interface_param)
            else:
                pass
            print(type(interface_param), interface_param)
            if interface_url != '':
                requrl = interface_url
                response = requests.put(url=requrl,
                                        headers=headerdata,
                                        data=interface_param,
                                        verify=False,
                                        timeout=40)
                if response.status_code == 200:
                    result = response.text
                else:
                    result = json.dumps({'接口返回状态:': response.status_code,"reason":response.reason}, ensure_ascii=False)
            elif interface_url == '':
                result = json.dumps({'接口地址参数为空': ''}, ensure_ascii=False)
                logger.error(result)
            else:
                result = json.dumps({'接口地址错误': ''}, ensure_ascii=False)
                logger.error(result)
        except Exception as e:
            result = json.dumps({'未知错误': str(e)}, ensure_ascii=False)
            logger.error(result)
        return result

    def set_http_head(self, headerdata):
        """
        公共设置请求头方法
        设置http请求头，参数为json格式的字符串：{"Content-Type":“application/json”}
        """

        if not headerdata:
            http_head = {}
        else:
            if isinstance(headerdata, dict):
                http_head = headerdata
            elif isinstance(headerdata, str) and headerdata.startswith('{') and headerdata.endswith('}'):
                http_head = json.loads(headerdata)
            elif isinstance(headerdata, bytes):
                http_head = pickle.loads(headerdata)
            else:
                pass
        http_head["Content-Type"] = "application/json"
        return http_head


    def set_http_body(self, body):
        """
        公共设置请求体方法
        设置http请求体，参数为json格式的字符串：{"demo":123}
        """
        try:
            if isinstance(body, str) and body.startswith('{'):
                http_body = json.loads(body)
                logger.debug('设置请求体成功')
            elif isinstance(body, dict):
                http_body = body
            elif isinstance(body, bytes):
                http_body = pickle.loads(body)
            else:
                pass
        except Exception as e:
            http_body = body
            logger.error('设置请求体失败:%s' % body)
        return http_body

    def set_http_url(self, interface_url):
        """
         公共设置URL方法
         设置http请求url,如：http://www.baidu.com
        """
        if not interface_url.startswith('https://') and not interface_url.startswith('http://'):
            http_url = self.apiDomain + interface_url
        else:
            http_url = interface_url
        return http_url


if __name__ == '__main__':
    '''
    DEB.ENV 配置文件添加参数
    LIMS_URL=http://localhost:8000/api/v1
    LIMS_TOKEN=""
    '''
    lims_jwtoken= "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjEwMzY3ODU3MzMyLjc2OTk1OCwiZW1haWwiOiJ0ZXN0QGRlbW8uY29tIiwib3JnX2NvZGUiOiJ0ZXN0Iiwib3JnX2lkIjoxMDIsInJvbGUiOiJPd25lciIsImRlZmF1bHRfdGVhbV9pZCI6MX0.pb3_NUWzkBP5zw9mg46cIaz9fa7FSJJJS-80wg_Mpu0"
    lims_domain= "http://localhost:8000/api/v1/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {lims_jwtoken} ",
    }
    requestUrl = "message/push_message"
    requestData = {
        "id":120,
        "type":"pc",
        "msg":""
        }
    
    http_client = HandleHttp()
    response = http_client.common_http_request("post",requestUrl,headers,requestData)