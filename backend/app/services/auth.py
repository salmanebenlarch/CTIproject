# Import de la date/heure avec support UTC
from datetime import UTC, datetime

# Types pour annotations
from typing import List, Optional

# Import des fonctions SQLAlchemy pour requêtes, agrégations et suppression
from sqlalchemy import delete, func, select

# Session SQLAlchemy pour interagir avec la base de données
from sqlalchemy.orm import Session

# Configuration globale de l’application
from app.core.config import get_settings

# Modèles ORM (tables base de données)
from app.db.models import AnalysisRecord, RevokedToken, User

# Schémas Pydantic liés à l’authentification
from app.schemas.auth import CreateUserRequest, UpdateUserRoleRequest, UserInfo

# Fonctions utilitaires de sécurité (JWT, hash, password, etc.)
from app.services.security import (
    create_access_token,   # génère un token JWT
    decode_access_token,   # décode un JWT
    hash_password,         # hash un mot de passe
    utcnow,                # retourne l'heure UTC actuelle
    verify_password,       # vérifie un mot de passe hashé
)


# Service central de gestion de l’authentification
class AuthService:

    # Retourne l’heure actuelle en UTC
    def utcnow(self) -> datetime:
        return utcnow()

    # Initialise (seed) des utilisateurs par défaut (admin + user)
    def seed_default_users(self, db: Session) -> None:
        settings = get_settings()

        # Création de l’admin par défaut si inexistant
        self._ensure_user(
            db,
            username=settings.demo_admin_username,
            password=settings.demo_admin_password,
            display_name=settings.demo_admin_display_name,
            role='admin',
        )

        # Création d’un utilisateur standard par défaut
        self._ensure_user(
            db,
            username=settings.demo_user_username,
            password=settings.demo_user_password,
            display_name=settings.demo_user_display_name,
            role='user',
        )

    # Vérifie si un utilisateur existe, sinon le crée
    def _ensure_user(self, db: Session, *, username: str, password: str, display_name: str, role: str) -> None:
        # Recherche utilisateur par username
        existing = db.scalar(select(User).where(User.username == username))

        # Si l’utilisateur existe déjà, on ne fait rien
        if existing:
            return

        # Création de l’utilisateur avec mot de passe hashé
        db.add(
            User(
                username=username,
                password_hash=hash_password(password),
                display_name=display_name,
                role=role,
            )
        )

    # Authentification utilisateur
    def login(self, db: Session, username: str, password: str) -> tuple[str, UserInfo] | None:
        # Récupération utilisateur en base
        user = db.scalar(select(User).where(User.username == username))

        # Vérification existence + mot de passe
        if not user or not verify_password(password, user.password_hash):
            return None

        # Génération d’un token JWT
        token = create_access_token(user.id)

        # Retour du token + informations utilisateur
        return token, self.to_user_info(user)

    # Déconnexion utilisateur (révocation du token)
    def logout(self, db: Session, token: str) -> None:
        try:
            # Décodage du token même expiré
            payload = decode_access_token(token, allow_expired=True)
        except Exception:
            return

        # Identifiant unique du token (JWT ID)
        jti = payload.get('jti')

        # Si pas de jti ou déjà révoqué → rien à faire
        if not jti or self.is_token_revoked(db, jti):
            return

        # Date d’expiration du token
        exp = payload.get('exp')
        expires_at = self._coerce_jwt_timestamp(exp)

        # Enregistrement du token comme révoqué
        db.add(
            RevokedToken(
                jti=jti,
                user_id=payload.get('sub'),
                expires_at=expires_at,
            )
        )

        # Sauvegarde en base
        db.commit()

        # Nettoyage des tokens expirés
        self.cleanup_revoked_tokens(db)

    # Supprime les tokens révoqués expirés
    def cleanup_revoked_tokens(self, db: Session) -> None:
        db.execute(delete(RevokedToken).where(RevokedToken.expires_at <= utcnow()))
        db.commit()

    # Vérifie si un token est révoqué
    def is_token_revoked(self, db: Session, jti: str | None) -> bool:
        if not jti:
            return True

        # Recherche du token dans la table des tokens révoqués
        record = db.scalar(select(RevokedToken).where(RevokedToken.jti == jti))

        # True si trouvé, sinon False
        return record is not None

    # Récupère un utilisateur par ID
    def get_user_by_id(self, db: Session, user_id: str) -> Optional[User]:
        return db.scalar(select(User).where(User.id == user_id))

    # Liste tous les utilisateurs
    def list_users(self, db: Session) -> List[UserInfo]:
        users = db.scalars(select(User).order_by(User.username.asc())).all()

        # Conversion ORM → schema Pydantic
        return [self.to_user_info(user) for user in users]

    # Création d’un nouvel utilisateur
    def create_user(self, db: Session, payload: CreateUserRequest) -> UserInfo:
        # Vérifie si username existe déjà
        existing = db.scalar(select(User).where(User.username == payload.username))
        if existing:
            raise ValueError('A user with this username already exists.')

        # Définition du display_name (fallback si non fourni)
        display_name = payload.display_name or payload.username.title()

        # Création de l’objet utilisateur
        user = User(
            username=payload.username,
            password_hash=hash_password(payload.password),
            display_name=display_name,
            role=payload.role,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return self.to_user_info(user)

    # Changement de mot de passe
    def change_password(self, db: Session, username: str, current_password: str, new_password: str) -> None:
        # Recherche utilisateur
        user = db.scalar(select(User).where(User.username == username))

        # Vérification mot de passe actuel
        if not user or not verify_password(current_password, user.password_hash):
            raise ValueError('Current password is incorrect.')

        # Empêche réutilisation du même mot de passe
        if current_password == new_password:
            raise ValueError('New password must be different from the current password.')

        # Mise à jour du mot de passe hashé
        user.password_hash = hash_password(new_password)

        db.add(user)
        db.commit()

    # Suppression d’un utilisateur
    def delete_user(self, db: Session, username: str, current_username: str) -> None:
        user = db.scalar(select(User).where(User.username == username))

        if not user:
            raise ValueError('User not found.')

        # Empêche un utilisateur de se supprimer lui-même
        if user.username == current_username:
            raise ValueError('You cannot delete your own account.')

        # Empêche suppression du dernier admin
        if user.role == 'admin' and self._admin_count(db) <= 1:
            raise ValueError('At least one admin account must remain.')

        # Désassocie les analyses liées à cet utilisateur
        analyses = db.scalars(select(AnalysisRecord).where(AnalysisRecord.user_id == user.id)).all()
        for record in analyses:
            record.user_id = None

        # Suppression utilisateur
        db.delete(user)
        db.commit()

    # Mise à jour du rôle utilisateur
    def update_user_role(self, db: Session, username: str, payload: UpdateUserRoleRequest, current_username: str) -> UserInfo:
        user = db.scalar(select(User).where(User.username == username))

        if not user:
            raise ValueError('User not found.')

        # Empêche un admin de changer son propre rôle
        if user.username == current_username and user.role != payload.role:
            raise ValueError('You cannot change your own role from the admin panel.')

        # Empêche de supprimer le dernier admin
        if user.role == 'admin' and payload.role != 'admin' and self._admin_count(db) <= 1:
            raise ValueError('At least one admin account must remain.')

        # Mise à jour du rôle
        user.role = payload.role
        db.add(user)
        db.commit()
        db.refresh(user)

        return self.to_user_info(user)

    # Statistiques du nombre d’analyses par utilisateur
    def analysis_count_by_user(self, db: Session) -> dict[str, int]:
        rows = db.execute(
            select(AnalysisRecord.username_snapshot, func.count(AnalysisRecord.id))
            .where(AnalysisRecord.username_snapshot.is_not(None))
            .group_by(AnalysisRecord.username_snapshot)
        ).all()

        # Transformation en dictionnaire {username: count}
        return {username: count for username, count in rows if username}

    # Compte le nombre d’admins
    def _admin_count(self, db: Session) -> int:
        return db.scalar(select(func.count(User.id)).where(User.role == 'admin')) or 0

    # Conversion d’un objet User ORM vers UserInfo (schema API)
    @staticmethod
    def to_user_info(user: User) -> UserInfo:
        return UserInfo(username=user.username, display_name=user.display_name, role=user.role)

    # Conversion d’un timestamp JWT en datetime UTC
    @staticmethod
    def _coerce_jwt_timestamp(value: int | float | datetime | None) -> datetime:
        if isinstance(value, datetime):
            return value.astimezone(UTC)
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=UTC)
        return utcnow()


# Instance globale du service (utilisée dans les routes)
auth_service = AuthService()