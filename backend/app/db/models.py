# Génération d'UUID (identifiants uniques)
import uuid
# Gestion du temps avec timezone UTC
from datetime import UTC, datetime

# Types SQLAlchemy pour définir les colonnes
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
# ORM pour mapper les classes Python aux tables DB
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Classe de base pour tous les modèles (ORM)
from app.db.base import Base


# Fonction pour obtenir la date actuelle en UTC
def utcnow() -> datetime:
    return datetime.now(UTC)


# =========================
# TABLE USERS
# =========================
class User(Base):
    __tablename__ = 'users'  # Nom de la table

    # ID unique (UUID en string)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Nom d'utilisateur unique (indexé pour recherche rapide)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    
    # Mot de passe hashé (jamais en clair)
    password_hash: Mapped[str] = mapped_column(String(200))
    
    # Nom affiché (ex: prénom)
    display_name: Mapped[str] = mapped_column(String(100))
    
    # Rôle (user ou admin)
    role: Mapped[str] = mapped_column(String(20), default='user', index=True)
    
    # Date de création
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    
    # Date de mise à jour automatique
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    # Relation avec les analyses (1 user → plusieurs analyses)
    analyses: Mapped[list['AnalysisRecord']] = relationship(back_populates='user')


# =========================
# TABLE ANALYSIS RECORDS
# =========================
class AnalysisRecord(Base):
    __tablename__ = 'analysis_records'

    # ID unique de l’analyse
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Valeur analysée (URL, IP, hash...)
    input_value: Mapped[str] = mapped_column(Text)
    
    # Type d’indicateur (url, ip, domain, file, hash...)
    indicator_type: Mapped[str] = mapped_column(String(20), index=True)
    
    # Verdict final (malicious, safe...)
    verdict: Mapped[str] = mapped_column(String(32), index=True)
    
    # Résumé de l’analyse (optionnel)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Statut brut venant de l’API externe
    raw_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Snapshot du username (utile si user supprimé plus tard)
    username_snapshot: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    
    # Clé étrangère vers user (peut être null si utilisateur non connecté)
    user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id'), nullable=True, index=True)
    
    # Date de création
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    # Relation vers l’utilisateur (plusieurs analyses → 1 user)
    user: Mapped[User | None] = relationship(back_populates='analyses')
    
    # Relation 1-1 avec les stats (chaque analyse a un seul stats record)
    stats: Mapped['AnalysisStatsRecord | None'] = relationship(
        back_populates='analysis',
        uselist=False,  # relation one-to-one
        cascade='all, delete-orphan',  # supprime les stats si analyse supprimée
    )


# =========================
# TABLE ANALYSIS STATS
# =========================
class AnalysisStatsRecord(Base):
    __tablename__ = 'analysis_stats_records'

    # ID auto-incrémenté
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Clé étrangère vers l’analyse (unique → 1-1)
    analysis_id: Mapped[str] = mapped_column(ForeignKey('analysis_records.id'), unique=True, index=True)
    
    # Compteurs venant de VirusTotal
    malicious_count: Mapped[int] = mapped_column(Integer, default=0)
    suspicious_count: Mapped[int] = mapped_column(Integer, default=0)
    harmless_count: Mapped[int] = mapped_column(Integer, default=0)
    undetected_count: Mapped[int] = mapped_column(Integer, default=0)
    timeout_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Date de création
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    # Relation inverse vers AnalysisRecord
    analysis: Mapped[AnalysisRecord] = relationship(back_populates='stats')


# =========================
# TABLE REVOKED TOKENS
# =========================
class RevokedToken(Base):
    __tablename__ = 'revoked_tokens'

    # ID auto-incrémenté
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # JTI (ID unique du token JWT)
    jti: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    
    # ID utilisateur associé (optionnel)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    
    # Date d’expiration du token
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    
    # Date de création (quand le token a été révoqué)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)