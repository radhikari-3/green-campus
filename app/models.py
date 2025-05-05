import datetime
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


@dataclass
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    role: so.Mapped[str] = so.mapped_column(sa.String(10), default="Normal")

    inventory: so.Mapped[Optional["Inventory"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    email_verified: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    email_otp: so.Mapped[Optional[str]] = so.mapped_column(sa.String(6), nullable=True)
    email_otp_expires: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime, nullable=True)
    signup_date: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow, nullable=False)


    # Relationship
    activity_logs: so.WriteOnlyMapped["ActivityLog"] = so.relationship(
        "ActivityLog", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        pwh= 'None' if not self.password_hash else f'...{self.password_hash[-5:]}'

        return f'User(id={self.id}, email={self.email}, role={self.role}, pwh={pwh})'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_otp(self):
        import random
        code = f"{random.randint(100000, 999999)}"
        self.email_otp = code
        self.email_otp_expires = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        return code


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class EnergyReading(db.Model):
    __tablename__ = 'energy_readings'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(sa.DateTime)
    building: so.Mapped[str] = so.mapped_column(sa.String(100))
    building_code: so.Mapped[str] = so.mapped_column(sa.String(10))
    zone: so.Mapped[str] = so.mapped_column(sa.String(50))
    value: so.Mapped[float] = so.mapped_column(sa.Float)
    category: so.Mapped[str] = so.mapped_column(sa.String(50))  # gas or electricity


    def __repr__(self):
        return f'EnergyReading(id={self.id}, timestamp={self.timestamp}, building={self.building}, ' \
               f'building_code={self.building_code}, zone={self.zone}, value={self.value}, category={self.category})'

class Inventory(db.Model):
    __tablename__ = 'inventory'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100))
    expiry_date: so.Mapped[date] = so.mapped_column(sa.Date())
    units: so.Mapped[int] = so.mapped_column(sa.Integer())
    category: so.Mapped[str] = so.mapped_column(sa.String(100))
    marked_price: so.Mapped[float] = so.mapped_column(sa.Float())
    discount: so.Mapped[float] = so.mapped_column(sa.Float(), default=0.75)
    final_price: so.Mapped[float] = so.mapped_column(sa.Float(), nullable=True)
    location: so.Mapped[str] = so.mapped_column(sa.String(200))
    user_id: so.Mapped[int] = so.mapped_column(ForeignKey("users.id"))
    user: so.Mapped["User"] = relationship(back_populates="inventory")

class ActivityLog(db.Model):
    __tablename__ = 'activity_log'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    email: so.Mapped[str] = so.mapped_column(
        sa.String(120),
        sa.ForeignKey('users.email'),
        nullable=False,
        index=True
    )
    date: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    activity_type: so.Mapped[str] = so.mapped_column(sa.String(50), default="walking")
    steps: so.Mapped[int] = so.mapped_column(sa.Integer, default=0)
    distance: so.Mapped[float] = so.mapped_column(sa.Float, default=0.0)
    eco_points: so.Mapped[float] = so.mapped_column(sa.Float, default=0.0)  # ✅ Now stores decimal values
    eco_last_updated: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    eco_last_redeemed: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime, nullable=True)

    user: so.Mapped["User"] = so.relationship("User", back_populates="activity_logs")

    def __repr__(self):
        return (
            f"<ActivityLog {self.email} on {self.date.date()} | {self.activity_type} | "
            f"{self.steps} steps | {self.distance}m = {self.eco_points} points>"

        )
