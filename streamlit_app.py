import streamlit as st
from SRT import SRT
import time
from datetime import datetime

# SRT adjacency 해시 테이블 (그래프 대신 dict)
srt_adj = {
    "SUSO": ["DONGTAN", "PYEONGTAEK_JIJE", "CHEONAN_ASAN", "OSONG", "DAEJEON", "GIMCHEON_GUMI", 
             "SEODAEGU", "DONGDAEGU", "GYEONGJU", "ULSAN", "BUSAN", "MIRYANG", "JIYEONG", 
             "CHANGWON_JUNGANG", "CHANGWON", "MASAN", "JINJU", "IKSAN", "JEONGEUP", 
             "GWANGJU_SONGJEONG", "NAJU", "MOKPO", "SUNCHEON", "GWANGYANG", "YEOSU_EXPO", 
             "POHANG", "GANGNEUNG"],
    
    "DONGTAN": ["PYEONGTAEK_JIJE", "CHEONAN_ASAN", "OSONG", "DAEJEON", "GIMCHEON_GUMI", 
                "SEODAEGU", "DONGDAEGU", "GYEONGJU", "ULSAN", "BUSAN", "MIRYANG", "JIYEONG", 
                "CHANGWON_JUNGANG", "CHANGWON", "MASAN", "JINJU", "IKSAN", "JEONGEUP", 
                "GWANGJU_SONGJEONG", "NAJU", "MOKPO", "SUNCHEON", "GWANGYANG", "YEOSU_EXPO", 
                "POHANG", "GANGNEUNG"],
    
    "PYEONGTAEK_JIJE": ["CHEONAN_ASAN", "OSONG", "DAEJEON", "GIMCHEON_GUMI", 
                        "SEODAEGU", "DONGDAEGU", "GYEONGJU", "ULSAN", "BUSAN", 
                        "MIRYANG", "JIYEONG", "CHANGWON_JUNGANG", "CHANGWON", "MASAN", "JINJU", 
                        "IKSAN", "JEONGEUP", "GWANGJU_SONGJEONG", "NAJU", "MOKPO", 
                        "SUNCHEON", "GWANGYANG", "YEOSU_EXPO", "POHANG", "GANGNEUNG"],
    
    "CHEONAN_ASAN": ["OSONG", "DAEJEON", "GIMCHEON_GUMI", "SEODAEGU", "DONGDAEGU", 
                     "GYEONGJU", "ULSAN", "BUSAN", "MIRYANG", "JIYEONG", "CHANGWON_JUNGANG", 
                     "CHANGWON", "MASAN", "JINJU", "IKSAN", "JEONGEUP", "GWANGJU_SONGJEONG", 
                     "NAJU", "MOKPO", "SUNCHEON", "GWANGYANG", "YEOSU_EXPO", "POHANG", "GANGNEUNG"],
    
    "OSONG": ["DAEJEON", "GIMCHEON_GUMI", "SEODAEGU", "DONGDAEGU", "GYEONGJU", "ULSAN", 
              "BUSAN", "MIRYANG", "JIYEONG", "CHANGWON_JUNGANG", "CHANGWON", "MASAN", "JINJU", 
              "IKSAN", "JEONGEUP", "GWANGJU_SONGJEONG", "NAJU", "MOKPO", "SUNCHEON", 
              "GWANGYANG", "YEOSU_EXPO", "POHANG", "GANGNEUNG"],
    
    "DAEJEON": ["GIMCHEON_GUMI", "SEODAEGU", "DONGDAEGU", "GYEONGJU", "ULSAN", "BUSAN", 
                "MIRYANG", "JIYEONG", "CHANGWON_JUNGANG", "CHANGWON", "MASAN", "JINJU"],
    
    "GIMCHEON_GUMI": ["SEODAEGU", "DONGDAEGU", "GYEONGJU", "ULSAN", "BUSAN", "MIRYANG", 
                      "JIYEONG", "CHANGWON_JUNGANG", "CHANGWON", "MASAN", "JINJU"],
    
    "SEODAEGU": ["DONGDAEGU", "GYEONGJU", "ULSAN", "BUSAN", "MIRYANG", "JIYEONG", 
                 "CHANGWON_JUNGANG", "CHANGWON", "MASAN", "JINJU"],
    
    "DONGDAEGU": ["GYEONGJU", "ULSAN", "BUSAN", "MIRYANG", "JIYEONG", "CHANGWON_JUNGANG", 
                  "CHANGWON", "MASAN", "JINJU", "POHANG"],
    
    "GYEONGJU": ["ULSAN", "BUSAN"],
    "ULSAN": ["BUSAN"],
    "MIRYANG": ["JIYEONG", "CHANGWON_JUNGANG", "CHANGWON", "MASAN", "JINJU"],
    "JIYEONG": ["CHANGWON_JUNGANG", "CHANGWON", "MASAN", "JINJU"],
    "CHANGWON_JUNGANG": ["CHANGWON", "MASAN", "JINJU"],
    "CHANGWON": ["MASAN", "JINJU"],
    "MASAN": ["JINJU"],
    "IKSAN": ["JEONGEUP", "GWANGJU_SONGJEONG", "NAJU", "MOKPO", "SUNCHEON", "GWANGYANG", "YEOSU_EXPO"],
    "JEONGEUP": ["GWANGJU_SONGJEONG", "NAJU", "MOKPO"],
    "GWANGJU_SONGJEONG": ["NAJU", "MOKPO"],
    "NAJU": ["MOKPO"],
    "SUNCHEON": ["GWANGYANG", "YEOSU_EXPO"],
    "GWANGYANG": ["YEOSU_EXPO"]
}

# 역 이름 해시
station_names = {
    "SUSO": "수서", "DONGTAN": "동탄", "PYEONGTAEK_JIJE": "평택지제", "CHEONAN_ASAN": "천안아산",
    "OSONG": "오송", "DAEJEON": "대전", "GIMCHEON_GUMI": "김천(구미)", "SEODAEGU": "서대구",
    "DONGDAEGU": "동대구", "GYEONGJU": "경주", "ULSAN": "울산", "BUSAN": "부산",
    "MIRYANG": "밀양", "JIYEONG": "진영", "CHANGWON_JUNGANG": "창원중앙", "CHANGWON": "창원",
    "MASAN": "마산", "JINJU": "진주", "IKSAN": "익산", "JEONGEUP": "정읍",
    "GWANGJU_SONGJEONG": "광주송정", "NAJU": "나주", "MOKPO": "목포",
    "YEOSU_EXPO": "여수EXPO", "SUNCHEON": "순천", "GWANGYANG": "광양", "POHANG": "포항",
    "GANGNEUNG": "강릉"
}

all_stations = list(srt_adj.keys()) + ["GANGNEUNG", "POHANG"]  # 종점 포함

# Session state 초기화
if 'departure_id' not in st.session_state:
    st.session_state.departure_id = "DONGTAN"


def main():
    st.title("🚄 SRT Reservation")

    # 로그인 및 조회 조건 입력
    col1, col2 = st.columns(2)
    with col1:
        USER_ID = st.text_input("SRT 아이디 (전화번호/회원번호)", "")
    with col2:
        USER_PW = st.text_input("비밀번호", type="password")

    col3, col4 = st.columns(2)
    with col3:
        # DEP = st.text_input("출발역", "동탄")
        departure_id = st.selectbox(
            "출발역 (해시 테이블 조회)",
            all_stations,
            index=all_stations.index(st.session_state.departure_id),
            format_func=lambda x: station_names.get(x, x)
        )
        st.session_state.departure_id = departure_id
        # 출발역이 바뀔 때 도착역 선택값을 초기화하여 바로 반영되도록 함
        st.session_state.pop("filtered_arrival", None)
        DEP = station_names[departure_id]
    with col4:
        # ARR = st.text_input("도착역", "순천")
        valid_arrivals = srt_adj.get(st.session_state.departure_id, [])
        if valid_arrivals:
            # 도착역 필터링 드롭다운
            arrival_id = st.selectbox(
                "도착역 (연결된 역만)",
                valid_arrivals,
                format_func=lambda x: station_names[x],
                key="filtered_arrival",
            )
            ARR = station_names[arrival_id]

    col5, col6 = st.columns(2)
    with col5:
        DATE = st.text_input("날짜 (YYMMDD)", "260215", max_chars=6)
    with col6:
        TIME = st.text_input("시간 (HHMM)", "0600", max_chars=4)

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
                trains = srt.search_train(DEP, ARR, f'20{DATE}', f'{TIME}00')
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
