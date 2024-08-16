import requests

# 天气API相关配置
API_KEY = '105484b2036786d8a43149e287f9ca40'
BASE_URL = 'https://restapi.amap.com/v3/weather/weatherInfo?'

def get_weather(city):
    # 调用天气API
    params = {
        'city': city,
        'key': API_KEY,
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if response.status_code == 200:
        # 解析并返回天气信息
        city = data['lives'][0]['city']
        weather = data['lives'][0]['weather']
        temperature = data['lives'][0]['temperature']
        return f"{city}现在的天气: {weather}, 温度: {temperature}°C"
        # return data
    else:
        return "无法获取天气信息"

if __name__ == '__main__':
    print(get_weather('洪山区'))
#信丰县360722
#北京市110000
#武汉市 420100   洪山区 420111
