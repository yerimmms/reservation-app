import streamlit as st
import requests
from datetime import datetime, time as dtime

from korail2 import (
    AdultPassenger,
    KorailError,
    NoResultsError,
    ReserveOption,
    SoldOutError,
    TrainType,
)

from korail_client import REQUEST_TIMEOUT, login

# 코레일+ 통합(2026-09 운행분~)으로 (구)SRT 노선도 KTX로 판매되고 수서/서울 출발역
# 구분이 사라졌다. 따라서 SRT 전용 인접 그래프 대신 단일 역 목록만 유지한다.
# korail2는 한글 역명을 서버로 그대로 전달하므로 역 코드 매핑이 필요 없다.
STATIONS = [
    "서울", "용산", "광명", "수서", "청량리",
    "동탄", "평택지제", "천안아산", "오송", "대전", "김천(구미)",
    "서대구", "동대구", "경주", "울산(통도사)", "밀양", "구포", "부산",
    "포항", "진영", "창원중앙", "창원", "마산", "진주",
    "익산", "정읍", "광주송정", "나주", "목포",
    "전주", "남원", "순천", "여수EXPO",
    "평창", "진부(오대산)", "강릉",
]

DEFAULT_DEP = "순천"
DEFAULT_ARR = "용산"

SEAT_OPTIONS = {
    "일반실 우선": ReserveOption.GENERAL_FIRST,
    "일반실만": ReserveOption.GENERAL_ONLY,
    "특실 우선": ReserveOption.SPECIAL_FIRST,
    "특실만": ReserveOption.SPECIAL_ONLY,
}


def fmt_time(hhmmss):
    return f"{hhmmss[:2]}:{hhmmss[2:4]}"


def train_row(train):
    return {
        "열차": f"{train.train_type_name} {train.train_no}",
        "출발": f"{train.dep_name} {fmt_time(train.dep_time)}",
        "도착": f"{train.arr_name} {fmt_time(train.arr_time)}",
        "특실": "○" if train.has_special_seat() else "—",
        "일반실": "○" if train.has_general_seat() else "—",
        "상태": (train.reserve_possible_name or "").replace("\n", " "),
    }


def train_label(train):
    return (
        f"{fmt_time(train.dep_time)} → {fmt_time(train.arr_time)} "
        f"{train.train_type_name} {train.train_no}"
    )


def show_network_error(exc):
    if isinstance(exc, requests.exceptions.Timeout):
        st.error(
            f"코레일 서버가 {REQUEST_TIMEOUT}초 안에 응답하지 않았습니다. "
            "잠시 후 다시 시도해 주세요."
        )
    else:
        st.error(f"네트워크 오류: {exc}")


def show_korail_error(exc):
    """코레일 서버 오류를 사용자에게 설명한다."""
    msg = str(exc)
    st.error(f"코레일 오류: {msg}")
    if "MACRO" in msg.upper():
        st.warning(
            "코레일의 매크로 탐지에 차단된 상태입니다. korail2가 보내는 앱 버전이 "
            "현재 코레일+ 앱과 달라 발생하며, 조회·예약 모두 동작하지 않습니다. "
            "예매는 코레일+ 앱을 이용해 주세요."
        )


def main():
    st.set_page_config(page_title="KTX Reservation", page_icon="🚄")
    st.title("🚄 KTX Reservation")
    st.caption("코레일+ 통합 기준 — (구)SRT 노선도 KTX로 조회됩니다.")

    col1, col2 = st.columns(2)
    with col1:
        user_id = st.text_input("코레일 아이디 (회원번호/이메일/휴대폰)", "")
    with col2:
        user_pw = st.text_input("비밀번호", type="password")

    col3, col4 = st.columns(2)
    with col3:
        dep = st.selectbox("출발역", STATIONS, index=STATIONS.index(DEFAULT_DEP))
    with col4:
        arrivals = [s for s in STATIONS if s != dep]
        # 출발역이 기본 도착역과 같아지면 목록에서 빠지므로 첫 역으로 대체한다.
        default_arr = DEFAULT_ARR if DEFAULT_ARR in arrivals else arrivals[0]
        arr = st.selectbox("도착역", arrivals, index=arrivals.index(default_arr))

    col5, col6 = st.columns(2)
    with col5:
        dep_date = st.date_input("출발 날짜", value=datetime.now().date())
    with col6:
        dep_time = st.time_input("출발 시각 (이후 열차 조회)", value=dtime(6, 0))

    col7, col8 = st.columns(2)
    with col7:
        adult = st.number_input("인원", min_value=1, max_value=9, value=1)
    with col8:
        seat_label = st.selectbox("좌석", list(SEAT_OPTIONS.keys()))

    if st.button("열차 조회", type="primary"):
        if not user_id or not user_pw:
            st.error("아이디와 비밀번호를 입력해 주세요.")
            return

        with st.spinner("로그인 중..."):
            try:
                korail = login(user_id, user_pw)
            except requests.exceptions.RequestException as exc:
                show_network_error(exc)
                return
            except ValueError:
                # 차단 페이지 등 JSON이 아닌 응답
                st.error("코레일 서버가 예상과 다른 응답을 보냈습니다. 매크로 차단 상태일 수 있습니다.")
                return
            except KorailError as exc:
                show_korail_error(exc)
                return

        if korail is None:
            st.error(
                "로그인에 실패했습니다. 아이디와 비밀번호를 확인해 주세요. "
                "정보가 맞다면 코레일의 매크로 차단일 수 있습니다."
            )
            return

        with st.spinner("열차 조회 중..."):
            try:
                trains = korail.search_train(
                    dep,
                    arr,
                    dep_date.strftime("%Y%m%d"),
                    dep_time.strftime("%H%M%S"),
                    train_type=TrainType.KTX,
                    passengers=[AdultPassenger(adult)],
                    include_no_seats=True,
                )
            except NoResultsError:
                st.session_state.pop("trains", None)
                st.info("조회된 열차가 없습니다.")
                return
            except requests.exceptions.RequestException as exc:
                show_network_error(exc)
                return
            except KorailError as exc:
                show_korail_error(exc)
                return

        st.session_state.korail = korail
        st.session_state.trains = trains
        st.session_state.adult = adult
        st.session_state.seat_label = seat_label

    trains = st.session_state.get("trains")
    if not trains:
        return

    st.subheader(f"조회 결과 {len(trains)}건")
    st.dataframe(
        [train_row(t) for t in trains],
        width="stretch",
        hide_index=True,
    )

    available = [t for t in trains if t.reserve_possible == "Y"]
    if not available:
        st.info("예약 가능한 좌석이 없습니다. 조건을 바꾸거나 다시 조회해 보세요.")
        return

    st.subheader("예약")
    picked = st.selectbox("예약할 열차", available, format_func=train_label)

    if st.button("예약하기"):
        with st.spinner("예약 중..."):
            try:
                reservation = st.session_state.korail.reserve(
                    picked,
                    passengers=[AdultPassenger(st.session_state.adult)],
                    option=SEAT_OPTIONS[st.session_state.seat_label],
                )
            except SoldOutError:
                st.error("이미 매진되었습니다. 다시 조회해 주세요.")
                return
            except requests.exceptions.RequestException as exc:
                show_network_error(exc)
                return
            except KorailError as exc:
                show_korail_error(exc)
                return

        st.success("✅ 예약 완료")
        st.write(reservation)
        st.info(
            f"결제 기한: {reservation.buy_limit_date} "
            f"{fmt_time(reservation.buy_limit_time)} — 코레일+ 앱에서 결제해 주세요."
        )


if __name__ == "__main__":
    main()
