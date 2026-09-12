#!/usr/bin/env bash
# macOS / Linux 로컬 개발환경 셋업.
# Windows PowerShell은 setup.ps1 을 사용하세요.
set -euo pipefail

PYTHON="${PYTHON:-python3}"
VENV="${VENV:-.venv}"

cd "$(dirname "$0")"

echo "==> 가상환경 생성: $VENV"
"$PYTHON" -m venv "$VENV"

PIP="$VENV/bin/pip"

echo "==> pip 업그레이드"
"$PIP" install --quiet --upgrade pip

echo "==> 의존성 설치"
if ! "$PIP" install --quiet -r requirements.txt; then
    # korail2는 레거시 setup.py 기반이라 최신 setuptools에서 빌드가 깨진다
    # (AttributeError: install_layout). 구버전 setuptools + 빌드 격리 해제로 우회.
    echo "    기본 설치 실패 — korail2 레거시 빌드 우회 적용"
    "$PIP" install --quiet "setuptools<70" wheel
    "$PIP" install --quiet --no-build-isolation -r requirements.txt
fi

echo "==> 설치 확인"
"$VENV/bin/python" - <<'PY'
import streamlit, korail2
from korail2 import Korail, TrainType
print(f"    streamlit {streamlit.__version__}")
print(f"    korail2 OK (TrainType.KTX={TrainType.KTX})")
PY

cat <<EOF

완료했습니다. 실행:

  $VENV/bin/streamlit run streamlit_app.py

CLI:

  export KORAIL_ID=... KORAIL_PW=...
  $VENV/bin/python ktx_reserve.py --dep 순천 --arr 용산 --date 20260925 --try-waiting
EOF
