"""SQLAlchemy models — Doc-08 9 tables + sign_assets (M1)."""

from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def _id_default():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"
    user_id = Column(String(36), primary_key=True, default=_id_default)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(50), default="viewer")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SignClass(Base):
    __tablename__ = "sign_classes"
    class_id = Column(String(50), primary_key=True)
    label = Column(String(100), unique=True, nullable=False)
    gloss = Column(String(100), default="")
    sign_type = Column(String(20), default="Dynamic")
    meaning = Column(Text, default="")
    handedness = Column(String(20), default="Both")


class RecognitionSession(Base):
    __tablename__ = "recognition_sessions"
    session_id = Column(String(36), primary_key=True, default=_id_default)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    status = Column(String(30), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    predictions = relationship("Prediction", back_populates="session")


class ModelVersion(Base):
    __tablename__ = "model_versions"
    model_id = Column(String(100), primary_key=True)
    version = Column(String(50), nullable=False)
    model_type = Column(String(50), default="lstm")
    seq_len = Column(Integer, default=45)
    feat_dim = Column(Integer, default=189)
    accuracy = Column(Float, nullable=True)
    macro_f1 = Column(Float, nullable=True)
    artifact_uri = Column(Text, default="")
    status = Column(String(30), default="development")


class Prediction(Base):
    __tablename__ = "predictions"
    prediction_id = Column(String(36), primary_key=True, default=_id_default)
    session_id = Column(String(36), ForeignKey("recognition_sessions.session_id"), nullable=False)
    class_id = Column(String(50), ForeignKey("sign_classes.class_id"), nullable=False)
    model_id = Column(String(100), ForeignKey("model_versions.model_id"), nullable=False)
    confidence = Column(Float, nullable=False)
    status = Column(String(30), default="recognized")
    sequence_id = Column(String(100), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    session = relationship("RecognitionSession", back_populates="predictions")


class ModelDeployment(Base):
    __tablename__ = "model_deployments"
    deployment_id = Column(String(36), primary_key=True, default=_id_default)
    model_id = Column(String(100), ForeignKey("model_versions.model_id"), nullable=False)
    environment = Column(String(30), default="staging")
    deployed_at = Column(DateTime(timezone=True), server_default=func.now())


class Feedback(Base):
    __tablename__ = "feedback"
    feedback_id = Column(String(36), primary_key=True, default=_id_default)
    prediction_id = Column(String(36), ForeignKey("predictions.prediction_id"), nullable=False)
    actual_class_id = Column(String(50), ForeignKey("sign_classes.class_id"), nullable=True)
    rating = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ApiLog(Base):
    __tablename__ = "api_logs"
    request_id = Column(String(36), primary_key=True, default=_id_default)
    path = Column(Text, default="")
    status_code = Column(Integer, default=200)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"
    audit_id = Column(String(36), primary_key=True, default=_id_default)
    actor = Column(String(100), default="")
    action = Column(String(100), default="")
    ip_hash = Column(String(128), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SignAsset(Base):
    __tablename__ = "sign_assets"
    asset_id = Column(String(36), primary_key=True, default=_id_default)
    class_id = Column(String(50), ForeignKey("sign_classes.class_id"), nullable=False)
    type = Column(String(30), default="video")
    uri = Column(Text, default="")
