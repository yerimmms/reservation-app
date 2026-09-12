# 🚄 KTX Reservation

[korail2](https://github.com/carpedm20/korail2) 기반 KTX 열차 조회·예약 Streamlit 앱입니다.

### 코레일+ 통합 반영 (2026-09)

2026년 9월 1일 운행분부터 KTX와 SRT가 `코레일+`로 통합되면서 다음을 반영했습니다.

- **(구)SRT 노선이 KTX로 판매** — `TrainType.KTX` 하나로 양쪽 노선을 조회합니다.
- **수서/서울 출발역 구분 소멸** — SRT 전용 인접 노선 그래프를 제거하고 통합 역 목록으로 대체했습니다.
- **SRT 백엔드 제거** — [`ryanking13/SRT`(PyPI `SRTrain`)](https://github.com/ryanking13/SRT)가 통합에 따라 2026-08-30 아카이브되어 의존성에서 뺐습니다.

### 실행 방법

가상환경을 만들고 의존성을 설치하는 셋업 스크립트가 있습니다. Python 3.9 이상이 필요합니다.

**Windows (PowerShell)**

```powershell
.\setup.ps1
.\.venv\Scripts\streamlit run streamlit_app.py
```

실행 정책 때문에 막히면 `PowerShell -ExecutionPolicy Bypass -File .\setup.ps1`

**macOS / Linux**

```bash
./setup.sh
.venv/bin/streamlit run streamlit_app.py
```

> 시스템 Python에 직접 설치하면 `korail2`가 레거시 `setup.py`를 쓰는 탓에
> `AttributeError: install_layout`으로 실패할 수 있습니다. 가상환경을 쓰면 대개 문제가 없고,
> 그래도 실패하면 셋업 스크립트가 `setuptools<70` + 빌드 격리 해제로 자동 재시도합니다.

### CLI 스크립트

빈 좌석이 생길 때까지 주기적으로 조회해 예약(또는 예약대기 신청)을 시도하는 CLI입니다.

**Windows (PowerShell)**

```powershell
$env:KORAIL_ID = "01012345678"; $env:KORAIL_PW = "비밀번호"
.\.venv\Scripts\python ktx_reserve.py --dep 순천 --arr 용산 --date 20260925 --try-waiting
```

**macOS / Linux**

```bash
export KORAIL_ID=01012345678 KORAIL_PW=비밀번호
.venv/bin/python ktx_reserve.py --dep 순천 --arr 용산 --date 20260925 --try-waiting
```

`--try-waiting`을 주면 매진 열차의 예약대기까지 신청을 시도합니다.

ID/비밀번호는 `KORAIL_ID`, `KORAIL_PW` 환경변수로 지정하거나 실행 시 프롬프트에 입력합니다. 옵션은 `python ktx_reserve.py --help`로 확인할 수 있습니다.

### 알려진 제약

코레일+ 앱에 도입된 매크로 탐지(Dynapath)로 인해 로그인 시 `MACRO ERROR`가 발생할 수 있습니다. korail2가 전송하는 앱 버전이 현재 코레일+ 앱과 다르기 때문이며, 이 경우 조회·예약이 동작하지 않습니다. 앱은 이 상태를 감지해 안내 메시지를 표시합니다. 실제 예매는 코레일+ 앱을 이용하세요.
