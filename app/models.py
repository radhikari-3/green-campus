from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


@dataclass
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    role: so.Mapped[str] = so.mapped_column(sa.String(10), default="Normal")


    def __repr__(self):
        pwh= 'None' if not self.password_hash else f'...{self.password_hash[-5:]}'
        return f'User(id={self.id}, username={self.username}, email={self.email}, role={self.role}, pwh={pwh})'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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
    category: so.Mapped[str] = so.mapped_column(sa.String(50))  # Category: gas or electricity

    def __repr__(self):
        return f'EnergyReading(id={self.id}, timestamp={self.timestamp}, building={self.building}, ' \
               f'building_code={self.building_code}, zone={self.zone}, value={self.value}, category={self.category})'


class StepData(db.Model):
    __tablename__ = 'step_data'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    date: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    steps: so.Mapped[int] = so.mapped_column(sa.Integer)

    # Relationship with the User table
    user: so.Mapped["User"] = so.relationship("User", back_populates="steps_data")

    def __repr__(self):
        return f'StepData(id={self.id}, user_id={self.user_id}, date={self.date}, steps={self.steps})'


class EcoPoints(db.Model):
    __tablename__ = 'eco_points'

    user_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('users.id'), primary_key=True)
    eco_points: so.Mapped[int] = so.mapped_column(sa.Integer, default=0)
    last_updated_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)

    # Relationship with the User table
    user: so.Mapped["User"] = so.relationship("User", back_populates="eco_points")

    def __repr__(self):
        return f'EcoPoints(user_id={self.user_id}, eco_points={self.eco_points}, last_updated_at={self.last_updated_at})'