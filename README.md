# TelePaparazzi_v2

* git clone
```
git clone https://github.com/sjjang61/TelePaparazzi_v2.git 
```

* Python version
  * over 3.10.x 
  * package install
```
pip install -r requirements.txt
```

* Project Settings
```
1) Create Telgram Application : https://core.telegram.org/api/obtaining_api_id
    - Create api_id, api_hash, ip( test/ production), public key 
2) run ChannelUsers.py 
    - Insert api_id, api_hash
    - URL : https://t.me/joinchat/AAAAAFRhb23DUnVI4m9zVA
3) Telegram Auth 
    - https://medium.com/better-programming/how-to-get-data-from-telegram-82af55268a4b
4) DB Create
    - Crate Mysql Database without tables     
    - Configure : config.init
5) run main.py
    - Receive tetegram mesage & insert DB
    - create database tables 
```

* 한국투자 OPEN API 사용신청
    - https://apiportal.koreainvestment.com/intro
    - app_key, secret_key 발급 필요 

* .env 설정 
```
cp .env.sample .env
한국투자 OPEN_API KEY 값 설정
```