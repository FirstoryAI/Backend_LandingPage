import os
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import resend
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Subscriber, EmailLog

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")


def is_release_reminder_day() -> bool:
    release_date_str = os.getenv("RELEASE_DATE")

    if not release_date_str:
        raise RuntimeError("RELEASE_DATE가 설정되지 않았습니다.")

    release_date = date.fromisoformat(release_date_str)
    reminder_date = release_date - timedelta(days=3)

    today = datetime.now(ZoneInfo("Asia/Seoul")).date()
    return today == reminder_date


def send_release_reminder(recipient: str):
    return resend.Emails.send({
        "from": EMAIL_FROM,
        "to": [recipient],
        "subject": "Firstory 출시가 3일 앞으로 다가왔습니다!",
        "html": """
            <h1>Firstory 출시가 3일 앞으로 다가왔습니다!</h1>
            <p>기다려주셔서 감사합니다.</p>
            <p>Firstory가 곧 출시됩니다.</p>
        """
    })


def send_release_reminders():
    if not is_release_reminder_day():
        print("오늘은 출시 3일 전이 아닙니다.")
        return

    db: Session = SessionLocal()

    try:
        subscribers = db.query(Subscriber).filter(
            Subscriber.is_subscribed == True
        ).all()

        for subscriber in subscribers:

            already_sent = db.query(EmailLog).filter(
                EmailLog.recipient == subscriber.email,
                EmailLog.email_type == "RELEASE_REMINDER",
                EmailLog.status == "success"
            ).first()

            if already_sent:
                continue

            try:
                send_release_reminder(subscriber.email)

                email_log = EmailLog(
                    recipient=subscriber.email,
                    subject="Firstory 출시가 3일 앞으로 다가왔습니다!",
                    email_type="RELEASE_REMINDER",
                    status="success"
                )

                db.add(email_log)
                db.commit()

            except Exception as e:
                db.rollback()

                email_log = EmailLog(
                    recipient=subscriber.email,
                    subject="Firstory 출시가 3일 앞으로 다가왔습니다!",
                    email_type="RELEASE_REMINDER",
                    status="failed",
                    error_message=str(e)
                )

                db.add(email_log)
                db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    send_release_reminders()