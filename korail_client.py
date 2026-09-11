"""korail2 클라이언트 생성 공용 헬퍼.

korail2는 어떤 요청에도 timeout을 지정하지 않아, 코레일 서버가 연결만 받아두고
응답하지 않으면 무한 대기한다. 또 `Korail._session`이 클래스 속성이라 모든
인스턴스가 세션 하나를 공유하므로, 세션을 한 번만 감싸 기본 타임아웃을 넣는다.
"""

from korail2 import Korail

REQUEST_TIMEOUT = 10


def apply_timeout(session, timeout=REQUEST_TIMEOUT):
    if getattr(session, "_timeout_patched", False):
        return
    original = session.request

    def request(method, url, **kwargs):
        kwargs.setdefault("timeout", timeout)
        return original(method, url, **kwargs)

    session.request = request
    session._timeout_patched = True


def login(user_id, user_pw):
    """타임아웃을 건 뒤 로그인한다. 실패 시 None을 반환한다.

    korail2의 `login()`은 실패해도 예외 대신 False를 돌려주므로, 잘못된
    자격증명과 매크로 차단을 호출부에서 구분할 수 없다.
    """
    korail = Korail(user_id, user_pw, auto_login=False)
    apply_timeout(korail._session)
    return korail if korail.login() else None
