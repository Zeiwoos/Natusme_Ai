from openai import OpenAI
import json
def get_response(message):
        client = OpenAI(
            api_key="111",
            base_url="https://api.chatanywhere.tech/v1"
        )
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
            model="gpt-3.5-turbo",
        )
        response = chat_completion.json()
        # 获取响应结果
        result_dict = json.loads(response)
        content = result_dict['choices'][0]['message']['content']
        # print('响应信息为:', content)
        return content

