from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import os
import resend
from email_service import send_welcome_email

from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

from database import engine, Base, get_db
from models import Subscriber, EmailLog
from schemas import (
    SubscriberCreate,
    SubscriberResponse,
    SubscriberListResponse
)

import models

app = FastAPI(
    title="Email Manager",
    description="이메일 수집 및 발송 관리 시스템",
    version="0.1.0"
)


# 데이터베이스 테이블 생성
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {
        "message": "Email Manager API is running!",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/db-test")
def db_test():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            value = result.scalar()

        return {
            "database": "connected",
            "result": value
        }

    except Exception as e:
        return {
            "database": "disconnected",
            "error": str(e)
        }


# 이메일 구독 API
@app.post(
    "/api/emails/subscribe",
    response_model=SubscriberResponse
)
def subscribe_email(
    request: SubscriberCreate,
    db: Session = Depends(get_db)
):
    email = request.email.lower()

    # 기존 이메일 확인
    existing_subscriber = db.query(Subscriber).filter(
        Subscriber.email == email
    ).first()

    if existing_subscriber:
        if existing_subscriber.is_subscribed:
            raise HTTPException(
                status_code=409,
                detail="이미 구독 중인 이메일입니다."
            )

        existing_subscriber.is_subscribed = True
        db.commit()
        db.refresh(existing_subscriber)

        return existing_subscriber

    # 신규 구독자 생성
    new_subscriber = Subscriber(
        email=email,
        is_subscribed=True
    )

    try:
        db.add(new_subscriber)
        db.commit()
        db.refresh(new_subscriber)

        try:
            send_welcome_email(new_subscriber.email)

            email_log = EmailLog(
                recipient=new_subscriber.email,
                subject="Firstory에 가입하신 여러분을 환영합니다!",
                email_type="WELCOME",
                status="success"
            )

            db.add(email_log)
            db.commit()

        except Exception as e:
            db.rollback()

            email_log = EmailLog(
                recipient=new_subscriber.email,
                subject="Firstory에 가입하신 여러분을 환영합니다!",
                email_type="WELCOME",
                status="failed",
                error_message=str(e)
            )

            db.add(email_log)
            db.commit()

        return new_subscriber

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="이미 등록된 이메일입니다."
        )    


@app.get(
    "/api/admin/emails",
    response_model=list[SubscriberListResponse]
)
def get_subscribers(
    db: Session = Depends(get_db)
):
    subscribers = db.query(Subscriber).order_by(
        Subscriber.id.desc()
    ).all()

    return subscribers    


#테스트용 이메일 API
@app.post("/api/test-email")
def test_email():
    try:
        response = resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": ["firstory.official@gmail.com"],
            "subject": "Email Manager 테스트 메일",
            "html": """
                <h1>테스트 성공!</h1>
                <p>FastAPI에서 Resend를 통해 보낸 테스트 이메일입니다.</p>
            """
        })

        return {
            "status": "success",
            "message": "테스트 이메일을 발송했습니다.",
            "resend_response": response
        }

    except Exception as e:
        return {
            "status": "failed",
            "message": "이메일 발송에 실패했습니다.",
            "error": str(e)
        }