# Import des types pour définir des valeurs fixes et optionnelles
from typing import Literal, Optional

# BaseModel pour créer des modèles de validation avec Pydantic
from pydantic import BaseModel, Field


# Type fixe pour définir les rôles utilisateur
# admin : utilisateur avec privilèges élevés
# user : utilisateur standard
UserRole = Literal['admin', 'user']


# Modèle utilisé pour la requête de login
class LoginRequest(BaseModel):
    # Nom d'utilisateur (obligatoire, entre 1 et 100 caractères)
    username: str = Field(min_length=1, max_length=100)

    # Mot de passe (obligatoire, entre 1 et 200 caractères)
    password: str = Field(min_length=1, max_length=200)


# Modèle représentant les informations d’un utilisateur
class UserInfo(BaseModel):
    # Nom d'utilisateur
    username: str

    # Nom affiché (ex: prénom / pseudo)
    display_name: str

    # Rôle de l’utilisateur (admin ou user)
    role: UserRole


# Modèle de réponse après authentification réussie
class LoginResponse(BaseModel):
    # Token JWT ou access token
    access_token: str

    # Type de token (par défaut "bearer")
    token_type: str = 'bearer'

    # Informations sur l'utilisateur connecté
    user: UserInfo


# Modèle utilisé pour créer un nouvel utilisateur
class CreateUserRequest(BaseModel):
    # Username (minimum 3 caractères)
    username: str = Field(min_length=3, max_length=100)

    # Mot de passe (minimum 8 caractères)
    password: str = Field(min_length=8, max_length=200)

    # Nom affiché optionnel
    display_name: Optional[str] = Field(default=None, max_length=100)

    # Rôle de l’utilisateur (par défaut: user)
    role: UserRole = 'user'


# Requête pour changer le mot de passe
class ChangePasswordRequest(BaseModel):
    # Mot de passe actuel
    current_password: str = Field(min_length=1, max_length=200)

    # Nouveau mot de passe
    new_password: str = Field(min_length=8, max_length=200)


# Réponse après changement de mot de passe
class ChangePasswordResponse(BaseModel):
    # Statut simple indiquant que le changement a réussi
    status: str = 'password_changed'


# Requête pour modifier le rôle d’un utilisateur
class UpdateUserRoleRequest(BaseModel):
    # Nouveau rôle assigné
    role: UserRole


# Modèle représentant le statut de configuration de la clé API
class ApiKeyStatus(BaseModel):
    # Indique si une clé API est configurée
    configured: bool

    # Source de la clé API :
    # - environment : via variables d’environnement
    # - runtime_override : définie dynamiquement à l’exécution
    source: Literal['environment', 'runtime_override']

    # Clé API masquée (ex: ****1234) pour affichage sécurisé
    masked_key: Optional[str] = None


# Requête pour mettre à jour la clé API
class UpdateApiKeyRequest(BaseModel):
    # Nouvelle clé API fournie
    api_key: str = Field(min_length=1, max_length=200)