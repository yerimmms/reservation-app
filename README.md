# 🎈 Blank app template

A simple Streamlit app template for you to modify!

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```

### KTX 자동 예약 스크립트

[korail2](https://github.com/carpedm20/korail2) 라이브러리를 사용해 KTX 좌석을 주기적으로 조회하고 빈 좌석이 생기면 자동 예약하는 CLI 스크립트입니다.

```
$ python ktx_reserve.py --dep 서울 --arr 동대구 --date 20260215 --time 060000
```

ID/비밀번호는 `KORAIL_ID`, `KORAIL_PW` 환경변수로 지정하거나 실행 시 프롬프트에 입력합니다. 옵션은 `python ktx_reserve.py --help`로 확인할 수 있습니다.
