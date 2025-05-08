from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login


# === User Model ===
@dataclass
class User(UserMixin, db.Model):
    """
    User model for authentication and role-based access.
    Includes relationships to inventory and activity logs.
    """
    __tablename__ = 'users'

    # Core fields
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    role: so.Mapped[str] = so.mapped_column(sa.String(10), default="Normal")

    # Email verification fields
    email_verified: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    email_otp: so.Mapped[Optional[str]] = so.mapped_column(sa.String(6), nullable=True)
    email_otp_expires: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime, nullable=True)
    signup_date: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    inventory: so.Mapped[Optional["Inventory"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    activity_logs: so.WriteOnlyMapped["ActivityLog"] = so.relationship(
        "ActivityLog", back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )

    # Password hashing and validation
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Debug-friendly representation
    def __repr__(self):
        pwh = 'None' if not self.password_hash else f'...{self.password_hash[-5:]}'
        return f'User(id={self.id}, email={self.email}, role={self.role}, pwh={pwh})'

# Flask-Login: Load user by ID for session handling
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


# === Energy Reading Model ===
class EnergyReading(db.Model):
    """
    Stores energy sensor readings (electricity/gas) with timestamps.
    """
    __tablename__ = 'energy_readings'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(sa.DateTime)
    value: so.Mapped[float] = so.mapped_column(sa.Float)
    category: so.Mapped[str] = so.mapped_column(sa.String(50))  # e.g., "electricity" or "gas"
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False)
    building: so.Mapped["Building"] = so.relationship("Building", back_populates="energy_readings")
    def __repr__(self):
        return (
            f'EnergyReading(id={self.id}, timestamp={self.timestamp}, building={self.building}, '
            f'building_code={self.building_code}, zone={self.zone}, value={self.value}, category={self.category})'
        )

# === Building Model ===
class Building(db.Model):
    """
    Represents campus buildings with their energy usage tracking.
    """
    __tablename__ = 'building'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100))
    code: so.Mapped[str] = so.mapped_column(sa.String(10), nullable=True)
    zone: so.Mapped[str] = so.mapped_column(sa.String(10))

    # Relationships
    energy_readings: so.WriteOnlyMapped["EnergyReading"] = relationship(
        back_populates="building", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f'Building(id={self.id}, name={self.name}, code={self.code}, '
            f'floors={self.floors}, energy_rating={self.energy_rating})'
        )


# === Inventory Model ===
class Inventory(db.Model):
    """
    Represents food products uploaded by users (vendors).
    """
    __tablename__ = 'inventory'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100))
    expiry_date: so.Mapped[date] = so.mapped_column(sa.Date())
    units: so.Mapped[int] = so.mapped_column(sa.Integer())
    category: so.Mapped[str] = so.mapped_column(sa.String(100))
    marked_price: so.Mapped[float] = so.mapped_column(sa.Float())
    discount: so.Mapped[float] = so.mapped_column(sa.Float(), default=0.75)
    final_price: so.Mapped[float] = so.mapped_column(sa.Float())
    location: so.Mapped[str] = so.mapped_column(sa.String(200))
    user_id: so.Mapped[int] = so.mapped_column(ForeignKey("users.id"))  # Foreign key to User
    user: so.Mapped["User"] = relationship(back_populates="inventory")  # Backref to User


# === Activity Log Model ===
class ActivityLog(db.Model):
    """
    Tracks daily physical activities (walking, cycling) with eco-point rewards.
    """
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
    eco_points: so.Mapped[float] = so.mapped_column(sa.Float, default=0.0)
    eco_last_updated: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    eco_last_redeemed: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime, nullable=True)

    user: so.Mapped["User"] = so.relationship("User", back_populates="activity_logs")

    def __repr__(self):
        return (
            f"<ActivityLog {self.email} on {self.date.date()} | {self.activity_type} | "
            f"{self.steps} steps | {self.distance}m = {self.eco_points} points>"
        )
