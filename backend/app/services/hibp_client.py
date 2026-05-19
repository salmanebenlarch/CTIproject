# Module pour les expressions régulières (regex)
import re

# Fonction pour décoder les entités HTML (ex: &amp; -> &)
from html import unescape

# Client HTTP asynchrone pour effectuer des requêtes API
import httpx

# Schémas Pydantic utilisés pour structurer les réponses HIBP
from app.schemas.hibp import HibpBreach, HibpLookupResponse


# Exception personnalisée pour gérer les erreurs du client HIBP
class HIBPClientError(Exception):
    def __init__(self, message: str, *, status_code: int = 502) -> None:
        super().__init__(message)
        # Code HTTP associé à l’erreur
        self.status_code = status_code


# Regex utilisée pour supprimer les balises HTML (<tag>)
_TAG_RE = re.compile(r'<[^>]+>')


# Client principal pour interagir avec l’API XposedOrNot (alternative à HIBP)
class HIBPClient:

    def __init__(self) -> None:
        # Timeout des requêtes HTTP (en secondes)
        self.timeout = 15

        # URL de base de l’API utilisée
        self.base_url = 'https://api.xposedornot.com/v1'

    # Fonction principale qui vérifie si un email est présent dans des breaches
    async def breached_account(self, email: str) -> HibpLookupResponse:
        # Nettoyage de l’email (suppression des espaces inutiles)
        email = email.strip()

        try:
            # Création d’un client HTTP asynchrone
            async with httpx.AsyncClient(timeout=self.timeout) as client:

                # Requête GET vers l’API avec l’email
                response = await client.get(
                    f'{self.base_url}/check-email/{email}',
                    headers={'Accept': 'application/json'},
                )

        except httpx.HTTPError as exc:
            # Erreur réseau ou problème de connexion à l’API
            raise HIBPClientError('Unable to reach the XposedOrNot API right now.') from exc

        # Gestion des erreurs HTTP spécifiques

        # Rate limiting (trop de requêtes)
        if response.status_code == 429:
            raise HIBPClientError(
                'XposedOrNot rate limit exceeded. Please retry shortly.',
                status_code=429
            )

        # Format email invalide
        if response.status_code == 400:
            raise HIBPClientError(
                'XposedOrNot rejected the email address format.',
                status_code=400
            )

        # Autres erreurs serveur
        if response.status_code >= 400:
            raise HIBPClientError(
                'XposedOrNot returned an unexpected error.',
                status_code=502
            )

        # Parsing de la réponse JSON
        payload = response.json()

        # Cas où aucune breach n’est trouvée
        # Exemple : {"Error": "Not found"}
        if 'Error' in payload or payload.get('status') != 'success':
            return HibpLookupResponse(
                email=email,
                breached=False,
                breaches=[],
                message='All clear! No breaches were found for this email.',
            )

        # Format attendu :
        # {"breaches": [["Site1", "Site2", ...]], "status": "success"}
        raw = payload.get('breaches', [])

        # Les breaches sont dans une liste imbriquée → on prend le premier élément
        site_list = raw[0] if raw and isinstance(raw[0], list) else []

        # Conversion des noms de sites en objets HibpBreach
        breaches = [self._to_breach_model(name) for name in site_list]

        # Construction de la réponse finale
        return HibpLookupResponse(
            email=email,
            breached=bool(breaches),  # True si au moins une breach existe
            breaches=breaches,
            message=(
                f'Found {len(breaches)} breach(es) for this email.'
                if breaches
                else 'All clear! No breaches were found for this email.'
            ),
        )

    # Conversion d’un nom de breach en objet structuré HibpBreach
    @staticmethod
    def _to_breach_model(name: str) -> HibpBreach:
        return HibpBreach(
            name=name,
            title=name,
            domain=None,
            breach_date=None,
            added_date=None,
            modified_date=None,
            pwn_count=None,
            description='',
            data_classes=[],
            logo_path=None,
            is_verified=False,
            is_sensitive=False,
            is_spam_list=False,
            is_malware=False,
            is_stealer_log=False,
        )


# Instance globale du client (utilisée dans toute l’application)
hibp_client = HIBPClient()