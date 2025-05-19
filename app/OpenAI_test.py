import openai
from openai import OpenAI
import os

# user_payload.txt 파일 읽기
with open('user_payload.txt', 'r', encoding='utf-8') as f:
    user_payload = f.read()

# xss.py 파일 읽기
with open('xss.py', 'r', encoding='utf-8') as f:
    pre_code = f.read()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
#openai.api_key = api_key
step = 2

# ChatGPT API 요청 데이터 구성
messages = [
    # system role
    {"role": "system", "content": "You're an assistant who generates vulnerable logic for XSS attacks and sends it to JSON"},
    # 페이로드 전달
    {"role": "user", "content": f"사용자가 입력한 페이로드는\n{user_payload}"},
    # 기본코드 제공
    {"role": "user", "content": f"현재 XSS를 발생시키는 로직은\n{pre_code}"},
    # 단계 지정
    {"role": "user", "content": f"사용자의 페이로드를 우회할 수 있어야 하며, 총 5단계중 {step}단계의 난이도에 맞게 단계적으로 XSS 공격에 취약한 로직을 만들어주세요."},
    # 조건 부여
    {"role": "user", "content": f"{pre_code}와 동일한 페이로드를 넣으면 XSS를 수행할 수 없게 만들어주세요."},
    {"role": "user", "content": f"생성된 로직에 {user_payload}\n를 입력했을 때, 예상되는 결과값과 새롭게 생성한 로직을 JSON 형태로 보여주세요."},
    {"role": "user", "content": f"127.0.0.1:5000에서 document.cookie를 탈취해야하므로 위와 관련된 내용을 필터링해서는 안됩니다."},
    {"role": "user", "content": f"무조건 JSON 결과값에 대해서만 응답해야하며 결과값 이외의 대답은 절대 하지말아주세요."},
    # 최종 결과 포맷 통일성
    {"role": "user", "content": f"생성된 새로운 로직의 JSON Key는 new_code이고, 예상되는 결과값은 predict_result입니다."},
    {"role": "user", "content": f"새롭게 생성한 함수의 포맷은 def display_input(payload)이며, 함수 내부에서 로직을 가공하고 최종적으로는 payload 변수로 반환되어야합니다."}
]

response = client.chat.completions.create(
    model="gpt-4.1",
    messages=messages,
    temperature=0.2
)

rst = response.choices[0].message.content

# 응답 결과를 result.txt에 저장
with open('result.txt', 'w', encoding='utf-8') as f:
    f.write(rst)
