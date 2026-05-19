# Import des outils FastAPI (routes, dépendances, erreurs HTTP)
from fastapi import APIRouter, Depends, HTTPException, status
# Pour récupérer le token Bearer depuis les headers
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
# Session base de données
from sqlalchemy.orm import Session

# Dépendance pour récupérer l'utilisateur connecté
from app.api.dependencies import get_current_user
# Fonction pour récupérer la DB
from app.db.session import get_db
# Schémas pour les requêtes/réponses liées à l'auth
from app.schemas.auth import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    LoginRequest,
    LoginResponse,
    UserInfo,
)
# Service métier pour l'authentification
from app.services.auth import auth_service

# Création du routeur avec préfixe /api/auth
router = APIRouter(prefix='/api/auth', tags=['auth'])

# Sécurité Bearer (token JWT dans Authorization header)
security = HTTPBearer(auto_error=False)


# Endpoint de login
@router.post('/login', response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    # Tente de connecter l'utilisateur avec username/password
    result = auth_service.login(db, payload.username, payload.password)

    # Si échec (mauvais identifiants)
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password.')

    # Sinon, retourne le token + infos utilisateur
    token, user = result
    return LoginResponse(access_token=token, user=user)


# Endpoint pour récupérer les infos de l'utilisateur connecté
@router.get('/me', response_model=UserInfo)
def me(user: UserInfo = Depends(get_current_user)) -> UserInfo:
    # get_current_user vérifie le token automatiquement
    return user


# Endpoint de logout
@router.post('/logout')
def logout(
    # Récupère le token depuis Authorization header
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> dict[str, str]:

    # Si token présent → on le révoque (blacklist)
    if credentials:
        auth_service.logout(db, credentials.credentials)

    # Réponse simple
    return {'status': 'logged_out'}


# Endpoint pour changer le mot de passe
@router.post('/change-password', response_model=ChangePasswordResponse)
def change_password(
    # Données: ancien mot de passe + nouveau
    payload: ChangePasswordRequest,
    # Utilisateur connecté (obligatoire)
    user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChangePasswordResponse:

    try:
        # Vérifie ancien mot de passe puis met à jour le nouveau
        auth_service.change_password(db, user.username, payload.current_password, payload.new_password)

    except ValueError as exc:
        # Erreur métier (ex: mauvais mot de passe actuel)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Réponse vide (succès)
    return ChangePasswordResponse()