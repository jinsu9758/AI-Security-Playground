import sys
import textwrap

def read_xss_py():
    with open("xss.py", "r", encoding="utf-8") as f:
        return f.read()


# 수정 필요
def send_chatgpt(user_payload, xss_py_content):
    msg = "balah" + user_payload + "\n\n" + "xss_py_content"
    api = "/chatgpt_api_route_example"
    
    new_code = textwrap.dedent("""
    def display_input(payload):
        return payload[::-1]
    """)
    
    predict_result = "cba"

    res = [new_code, predict_result]
    return res


def execute_gen_code(new_code, user_payload):
    exec_env = {}
    exec(new_code, exec_env)
    return exec_env['display_input'](user_payload)


def overwrite_xss_py(new_code):
    with open("xss.py", "w", encoding="utf-8") as f:
        f.write(new_code)


def process_payload(user_payload):
    print("user_payload : ", user_payload)
    xss_py_content = read_xss_py()
    print("xss.py : ", xss_py_content)

    while True:
        new_code, predict_result = send_chatgpt(user_payload, xss_py_content)

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


