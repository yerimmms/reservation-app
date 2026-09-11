#!/usr/bin/env python3
"""KTX(코레일) 자동 예약 스크립트.

korail2(https://github.com/carpedm20/korail2) 오픈소스 라이브러리를 사용해
지정한 구간/시간대의 열차를 주기적으로 조회하고, 빈 좌석이 발생하면 즉시 예약을 시도한다.

설치:
    pip install korail2

사용 예:
    python ktx_reserve.py --dep 서울 --arr 동대구 --date 20260215 --time 060000

ID/비밀번호는 KORAIL_ID, KORAIL_PW 환경변수로 지정하거나, 실행 시 프롬프트로 입력한다.
"""

import argparse
import getpass
import os
import random
import sys
import time
from datetime import datetime

from korail2 import (
    AdultPassenger,
    ChildPassenger,
    NoResultsError,
    ReserveOption,
    SeniorPassenger,
    SoldOutError,
    TrainType,
)

from korail_client import login

SEAT_OPTIONS = {
    "general_first": ReserveOption.GENERAL_FIRST,
    "general_only": ReserveOption.GENERAL_ONLY,
    "special_first": ReserveOption.SPECIAL_FIRST,
    "special_only": ReserveOption.SPECIAL_ONLY,
}

TRAIN_TYPES = {
    "all": TrainType.ALL,
    "ktx": TrainType.KTX,
    "saemaeul": TrainType.SAEMAEUL,
    "mugunghwa": TrainType.MUGUNGHWA,
    "itx_saemaeul": TrainType.ITX_SAEMAEUL,
    "itx_cheongchun": TrainType.ITX_CHEONGCHUN,
}


def build_passengers(adult, child, senior):
    passengers = []
    if adult:
        passengers.append(AdultPassenger(adult))
    if child:
        passengers.append(ChildPassenger(child))
    if senior:
        passengers.append(SeniorPassenger(senior))
    return passengers or None


def parse_args():
    parser = argparse.ArgumentParser(description="KTX 자동 예약 스크립트 (korail2 기반)")
    parser.add_argument("--id", default=os.environ.get("KORAIL_ID"),
                         help="코레일 회원번호/이메일/휴대폰번호 (환경변수 KORAIL_ID로도 지정 가능)")
    parser.add_argument("--password", default=os.environ.get("KORAIL_PW"),
                         help="코레일 비밀번호 (환경변수 KORAIL_PW로도 지정 가능)")
    parser.add_argument("--dep", required=True, help="출발역 (예: 서울)")
    parser.add_argument("--arr", required=True, help="도착역 (예: 동대구)")
    parser.add_argument("--date", required=True, help="출발 날짜 yyyyMMdd (예: 20260215)")
    parser.add_argument("--time", default="000000", help="이 시각(hhmmss) 이후 열차만 조회 (기본: 000000)")
    parser.add_argument("--train-type", default="ktx", choices=TRAIN_TYPES.keys(), help="열차 종류 (기본: ktx)")
    parser.add_argument("--adult", type=int, default=1, help="성인 인원수 (기본: 1)")
    parser.add_argument("--child", type=int, default=0, help="어린이 인원수 (기본: 0)")
    parser.add_argument("--senior", type=int, default=0, help="노인 인원수 (기본: 0)")
    parser.add_argument("--seat", default="general_first", choices=SEAT_OPTIONS.keys(),
                         help="좌석 옵션 (기본: general_first)")
    parser.add_argument("--try-waiting", action="store_true", help="매진 시 예약대기 신청도 시도")
    parser.add_argument("--interval", type=float, default=5.0,
                         help="조회 재시도 간격(초). 서버 부담을 줄이기 위해 최소 3초 이상 권장 (기본: 5)")
    parser.add_argument("--max-tries", type=int, default=0, help="최대 재시도 횟수 (0=무제한, 기본: 0)")
    return parser.parse_args()


def reserve_loop(korail, args, passengers, train_type, seat_option):
    attempt = 0
    while args.max_tries == 0 or attempt < args.max_tries:
        attempt += 1
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            # include_no_seats=True로 매진 열차도 함께 받아와, 좌석이 풀리는 순간을 감지한다.
            trains = korail.search_train(
                args.dep, args.arr, args.date, args.time,
                train_type=train_type,
                passengers=passengers,
                include_no_seats=True,
            )
        except NoResultsError:
            print(f"[{now}] (#{attempt}) 조회 결과 없음. {args.interval}초 후 재시도.")
            time.sleep(args.interval)
            continue
        except Exception as exc:
            print(f"[{now}] (#{attempt}) 조회 오류: {exc}. {args.interval}초 후 재시도.")
            time.sleep(args.interval)
            continue

        candidates = [t for t in trains if t.reserve_possible == "Y"]
        print(f"[{now}] (#{attempt}) 조회된 열차 {len(trains)}건, 예약가능 {len(candidates)}건")

        for train in candidates:
            try:
                reservation = korail.reserve(
                    train, passengers=passengers, option=seat_option,
                    try_waiting=args.try_waiting,
                )
                print("\n✅ 예약 성공!")
                print(reservation)
                return reservation
            except SoldOutError:
                continue
            except Exception as exc:
                print(f"  - 열차 {train.train_no} 예약 시도 실패: {exc}")
                continue

        # 약간의 무작위 지연을 더해 동시 요청 패턴을 피한다.
        time.sleep(args.interval + random.uniform(0, 1))

    print("\n❌ 최대 재시도 횟수에 도달했습니다. 예약에 실패했습니다.")
    return None


def main():
    args = parse_args()

    if not args.id:
        args.id = input("코레일 ID(회원번호/이메일/휴대폰번호): ")
    if not args.password:
        args.password = getpass.getpass("코레일 비밀번호: ")

    passengers = build_passengers(args.adult, args.child, args.senior)
    train_type = TRAIN_TYPES[args.train_type]
    seat_option = SEAT_OPTIONS[args.seat]

    try:
        korail = login(args.id, args.password)
    except Exception as exc:
        print(f"로그인 실패: {exc}", file=sys.stderr)
        sys.exit(1)

    if korail is None:
        print(
            "로그인 실패: 아이디와 비밀번호를 확인해 주세요. "
            "정보가 맞다면 코레일의 매크로 차단일 수 있습니다.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"로그인 성공. {args.dep} → {args.arr} ({args.date} {args.time} 이후) 열차 탐색을 시작합니다.")

    reservation = reserve_loop(korail, args, passengers, train_type, seat_option)
    sys.exit(0 if reservation else 2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
        sys.exit(130)
