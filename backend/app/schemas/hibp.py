# Types pour listes et valeurs optionnelles
from typing import List, Optional

# BaseModel pour définir des modèles de données avec validation
from pydantic import BaseModel, EmailStr, Field


# Modèle de requête pour rechercher un email dans Have I Been Pwned (HIBP)
class HibpLookupRequest(BaseModel):
    # Email validé automatiquement au format email
    email: EmailStr


# Modèle représentant une fuite de données (breach)
class HibpBreach(BaseModel):
    # Nom interne de la breach
    name: str

    # Titre lisible de la breach
    title: str

    # Domaine associé à la breach (optionnel)
    domain: Optional[str] = None

    # Date de la fuite (optionnelle)
    breach_date: Optional[str] = None

    # Date d’ajout dans la base
    added_date: Optional[str] = None

    # Date de modification
    modified_date: Optional[str] = None

    # Nombre de comptes affectés
    pwn_count: Optional[int] = None

    # Description de la breach
    description: str = ''

    # Types de données compromises (emails, passwords, etc.)
    data_classes: List[str] = Field(default_factory=list)

    # Chemin du logo de la breach
    logo_path: Optional[str] = None

    # Indique si la breach est vérifiée
    is_verified: bool = False

    # Indique si les données sont sensibles
    is_sensitive: bool = False

    # Indique si la breach est liée à du spam
    is_spam_list: bool = False

    # Indique si elle contient des données liées à malware
    is_malware: bool = False

    # Indique si elle provient de logs de stealer (malware vol de données)
    is_stealer_log: bool = False


# Modèle de réponse pour une recherche HIBP
class HibpLookupResponse(BaseModel):
    # Email recherché
    email: EmailStr

    # Indique si l’email est présent dans des breaches
    breached: bool = False

    # Liste des breaches associées à l’email
    breaches: List[HibpBreach] = Field(default_factory=list)

    # Message informatif (ex: "found", "not found", etc.)
    message: str