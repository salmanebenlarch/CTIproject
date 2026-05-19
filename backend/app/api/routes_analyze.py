# Import des outils FastAPI pour créer les routes et gérer les fichiers
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
# Session base de données
from sqlalchemy.orm import Session

# Dépendances (DB + utilisateur optionnel)
from app.api.dependencies import get_db, get_optional_current_user
# Configuration globale (ex: taille max fichier)
from app.core.config import get_settings
# Schémas de requêtes et réponses pour les analyses
from app.schemas.analysis import AnalysisResult, IndicatorAnalyzeRequest, UrlAnalyzeRequest
# Schéma utilisateur
from app.schemas.auth import UserInfo
# Service pour enregistrer l’historique des analyses
from app.services.history import history_service
# Fonctions pour normaliser les réponses API (VirusTotal)
from app.services.normalizers import normalize_analysis_response, normalize_object_response
# Client VirusTotal + gestion des erreurs
from app.services.vt_client import VTClient, VTClientError
# Outils pour détecter le type d’indicateur (IP, URL, hash...)
from app.utils.indicators import classify_indicator, normalize_input

# Création du routeur avec préfixe /api/analyze
router = APIRouter(prefix='/api/analyze', tags=['analysis'])

# Initialisation du client VirusTotal
vt_client = VTClient()


# Fonction interne pour enregistrer le résultat en base
def _record_result(db: Session, result: AnalysisResult, user: UserInfo | None) -> AnalysisResult:
    # Ajoute l’analyse dans l’historique avec username si connecté
    history_service.add(db, result, username=user.username if user else None)
    return result


# Endpoint pour analyser une URL
@router.post('/url', response_model=AnalysisResult)
async def analyze_url(
    # Données envoyées (URL)
    payload: UrlAnalyzeRequest,
    # Utilisateur optionnel (connecté ou non)
    user: UserInfo | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> AnalysisResult:
    url_value = str(payload.url)

    try:
        # Envoie l’URL à VirusTotal pour scan
        submit_payload = await vt_client.scan_url(url_value)
        # Récupère l’id de l’analyse
        analysis_id = submit_payload['data']['id']
        # Attend le résultat de l’analyse
        analysis_payload = await vt_client.poll_analysis(analysis_id)
        # Normalise la réponse pour ton format interne
        result = normalize_analysis_response(analysis_payload, input_value=url_value, indicator_type='url')
        # Sauvegarde en base et retourne le résultat
        return _record_result(db, result, user)

    except VTClientError as exc:
        # Erreur côté VirusTotal
        raise HTTPException(status_code=502, detail=str(exc)) from exc


# Endpoint pour analyser un fichier
@router.post('/file', response_model=AnalysisResult)
async def analyze_file(
    # Fichier uploadé
    file: UploadFile = File(...),
    user: UserInfo | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> AnalysisResult:

    # Récupère la config (ex: taille max autorisée)
    settings = get_settings()
    # Lit le contenu du fichier
    content = await file.read()
    # Convertit la limite en bytes
    max_bytes = settings.max_file_size_mb * 1024 * 1024

    # Vérifications de base
    if not file.filename:
        raise HTTPException(status_code=400, detail='Filename is required.')
    if not content:
        raise HTTPException(status_code=400, detail='Empty file uploads are not allowed.')
    # Limite VirusTotal (650 MB)
    if len(content) > 650 * 1024 * 1024:
        raise HTTPException(status_code=400, detail='VirusTotal does not accept files larger than 650MB.')

    try:
        # Si fichier petit → upload normal
        if len(content) <= max_bytes:
            submit_payload = await vt_client.upload_file(file.filename, content)
        else:
            # Sinon → upload spécial (large file)
            submit_payload = await vt_client.upload_large_file(file.filename, content)

        # Récupère l’id d’analyse
        analysis_id = submit_payload['data']['id']
        # Récupère le résultat
        analysis_payload = await vt_client.poll_analysis(analysis_id)

        # Normalisation du résultat
        result = normalize_analysis_response(
            analysis_payload,
            input_value=file.filename,
            indicator_type='file',
            # Données fallback si API ne retourne pas tout
            fallback_metadata={'file_name': file.filename, 'file_size': len(content)},
        )

        # Ajout manuel des métadonnées fichier
        result.metadata.file_name = file.filename
        result.metadata.file_size = len(content)

        # Sauvegarde et retour
        return _record_result(db, result, user)

    except VTClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


# Endpoint générique pour analyser n’importe quel indicateur (URL, IP, domain, hash)
@router.post('/indicator', response_model=AnalysisResult)
async def analyze_indicator(
    payload: IndicatorAnalyzeRequest,
    user: UserInfo | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> AnalysisResult:

    # Nettoie/normalise la valeur (trim, format...)
    value = normalize_input(payload.value)

    try:
        # Détecte le type (url, ip, domain, hash)
        kind = classify_indicator(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        # Si URL → scan comme une URL
        if kind == 'url':
            submit_payload = await vt_client.scan_url(value)
            analysis_id = submit_payload['data']['id']
            analysis_payload = await vt_client.poll_analysis(analysis_id)
            result = normalize_analysis_response(analysis_payload, input_value=value, indicator_type='url')
            return _record_result(db, result, user)

        # Si IP → récupérer rapport
        if kind == 'ip':
            object_payload = await vt_client.get_ip_report(value)
            result = normalize_object_response(object_payload, input_value=value, indicator_type='ip')
            return _record_result(db, result, user)

        # Si domaine → récupérer rapport
        if kind == 'domain':
            object_payload = await vt_client.get_domain_report(value)
            result = normalize_object_response(object_payload, input_value=value, indicator_type='domain')
            return _record_result(db, result, user)

        # Si hash → récupérer rapport fichier
        if kind == 'hash':
            object_payload = await vt_client.get_file_report(value)
            result = normalize_object_response(object_payload, input_value=value, indicator_type='hash')
            return _record_result(db, result, user)

    except VTClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    # Si type non supporté
    raise HTTPException(status_code=400, detail='Unsupported indicator type.')