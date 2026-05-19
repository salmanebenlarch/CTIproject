from pydantic import BaseModel
from typing import Optional, List

class AbuseReport(BaseModel):
    reporterId: Optional[int]
    categories: List[int]
    reporterCountryCode: Optional[str]
    reportedAt: Optional[str]
    comment: Optional[str]

class IPReputationResult(BaseModel):
    ipAddress: str
    isPublic: bool
    ipVersion: int
    isWhitelisted: Optional[bool]
    abuseConfidenceScore: int   # 0-100, le score clé
    countryCode: Optional[str]
    usageType: Optional[str]
    isp: Optional[str]
    domain: Optional[str]
    totalReports: int
    numDistinctUsers: int
    lastReportedAt: Optional[str]
    reports: Optional[List[AbuseReport]]