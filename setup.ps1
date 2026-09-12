# Windows PowerShell 로컬 개발환경 셋업.
# macOS / Linux는 setup.sh 를 사용하세요.
#
# 실행 정책 때문에 막히면:
#   PowerShell -ExecutionPolicy Bypass -File .\setup.ps1

$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$Python = if ($env:PYTHON) { $env:PYTHON } else { "python" }
$Venv = if ($env:VENV) { $env:VENV } else { ".venv" }

Write-Host "==> 가상환경 생성: $Venv"
& $Python -m venv $Venv

$Pip = Join-Path $Venv "Scripts\pip.exe"
$VenvPython = Join-Path $Venv "Scripts\python.exe"

Write-Host "==> pip 업그레이드"
& $Pip install --quiet --upgrade pip

Write-Host "==> 의존성 설치"
& $Pip install --quiet -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    # korail2는 레거시 setup.py 기반이라 최신 setuptools에서 빌드가 깨진다
    # (AttributeError: install_layout). 구버전 setuptools + 빌드 격리 해제로 우회.
    Write-Host "    기본 설치 실패 - korail2 레거시 빌드 우회 적용"
    & $Pip install --quiet "setuptools<70" wheel
    & $Pip install --quiet --no-build-isolation -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw "의존성 설치 실패" }
}

Write-Host "==> 설치 확인"
& $VenvPython -c "import streamlit, korail2; from korail2 import TrainType; print(f'    streamlit {streamlit.__version__}'); print(f'    korail2 OK (TrainType.KTX={TrainType.KTX})')"

Write-Host ""
Write-Host "완료했습니다. 실행:"
Write-Host ""
Write-Host "  .\$Venv\Scripts\streamlit run streamlit_app.py"
Write-Host ""
Write-Host "CLI:"
Write-Host ""
Write-Host "  `$env:KORAIL_ID = '...'; `$env:KORAIL_PW = '...'"
Write-Host "  .\$Venv\Scripts\python ktx_reserve.py --dep 순천 --arr 용산 --date 20260925 --try-waiting"
