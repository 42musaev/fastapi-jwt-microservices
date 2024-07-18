from datetime import datetime

from db.db_helper import Base
from sqlalchemy import BigInteger
from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class RefreshSession(Base):
    __tablename__ = 'refresh_sessions'

    user_email: Mapped[str]
    refresh_token_jit: Mapped[str] = mapped_column(unique=True)
    user_agent: Mapped[str]
    ip: Mapped[str]
    fingerprint: Mapped[str]
    expires: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
