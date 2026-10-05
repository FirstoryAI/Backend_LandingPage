import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")


def send_welcome_email(recipient: str):
    response = resend.Emails.send({
        "from": EMAIL_FROM,
        "to": [recipient],
        "subject": "FIRSTORY 서비스 사전 등록이 완료됐어요!",
        "html": f"""
            <p>{recipient}로 서비스 사전 등록이 완료됐어요.</p>

            <p>
                FIRSTORY는 아이가 겪은 일을 AI 맞춤 동화로 만들어,<br>
                부모와 아이가 함께 읽고 이야기 나눌 수 있게 돕는 서비스예요.
            </p>

            <p>
                서비스 출시가 다가오면, 서비스 출시 소식과 할인 쿠폰을 여기로 보내드릴게요.
            </p>

            <p>
                서비스에 대해 궁금한 점이 있다면,<br>
                아래 메일로 편하게 보내주세요.<br>
                firstory.official@gmail.com
            </p>

            <p>감사합니다.</p>

            <p>──────────<br>
            FIRSTORY 드림.</p>
        """
    })

    return response