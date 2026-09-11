# 🚄 KTX Reservation

[korail2](https://github.com/carpedm20/korail2) 기반 KTX 열차 조회·예약 Streamlit 앱입니다.

### 코레일+ 통합 반영 (2026-09)

2026년 9월 1일 운행분부터 KTX와 SRT가 `코레일+`로 통합되면서 다음을 반영했습니다.

- **(구)SRT 노선이 KTX로 판매** — `TrainType.KTX` 하나로 양쪽 노선을 조회합니다.
- **수서/서울 출발역 구분 소멸** — SRT 전용 인접 노선 그래프를 제거하고 통합 역 목록으로 대체했습니다.
- **SRT 백엔드 제거** — [`ryanking13/SRT`(PyPI `SRTrain`)](https://github.com/ryanking13/SRT)가 통합에 따라 2026-08-30 아카이브되어 의존성에서 뺐습니다.

### 실행 방법

1. 의존성 설치

   ```
   $ pip install -r requirements.txt
   ```

   > `korail2` 설치가 `install_layout` 오류로 실패하면 `pip install "setuptools<70"` 후 다시 시도하세요.

2. 앱 실행

   ```
   $ streamlit run streamlit_app.py
   ```

### CLI 스크립트

빈 좌석이 생길 때까지 주기적으로 조회해 예약을 시도하는 CLI입니다.

```
$ python ktx_reserve.py --dep 수서 --arr 부산 --date 20260915 --time 060000
```

ID/비밀번호는 `KORAIL_ID`, `KORAIL_PW` 환경변수로 지정하거나 실행 시 프롬프트에 입력합니다. 옵션은 `python ktx_reserve.py --help`로 확인할 수 있습니다.

### 알려진 제약

코레일+ 앱에 도입된 매크로 탐지(Dynapath)로 인해 로그인 시 `MACRO ERROR`가 발생할 수 있습니다. korail2가 전송하는 앱 버전이 현재 코레일+ 앱과 다르기 때문이며, 이 경우 조회·예약이 동작하지 않습니다. 앱은 이 상태를 감지해 안내 메시지를 표시합니다. 실제 예매는 코레일+ 앱을 이용하세요.
