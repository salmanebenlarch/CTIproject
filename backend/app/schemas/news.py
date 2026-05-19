# Types pour listes, valeurs optionnelles et valeurs fixes
from typing import List, Literal, Optional

# BaseModel pour définir des modèles de données avec validation via Pydantic
from pydantic import BaseModel, Field


# Type fixe représentant les catégories de news possibles
# Chaque news peut appartenir à une ou plusieurs catégories
NewsCategory = Literal[
    'all',        # toutes les catégories
    'security',   # cybersécurité
    'ai',         # intelligence artificielle
    'cloud',      # cloud computing
    'privacy',    # confidentialité / vie privée
    'devtools',   # outils de développement
    'startups'    # startups
]


# Modèle représentant une actualité (news story)
class NewsStory(BaseModel):
    # Identifiant unique de l’article
    id: int

    # Titre de l’article
    title: str

    # Auteur de l’article (optionnel)
    by: Optional[str] = None

    # URL externe de l’article (optionnel)
    url: Optional[str] = None

    # Score de popularité (votes / likes)
    score: int = 0

    # Nombre de commentaires
    descendants: int = 0

    # Timestamp de publication (format Unix)
    time: int

    # URL vers l’article sur Hacker News
    hn_url: str

    # Liste des catégories associées à l’article
    categories: List[NewsCategory] = Field(default_factory=list)