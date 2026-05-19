from app.schemas.analysis import AnalysisMetadata, DetectionStat


# Fonction qui détermine le verdict d’un indicateur à partir des statistiques de détection
def compute_verdict(stats: DetectionStat, metadata: AnalysisMetadata) -> tuple[str, str]:
    # Nombre de moteurs ayant détecté comme malveillant
    malicious = stats.malicious

    # Nombre de moteurs ayant détecté comme suspect
    suspicious = stats.suspicious

    # Nombre de moteurs ayant détecté comme sain
    harmless = stats.harmless

    # Nombre de moteurs n’ayant rien détecté
    undetected = stats.undetected

    # Score de réputation communautaire (peut être négatif ou positif)
    reputation = metadata.reputation or 0

    # Si au moins un moteur détecte comme malveillant → verdict suspect
    if malicious > 0:
        return 'suspicious', f'{malicious} engine(s) flagged this indicator as malicious.'

    # Si au moins 2 moteurs détectent comme suspects → verdict suspect
    if suspicious >= 2:
        return 'suspicious', f'{suspicious} engine(s) marked this indicator as suspicious.'

    # Si un seul moteur suspect + réputation négative → suspicion renforcée
    if suspicious == 1 and reputation < 0:
        return 'suspicious', 'Single suspicious detection reinforced by negative community reputation.'

    # Si aucun moteur n’est suspect ou malveillant et que des résultats existent
    if malicious == 0 and suspicious == 0 and (harmless + undetected) > 0:
        # Cas où la réputation est très négative malgré des résultats propres
        if reputation < -10:
            return 'unknown', 'Scanner detections are clean, but community reputation is negative.'

        # Cas normal : aucun problème détecté
        return 'not_suspicious', 'No malicious or suspicious detections were reported.'

    # Cas par défaut : manque de données ou analyse incomplète
    return 'unknown', 'Insufficient or still-queued evidence from VirusTotal.'