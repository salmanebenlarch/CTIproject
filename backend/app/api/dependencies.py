from typing import Optional

# Import des dépendances FastAPI pour gérer l'authentification et les erreurs HTTP
from fastapi import Depends, HTTPException, status
# Permet de récupérer le token Bearer depuis les headers Authorization
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
# Session SQLAlchemy pour interagir avec la base de données
from sqlalchemy.orm import Session

# Fonction pour récupérer une session DB
from app.db.session import get_db
# Schéma représentant les infos d'un utilisateur
from app.schemas.auth import UserInfo
# Service d'authentification (logique métier liée aux utilisateurs)
from app.services.auth import auth_service
# Gestion des tokens (JWT) et exceptions personnalisées
from app.services.security import TokenExpiredError, TokenInvalidError, decode_access_token

# Définition du système de sécurité Bearer (Authorization: Bearer <token>)
# auto_error=False → ne renvoie pas automatiquement une erreur si le token est absent
security = HTTPBearer(auto_error=False)


def get_optional_current_user(
    # Récupère les credentials (token) depuis la requête HTTP
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    # Injection de la session base de données
    db: Session = Depends(get_db),
) -> Optional[UserInfo]:
    # Si aucun token n'est fourni → utilisateur non connecté (optionnel)
    if credentials is None:
        return None

    # Vérifie que le schéma est bien "Bearer"
    if credentials.scheme.lower() != 'bearer':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authentication scheme.')

    try:
        # Décodage du token JWT pour récupérer le payload (contenu)
        payload = decode_access_token(credentials.credentials)
    except TokenExpiredError as exc:
        # Token expiré
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token expired.') from exc
    except TokenInvalidError as exc:
        # Token invalide (signature incorrecte, format, etc.)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token.') from exc

    # Vérifie si le token a été révoqué (ex: logout)
    if auth_service.is_token_revoked(db, payload.get('jti')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Session expired or invalid token.')

    # Récupère l'utilisateur à partir de l'id (sub = subject dans JWT)
    user = auth_service.get_user_by_id(db, str(payload.get('sub')))
    if not user:
        # Si utilisateur introuvable → session invalide
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Session expired or invalid token.')

    # Convertit l'utilisateur en objet UserInfo (schéma simplifié)
    return auth_service.to_user_info(user)


def get_current_user(user: Optional[UserInfo] = Depends(get_optional_current_user)) -> UserInfo:
    # Si aucun utilisateur (pas connecté)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required.')
    
    # Retourne l'utilisateur connecté
    return user


def get_admin_user(user: UserInfo = Depends(get_current_user)) -> UserInfo:
    # Vérifie si l'utilisateur a le rôle admin
    if user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin access required.')
    
    # Retourne l'utilisateur admin
    return user