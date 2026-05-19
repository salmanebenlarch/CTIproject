# Import des outils FastAPI pour créer des routes, gérer les dépendances et les erreurs
from fastapi import APIRouter, Depends, HTTPException, status
# Session base de données avec SQLAlchemy
from sqlalchemy.orm import Session

# Dépendances personnalisées (auth admin + DB)
from app.api.dependencies import get_admin_user, get_db
# Schéma pour l'overview admin
from app.schemas.admin import AdminOverview
# Schéma pour les analyses
from app.schemas.analysis import AnalysisRecord
# Schémas liés à l'authentification et gestion utilisateurs
from app.schemas.auth import ApiKeyStatus, CreateUserRequest, UpdateApiKeyRequest, UpdateUserRoleRequest, UserInfo
# Services métier (authentification, historique, config runtime)
from app.services.auth import auth_service
from app.services.history import history_service
from app.services.runtime_config import runtime_config

# Création du routeur avec préfixe /api/admin
router = APIRouter(prefix='/api/admin', tags=['admin'])


# Endpoint pour obtenir une vue globale (dashboard admin)
@router.get('/overview', response_model=AdminOverview)
def admin_overview(
    # Vérifie que l'utilisateur est admin
    _: UserInfo = Depends(get_admin_user),
    # Injection DB
    db: Session = Depends(get_db),
) -> AdminOverview:
    return AdminOverview(
        # Etat de la clé API (ex: VirusTotal)
        api_key_status=runtime_config.status(),
        # Liste des utilisateurs
        users=auth_service.list_users(db),
        # Dernières analyses (max 200)
        analyses=history_service.list_recent(db, 200),
        # Nombre d’analyses par utilisateur
        analysis_counts_by_user=auth_service.analysis_count_by_user(db),
    )


# Endpoint pour récupérer tous les utilisateurs
@router.get('/users', response_model=list[UserInfo])
def list_users(
    _: UserInfo = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> list[UserInfo]:
    return auth_service.list_users(db)


# Endpoint pour créer un utilisateur
@router.post('/users', response_model=UserInfo, status_code=status.HTTP_201_CREATED)
def create_user(
    # Données envoyées (username, password, role...)
    payload: CreateUserRequest,
    _: UserInfo = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> UserInfo:
    try:
        return auth_service.create_user(db, payload)
    except ValueError as exc:
        # Gestion des erreurs métier (ex: user déjà existant)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# Endpoint pour supprimer un utilisateur
@router.delete('/users/{username}')
def delete_user(
    # Username à supprimer (dans l'URL)
    username: str,
    # Utilisateur actuel (admin)
    current_user: UserInfo = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    try:
        # Suppression avec vérification (ex: empêcher auto-suppression)
        auth_service.delete_user(db, username, current_user.username)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    
    # Réponse simple
    return {'status': 'deleted'}


# Endpoint pour modifier le rôle d’un utilisateur (user → admin ou inverse)
@router.put('/users/{username}/role', response_model=UserInfo)
def update_user_role(
    username: str,
    payload: UpdateUserRoleRequest,
    current_user: UserInfo = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> UserInfo:
    try:
        return auth_service.update_user_role(db, username, payload, current_user.username)
    except ValueError as exc:
        # Si utilisateur non trouvé → 404, sinon erreur classique → 400
        status_code = 404 if 'not found' in str(exc).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


# Endpoint pour récupérer les analyses d’un utilisateur spécifique
@router.get('/users/{username}/analyses', response_model=list[AnalysisRecord])
def list_user_analyses(
    username: str,
    _: UserInfo = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> list[AnalysisRecord]:
    # Filtrage par username
    return history_service.list_recent(db, 200, username=username)


# Endpoint pour récupérer toutes les analyses
@router.get('/analyses', response_model=list[AnalysisRecord])
def list_analyses(
    _: UserInfo = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> list[AnalysisRecord]:
    return history_service.list_recent(db, 200)


# Endpoint pour modifier la clé API (runtime, sans redéploiement)
@router.put('/api-key', response_model=ApiKeyStatus)
def update_runtime_api_key(payload: UpdateApiKeyRequest, _: UserInfo = Depends(get_admin_user)) -> ApiKeyStatus:
    # Mise à jour de la clé API en mémoire
    runtime_config.vt_api_key_override = payload.api_key.strip()
    return runtime_config.status()


# Endpoint pour supprimer/reset la clé API runtime
@router.delete('/api-key', response_model=ApiKeyStatus)
def clear_runtime_api_key(_: UserInfo = Depends(get_admin_user)) -> ApiKeyStatus:
    # Suppression de la clé
    runtime_config.vt_api_key_override = None
    return runtime_config.status()