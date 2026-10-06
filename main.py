from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import os
import resend
from email_service import send_welcome_email
from apscheduler.schedulers.background import BackgroundScheduler
from release_scheduler import send_release_reminders
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Header

from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")

if not ADMIN_TOKEN:
    raise RuntimeError("ADMIN_TOKEN 환경변수가 설정되지 않았습니다.")

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

scheduler = BackgroundScheduler(
    timezone="Asia/Seoul"
)

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://firstory-landing.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 데이터베이스 테이블 생성
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

    scheduler.add_job(
        send_release_reminders,
        "cron",
        hour=9,
        minute=0,
        id="release_reminder",
        replace_existing=True
    )

    scheduler.start()

    print("Release reminder scheduler started.")

@app.on_event("shutdown")
def shutdown():
    scheduler.shutdown()

    print("Release reminder scheduler stopped.")    


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


#admin 인증 함수
def verify_admin_token(
    authorization: str | None = Header(default=None)
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header가 필요합니다."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Bearer Token 형식이 필요합니다."
        )

    token = authorization.replace("Bearer ", "", 1)

    if token != ADMIN_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="유효하지 않은 관리자 토큰입니다."
        )

    return True    

@app.get("/api/admin/emails", response_model=list[SubscriberListResponse])
def get_subscribers(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_token)
):
    subscribers = db.query(Subscriber).order_by(Subscriber.id.desc()).all()
    return subscribers 