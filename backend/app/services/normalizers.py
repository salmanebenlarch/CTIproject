from typing import Any, Dict, List

from app.schemas.analysis import AnalysisMetadata, AnalysisResult, DetectionStat, EngineDetection
from app.services.verdict import compute_verdict


def _normalize_stats(stats: Dict[str, Any]) -> DetectionStat:
    return DetectionStat.model_validate(stats or {})


def _normalize_engines(results: Dict[str, Any]) -> List[EngineDetection]:
    engines: List[EngineDetection] = []
    for engine_name, data in (results or {}).items():
        engines.append(
            EngineDetection(
                engine_name=data.get('engine_name') or engine_name,
                category=data.get('category'),
                result=data.get('result'),
                method=data.get('method'),
                engine_version=data.get('engine_version'),
                engine_update=data.get('engine_update'),
            )
        )
    return sorted(
        engines,
        key=lambda item: (
            0 if item.category in {'malicious', 'suspicious'} else 1,
            item.engine_name.lower(),
        ),
    )


def _popular_threat_name(attributes: Dict[str, Any]) -> str | None:
    popular = attributes.get('popular_threat_classification') or {}
    names = popular.get('popular_threat_name') or []
    if names:
        return names[0].get('value')
    return None


def _popular_threat_category(attributes: Dict[str, Any]) -> str | None:
    popular = attributes.get('popular_threat_classification') or {}
    categories = popular.get('popular_threat_category') or []
    if categories:
        return categories[0].get('value')
    return None


def normalize_object_response(payload: Dict[str, Any], *, input_value: str, indicator_type: str) -> AnalysisResult:
    data = payload.get('data', {})
    attributes = data.get('attributes', {})
    stats = _normalize_stats(attributes.get('last_analysis_stats', {}))
    engines = _normalize_engines(attributes.get('last_analysis_results', {}))

    metadata = AnalysisMetadata(
        vt_object_type=data.get('type'),
        vt_id=data.get('id'),
        permalink=data.get('links', {}).get('self'),
        reputation=attributes.get('reputation'),
        categories=attributes.get('categories') or {},
        tags=attributes.get('tags') or [],
        total_votes=attributes.get('total_votes') or {},
        title=attributes.get('title'),
        last_final_url=attributes.get('last_final_url'),
        http_status=attributes.get('last_http_response_code'),
        file_size=attributes.get('size'),
        type_description=attributes.get('type_description'),
        type_tag=attributes.get('type_tag'),
        popular_threat_name=_popular_threat_name(attributes),
        popular_threat_category=_popular_threat_category(attributes),
    )

    verdict, summary = compute_verdict(stats, metadata)

    return AnalysisResult(
        input_value=input_value,
        indicator_type=indicator_type,
        verdict=verdict,
        summary=summary,
        detection_stats=stats,
        engines=engines,
        metadata=metadata,
        raw_status=None,
        queued=False,
    )


def normalize_analysis_response(
    payload: Dict[str, Any],
    *,
    input_value: str,
    indicator_type: str,
    fallback_metadata: dict | None = None,
) -> AnalysisResult:
    data = payload.get('data', {})
    attributes = data.get('attributes', {})
    stats = _normalize_stats(attributes.get('stats', {}))
    engines = _normalize_engines(attributes.get('results', {}))

    metadata = AnalysisMetadata(**(fallback_metadata or {}), vt_object_type=data.get('type'), vt_id=data.get('id'))
    verdict, summary = compute_verdict(stats, metadata)
    status = attributes.get('status')
    queued = status in {'queued', 'in-progress'}
    if queued:
        verdict = 'unknown'
        summary = f'Analysis status: {status}. Poll again or retry shortly.'

    return AnalysisResult(
        input_value=input_value,
        indicator_type=indicator_type,
        verdict=verdict,
        summary=summary,
        detection_stats=stats,
        engines=engines,
        metadata=metadata,
        raw_status=status,
        queued=queued,
    )
