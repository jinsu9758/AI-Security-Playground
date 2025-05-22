import sys
import textwrap
import os
import openai
from openai import OpenAI
import json

def read_xss_py():
    with open("xss.py", "r", encoding="utf-8") as f:
        return f.read()


# Chatgpt API 사용
def send_chatgpt(user_payload, xss_py_content, step_level):
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    #{"role": "user", "content": f"또한 새로운 new_code는 이전 단계의 로직은 삭제하며, 이전 단계들의 로직은 중복이 안되게 하고, 소문자 필터링에서 대문자 필터링 추가 같은 유사한 취약한 로직은 만들지마세요."},
    messages = [
        # system role
        {"role": "system", "content": "You're an assistant who generates vulnerable logic for XSS attacks and sends it to JSON"},
        # 페이로드 전달
        {"role": "user", "content": f"사용자가 입력한 페이로드는\n{user_payload}"},
        # 기본코드 제공
        {"role": "user", "content": f"현재 XSS를 발생시키는 로직은\n{xss_py_content}"},
        # 단계 지정
        {"role": "user", "content": f"사용자의 페이로드를 우회할 수 있어야 하며, 총 5단계중 {step_level}단계의 난이도에 맞게 단계적으로 XSS 공격에 취약한 로직을 만들어주세요."},
        # 조건 부여
        {"role": "user", "content": f"{xss_py_content}와 동일한 페이로드를 넣으면 XSS를 수행할 수 없게 만들어주세요."},
        {"role": "user", "content": f"생성된 로직에 {user_payload}\n를 입력했을 때, 예상되는 결과값과 새롭게 생성한 로직을 JSON 형태로 보여주세요."},
        {"role": "user", "content": f"127.0.0.1:5000에서 document.cookie를 탈취해야하므로 위와 관련된 내용을 필터링해서는 안됩니다."},
        {"role": "user", "content": f"'<','>'는 필터링 요소에 포함시키면 안됩니다."},
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

    # JSON 응답 파싱
    content = response.choices[0].message.content.strip()
    
    rst = response.choices[0].message.content

    # 결과 추출 (JSON 포맷 예상)
    json_data = json.loads(content)

    new_code = json_data["new_code"]
    predict_result = json_data["predict_result"]


    # 응답 결과를 result.txt에 저장(일단 값 확인해볼려고 넣어놨음)
    with open('result.txt', 'w', encoding='utf-8') as f:
        f.write(rst)

    return new_code, predict_result


def execute_gen_code(new_code, user_payload):
    exec_env = {}
    exec(new_code, exec_env)
    return exec_env['display_input'](user_payload)


def overwrite_xss_py(new_code):
    with open("xss.py", "w", encoding="utf-8") as f:
        f.write(new_code)


def process_payload(user_payload, step_level):
    print("user_payload : ", user_payload)
    xss_py_content = read_xss_py()
    print("xss.py : ", xss_py_content)

    while True:
        new_code, predict_result = send_chatgpt(user_payload, xss_py_content, step_level)

        try:
            result = execute_gen_code(new_code, user_payload)
            print("result: ", result)

            assert result == predict_result
            overwrite_xss_py(new_code)
            print("예상 결과와 일치. xss.py 파일이 업데이트되었습니다.")
            break
        except AssertionError:
            print("결과 불일치. send_chatgpt 재실행 중...\n")


if __name__ == "__main__":
    user_payload = sys.argv[1]
    process_payload(user_payload)


