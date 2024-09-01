#gpt(中)-->translate(日)-->voice(日)
#or
#translate(日)-->gpt(日)-->voice(日)--->translate(中)

import requests
import hashlib
import time
# 定义API请求的URL和数据
url = "http://api.fanyi.baidu.com/api/trans/vip/translate?"
appid = "qqq"
key = "111"
def translate(text, target_language):

    salt = str(time.time())

    pre_sign=appid+text+salt+key
    md5_object = hashlib.md5()  # 创建一个MD5对象
    md5_object.update(pre_sign.encode('utf-8'))  # 添加去要加密的文本
    sign = md5_object.hexdigest()  # 获取加密结果



    data = {
        "q": text,
        "from": "auto",
        "to": target_language,
        "appid": appid,
        "salt": salt,
        "sign": sign
    }
    responce=requests.get(url, data)

    return responce.json()

def Start(text, target_language):
    # 提示用户输入text值
    # 调用翻译API
    response = translate(text, target_language)

    result = response['trans_result'][0]['dst']
    # 输出翻译结果
    return result

