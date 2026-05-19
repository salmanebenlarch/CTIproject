# Import des outils FastAPI pour créer les routes et gérer les erreurs
from fastapi import APIRouter, HTTPException, Query
# Permet de retourner une réponse personnalisée (ex: image)
from fastapi.responses import Response

# Schémas pour les news (catégorie + structure d’un article)
from app.schemas.news import NewsCategory, NewsStory
# Client Hacker News + gestion des erreurs
from app.services.hn_client import HNClientError, hn_client

# Création du routeur avec préfixe /api/news
router = APIRouter(prefix='/api/news', tags=['news'])


# Endpoint pour récupérer les top news
@router.get('/top', response_model=list[NewsStory])
async def get_top_news(
    # Nombre d'articles à retourner (min 1, max 20, défaut 10)
    limit: int = Query(default=10, ge=1, le=20),
    # Catégorie (ex: all, tech, etc.)
    category: NewsCategory = Query(default='all'),
) -> list[NewsStory]:

    try:
        # Appel au client pour récupérer les top stories
        return await hn_client.get_top_stories(limit=limit, category=category)

    except HNClientError as exc:
        # Gestion des erreurs venant du client HN
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


# Endpoint pour récupérer l’image d’un article spécifique
@router.get('/{story_id}/image')
async def get_story_image(story_id: int) -> Response:

    try:
        # Récupère les bytes de l'image + son type (image/png, image/jpeg...)
        image_bytes, content_type = await hn_client.get_story_image(story_id)

    except HNClientError as exc:
        # Gestion des erreurs (ex: article non trouvé)
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    # Retourne l’image directement comme réponse HTTP
    return Response(
        content=image_bytes,
        media_type=content_type,
        # Cache côté navigateur pendant 30 minutes (1800 secondes)
        headers={'Cache-Control': 'public, max-age=1800'},
    )