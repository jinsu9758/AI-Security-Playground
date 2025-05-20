from flask import Flask, render_template, request, flash, make_response
from xss import display_input
from valid import process_payload
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from urllib.parse import quote
import os
import time

app = Flask(__name__)
app.secret_key = 'your-very-secret-key'
BOT_INTERVAL = 10  # 초

flag1 = os.getenv('FLAG1')
flag2 = os.getenv('FLAG2')
flag3 = os.getenv('FLAG3')
flag4 = os.getenv('FLAG4')
flag5 = os.getenv('FLAG5')

def compare_flag(submitted_flag):
    sf = submitted_flag
    
    if sf == flag1:
        level = 1
    elif sf == flag2:
        level = 2
    elif sf == flag3:
        level = 3
    elif sf == flag4:
        level = 4
    elif sf == flag5:
        level = 5
    else:
        level = 0
    
    return level


def create_options():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("disable-dev-shm-usage")
    return options


def visit_payload(level):
    driver = None  # 먼저 정의해서 UnboundLocalError 방지
    try:
        options = create_options()
        driver_path = '/usr/local/bin/chromedriver'
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        app.logger.info("드라이버가 연결되었습니다.")
        
        with open("user_payload.txt", "r", encoding='utf-8') as f:
            payload = f.read().strip()

        encoded_payload = quote(payload)
        url = f"http://127.0.0.1:5000/vuln?q={encoded_payload}"
        app.logger.info(f"[BOT] Visiting: {url}")
        
        driver.implicitly_wait(3)
        driver.set_page_load_timeout(5)
        driver.get("http://127.0.0.1:5000/")

        flag_map = {
            1: flag1,
            2: flag2,
            3: flag3,
            4: flag4,
            5: flag5
        }
        FLAG = flag_map.get(level, flag1)

        driver.add_cookie({
            "name": "flag", 
            "value": FLAG, 
            "domain": "127.0.0.1", 
            "path": "/", 
            "secure": False, 
            "httpOnly": False
        })

        driver.get(url)
        time.sleep(5)  # JS 실행 여유 시간
        return True

    except Exception as e:
        app.logger.error(f"[BOT ERROR] {e}")
        return False

    finally:
        if driver is not None:
            try:
                driver.quit()
                app.logger.info("[BOT] 드라이버 종료됨.")
            except Exception as e:
                app.logger.warning(f"[BOT CLEANUP ERROR] {e}")


@app.route('/')
def home():
    level = request.cookies.get('level', '1')
    return render_template('index.html')


@app.route('/search')
def search():
    query = request.args.get('q', '')
    
    with open('user_payload.txt', 'w', encoding='utf-8') as f:
        f.write(query)
    
    level = int(request.cookies.get('level', 1))
    if visit_payload(level):
        return "Payload visited."
    else:
        return "Fail"
    #result = display_input(query)
    #return render_template('post.html', content=result)


@app.route('/vuln')
def vuln():
    query = request.args.get('q', '')
    result = display_input(query)
    return render_template('post.html', content=result)
    

@app.route('/flag', methods=['GET', 'POST'])
def flag():
    if request.method == 'POST':
        submitted_flag = request.form.get('flag')
        cur_level = compare_flag(submitted_flag)
        prev_level = int(request.cookies.get('level', 1))
        
        if cur_level:
            if cur_level == 5:
                flash('🎉 모든 단계를 완료했습니다! 더 이상 제출할 플래그가 없습니다.', 'success')
                resp = make_response(render_template('flag.html', success=False))
                resp.set_cookie('level', str(cur_level))  # 그대로 유지
                return resp
            
            cur_level += 1
            if cur_level > prev_level:
                flash('정답입니다! 🎉', 'success')
                resp = make_response(render_template('flag.html', success=True))
                resp.set_cookie('level', str(cur_level))
            else:
                flash('틀렸습니다. 다시 시도하세요.', 'danger')
                return render_template('flag.html', success=False)
            return resp
        else:
            flash('틀렸습니다. 다시 시도하세요.', 'danger')
            return render_template('flag.html', success=False)
    else:
        return render_template('flag.html', success=False)


@app.route('/next_step')
def next_step():
    with open('user_payload.txt', 'r', encoding='utf-8') as f:
        user_payload = f.read().strip()
        step_level = int(request.cookies.get('level', 1))

    process_payload(user_payload, step_level)
    flash('새로운 AI 동적 로직이 생성되었습니다.', 'info')
    return render_template('index.html')
    

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000", debug=True)
