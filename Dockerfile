FROM python:3.9-slim

ENV FLAG1=flag{example_flag_1}
ENV FLAG2=flag{example_flag_2}
ENV FLAG3=flag{example_flag_3}
ENV FLAG4=flag{example_flag_4}
ENV FLAG5=flag{example_flag_5}

# 출처 : https://faper.tistory.com/102
# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    curl \
    libxss1 \
    libappindicator1 \
    libgconf-2-4 \
    fonts-liberation \
    libasound2 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    libgbm1 \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libappindicator3-1 \ 
    libgdk-pixbuf2.0-0 \  
    && apt-get clean

# Goole Chrome 80.0.3987.106 버전 다운로드 및 설치
RUN wget https://mirror.cs.uchicago.edu/google-chrome/pool/main/g/google-chrome-stable/google-chrome-stable_80.0.3987.106-1_amd64.deb && \
    dpkg -i google-chrome-stable_80.0.3987.106-1_amd64.deb && \
    apt-get install -f && \
    rm google-chrome-stable_80.0.3987.106-1_amd64.deb

# Chrome 드라이버 80.0.3987.106 버전 다운로드 및 설치
RUN wget https://chromedriver.storage.googleapis.com/80.0.3987.106/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/ && \
    rm chromedriver_linux64.zip


WORKDIR /app
COPY ./app /app
RUN pip install flask
RUN pip install selenium

CMD ["python", "app.py"]
