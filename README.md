# 👋 HelloWorld Club Backend

<div align="center">

### Club Community & Management Platform

**동아리 회원 관리 · 게시판 · 일정 · 피드 · 실시간 채팅을
하나의 서비스로 연결한 FastAPI 기반 동아리 통합 플랫폼 Backend**

<br>

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge\&logo=fastapi\&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge\&logo=postgresql\&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge\&logo=sqlalchemy\&logoColor=white)
![WebSocket](https://img.shields.io/badge/WebSocket-010101?style=for-the-badge\&logo=socketdotio\&logoColor=white)

</div>

---

# 📌 Project Overview

**HelloWorld Club App**은 동아리 활동에 필요한 기능을 하나의 애플리케이션에서 사용할 수 있도록 개발한 팀 프로젝트입니다.

이 저장소는 서비스의 Backend Server이며 다음 기능을 담당합니다.

* 회원가입 / 로그인
* 동아리 가입 승인
* 역할 기반 권한 관리
* 공지 / 일반 / 질문 / 동아리활동 게시판
* 댓글 / 좋아요
* 동아리 Feed
* 공모전 정보 제공
* 개인 일정 / 동아리 일정
* 실시간 채팅
* 채팅 파일 공유
* 파일 업로드 / 다운로드
* 사용자 Profile
* 동아리 회원 관리
* Idea Note

서비스의 각 기능은 독립적인 CRUD로 끝나지 않고
동일한 `User`, `Post`, `File`, `Chat`, `Schedule` 데이터를 중심으로 연결됩니다.

```text
User
 │
 ├── Authentication
 │
 ├── Membership / Role
 │
 ├── Post / Comment / Like
 │
 ├── Feed
 │
 ├── Schedule
 │
 ├── Chat / Message
 │
 ├── File
 │
 └── Profile
 │
 ▼
Club Activity Platform
```

---

# 🎯 Project Goal

기존 동아리 운영에서는

* 공지 전달
* 일정 관리
* 회원 관리
* 파일 공유
* 대화
* 공모전 정보 탐색

등의 활동이 서로 다른 서비스에서 이루어지는 경우가 많습니다.

HelloWorld Club App은 이를 하나의 시스템으로 통합하여

```text
회원
 ↓
공지 확인
 ↓
일정 관리
 ↓
동아리 활동
 ↓
실시간 대화
 ↓
자료 공유
```

와 같은 동아리 활동 흐름을 하나의 애플리케이션에서 처리할 수 있도록 설계했습니다.

---

# 🏗️ System Architecture

```text
┌───────────────────────────────┐
│            Client             │
└───────────────┬───────────────┘
                │
        REST API / WebSocket
                │
                ▼
┌───────────────────────────────┐
│        FastAPI Backend        │
│                               │
│ Auth        Users             │
│ Posts       Comments          │
│ Likes       Schedules         │
│ Chats       Files             │
│ Feed        Home              │
│ Ideas                         │
└───────────────┬───────────────┘
                │
                │ SQLAlchemy
                ▼
┌───────────────────────────────┐
│          PostgreSQL           │
│                               │
│ User / Role / Permission      │
│ Post / Comment / Like         │
│ Chat / Message                │
│ Schedule / Idea               │
│ Feed / File                   │
│ Contest                       │
└───────────────────────────────┘
        │
        ├──────────────────┐
        ▼                  ▼
   Local Storage       External Service

   /uploads            Gmail SMTP
                       Linkareer GraphQL API
```

---

# 🧱 Backend Architecture

프로젝트 내부는 역할에 따라 계층을 분리했습니다.

```text
Client
  ↓
API Router
  ↓
Service
  ↓
CRUD
  ↓
SQLAlchemy
  ↓
PostgreSQL
```

### Layer Responsibility

| Layer       | Responsibility                          |
| ----------- | --------------------------------------- |
| `api/`      | HTTP Request / Response 및 인증 Dependency |
| `services/` | Business Logic                          |
| `crud/`     | Database Query                          |
| `models/`   | SQLAlchemy ORM                          |
| `schemas/`  | Pydantic Request / Response Validation  |
| `core/`     | Database / Config / Security / Enum     |
| `utils/`    | WebSocket / Email Utility               |
| `scripts/`  | 공모전 데이터 수집 등 독립 실행 작업                   |

---

# 🔐 Authentication

인증은 **JWT Access Token** 기반으로 구성했습니다.

```text
Student ID
     +
Password
     ↓
Authentication
     ↓
bcrypt
     ↓
JWT Access Token
     ↓
Client
```

로그인 성공 시 JWT의 `sub` Claim에 사용자의 학번을 저장합니다.

```text
JWT
 ↓
sub = student_id
 ↓
get_current_user()
 ↓
User
```

보호된 API에서는 공통 Dependency를 통해 현재 사용자를 확인합니다.

```python
Depends(get_current_user)
```

---

# 🔒 Password Security

사용자 비밀번호는 평문으로 저장하지 않습니다.

```text
Plain Password
      ↓
bcrypt + salt
      ↓
Password Hash
      ↓
Database
```

로그인 시에는 입력한 Password와 DB의 Hash를 `bcrypt.checkpw()`로 검증합니다.

---

# 📧 Password Recovery

비밀번호 재설정에는 Email Verification을 사용합니다.

```text
Email
 ↓
6-Digit Verification Code
 ↓
Gmail SMTP
 ↓
10 Minute Expiration
 ↓
Verification
 ↓
New Password
```

### API Flow

```text
POST /password-reset/request
          ↓
POST /password-reset/verify
          ↓
POST /password-reset/confirm
```

인증이 완료된 후 새로운 비밀번호를 bcrypt로 Hashing하여 저장하며,
사용이 끝난 인증 정보는 Database에서 제거합니다.

---

# 🏛️ Club Membership

단순 서비스 회원가입과
**실제 동아리 가입 승인 상태를 분리하여 관리**합니다.

```text
PENDING
APPROVED
REJECTED
```

### Membership Flow

```text
Sign Up
   ↓
PENDING
   ↓
Executive Review
   ↓
┌───────────────┐
│               │
▼               ▼
APPROVED      REJECTED
│
▼
Service Access
```

가입 승인 대기 또는 거절 상태인 사용자는 로그인 단계에서 상태를 확인합니다.

---

# 👑 RBAC

동아리 운영 권한을 관리하기 위해
Role Based Access Control 구조를 사용합니다.

### Roles

```text
일반회원
회장
부회장
총무
```

Database 구조:

```text
Role
 │
 │ N:M
 ▼
RolePermission
 │
 ▼
Permission
```

이를 통해 Role과 개별 Permission을 분리하고
향후 권한 정책을 확장할 수 있도록 설계했습니다.

---

# 👥 Join Request Management

회장 · 부회장 · 총무는 동아리 가입 신청을 관리할 수 있습니다.

### Features

* 승인 대기 인원 조회
* 전체 회원 수 조회
* 가입 신청 목록 조회
* 가입 승인
* 가입 거절

```text
Pending User
      ↓
Role Check
      ↓
President / Vice President / Treasurer
      ↓
Approve / Reject
```

---

# 📰 Board System

게시판은 하나의 `Post` Domain을 중심으로 구성하고
Category를 통해 게시판 종류를 구분합니다.

### Categories

```text
공지
일반
질문
동아리활동
```

```text
Post
 ├── Notice
 ├── Free
 ├── Q&A
 └── Activity
```

게시판 종류에 따라 작성 권한 및 Business Rule을 다르게 적용합니다.

---

# 📢 Notice Board

공지사항은 동아리 운영 권한을 가진 사용자만 작성할 수 있습니다.

### Features

* 공지 작성
* 공지 목록 조회
* 공지 수정
* 공지 삭제
* 첨부파일
* Thumbnail
* 게시 기간

공지에는 다음 일정 정보도 저장할 수 있습니다.

```text
start_date
end_date
```

이 데이터는 Calendar의 동아리 일정과 연결됩니다.

---

# 📝 General / Q&A Board

일반 게시판과 질문 게시판에서는 다음 기능을 제공합니다.

* 게시글 작성
* 게시글 목록
* Pagination
* 게시글 상세
* 수정
* 삭제
* 댓글
* 좋아요
* 파일 첨부

수정 및 삭제 시

```text
Current User
     ↓
Author?
or
Administrator?
     ↓
Allow / Reject
```

방식으로 권한을 검증합니다.

---

# 🎉 Club Activity Board

동아리 활동 기록은 별도의 Category로 관리합니다.

```text
PostCategory.ACTIVITY
```

일반적인 게시글 작성일과 실제 활동일을 구분하기 위해

```text
activity_date
```

를 별도로 저장합니다.

---

# 💬 Comments

게시글별 Comment 기능을 제공합니다.

### Features

* 댓글 작성
* 댓글 수정
* 댓글 삭제
* 댓글 목록

공지사항에서는 댓글 작성을 제한하고,

댓글 수정 및 삭제 시에는 작성자 여부를 검증합니다.

---

# ❤️ Likes

게시글의 Like는 Toggle 방식으로 동작합니다.

```text
Like 없음
   ↓
Create
   ↓
liked = true

Like 존재
   ↓
Delete
   ↓
liked = false
```

Database에는

```text
UNIQUE(post_id, user_id)
```

제약을 적용하여 동일 사용자의 중복 Like 생성을 방지합니다.

---

# 👁️ Post Read Tracking

게시글 조회 여부도 별도의 데이터로 관리합니다.

```text
PostReadLog
├── post_id
├── user_id
└── read_at
```

```text
UNIQUE(post_id, user_id)
```

제약을 통해 사용자와 게시글 간 조회 관계가 중복 생성되지 않도록 합니다.

---

# 📎 Post File Management

게시물과 File은 중간 Mapping Table을 사용합니다.

```text
Post
 │
 │ N:M
 ▼
PostFile
 │
 ▼
File
```

이를 통해 하나의 게시글에 여러 File을 연결할 수 있습니다.

대표 이미지는

```text
thumbnail_file_id
```

로 별도로 관리합니다.

---

# 📸 Feed

동아리 활동 사진을 공유하기 위한 Feed 기능을 제공합니다.

### Features

* Feed 생성
* Feed 목록
* Feed 상세
* Feed 수정
* Feed 삭제
* Chat Room 공유

Feed는 다음 관계를 중심으로 구성됩니다.

```text
User
 ↓
Feed
 ↓
File
```

---

# 🔗 Feed → Chat

Feed는 Chat Room으로 바로 공유할 수 있습니다.

```text
Feed
 ↓
Share
 ↓
Chat Room
 ↓
Message
 ↓
WebSocket Broadcast
```

### Flow

```text
Feed Validation
      ↓
Chat Participant Validation
      ↓
Create Message
      ↓
Database
      ↓
WebSocket Broadcast
```

Feed와 Chat이라는 서로 다른 Domain을
실제 사용자 Interaction 기준으로 연결했습니다.

---

# 📅 Calendar

Calendar는 서로 다른 두 종류의 일정 데이터를 통합합니다.

```text
Club Schedule
     +
Personal Schedule
     ↓
Unified Calendar
```

### Club Schedule

공지 및 게시물에서 관리하는

```text
Post.start_date
Post.end_date
```

를 사용합니다.

### Personal Schedule

사용자 개인 데이터인

```text
Schedule
```

을 사용합니다.

---

# 🗓️ Schedule

### Features

* 월별 일정 조회
* 일별 일정 조회
* 개인 일정 작성
* 수정
* 삭제
* 일정 Color

```text
Schedule
├── user_id
├── title
├── content
├── start_date
├── end_date
└── color
```

개인 일정 수정 및 삭제 시 현재 로그인한 사용자와
일정의 실제 소유자를 비교합니다.

---

# 💬 Real-time Chat

채팅 기능은

* REST API
* WebSocket

을 함께 사용합니다.

```text
REST API
→ Chat Room
→ Message History
→ File History

WebSocket
→ New Message
→ Read Update
→ Real-time Event
```

---

# 🏠 Chat Room

### Features

* 내 채팅방 목록
* Chat Room 생성
* 1:1 채팅방 중복 생성 방지
* Message History
* Message Pagination
* Chat Room 나가기
* 상단 고정

1:1 Chat에서는 동일한 두 사용자로 구성된 Room이 이미 존재하는 경우
새로운 Room을 만들지 않고 기존 Room을 반환합니다.

---

# ⚡ WebSocket

WebSocket Endpoint:

```text
/api/v1/chats/ws/{room_id}/{user_id}
```

### Event Types

```text
NEW_MESSAGE
READ_UPDATE
DELETE_MESSAGE
INFO
ERROR
```

### New Message Flow

```text
Client
 ↓
WebSocket
 ↓
NEW_MESSAGE
 ↓
Database
 ↓
Connection Manager
 ↓
Room Broadcast
 ↓
Participants
```

실시간 전달과 Message Persistence를 함께 처리합니다.

---

# 👀 Message Read Status

메시지별 읽음 상태를 별도 Table로 관리합니다.

```text
Message
   ↓
MessageReadStatus
   ↓
User
```

### Structure

```text
message_id
user_id
is_read
```

`READ_UPDATE` Event가 전달되면 Database 상태를 갱신한 후
해당 Chat Room 사용자들에게 상태 변화를 Broadcast합니다.

---

# 📌 Pinned Chat

Chat Room Pin 상태는 Room 자체에 저장하지 않습니다.

```text
ChatParticipant
      ↓
is_pinned
```

따라서 동일한 Chat Room이라도
사용자마다 서로 다른 Pin 상태를 유지할 수 있습니다.

---

# ☁️ Chat File Cloud

특정 Chat Room에서 공유된 File을 별도로 조회할 수 있습니다.

```text
ChatRoom
   ↓
Message
   ↓
File
   ↓
Chat File Cloud
```

### Response

```text
file_id
file_url
file_type
file_size
original_name
created_at
is_expired
```

파일 생성 시점에서 30일을 기준으로 만료 여부를 계산합니다.

```text
created_at
   +
30 Days
   ↓
Expiration Date
   ↓
Current Time
   ↓
is_expired
```

현재 구현에서는 자동 File Delete가 아니라
Client에서 사용할 **만료 상태 정보**를 제공합니다.

---

# 📂 File Management

여러 Domain에서 공통으로 사용할 수 있는 File API를 제공합니다.

```text
Post
Chat
Profile
Feed
   │
   ▼
 File
```

---

## Upload

```text
UploadFile
   ↓
Size Validation
   ↓
UUID File Name
   ↓
/uploads
   ↓
File Metadata
   ↓
PostgreSQL
```

최대 업로드 크기:

```text
20MB
```

실제 서버 저장 파일명은 UUID를 이용하여 생성하고
원래 파일명은 Metadata로 별도 관리합니다.

---

## Download

```text
GET /api/v1/files/{file_id}/download
```

Database에서 File 정보를 조회한 후
실제 저장 경로를 검증하고 `FileResponse`로 반환합니다.

Upload Directory 외부로 이동하는 Path Traversal을 방지하기 위한
경로 검증 로직도 포함합니다.

---

# 👤 My Page

### Features

* 내 Profile 조회
* Header Profile
* Profile 수정
* 내가 작성한 게시물
* 좋아요한 게시물
* 사용자 검색
* 동아리 Member 조회
* 회원탈퇴

---

# 🖼️ Profile

사용자는 다음 정보를 수정할 수 있습니다.

```text
Profile Image
Background Image
Status
Bio
Hashtags
```

학적 상태:

```text
재학
졸업
취업
```

프로필 이미지:

```text
jpg
jpeg
png
```

파일 확장자와 최대 크기를 검증한 후 저장합니다.

---

# 👥 Club Members

동아리 회원은 입학 연도를 기준으로 그룹화하여 조회합니다.

```text
Users
 ↓
Admission Year
 ↓
Grouped Members
```

옵션을 통해 졸업생을 포함한 전체 Member도 조회할 수 있습니다.

---

# 🗑️ Account Withdrawal

회원탈퇴 시 사용자 Row를 즉시 제거하는 Hard Delete 대신
Soft Delete를 사용합니다.

```text
Current Password
      ↓
bcrypt Verification
      ↓
is_deleted
```

탈퇴 이후 기존 게시물이나 댓글처럼
다른 Domain과 연결된 데이터 관계를 유지할 수 있도록 구성했습니다.

탈퇴 회원의 Display Name은

```text
알 수 없음
```

으로 처리할 수 있습니다.

---

# 💡 Idea Note

사용자가 개인적으로 아이디어를 기록할 수 있는 기능입니다.

### Features

* Idea 작성
* 목록 조회
* Pagination
* 삭제
* 사용자 소유권 검증

```text
User
 ↓
Idea
├── title
├── content
└── updated_at
```

---

# 🏆 Contest Data Collection

Home 화면에서 제공하는 IT 관련 공모전 정보를 위해
외부 데이터를 수집하는 별도 Script를 운영합니다.

```text
Linkareer GraphQL API
        ↓
Category Filtering
        ↓
Pagination
        ↓
Data Parsing
        ↓
Duplicate Validation
        ↓
Normalization
        ↓
PostgreSQL
```

---

## Target Categories

현재 주요 수집 대상:

```text
기획 / 아이디어
과학 / 공학
학술
창업
기타
```

---

## Pagination

각 Category에 대해 마지막 Page까지 순차적으로 요청합니다.

```text
Category
 ↓
Page 1
 ↓
Page 2
 ↓
...
 ↓
Empty Response
 ↓
Complete
```

외부 서비스에 과도한 요청을 보내지 않도록
각 Page 요청 사이에 Delay를 적용합니다.

---

## Duplicate Prevention

공모전 Detail URL을 고유 기준으로 사용합니다.

```text
detail_url
```

```text
External Contest
      ↓
Find detail_url
      ↓
┌───────────┐
│           │
Exists     New
│           │
Reuse      Create
```

---

## Contest Data Modeling

수집한 외부 데이터를 하나의 JSON으로 저장하지 않고
관계형 데이터로 분리합니다.

```text
Host
  ▲
  │
Contest
  │
  ▼
ContestCategory
  │
  ▼
Category
```

### Main Tables

```text
hosts
categories
contests
contest_categories
```

`Contest`와 `Category`의 N:M 관계를
`ContestCategory` Mapping Table로 해소합니다.

---

## Expired Data Cleanup

Crawler 실행 시 오래된 공모전 데이터도 함께 정리합니다.

```text
Contest.end_date
       ↓
6 Months Threshold
       ↓
Old Contest
       ↓
Delete
```

지속적으로 데이터를 수집하면서 오래된 Data가
무한히 누적되지 않도록 관리합니다.

---

# 🏠 Home

Home API에서는 최신 공모전 정보를 제공합니다.

```text
Contest Database
      ↓
Not Expired
      ↓
IT Keyword Filter
      ↓
Latest Contests
      ↓
Home Banner
```

주요 Keyword:

```text
IT
SW
소프트웨어
해커톤
데이터
웹
앱
ICT
개발
코딩
디지털
블록체인
보안
```

마감되지 않은 공모전 중 IT 관련 공모전을 선별하여
최대 5개의 Home Banner로 반환합니다.

---

# 🗄️ Database Domains

Database는 기능별 Domain을 중심으로 분리했습니다.

```text
AUTH / MEMBER
│
├── users
├── roles
├── permissions
├── role_permissions
└── email_verifications


BOARD
│
├── posts
├── post_files
├── post_read_logs
├── comments
└── likes


CHAT
│
├── chat_rooms
├── chat_participants
├── messages
└── message_read_statuses


SCHEDULE
│
├── schedules
└── ideas


CONTENT
│
├── files
└── feeds


CONTEST
│
├── contests
├── hosts
├── categories
└── contest_categories
```

---

# 🔗 Main Data Relationships

```text
Role
 │
 │ 1:N
 ▼
User
 │
 ├──────────────┬──────────────┬──────────────┐
 │              │              │              │
 ▼              ▼              ▼              ▼
Post         Schedule       Feed       ChatParticipant
 │                                          │
 ├── Comment                                ▼
 │                                      ChatRoom
 ├── Like                                  │
 │                                          ▼
 ├── PostFile                            Message
 │                                          │
 └── PostReadLog                            ▼
                                          File
```

---

# 📂 Project Structure

```text
HelloWorld_BackEnd/
│
├── alembic/
│   └── versions/
│
├── app/
│   │
│   ├── api/
│   │   ├── dependencies.py
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── chats.py
│   │       ├── comments.py
│   │       ├── feed.py
│   │       ├── files.py
│   │       ├── home.py
│   │       ├── ideas.py
│   │       ├── likes.py
│   │       ├── posts.py
│   │       ├── schedules.py
│   │       └── users.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── file_paths.py
│   │   ├── security.py
│   │   └── enum/
│   │
│   ├── crud/
│   │   ├── crud_chat.py
│   │   ├── crud_comment.py
│   │   ├── crud_feed.py
│   │   ├── crud_file.py
│   │   ├── crud_home.py
│   │   ├── crud_idea.py
│   │   ├── crud_like.py
│   │   ├── crud_post.py
│   │   ├── crud_schedule.py
│   │   └── crud_user.py
│   │
│   ├── models/
│   │   ├── chat.py
│   │   ├── contest.py
│   │   ├── feed.py
│   │   ├── file.py
│   │   ├── post.py
│   │   ├── schedule.py
│   │   └── user.py
│   │
│   ├── schemas/
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── chat_service.py
│   │   ├── comment_service.py
│   │   ├── file_service.py
│   │   ├── post_service.py
│   │   └── user_service.py
│   │
│   ├── utils/
│   │   ├── email_sender.py
│   │   └── ws_manager.py
│   │
│   └── main.py
│
├── scripts/
│   └── crawl_and_save.py
│
├── uploads/
├── alembic.ini
├── requirements.txt
└── README.md
```

---

# ⚙️ Tech Stack

## Backend

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge\&logo=fastapi\&logoColor=white)

`REST API` `Pydantic` `Uvicorn`

## Database

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge\&logo=postgresql\&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge\&logo=sqlalchemy\&logoColor=white)

`SQLAlchemy 2.0` `psycopg2` `Alembic`

## Authentication

`JWT` `PyJWT` `bcrypt` `OAuth2PasswordBearer`

## Authorization

`RBAC` `Role / Permission`

## Real-time

`FastAPI WebSocket` `Connection Manager` `Room Broadcast`

## File

`UploadFile` `StaticFiles` `FileResponse` `Multipart`

## Email

`aiosmtplib` `Gmail SMTP`

## External Data

`Requests` `Linkareer GraphQL API`

---

# 📡 API Domains

Base URL:

```text
/api/v1
```

| Domain         | Prefix       |
| -------------- | ------------ |
| Authentication | `/auth`      |
| Home           | `/home`      |
| User           | `/users`     |
| Post           | `/posts`     |
| Comment        | `/comments`  |
| Schedule       | `/schedules` |
| Chat           | `/chats`     |
| File           | `/files`     |
| Feed           | `/feed`      |
| Idea           | `/ideas`     |

---

# 🔐 Environment Variables

프로젝트 Root에 `.env`를 생성합니다.

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE

SECRET_KEY=YOUR_JWT_SECRET

EMAIL_USER=YOUR_GMAIL_ADDRESS
EMAIL_PASSWORD=YOUR_GMAIL_APP_PASSWORD
EMAIL_FROM=YOUR_GMAIL_ADDRESS
```

> Database Password, JWT Secret 및 Email Password와 같은 민감한 정보는 Repository에 Commit하지 않습니다.

---

# 🚀 Getting Started

## 1. Clone Repository

```bash
git clone https://github.com/HelloWorld-ClubApp/HelloWorld_BackEnd.git
cd HelloWorld_BackEnd
```

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Configure Environment

`.env`

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/helloworld

SECRET_KEY=YOUR_SECRET_KEY

EMAIL_USER=example@gmail.com
EMAIL_PASSWORD=YOUR_GMAIL_APP_PASSWORD
EMAIL_FROM=example@gmail.com
```

## 5. Create PostgreSQL Database

```sql
CREATE DATABASE helloworld;
```

## 6. Run Migration

```bash
alembic upgrade head
```

Migration 확인:

```bash
alembic current
```

## 7. Start Server

```bash
uvicorn app.main:app --reload
```

Server:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

# 🌱 Initial Seed

Application 시작 시 필수 Role을 확인합니다.

```text
일반회원
회장
부회장
총무
```

존재하지 않는 Role은 자동으로 생성합니다.

```text
Server Start
    ↓
Role Validation
    ↓
Missing Role
    ↓
Insert Seed
```

---

# 🏆 Contest Data Update

공모전 데이터를 갱신하려면 Project Root에서 다음 Script를 실행합니다.

```bash
python scripts/crawl_and_save.py
```

Crawler는

```text
Old Data Cleanup
      ↓
Linkareer API
      ↓
IT-related Categories
      ↓
Pagination
      ↓
Duplicate Validation
      ↓
Database Save
```

순서로 동작합니다.

---

# 💡 Design Highlights

## 1. Service Account와 Club Membership 분리

```text
Registered User
      ≠
Approved Club Member
```

회원가입 이후 별도의 가입 승인 절차를 Backend Domain으로 구현했습니다.

## 2. RBAC

관리 기능을 단순 `is_admin` Boolean으로 처리하지 않고
Role과 Permission 관계로 확장할 수 있도록 구성했습니다.

## 3. Unified Calendar

```text
Post Schedule
      +
Personal Schedule
      ↓
Calendar
```

서로 다른 Domain 데이터를 하나의 Calendar Response로 통합합니다.

## 4. REST + WebSocket

```text
REST
→ Persistence / Query

WebSocket
→ Real-time Event
```

각 통신 방식의 역할을 분리했습니다.

## 5. Integrated Post Domain

공지 · 일반 · 질문 · 동아리 활동을 별도 Table로 분산시키지 않고

```text
Post + Category
```

구조로 관리합니다.

## 6. Shared File Domain

```text
Post
Chat
Feed
Profile
   ↓
 File
```

여러 Domain에서 공통 File 데이터를 사용할 수 있도록 설계했습니다.

## 7. Soft Delete

회원탈퇴 이후에도 기존 Community Data의 관계를 유지할 수 있도록
사용자 계정에 Soft Delete를 적용했습니다.

## 8. External Data Normalization

외부 공모전 데이터를 그대로 저장하지 않고

```text
Contest
Host
Category
ContestCategory
```

로 정규화합니다.

---

# 👥 Team & Contributions

HelloWorld Club App은 팀 프로젝트로 진행되었으며,
기능별로 담당 영역을 분담한 뒤 Backend 전체 구조와 API 규격에 맞춰 통합하는 방식으로 개발했습니다.

프로젝트 진행 과정에서 일부 기능은 팀원이 초기 구현을 담당하고,
이후 기능 간 데이터 구조 · 권한 · API Response · Frontend 연동 과정에서 추가적인 보완과 리팩터링을 진행했습니다.

---

## 🏗️ Backend Architecture & Foundation

### 엄인섭(https://github.com/EddieEom)

Backend 개발의 공통 기반과 전체 구조를 담당했습니다.

* Backend Directory / Layer Architecture 설계
* ERD 및 Database 구조 설계
* SQLAlchemy ORM Model 설계
* User / Post / Comment / Like Domain
* Chat / Message Domain
* Schedule Domain
* File Domain
* Contest Domain
* FastAPI Router 구조
* Service / CRUD / Schema 역할 분리
* 공통 Database Session
* Environment Configuration
* JWT Authentication 구조
* Dependency Injection
* Alembic Migration 환경 구성

```text
Requirements
     ↓
ERD / Database
     ↓
Model
     ↓
Router / Service / CRUD / Schema
     ↓
Feature Development
```

프로젝트의 기능들이 서로 다른 방식으로 구현되지 않도록
Backend의 기본 구조와 데이터 관계를 먼저 정의한 뒤 기능 개발을 진행했습니다.

---

## 📰 Board & Community

### 초기 구현

**김세연(https://github.com/seye888-gif) · 천석훈(https://github.com/seoghuncheon) · 김호성**

게시판 관련 기능의 초기 구현을 분담했습니다.

* 공지사항
* 일반 게시판
* 질문 게시판
* 댓글
* 게시판별 기본 CRUD
* 게시글 목록 / Pagination
* 기본 작성자 권한 검사

### 기능 보완 및 최종 통합

**엄인섭**

초기 구현 이후 실제 서비스 요구사항과 Frontend 연동 과정에서
게시판 Domain을 다시 정리하고 기능을 확장했습니다.

* 공지 / 일반 / 질문 게시글 수정 API 통합
* `PostCategory` 기반 Category 규격 통일
* 게시글 상세 조회 구조 재설계
* 작성자 정보 Mapping
* `is_author` 상태 추가
* `is_liked` 상태 추가
* 댓글 수 / 좋아요 수 Aggregate
* 댓글 목록을 게시글 상세 Response에 통합
* 댓글 수정 기능 추가
* 중복 댓글 조회 API Deprecated 처리
* 게시글별 File 연결
* 다중 첨부파일 동기화
* Thumbnail 선택 기능
* 게시글 삭제 권한 통합
* 관리자 / 작성자 권한 분기
* 동아리활동 Category 추가
* 활동일(`activity_date`) 데이터 추가
* 게시글 일정 `start_date / end_date` 구조 정리
* Frontend Response Contract 보완
* API 오류 및 DB Schema 불일치 수정

```text
Initial Board API
       ↓
Requirement Review
       ↓
Data / Permission Review
       ↓
API Refactoring
       ↓
File / Comment / Like Integration
       ↓
Frontend Contract
```

---

## 👤 My Page & Utility

### 초기 구현

**김세연(https://github.com/seye888-gif) · 천석훈(https://github.com/seoghuncheon) · 김호성**

다음 기능의 초기 구현을 분담했습니다.

* Profile Edit
* Chat File Cloud
* Idea Note

### 기능 확장 및 통합

**엄인섭**

초기 기능을 전체 User / File / Chat Domain과 연결하고
실제 화면 요구사항에 맞게 기능을 확장했습니다.

#### Profile

* Profile 상세 조회
* 학적 상태 수정
* Profile Image
* Background Image
* Bio
* Hashtags
* Profile / Background File FK 구조
* 이미지 파일 검증
* Upload 경로 공통화
* File Size 정책 통합
* Profile Response 확장

#### Chat File Cloud

* Chat Room 참여자 접근 권한 연동
* Message ↔ File 관계 연동
* File Metadata Response 정리
* 30일 기준 File 만료 상태 계산
* Chat 기능과 공통 File Domain 연결

#### Idea Note

* User별 Idea 관리
* Pagination (`skip / limit`)
* 사용자 소유권 기준 조회 / 삭제
* Backend Router 구조와 최종 통합

---

## ⚙️ Core Backend Features

### 엄인섭(https://github.com/EddieEom)

위 협업 영역을 제외한 Backend 주요 기능을 구현했습니다.

### Authentication

* 회원가입
* 로그인
* bcrypt Password Hashing
* JWT Access Token
* Authentication Dependency
* 이메일 인증
* 비밀번호 재설정
* Gmail SMTP
* 입력 Validation 및 인증 예외 처리

### Membership / Authorization

* 동아리 가입 상태 관리

  * `PENDING`
  * `APPROVED`
  * `REJECTED`
* 가입 승인 / 거절
* 가입 승인 관리자 Dependency
* Role 기반 접근 제어
* RBAC 구조

### Calendar / Schedule

* 개인 일정 CRUD
* 월별 Calendar
* 일별 Schedule
* 게시글 일정 + 개인 일정 통합
* 일정 데이터 규격 통합

### Real-time Chat

* Chat Room
* 1:1 Chat Room 중복 생성 방지
* Chat Participant
* Message History
* WebSocket Connection Manager
* `NEW_MESSAGE`
* `READ_UPDATE`
* Message Read Status
* Message Delete
* Chat Room Leave
* Chat Pin
* File Message 연동

### File

* File Upload
* File Download
* UUID 기반 저장 파일명
* File Metadata 관리
* Upload Size Validation
* Path Traversal 방어
* Static File Serving

### Feed

* Feed CRUD
* File Join
* Feed 상세
* Feed → Chat Room 공유
* WebSocket 공유 Message Broadcast

### Home / Contest

* IT 공모전 데이터 수집
* Linkareer GraphQL API 연동
* Category별 Pagination 수집
* 중복 데이터 방지
* Host / Category 정규화
* 오래된 공모전 Cleanup
* Home IT Contest Banner API

---

## 🔧 Final Integration & Refactoring

### 엄인섭

프로젝트 후반에는 특정 기능 하나보다
전체 Backend가 동일한 데이터 규격과 Business Rule을 사용하도록 통합하는 작업을 담당했습니다.

주요 통합 작업:

* 팀원이 구현한 API 구조 검토
* Backend 요구사항과 실제 구현 비교
* API Endpoint 규격 정리
* 중복 API 제거
* Response Schema 통일
* Frontend 요구 데이터 추가
* DB Model ↔ Migration 동기화
* Category Enum 통일
* 권한 누락 보완
* 작성자 / 관리자 권한 정리
* File ↔ Post ↔ Feed ↔ Chat 관계 정리
* 게시글 / 댓글 / 좋아요 Join 구조 개선
* User Profile 데이터 확장
* 가입 승인 Workflow 추가
* 일정 Domain 구조 변경
* Migration 오류 해결
* 전체 기능 Integration Debugging

```text
Team Feature Implementation
          ↓
Backend Integration
          ↓
API Contract Review
          ↓
Database / Relation Review
          ↓
Business Rule Validation
          ↓
Frontend Integration
          ↓
Final Refactoring
```

각 기능을 단순히 개별적으로 완성하는 것보다
여러 팀원이 구현한 기능이 하나의 Backend Application 안에서 일관된 구조로 동작하도록 최종 통합했습니다.

---

## 🤝 Collaboration Workflow

```text
Backend Architecture / DB Design
              ↓
        기능 역할 분담
              ↓
      Feature Branch 개발
              ↓
        Pull Request / Merge
              ↓
       기능별 API Integration
              ↓
      Frontend 연동 및 테스트
              ↓
   누락된 요구사항 / 오류 확인
              ↓
       Refactoring / Fix
              ↓
          Final Backend
```

HelloWorld Backend는 개별 기능 담당자가 자신의 기능을 구현한 후
프로젝트 전체 구조와 Frontend 요구사항에 맞게 지속적으로 통합·보완하는 방식으로 개발했습니다.

---

# 📊 Project Summary

| Item           | Description                                    |
| -------------- | ---------------------------------------------- |
| Project        | HelloWorld Club App                            |
| Type           | Team Project                                   |
| Backend        | FastAPI                                        |
| Language       | Python                                         |
| Database       | PostgreSQL                                     |
| ORM            | SQLAlchemy                                     |
| Migration      | Alembic                                        |
| Authentication | JWT / bcrypt                                   |
| Authorization  | RBAC                                           |
| Real-time      | WebSocket                                      |
| File Storage   | Local File System                              |
| Email          | Gmail SMTP                                     |
| External Data  | Linkareer GraphQL API                          |
| Main Domains   | Auth / Member / Board / Schedule / Chat / Feed |
| API Style      | REST API + WebSocket                           |

---

<div align="center">

### HelloWorld Club App

**동아리 운영과 커뮤니티 기능을 하나의 서비스로 연결합니다.**

</div>
