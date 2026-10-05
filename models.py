from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    func
)

from database import Base


# 이메일 구독자 테이블
class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    is_subscribed = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


# 이메일 발송 기록 테이블
class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)

    recipient = Column(
        String(255),
        nullable=False
    )

    subject = Column(
        String(255),
        nullable=False
    )

    email_type = Column(
    String(50),
    nullable=False
    )

    status = Column(
        String(20),
        nullable=False
    )

    error_message = Column(
        Text,
        nullable=True
    )

    sent_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )