import time
from fastapi import HTTPException
from jose.exceptions import JWTError
from starlette.status import HTTP_401_UNAUTHORIZED
from dispatch.config import redis_pool
from jose import jwt
from datetime import datetime, timedelta, date
import base64
from Crypto.Cipher import AES
import redis
from dispatch.config import (
    DISPATCH_JWT_SECRET,
    DISPATCH_JWT_ALG,
    LOCAL_ENCRYPT_KEY
)

'''
AES对称加密算法
'''
# 需要补位，str不是16的倍数那就补足为16的倍数


def add_to_16(value):
    value = str(value)
    while len(value) % 16 != 0:
        value += '\0'
    return str.encode(value)  # 返回bytes


def change_chart(text, flag):
    if flag:
        text = text.replace('/', "1abc1")
    else:
        text = text.replace('1abc1', "/")
    return text


def encrypt(text):
    '''
    加密
    '''

    aes = AES.new(add_to_16(LOCAL_ENCRYPT_KEY), AES.MODE_ECB)  # 初始化加密器
    encrypt_aes = aes.encrypt(add_to_16(text))  # 先进行aes加密
    encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
    encrypted_text = change_chart(encrypted_text, True)
    return encrypted_text


def decrypt(text):
    """
     解密方法
    """
    text = change_chart(text, False)
    aes = AES.new(add_to_16(LOCAL_ENCRYPT_KEY), AES.MODE_ECB)  # 初始化加密器
    base64_decrypted = base64.decodebytes(text.encode(encoding='utf-8'))  # 优先逆向解密base64成bytes
    decrypted_text = str(aes.decrypt(base64_decrypted),
                         encoding='utf-8').replace('\0', '')  # 执行解密密并转码返回str

    return decrypted_text


edit_job_token = 'job_edit_token|{}'


def token(job_code):
    DISPATCH_JWT_EXP = 3600 * 24 * 7
    today = date.today()
    now = datetime(
        year=today.year,
        month=today.month,
        day=today.day,
    )
    exp = int(now.timestamp()) + int(DISPATCH_JWT_EXP)
    data = {
        "exp": exp,
        "job_code": job_code,
    }
    token = jwt.encode(data, DISPATCH_JWT_SECRET, algorithm=DISPATCH_JWT_ALG)
    token_key = edit_job_token.format(job_code)
    redis_conn = redis.Redis(connection_pool=redis_pool)
    redis_conn.set(token_key, token)
    return token


def check_edit_job_token(job_code, token):
    info = get_jwt_info(token)
    # if info and str(info.get('job_code', '')) == str(job_code):
    #     return True
    return False if not info else True


def get_jwt_info(token):

    try:
        data = jwt.decode(token, DISPATCH_JWT_SECRET, algorithms=[DISPATCH_JWT_ALG])
    except JWTError as e:
        data = None
    return data


if __name__ == '__main__':
    pass
    # a = encrypt('job_edit_token|489')
    # print(a)
    # b = decrypt(a)
    # print(b)
    job_code = 489
    token_str = token(job_code)
    print(token_str)
    check_edit_job_token(job_code, token_str)
