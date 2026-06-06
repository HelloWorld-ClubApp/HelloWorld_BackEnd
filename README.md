# 🚀 대학 동아리 전용 SNS 앱 백엔드 (Backend)

이 레포지토리는 한국폴리텍대학 부산캠퍼스 소프트웨어융합과 동아리 전용 SNS 애플리케이션의 백엔드 API 서버입니다. 
FastAPI를 기반으로 구축되었으며, 확장성과 유지보수성을 고려한 계층형 아키텍처(Layered Architecture)를 따릅니다.

---

## 📦 기술 스택 및 라이브러리 (Tech Stack)

### 1. Core Framework (핵심 프레임워크 및 서버)
* **`fastapi`**: 우리가 사용할 핵심 앱 프레임워크
* **`uvicorn`**: FastAPI 서버를 실행시켜 줄 초고속 비동기 서버 엔진

### 2. Database & ORM (데이터베이스 및 데이터 조작)
* **`sqlalchemy`**: 파이썬 코드(클래스)와 DB 테이블을 매핑하여 객체 지향적인 데이터 조작을 돕는 강력한 ORM 라이브러리
* **`psycopg2-binary`**: SQLAlchemy가 PostgreSQL 데이터베이스와 원활하게 통신할 수 있도록 연결해 주는 핵심 데이터베이스 어댑터
* **`alembic`**: 데이터베이스 모델(스키마)의 변경 사항을 안전하게 추적하고 관리(마이그레이션)해 주는 필수 도구

### 3. Security & Authentication (보안 및 회원 인증)
* **`passlib[bcrypt]`**: 사용자 비밀번호를 데이터베이스에 평문으로 저장하지 않고, 안전하게 단방향 해시(Hash) 암호화하여 저장 및 검증
* **`pyjwt`**: 로그인 성공 시 무상태(Stateless) 기반의 세션 유지를 위한 JWT(JSON Web Token)를 발급하고 위변조 여부를 검증

### 4. Validation & Configuration (데이터 검증 및 환경 설정)
* **`pydantic[email]`**: 프론트엔드로부터 들어오는 요청 데이터의 타입과 유효성(예: 이메일 정규식, 글자 수 제한 등)을 서버 진입 전에 엄격하게 검증
* **`python-dotenv`**: 외부 유출이 치명적인 보안 정보(DB 비밀번호, JWT 시크릿 키 등)를 `.env` 파일로 분리하여 프로젝트 전역의 환경 변수로 관리

### 5. Storage & Media (클라우드 스토리지 및 파일 처리)
* **`python-multipart`**: FastAPI에서 프론트엔드가 보낸 파일(이미지, 첨부파일)과 폼(Form) 데이터를 정상적으로 파싱하고 읽기 위해 반드시 필요한 필수 라이브러리
* **`supabase`**: 파싱된 프로필 이미지 및 게시글 첨부파일 등을 안전하게 업로드하고 중앙 관리하기 위한 Supabase Storage 연동 클라이언트 (PostgreSQL DB 배포 시 필요)

### 6. Real-time & Caching (실시간 통신 및 캐싱)
* **`redis`**: 다중 서버 환경에서도 채팅(WebSocket) 메시지가 끊기지 않도록 상태를 동기화하고, 빠른 데이터 조회를 돕는 인메모리 데이터 스토어 (1:N 채팅 시 반드시 필요)

---

## 🛠️ 시작하기 (Getting Started)

**1. 가상환경 생성**
```bash
python -m venv venv

```

**2. 가상환경 실행**

* Windows:

```bash
venv\Scripts\activate

```

* macOS/Linux:

```bash
source venv/bin/activate

```

**3. 패키지 설치**

```bash
pip install -r requirements.txt

```

**4. 서버 실행**

```bash
uvicorn app.main:app --reload

```

> 서버가 실행되면 `http://127.0.0.1:8000/docs`로 접속하여 Swagger UI API 문서를 확인할 수 있습니다.

---

## 🏗️ 아키텍처 및 핵심 파일의 역할

### 📌 루트 파일

#### **`main.py`**: FastAPI 애플리케이션이 시작되는 진입점. 모든 라우터(API 주소)를 하나로 모으고, 앱이 실행될 때 DB 연결 등 전체적인 실행을 담당.
* **`.env`**: 데이터베이스 비밀번호, JWT 암호화 키 등 외부에 유출되면 안 되는 보안 정보를 담아두는 파일. (**GitHub 절대 업로드 금지**)
* **`requirements.txt`**: 프로젝트에 설치된 외부 라이브러리 목록. `pip install -r requirements.txt` 명령어로 동일한 개발 환경을 한 번에 세팅 가능.

### 📌 계층별 디렉토리 역할 (`app/`)

#### **`core/` (전역 설정 및 핵심 모듈)**
* `config.py`: `.env` 파일의 값을 읽어와 프로젝트 전역에서 쓸 수 있게 세팅.
* `database.py`: PostgreSQL 데이터베이스와 파이썬을 연결해 주는 세션(Session) 생성 및 관리.
* `security.py`: 비밀번호 해시 암호화, JWT 발급/검증 등 보안 기능 전담.


#### **`api/` (API 엔드포인트 / 컨트롤러)**
* `v1/*.py`: 프론트엔드 요청(URL)을 제일 먼저 받으며, 복잡한 로직은 Service 계층에 넘기고 결과만 응답.
* `dependencies.py`: API 실행 전 로그인 여부, 권한 등을 확인하는 미들웨어(검문소) 역할.


#### **`schemas/` (데이터 검증 / Pydantic)**
* 프론트엔드가 보낸 데이터의 형식과 유효성을 검사 (예: 비밀번호 8자 이상 규칙 검사). 규칙 위반 시 서버 내부 진입 전 차단(422 Error).


#### **`services/` (핵심 비즈니스 로직 / 두뇌)**
* 프로젝트의 핵심 로직 집중 (예: 이메일 난수 인증 로직, 파일 용량 검증 및 서버 저장 로직 등). 라우터로부터 일을 넘겨받아 처리.


#### **`models/` (DB 테이블 정의 / SQLAlchemy)**
* DB 테이블 구조(Users, Posts 등)를 파이썬 클래스 코드로 정의한 설계도.


#### **`crud/` (DB 데이터 조작)**
* 오직 데이터베이스에 쿼리를 날려 데이터를 넣고 빼는 역할만 수행 (Create, Read, Update, Delete).


#### **`utils/` (공통 유틸리티)**
* 프로젝트 전역에서 공통으로 쓰이는 도우미 함수 모음 (예: SMTP 메일 발송, WebSocket 채팅 접속자 관리).



---

## 📂 디렉토리 구조 (Directory Structure)

```text
backend/
├── app/
│   ├── main.py                 # FastAPI 애플리케이션 진입점 (설정 로드, 라우터 등록)
│   ├── core/                   # 전역 설정 및 핵심 모듈
│   │   ├── config.py           # 환경변수 (DB URL, JWT Secret 등)
│   │   ├── security.py         # 비밀번호 해싱(bcrypt), JWT 토큰 발급 및 검증
│   │   └── database.py         # SQLAlchemy 세션 생성 및 DB 연결 설정
│   │
│   ├── api/                    # API 엔드포인트 (컨트롤러 역할)
│   │   ├── dependencies.py     # 공통 의존성 주입 (get_db, get_current_user 등)
│   │   └── v1/                 # API 버전 관리
│   │       ├── auth.py         # 회원가입, 로그인, 이메일 인증 (User_001~005)
│   │       ├── users.py        # 마이페이지, 프로필 수정, 회원탈퇴 (MY_001~007)
│   │       ├── posts.py        # 게시판(공지, 자유, 질문), 좋아요 (Post_001~003)
│   │       ├── comments.py     # 댓글 작성 및 삭제 (Comment_001)
│   │       ├── schedules.py    # 캘린더, 일정 관리 (SCH_001~002)
│   │       ├── chats.py        # 채팅방 조회, WebSocket 연결 (Chat_001~003)
│   │       └── home.py         # 홈 화면 데이터 조회 (Home_001~004)
│   │
│   ├── schemas/                # 데이터 유효성 검사 및 입출력 포맷 (Pydantic)
│   │   ├── user.py             # 회원가입 입력 형식(8~20자 제한, 이메일 정규식 등)
│   │   ├── post.py             # 게시글 작성 폼, 페이징 응답 폼
│   │   ├── chat.py             # 메시지 전송 포맷
│   │   └── token.py            # JWT 토큰 응답 포맷
│   │
│   ├── models/                 # DB 테이블 정의 (SQLAlchemy)
│   │   ├── user.py             # Users, Role 등
│   │   ├── post.py             # Posts, Comments, Likes 등
│   │   ├── chat.py             # ChatRooms, Messages 등
│   │   └── schedule.py         # Schedules 등
│   │
│   ├── crud/                   # DB 데이터 조작 (Create, Read, Update, Delete)
│   │   ├── crud_user.py        # 학번/이메일 중복 검사 쿼리
│   │   ├── crud_post.py        # 게시글 조회, 페이징 로직
│   │   └── crud_chat.py        # 채팅 내역 저장 쿼리
│   │
│   ├── services/               # 핵심 비즈니스 로직 (컨트롤러와 DB 사이의 두뇌)
│   │   ├── auth_service.py     # 이메일 난수 생성 로직, 인증 시간(10분) 만료 검사
│   │   ├── chat_service.py     # 채팅방 개설 인원 제한(50명) 검사 로직
│   │   ├── file_service.py     # 파일 용량(10MB) 검증 및 S3 업로드 로직
│   │   └── post_service.py     # 작성 권한 확인, 조회수 처리 로직
│   │
│   └── utils/                  # 프로젝트 전역에서 쓰이는 유틸리티 함수
│       ├── email_sender.py     # SMTP 메일 발송 함수
│       └── ws_manager.py       # WebSocket 연결 관리 (채팅 접속자 관리)
│
├── requirements.txt            # 설치 패키지 목록
├── .env                        # 환경 변수 (GitHub 등에 절대 올리면 안 됨)
└── README.md                   # 프로젝트 설명서

```