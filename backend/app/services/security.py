import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from app.core.config import get_settings


# Exception levée lorsque le token JWT est expiré
class TokenExpiredError(Exception):
    pass


# Exception levée lorsque le token JWT est invalide
class TokenInvalidError(Exception):
    pass


# Retourne l'heure actuelle en UTC
def utcnow() -> datetime:
    return datetime.now(UTC)


# Hash un mot de passe en utilisant bcrypt
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


# Vérifie qu'un mot de passe correspond à son hash bcrypt
def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except ValueError:
        # Retourne False si le hash est invalide
        return False


# Crée un token JWT d'accès
def create_access_token(subject: str) -> str:
    settings = get_settings()
    now = utcnow()

    # Payload du token JWT
    payload = {
        'sub': subject,  # sujet (ex: username)
        'jti': str(uuid.uuid4()),  # identifiant unique du token
        'type': 'access',  # type de token
        'iat': now,  # date de création
        'exp': now + timedelta(minutes=settings.access_token_expire_minutes),  # expiration
    }

    # Encodage du token avec la clé secrète et l'algorithme configuré
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


# Décode et valide un token JWT
def decode_access_token(token: str, *, allow_expired: bool = False) -> dict[str, Any]:
    settings = get_settings()

    try:
        # Décodage du token avec vérification optionnelle de l'expiration
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={'verify_exp': not allow_expired},
        )

    except ExpiredSignatureError as exc:
        # Token expiré
        raise TokenExpiredError('Token expired.') from exc

    except InvalidTokenError as exc:
        # Token invalide (signature incorrecte, format invalide, etc.)
        raise TokenInvalidError('Invalid token.') from exc