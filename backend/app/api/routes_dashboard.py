# Import des outils FastAPI pour créer les routes et gérer les dépendances
from fastapi import APIRouter, Depends
# Session base de données
from sqlalchemy.orm import Session

# Dépendances (DB + utilisateur optionnel)
from app.api.dependencies import get_db, get_optional_current_user
# Schéma utilisateur
from app.schemas.auth import UserInfo
# Schéma de réponse pour le dashboard
from app.schemas.dashboard import DashboardOverview
# Service pour gérer l’historique et générer les stats
from app.services.history import history_service

# Création du routeur avec préfixe /api/dashboard
router = APIRouter(prefix='/api/dashboard', tags=['dashboard'])


# Endpoint pour récupérer un aperçu du dashboard
@router.get('/overview', response_model=DashboardOverview)
def get_dashboard_overview(
    # Utilisateur optionnel (connecté ou non)
    user: UserInfo | None = Depends(get_optional_current_user),
    # Injection de la base de données
    db: Session = Depends(get_db),
) -> DashboardOverview:

    # Appel du service pour générer les statistiques du dashboard
    # is_admin = True si l'utilisateur existe ET son rôle est admin
    return history_service.overview(db, is_admin=bool(user and user.role == 'admin'))