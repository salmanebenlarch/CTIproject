import asyncio
import re
import time
from html import unescape
from typing import List
from urllib.parse import urljoin

import httpx

from app.core.config import get_settings
from app.schemas.news import NewsCategory, NewsStory

# Règles de catégorisation basées sur des mots-clés
CATEGORY_RULES: dict[str, tuple[str, ...]] = {
    'security': (
        'security', 'cve', 'exploit', 'malware', 'phishing', 'ransomware', 'vulnerability', 'zero-day', 'zeroday',
        'xss', 'auth', 'breach', 'incident', 'threat', 'sandbox', 'botnet', 'apt', 'supply chain', 'infosec',
        'encryption', 'firewall', 'virus', 'trojan', 'cyber',
    ),
    'ai': (
        'ai', 'artificial intelligence', 'llm', 'gpt', 'openai', 'anthropic', 'prompt', 'rag', 'agent', 'agents',
        'transformer', 'model', 'inference', 'genai', 'machine learning', 'ml',
    ),
    'cloud': (
        'aws', 'azure', 'gcp', 'cloud', 'kubernetes', 'k8s', 'docker', 'container', 'serverless', 'terraform',
    ),
    'privacy': (
        'privacy', 'tracking', 'surveillance', 'gdpr', 'data broker', 'metadata', 'anonymous', 'anonymity',
    ),
    'devtools': (
        'typescript', 'javascript', 'python', 'rust', 'go ', 'golang', 'react', 'database', 'sqlite', 'postgres',
        'compiler', 'framework', 'api', 'orm', 'cli', 'open source',
    ),
    'startups': (
        'startup', 'funding', 'yc', 'acquired', 'acquisition', 'founder', 'launch', 'series a', 'series b',
    ),
}

# Regex pour extraire l'image Open Graph (og:image)
OG_IMAGE_RE = re.compile(
    r'<meta[^>]+(?:property|name)=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
OG_IMAGE_RE_ALT = re.compile(
    r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']og:image["\']',
    re.IGNORECASE,
)


# Exception personnalisée pour gérer les erreurs du client Hacker News
class HNClientError(Exception):
    def __init__(self, message: str, *, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


class HNClient:
    def __init__(self) -> None:
        # URL de base de l'API Hacker News
        self.base_url = 'https://hacker-news.firebaseio.com/v0'
        # Timeout des requêtes HTTP
        self.timeout = 10

        # Cache des résultats des top stories (clé = (category, limit))
        self.cache: dict[tuple[str, int], tuple[float, list[NewsStory]]] = {}

        # Cache des items individuels (story data)
        self.item_cache: dict[int, tuple[float, dict]] = {}

        # Cache des URLs d'images Open Graph
        self.og_image_cache: dict[int, tuple[float, str | None]] = {}

        # Cache des images téléchargées (bytes + content-type)
        self.image_bytes_cache: dict[int, tuple[float, bytes, str]] = {}

    async def get_top_stories(self, limit: int = 10, category: NewsCategory = 'all') -> List[NewsStory]:
        # Clé de cache basée sur la catégorie et la limite
        cache_key = (category, limit)
        cached = self.cache.get(cache_key)

        # TTL du cache configuré dans les settings
        ttl = get_settings().news_cache_ttl_seconds

        # Retourne les données si elles sont encore valides en cache
        if cached and (time.time() - cached[0]) < ttl:
            return cached[1]

        try:
            # Client HTTP asynchrone
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:

                # Récupération des IDs des top stories
                ids_response = await client.get(f'{self.base_url}/topstories.json')

                # Gestion d'erreur HTTP
                if ids_response.status_code >= 400:
                    raise HNClientError(f'Failed to fetch top stories: {ids_response.text}')

                # Limite du nombre d'IDs selon la catégorie
                max_ids = 60 if category == 'all' else 100
                story_ids = ids_response.json()[:max_ids]

                # Récupération parallèle des détails de chaque story
                items = await asyncio.gather(
                    *(self.get_item(item_id, client=client) for item_id in story_ids)
                )

        except httpx.HTTPError as exc:
            # Erreur réseau globale
            raise HNClientError('Unable to reach Hacker News API at the moment.') from exc

        stories: List[NewsStory] = []

        # Transformation des items en objets NewsStory
        for item in items:
            # Filtrage des items invalides
            if not item or item.get('type') != 'story' or not item.get('title'):
                continue

            # Catégorisation de la story
            categories = self._categorize_story(item)

            # Filtrage par catégorie demandée
            if category != 'all' and category not in categories:
                continue

            # Construction de l'objet NewsStory
            stories.append(
                NewsStory(
                    id=item['id'],
                    title=item['title'],
                    by=item.get('by'),
                    url=item.get('url'),
                    score=item.get('score') or 0,
                    descendants=item.get('descendants') or 0,
                    time=item.get('time') or 0,
                    hn_url=f"https://news.ycombinator.com/item?id={item['id']}",
                    categories=categories,
                )
            )

            # Respect de la limite demandée
            if len(stories) >= limit:
                break

        # Mise en cache du résultat
        self.cache[cache_key] = (time.time(), stories)
        return stories

    async def get_item(self, item_id: int, *, client: httpx.AsyncClient | None = None) -> dict:
        # TTL pour le cache des items
        ttl = get_settings().news_cache_ttl_seconds

        # Vérifie si l'item est déjà en cache
        cached = self.item_cache.get(item_id)
        if cached and (time.time() - cached[0]) < ttl:
            return cached[1]

        owns_client = client is None

        # Si aucun client n'est fourni, on en crée un
        if owns_client:
            client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)

        assert client is not None

        try:
            # Requête vers l'API Hacker News pour récupérer un item
            response = await client.get(f'{self.base_url}/item/{item_id}.json')

            # En cas d'erreur HTTP, on retourne un dict vide
            if response.status_code >= 400:
                return {}

            item = response.json()

            # Mise en cache de l'item
            self.item_cache[item_id] = (time.time(), item)
            return item

        finally:
            # Fermeture du client si on l'a créé ici
            if owns_client:
                await client.aclose()

    async def get_story_image(self, story_id: int) -> tuple[bytes, str]:
        # TTL du cache des images
        ttl = get_settings().news_image_cache_ttl_seconds

        # Vérifie le cache des images
        cached_image = self.image_bytes_cache.get(story_id)
        if cached_image and (time.time() - cached_image[0]) < ttl:
            _, content, content_type = cached_image
            return content, content_type

        # Création d'un client HTTP
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            item = await self.get_item(story_id, client=client)

            # Vérifie que l'item existe
            if not item:
                raise HNClientError('Story not found.', status_code=404)

            article_url = item.get('url')

            # Vérifie que l'URL de l'article existe
            if not article_url:
                raise HNClientError('This Hacker News item does not have an article URL.', status_code=404)

            # Récupération de l'image Open Graph
            og_image_url = await self._get_og_image_url(story_id, article_url, client=client)

            if not og_image_url:
                raise HNClientError('No Open Graph image was found for this article.', status_code=404)

            try:
                # Téléchargement de l'image
                image_response = await client.get(og_image_url)
            except httpx.HTTPError as exc:
                raise HNClientError('Unable to fetch the article image right now.') from exc

            # Gestion des erreurs HTTP lors du téléchargement
            if image_response.status_code >= 400:
                raise HNClientError('Unable to fetch the article image right now.', status_code=404)

            # Type de contenu de l'image
            content_type = image_response.headers.get('content-type', 'image/jpeg')

            # Contenu binaire de l'image
            content = image_response.content

            # Mise en cache de l'image
            self.image_bytes_cache[story_id] = (time.time(), content, content_type)

            return content, content_type

    async def _get_og_image_url(self, story_id: int, article_url: str, *, client: httpx.AsyncClient) -> str | None:
        # TTL pour le cache des URLs d'images OG
        ttl = get_settings().news_image_cache_ttl_seconds

        # Vérifie le cache
        cached = self.og_image_cache.get(story_id)
        if cached and (time.time() - cached[0]) < ttl:
            return cached[1]

        try:
            # Récupération de la page HTML
            response = await client.get(article_url)
        except httpx.HTTPError:
            # En cas d'erreur, on met None en cache
            self.og_image_cache[story_id] = (time.time(), None)
            return None

        # Vérifie les erreurs HTTP
        if response.status_code >= 400:
            self.og_image_cache[story_id] = (time.time(), None)
            return None

        # Vérifie que le contenu est du HTML
        content_type = response.headers.get('content-type', '')
        if 'html' not in content_type.lower():
            self.og_image_cache[story_id] = (time.time(), None)
            return None

        # Limite la taille du HTML analysé
        html = response.text[:400_000]

        # Recherche de l'image Open Graph dans le HTML
        match = OG_IMAGE_RE.search(html) or OG_IMAGE_RE_ALT.search(html)

        # Construction de l'URL absolue de l'image
        image_url = urljoin(str(response.url), unescape(match.group(1)).strip()) if match else None

        # Mise en cache du résultat
        self.og_image_cache[story_id] = (time.time(), image_url)
        return image_url

    def _categorize_story(self, item: dict) -> list[NewsCategory]:
        # Concatène les champs pertinents pour l'analyse
        haystack = ' '.join(
            filter(
                None,
                [
                    str(item.get('title', '')).lower(),
                    str(item.get('url', '')).lower(),
                    str(item.get('text', '')).lower(),
                ],
            )
        )

        matches: list[NewsCategory] = []

        # Vérifie la présence de mots-clés pour chaque catégorie
        for category, keywords in CATEGORY_RULES.items():
            if any(keyword in haystack for keyword in keywords):
                matches.append(category)  # type: ignore[arg-type]

        return matches


# Instance globale du client Hacker News
hn_client = HNClient()