from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean, String
from src.db.base import Base


class AdminUser(Base):
    __tablename__ = "admin_users"
    id: Mapped[int] = mapped_column(primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(13), nullable=False, unique=True)
    phone_number_validated: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    national_id: Mapped[str] = mapped_column(String(10), nullable=True, unique=True)
    national_id_validated: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    sheba_number: Mapped[str] = mapped_column(String(26), nullable=True, unique=True)
    sheba_number_validated: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    full_nane: Mapped[str] = mapped_column(String(200), nullable=False)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    otp_token: Mapped[str] = mapped_column(String(255), nullable=False)
