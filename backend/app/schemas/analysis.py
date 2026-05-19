# Import pour manipuler les dates/temps
from datetime import datetime

# Types pour annotations (Listes, dictionnaires, options, valeurs fixes)
from typing import Dict, List, Literal, Optional

# BaseModel pour créer des modèles de données validés avec Pydantic
from pydantic import BaseModel, Field, HttpUrl


# Type fixe (enum) représentant le verdict d’une analyse
# - suspicious : suspect
# - not_suspicious : non suspect
# - unknown : indéterminé
Verdict = Literal['suspicious', 'not_suspicious', 'unknown']

# Type fixe représentant le type d’indicateur analysé
# (fichier, URL, IP, domaine, hash)
IndicatorType = Literal['file', 'url', 'ip', 'domain', 'hash']


# Requête utilisée pour analyser une URL
class UrlAnalyzeRequest(BaseModel):
    # URL validée automatiquement (format URL)
    url: HttpUrl


# Requête utilisée pour analyser un indicateur générique
class IndicatorAnalyzeRequest(BaseModel):
    # Valeur brute à analyser (URL, IP, hash, etc.)
    # Contraintes : longueur minimale 1 et maximale 2048 caractères
    value: str = Field(min_length=1, max_length=2048)


# Statistiques des moteurs d’analyse (ex: VirusTotal engines)
class DetectionStat(BaseModel):
    # Nombre de résultats considérés comme sûrs
    harmless: int = 0

    # Nombre de résultats malveillants
    malicious: int = 0

    # Nombre de résultats suspects
    suspicious: int = 0

    # Nombre de moteurs qui n’ont rien détecté
    undetected: int = 0

    # Nombre de timeouts
    timeout: int = 0

    # Nombre d’échecs
    failure: int = 0

    # Timeout confirmés (clé avec tiret → alias utilisé)
    confirmed_timeout: int = Field(default=0, alias='confirmed-timeout')

    # Types non supportés par certains moteurs
    type_unsupported: int = Field(default=0, alias='type-unsupported')

    # Permet de remplir les champs en utilisant leurs alias (noms alternatifs)
    model_config = {'populate_by_name': True}


# Résultat d’un moteur d’analyse individuel
class EngineDetection(BaseModel):
    # Nom du moteur (ex: Kaspersky, McAfee, etc.)
    engine_name: str

    # Catégorie du résultat (optionnelle)
    category: Optional[str] = None

    # Résultat retourné par le moteur (malicious, clean, etc.)
    result: Optional[str] = None

    # Méthode utilisée par le moteur
    method: Optional[str] = None

    # Version du moteur
    engine_version: Optional[str] = None

    # Date de mise à jour du moteur
    engine_update: Optional[str] = None


# Métadonnées générales associées à une analyse
class AnalysisMetadata(BaseModel):
    # Source de l’analyse (ici VirusTotal par défaut)
    source: str = 'virustotal'

    # Type d’objet dans VirusTotal (file, url, etc.)
    vt_object_type: Optional[str] = None

    # Identifiant dans VirusTotal
    vt_id: Optional[str] = None

    # Lien permanent vers le rapport
    permalink: Optional[str] = None

    # Score de réputation
    reputation: Optional[int] = None

    # Catégories associées (clé → valeur)
    categories: Dict[str, str] = Field(default_factory=dict)

    # Tags associés à l’analyse
    tags: List[str] = Field(default_factory=list)

    # Votes des utilisateurs (ex: malicious / harmless)
    total_votes: Dict[str, int] = Field(default_factory=dict)

    # Titre de la ressource analysée
    title: Optional[str] = None

    # Dernière URL finale (après redirections)
    last_final_url: Optional[str] = None

    # Code HTTP retourné
    http_status: Optional[int] = None

    # Nom du fichier analysé (si applicable)
    file_name: Optional[str] = None

    # Taille du fichier
    file_size: Optional[int] = None

    # Description du type
    type_description: Optional[str] = None

    # Tag du type
    type_tag: Optional[str] = None

    # Nom de menace populaire détectée
    popular_threat_name: Optional[str] = None

    # Catégorie de la menace
    popular_threat_category: Optional[str] = None


# Résultat global d’une analyse
class AnalysisResult(BaseModel):
    # Valeur analysée (URL, IP, hash, etc.)
    input_value: str

    # Type de l’indicateur
    indicator_type: IndicatorType

    # Verdict global de l’analyse
    verdict: Verdict

    # Résumé textuel de l’analyse
    summary: str

    # Statistiques des détections
    detection_stats: DetectionStat

    # Liste des résultats des moteurs d’analyse
    engines: List[EngineDetection] = Field(default_factory=list)

    # Métadonnées associées
    metadata: AnalysisMetadata

    # Statut brut (optionnel, ex: queued, completed)
    raw_status: Optional[str] = None

    # Indique si l’analyse est en file d’attente
    queued: bool = False


# Enregistrement d’une analyse stockée (historique / base de données)
class AnalysisRecord(BaseModel):
    # Identifiant unique de l’analyse
    id: str

    # Valeur analysée
    input_value: str

    # Type d’indicateur
    indicator_type: IndicatorType

    # Verdict final
    verdict: Verdict

    # Nom d’utilisateur ayant lancé l’analyse
    username: Optional[str] = None

    # Date de création de l’analyse
    created_at: datetime

    # Statut brut (optionnel)
    raw_status: Optional[str] = None