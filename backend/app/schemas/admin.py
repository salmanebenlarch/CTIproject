# Types génériques pour les listes et dictionnaires
from typing import Dict, List

# BaseModel de Pydantic pour définir des schémas de validation/serialization
from pydantic import BaseModel, Field

# Schéma représentant une analyse
from app.schemas.analysis import AnalysisRecord
# Schéma pour l’état de la clé API et les infos utilisateur
from app.schemas.auth import ApiKeyStatus, UserInfo


# Schéma utilisé pour l’endpoint admin overview (dashboard admin)
class AdminOverview(BaseModel):

    # Statut de la clé API (ex: active, missing, invalid)
    api_key_status: ApiKeyStatus

    # Liste des utilisateurs (par défaut liste vide)
    users: List[UserInfo] = Field(default_factory=list)

    # Liste des analyses récentes (par défaut liste vide)
    analyses: List[AnalysisRecord] = Field(default_factory=list)

    # Dictionnaire qui contient le nombre d’analyses par utilisateur
    # Exemple: {"admin": 10, "user1": 5}
    analysis_counts_by_user: Dict[str, int] = Field(default_factory=dict)