from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


@dataclass
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: so.Mapped[int]      = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str]    = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    role: so.Mapped[str]     = so.mapped_column(sa.String(10), default="Normal")

    # backwards relationships
    steps_data: so.Mapped[List["StepData"]] = so.relationship(
        "StepData", back_populates="user", cascade="all, delete-orphan"
    )
    eco_points: so.Mapped[Optional["EcoPoints"]] = so.relationship(
        "EcoPoints", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class EnergyReading(db.Model):
    __tablename__ = 'energy_readings'
    id: so.Mapped[int]        = so.mapped_column(primary_key=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(sa.DateTime)
    building: so.Mapped[str]  = so.mapped_column(sa.String(100))
    building_code: so.Mapped[str] = so.mapped_column(sa.String(10))
    zone: so.Mapped[str]      = so.mapped_column(sa.String(50))
    value: so.Mapped[float]   = so.mapped_column(sa.Float)
    category: so.Mapped[str]  = so.mapped_column(sa.String(50))


class StepData(db.Model):
    __tablename__ = 'step_data'

    id: so.Mapped[int]             = so.mapped_column(primary_key=True)
    username: so.Mapped[str]       = so.mapped_column(
        sa.String(64),
        sa.ForeignKey('users.username'),
        nullable=False,
        index=True
    )
    date: so.Mapped[datetime]      = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    steps: so.Mapped[int]          = so.mapped_column(sa.Integer)

    user: so.Mapped["User"]        = so.relationship("User", back_populates="steps_data")

    def __repr__(self):
        return f"<StepData {self.username} @ {self.date.date()}: {self.steps} steps>"


class EcoPoints(db.Model):
    __tablename__ = 'eco_points'

    username: so.Mapped[str]       = so.mapped_column(
        sa.String(64),
        sa.ForeignKey('users.username'),
        primary_key=True
    )
    eco_points: so.Mapped[int]     = so.mapped_column(sa.Integer, default=0)
    last_updated_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)

    user: so.Mapped["User"]        = so.relationship("User", back_populates="eco_points")

    def __repr__(self):
        return f"<EcoPoints {self.username}: {self.eco_points}>"
