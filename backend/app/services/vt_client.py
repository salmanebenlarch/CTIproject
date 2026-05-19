import asyncio
import base64
from typing import Any, Dict, Optional

import httpx

from app.core.config import get_settings
from app.services.runtime_config import runtime_config


# Exception personnalisée pour gérer les erreurs liées à VirusTotal
class VTClientError(Exception):
    pass


class VTClient:
    def __init__(self) -> None:
        settings = get_settings()

        # URL de base de l’API VirusTotal
        self.base_url = settings.vt_base_url.rstrip('/')

        # Timeout des requêtes HTTP
        self.timeout = settings.request_timeout_seconds

        # Intervalle entre deux tentatives de polling
        self.poll_interval_seconds = settings.poll_interval_seconds

        # Nombre maximum de tentatives pour le polling
        self.poll_max_attempts = settings.poll_max_attempts

    # Construction des headers HTTP avec l’API key dynamique
    def _headers(self) -> Dict[str, str]:
        return {
            'x-apikey': runtime_config.current_vt_api_key(),  # clé API récupérée au runtime
            'accept': 'application/json',
        }

    # Méthode générique pour effectuer une requête HTTP vers VirusTotal
    async def _request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        url = f'{self.base_url}{path}'

        # Timeout personnalisable
        timeout = kwargs.pop('timeout', self.timeout)

        # Fusion des headers par défaut et des headers fournis
        request_headers = {**self._headers(), **kwargs.pop('headers', {})}

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(method, url, headers=request_headers, **kwargs)

        # Gestion des erreurs HTTP
        if response.status_code >= 400:
            try:
                payload = response.json()
            except Exception:
                # Si la réponse n’est pas en JSON
                payload = {'error': {'message': response.text}}

            # Extraction du message d’erreur
            message = payload.get('error', {}).get('message', 'VirusTotal request failed')

            raise VTClientError(f'{response.status_code}: {message}')

        return response.json()

    # Récupération du rapport d’un fichier via son hash
    async def get_file_report(self, file_hash: str) -> Dict[str, Any]:
        return await self._request('GET', f'/files/{file_hash}')

    # Récupération du rapport d’un domaine
    async def get_domain_report(self, domain: str) -> Dict[str, Any]:
        return await self._request('GET', f'/domains/{domain}')

    # Récupération du rapport d’une adresse IP
    async def get_ip_report(self, ip: str) -> Dict[str, Any]:
        return await self._request('GET', f'/ip_addresses/{ip}')

    # Récupération d’un rapport d’analyse d’URL via son ID encodé
    async def get_url_report_by_id(self, url_id: str) -> Dict[str, Any]:
        return await self._request('GET', f'/urls/{url_id}')

    # Soumission d’une URL pour analyse
    async def scan_url(self, url: str) -> Dict[str, Any]:
        data = {'url': url}
        return await self._request(
            'POST',
            '/urls',
            data=data,
            headers={'content-type': 'application/x-www-form-urlencoded'},
        )

    # Upload d’un fichier (petits fichiers)
    async def upload_file(self, filename: str, content: bytes) -> Dict[str, Any]:
        files = {'file': (filename, content)}
        return await self._request('POST', '/files', files=files)

    # Récupère une URL d’upload spéciale pour les fichiers volumineux
    async def get_large_file_upload_url(self) -> str:
        payload = await self._request('GET', '/files/upload_url')
        return payload['data']

    # Upload de fichiers volumineux via une URL dédiée
    async def upload_large_file(self, filename: str, content: bytes) -> Dict[str, Any]:
        upload_url = await self.get_large_file_upload_url()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                upload_url,
                headers=self._headers(),
                files={'file': (filename, content)},
            )

        # Gestion des erreurs
        if response.status_code >= 400:
            raise VTClientError(response.text)

        return response.json()

    # Récupération du statut d’une analyse
    async def get_analysis(self, analysis_id: str) -> Dict[str, Any]:
        return await self._request('GET', f'/analyses/{analysis_id}')

    # Polling pour attendre la fin d’une analyse
    async def poll_analysis(self, analysis_id: str) -> Dict[str, Any]:
        last_payload: Optional[Dict[str, Any]] = None

        # Boucle de polling avec nombre maximal de tentatives
        for _ in range(self.poll_max_attempts):
            payload = await self.get_analysis(analysis_id)
            last_payload = payload

            # Récupération du statut de l’analyse
            status = payload.get('data', {}).get('attributes', {}).get('status')

            # Si terminé → retour immédiat
            if status == 'completed':
                return payload

            # Attente avant la prochaine tentative
            await asyncio.sleep(self.poll_interval_seconds)

        # Retourne le dernier état connu si jamais terminé
        return last_payload or {}

    # Encode une URL en base64 URL-safe pour l’utiliser comme ID
    @staticmethod
    def build_url_id(url: str) -> str:
        return base64.urlsafe_b64encode(url.encode()).decode().strip('=')