# 작성자 : 엄인섭
import aiosmtplib
from email.utils import formatdate, make_msgid
from email.message import EmailMessage
from app.core.config import settings

async def send_email(to_email: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = settings.EMAIL_FROM
    message["To"] = to_email
    message["Subject"] = subject

    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid()
    
    message.set_content(body)

    try:
        # 587 포트는 use_tls=False로 두면 aiosmtplib이 자동으로 STARTTLS를 진행합니다.
        async with aiosmtplib.SMTP(
            hostname="smtp.gmail.com",
            port=587,
            use_tls=False, 
        ) as smtp:
            # 연결 후 곧바로 로그인 및 발송 진행
            await smtp.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
            await smtp.send_message(message)
            return True
    except Exception as e:
        print(f"이메일 발송 상세 에러 로그: {e}")
        return False


# 디버깅 모드: 실제 이메일 발송 대신 로그 출력
    # print(f"\n[디버깅 모드] 이메일 발송 시뮬레이션")
    # print(f"받는 사람: {to_email}")
    # print(f"제목: {subject}")
    # print(f"내용: {body}")
    
    # # 실제 메일은 안 보내지만, 보낸 척(True)을 해서 로직을 통과시킵니다.
    # return True