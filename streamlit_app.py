import streamlit as st
from SRT import SRT
import time
from datetime import datetime

def main():
    st.title("SRT 열차 예약")

    # 로그인 및 조회 조건 입력
    col1, col2 = st.columns(2)
    with col1:
        USER_ID = st.text_input("SRT 아이디 (전화번호/회원번호)", "")
    with col2:
        USER_PW = st.text_input("비밀번호", type="password")

    col3, col4 = st.columns(2)
    with col3:
        DEP = st.text_input("출발역", "동탄")
    with col4:
        ARR = st.text_input("도착역", "순천")

    col5, col6 = st.columns(2)
    with col5:
        DATE = st.text_input("날짜 (YYYYMMDD)", "20251004")
    with col6:
        TIME = st.text_input("시간 (HHMMSS)", "060000")

    if st.button("예약 시작"):
        try:
            srt = SRT(USER_ID, USER_PW)
        except Exception as e:
            st.error(f"로그인 오류: {e}")
            return

        placeholder = st.empty()
        while True:
            with placeholder.container():
                st.write(f"[{datetime.now()}] {DATE} {TIME} 이후 {DEP} → {ARR} 열차 검색 중...")
                trains = srt.search_train(DEP, ARR, DATE, TIME)
                if not trains:
                    st.write("검색 결과가 없습니다.")
                    time.sleep(1)
                    continue

                # 검색된 열차 목록 출력
                for idx, train in enumerate(trains, start=1):
                    st.write(f"[{idx}] {train}")

                st.write("\n잔여석이 있는 첫 번째 열차를 자동으로 예약 시도합니다...")
                for train in trains:
                    txt = str(train)
                    if "예약가능" in txt:  # 예약 가능한 경우
                        try:
                            reservation = srt.reserve(train)
                            st.success("✅ 예약 성공:")
                            st.write(reservation)
                            return
                        except Exception as e:
                            st.error("예약 도중 오류 발생:")
                            st.write(e)
                            time.sleep(5)
                            continue

                st.write("❌ 잔여석이 있는 열차를 찾지 못했습니다.")
                time.sleep(1)

if __name__ == "__main__":
    main()
