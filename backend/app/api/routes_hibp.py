# Import des outils FastAPI pour créer les routes et gérer les erreurs
from fastapi import APIRouter, HTTPException, Query
# Validation d'email avec Pydantic
from pydantic import EmailStr

# Schéma de réponse pour HIBP (Have I Been Pwned)
from app.schemas.hibp import HibpLookupResponse
# Client HIBP + gestion des erreurs
from app.services.hibp_client import HIBPClientError, hibp_client

# Création du routeur avec préfixe /api/hibp
router = APIRouter(prefix='/api/hibp', tags=['hibp'])


# Endpoint pour vérifier si un email a été compromis (data breach)
@router.get('/breached-account', response_model=HibpLookupResponse)
async def get_breached_account(
    # Paramètre email dans l'URL (ex: ?email=test@gmail.com)
    email: EmailStr = Query(...)
) -> HibpLookupResponse:

    try:
        # Appel au service HIBP pour vérifier les fuites de données
        return await hibp_client.breached_account(str(email))

    except HIBPClientError as exc:
        # Gestion des erreurs venant de l'API HIBP (ex: rate limit, not found...)
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc