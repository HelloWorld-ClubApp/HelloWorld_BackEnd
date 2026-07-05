# Troubleshooting & Known Issues

### 1. SMTP SSL Error 해결

* **현상**: 로컬 환경에서 `aiosmtplib` 사용 시 SSL 핸드쉐이크 에러 발생.
* **해결**: 실제 배포 서버 환경에서는 정삭 작동하므로, 로컬 개발 시에는 SMTP 코드를 주석 처리하고 콘솔 로그를 출력하는 '디버깅 모드'를 도입하여 개발 속도를 확보함.

### 2. 이메일 스팸함 분류 이슈

* **현상**: 전송한 이메일이 수신자의 스팸함으로 들어감.
* **해결**: `email.utils`를 사용하여 `Date`와 `Message-ID`를 명시적으로 삽입하여 메일 서버 간의 신뢰도(Reputation)를 높임.

### 3. 외부 I/O 작업의 Silent Failure (조용한 실패) 방지

* **현상**: 코드상 에러가 발생하지 않고 HTTP 상태 코드 200(OK)이 반환되었으나, 실제로는 메일이 오지 않는 현상 발생.
* **원인**: 이메일 발송 함수(`send_email`)가 내부 예외 처리 후 `False`를 반환했으나, 비즈니스 로직(Service)에서 이 결과를 무시하고 무조건 성공 메시지를 반환하도록 설계됨.
* **해결**: 이메일 발송과 같은 외부 시스템 연동 로직은 반드시 성공 여부를 반환값으로 체크하고, 실패 시 `raise HTTPException`을 통해 프론트엔드에 명확한 장애 상황을 알리도록 구조를 개선함.

### 4. 구글 SMTP 앱 비밀번호 포맷팅 이슈

* **현상**: 587 포트(STARTTLS) 연결 설정이 완벽함에도 `535, 5.7.8 Authentication failed` 에러 지속 발생.
* **원인**: 구글 계정에서 발급받은 16자리 앱 비밀번호를 `.env` 파일에 복사하는 과정에서 `xxxx xxxx xxxx xxxx` 형태의 공백이 그대로 포함되어, 파이썬 내부에서 비밀번호 불일치로 판정됨.
* **해결**: `EMAIL_PASSWORD=xxxxxxxxxxxxxxxx` 형태로 공백을 완전히 제거하여 인증에 성공함. (환경변수 세팅 시 공백 주의)


### 5. Bcrypt 비밀번호 72바이트 길이 제한 (72-byte Limit) 방어

* **현상**: 회원가입 또는 로그인 시 사용자가 비정상적으로 긴 비밀번호(72바이트 초과)를 입력할 경우, 서버에서 `ValueError`가 발생하며 `500 Internal Server Error`로 뻗어버리는 현상.
* **원인**: 프로젝트에서 비밀번호 단방향 암호화를 위해 사용하는 `passlib`의 `bcrypt` 알고리즘은 설계 스펙상 최대 72바이트까지만 해싱이 가능함. 이를 초과하는 문자열이 들어오면 자체적으로 예외(Exception)를 발생시키거나 문자열을 조용히 잘라버림(Truncation).
* **해결**: 프론트엔드의 입력 제한에만 의존하지 않고, 백엔드 진입점인 Pydantic 스키마(`schemas/user.py`)에서 비밀번호 필드에 `max_length=19` 속성을 부여함. 이를 통해 72바이트를 넘는 요청이 해싱 함수에 도달하기 전에 `422 Unprocessable Entity` 에러로 안전하게 튕겨내도록 구조적으로 차단함.

### 6. 웹 크롤링 시 데이터 중복 적재 (Data Duplication) 이슈 해결
* **현상**: 스케줄러나 수동 스크립트(crawl_and_save.py)를 통해 크롤링을 여러 번 실행할 때마다, 동일한 공모전 데이터가 DB(contests 테이블)에 중복으로 계속 쌓이는 현상.

* **원인**: 파싱한 공모전 데이터를 DB에 삽입할 때, 기존 데이터의 존재 여부를 검증하지 않고 무조건 db.add()를 수행하도록 로직이 작성됨.

* **해결**: 공모전의 고유한 식별값(detail_url 또는 title)을 기준으로 기존 DB 데이터를 먼저 조회하는 방어 로직을 추가함. 데이터가 없으면 새로 삽입(Insert)하고, 이미 존재하면 최신 정보로 갱신(Update)하거나 스킵하는 Upsert(Update + Insert) 처리를 구현하여 DB 무결성을 확보함.


### 7. Pydantic 스키마 클래스 중첩(Indentation)으로 인한 런타임 ImportError 해결

* **현상**: 서버 구동 시 `ImportError: cannot import name 'UserProfileHeaderResponse' from 'app.schemas.user'` 에러가 발생하며 서버 애플리케이션이 뻗어버리는 현상.
* **원인**: `schemas/user.py` 파일에 응답 스키마를 추가하는 과정에서, 새로 작성한 `UserProfileHeaderResponse` 클래스의 들여쓰기(Indentation)가 잘못되어 직전 클래스(`PasswordResetConfirm`)의 내부(중첩) 클래스로 선언됨. 이로 인해 외부 라우터 모듈에서 해당 스키마를 전역 스코프에서 찾지 못해 발생한 문제.
* **해결**: 파이썬의 들여쓰기를 수정하여 해당 스키마를 외부로 빼내어 파일의 최상위 레벨(Global scope)로 분리함. 이를 통해 라우터에서 정상적으로 import 할 수 있도록 조치함.

### 8. 다대다(N:M) 매핑 테이블 복합키(Composite Key) 참조 오류 해결

* **현상**: 메인 페이지 앨범 피드 조회 API (`GET /api/v1/posts/feed`) 호출 시 `500 Internal Server Error` 발생. 에러 로그 확인 결과 `AttributeError: type object 'PostFile' has no attribute 'id'` 출력됨.
* **원인**: 게시글(`posts`)과 파일(`files`)을 연결하는 중간 매핑 테이블인 `post_files`가 정규화 설계에 따라 단일 `id` 없이 `post_id`와 `file_id`를 복합 기본키(Composite PK)로 사용하고 있었음. 그러나 쿼리의 `order_by()` 절에서 가장 먼저 등록된 사진을 찾기 위해 존재하지 않는 단일 키(`PostFile.id`)를 기준으로 정렬을 시도하여 속성 참조 에러가 발생함.
* **해결**: 쿼리의 정렬 기준을 중간 매핑 테이블(`PostFile`)이 아닌 원본 파일 테이블의 고유 식별자(`File.id.asc()`)로 변경함. 이를 통해 복합키 구조를 유지하면서도 원하는 정렬 및 다중 조인 결과를 에러 없이 도출하는 데 성공함.

### 9. Pydantic 타입 어댑터(TypeAdapter) 검증 오류 해결

* **현상** : 공지사항 리스트 조회 API(GET /api/v1/posts/notices) 호출 시 500 Internal Server Error 발생. 서버 로그에서 PydanticUserError: ... is not fully defined 메시지 출력.

* **원인** : schemas/post.py 파일 내 NoticeListResponse 스키마를 작성하는 과정에서 리스트 타입을 감싸는 List 모듈을 임포트하지 않았음. 이로 인해 Pydantic이 리스트 내부의 NoticeResponse 객체 타입을 파악하지 못하고 검증 과정에서 런타임 에러를 발생시킴.

* **해결**: from typing import List 구문을 파일 상단에 추가하여 명시적으로 타입을 정의함. 이후 스키마 클래스 내부에서 notices: List[NoticeResponse] = Field(...)와 같이 정상적으로 타입을 지정하여 타입 어댑터가 올바르게 작동하도록 구조를 바로잡음.

### 10. API 라우터 스키마 미등록으로 인한 NameError 발생
* **현상**: 서버 구동 시 NameError: name 'NoticeListResponse' is not defined 에러 발생.

* **원인**: app/api/v1/posts.py 라우터 파일에서 새로 작성한 NoticeListResponse 스키마를 사용했으나, 해당 파일의 import 구문에 클래스 이름을 누락하여 라우터가 스키마의 존재를 인식하지 못함.

* **해결**: app/api/v1/posts.py 상단의 from app.schemas.post import ... 부분에 NoticeListResponse를 추가하여 모듈 간 의존성을 정상적으로 연결함.

### 11. 인증 토큰 누락으로 인한 API 접근 불가 에러 해결
* **현상**: 인가(Authorization)가 필요한 API(예: 게시글 작성)를 Postman으로 테스트할 때, 요청이 거부되거나 권한 관련 에러(401 Unauthorized 등)가 발생하여 로직이 수행되지 않는 현상.

* **원인**: API 테스트 과정에서 요청 헤더(Header)에 필수적인 인증 토큰(Access Token)을 포함하지 않고 요청을 보내, 백엔드 서버가 인가받지 않은 사용자의 접근으로 간주하고 차단함.

* **해결**: 회원가입(Signup) API를 통해 사용자 계정을 생성한 후, 로그인(Login) API를 호출하여 정상적으로 Access Token을 발급받음. 이후 Postman의 Authorization 탭(Bearer Token)에 해당 토큰을 삽입하고 재요청하여 API가 정상적으로 작동함을 확인함.


### 12. DB 스키마와 백엔드 ORM 모델 불일치로 인한 500 에러 해결
* **현상**: 게시글 작성 API를 호출하여 데이터를 전송했을 때, 파이썬 코드상에는 문법적 오류가 없음에도 500 Internal Server Error가 발생하며 데이터가 저장되지 않음. (서버 로그: column "schedule_date" of relation "posts" does not exist)

* **원인**: 백엔드 파이썬 모델(models/post.py)과 스키마 구조에는 일정(schedule_date) 데이터를 처리하도록 정의되어 있었으나, 실제 데이터베이스(PostgreSQL)의 posts 테이블에는 해당 컬럼이 아직 존재하지 않아 데이터를 삽입(Insert)하려는 순간 쿼리 충돌이 발생함.

* **해결**: pgAdmin의 쿼리 도구(Query Tool)를 활용하여 ALTER TABLE posts ADD COLUMN schedule_date timestamp with time zone; DDL 쿼리를 직접 실행함. 실제 DB 테이블에 누락된 컬럼을 수동으로 추가하여 백엔드 코드와 DB 스키마 간의 구조를 완벽하게 동기화함으로써 에러를 해결함.