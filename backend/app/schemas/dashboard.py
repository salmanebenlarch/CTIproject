# Types pour dictionnaires, listes et valeurs fixes
from typing import Dict, List, Literal

# BaseModel pour créer des modèles Pydantic (validation + serialization)
from pydantic import BaseModel, Field

# Schéma représentant un enregistrement d’analyse
from app.schemas.analysis import AnalysisRecord


# Modèle représentant un lien rapide (quick access) dans le dashboard
class QuickLink(BaseModel):
    # Texte affiché pour le lien
    label: str

    # Onglet cible dans l’application (valeurs limitées)
    # Ex: dashboard, news, hibp, file, url, indicator, admin
    tab: Literal['dashboard', 'news', 'hibp', 'file', 'url', 'indicator', 'admin']

    # Description du lien (aide utilisateur)
    description: str


# Modèle représentant un point de comptage (utilisé pour statistiques / graphiques)
class CountPoint(BaseModel):
    # Label (ex: jour, semaine, catégorie)
    label: str

    # Nombre associé à ce label
    count: int = 0


# Modèle principal pour le résumé du dashboard
class DashboardOverview(BaseModel):

    # Nombre total d’analyses effectuées
    total_analyses: int = 0

    # Nombre d’analyses avec verdict suspect
    suspicious_count: int = 0

    # Nombre d’analyses non suspectes
    not_suspicious_count: int = 0

    # Nombre d’analyses avec verdict inconnu
    unknown_count: int = 0

    # Répartition des analyses par type (url, file, ip, etc.)
    analyses_by_type: Dict[str, int] = Field(default_factory=dict)

    # Évolution des analyses par jour (liste de points temporels)
    analyses_over_time_day: List[CountPoint] = Field(default_factory=list)

    # Évolution des analyses par semaine
    analyses_over_time_week: List[CountPoint] = Field(default_factory=list)

    # Distribution des verdicts (suspicious / not_suspicious / unknown)
    verdict_distribution: List[CountPoint] = Field(default_factory=list)

    # Liste des analyses récentes (historique)
    recent_analyses: List[AnalysisRecord] = Field(default_factory=list)

    # Liens rapides pour navigation dans le dashboard
    quick_links: List[QuickLink] = Field(default_factory=list)