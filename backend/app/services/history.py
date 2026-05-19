from collections import Counter
from datetime import UTC, datetime, timedelta

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.db.models import AnalysisRecord as AnalysisRecordModel
from app.db.models import AnalysisStatsRecord, User
from app.schemas.analysis import AnalysisRecord, AnalysisResult
from app.schemas.dashboard import CountPoint, DashboardOverview, QuickLink


class AnalysisHistoryService:
    def add(self, db: Session, result: AnalysisResult, username: str | None = None) -> AnalysisRecord:
        user = db.scalar(select(User).where(User.username == username)) if username else None
        record = AnalysisRecordModel(
            input_value=result.input_value,
            indicator_type=result.indicator_type,
            verdict=result.verdict,
            summary=result.summary,
            raw_status=result.raw_status,
            username_snapshot=username,
            user_id=user.id if user else None,
        )
        record.stats = AnalysisStatsRecord(
            malicious_count=result.detection_stats.malicious,
            suspicious_count=result.detection_stats.suspicious,
            harmless_count=result.detection_stats.harmless,
            undetected_count=result.detection_stats.undetected,
            timeout_count=result.detection_stats.timeout,
            failure_count=result.detection_stats.failure,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return self._to_schema(record)

    def list_recent(self, db: Session, limit: int = 20, username: str | None = None) -> list[AnalysisRecord]:
        stmt = select(AnalysisRecordModel).order_by(desc(AnalysisRecordModel.created_at)).limit(limit)
        if username:
            stmt = (
                select(AnalysisRecordModel)
                .where(AnalysisRecordModel.username_snapshot == username)
                .order_by(desc(AnalysisRecordModel.created_at))
                .limit(limit)
            )
        records = db.scalars(stmt).all()
        return [self._to_schema(record) for record in records]

    def overview(self, db: Session, is_admin: bool = False) -> DashboardOverview:
        total_analyses = db.scalar(select(func.count(AnalysisRecordModel.id))) or 0
        verdict_rows = db.execute(
            select(AnalysisRecordModel.verdict, func.count(AnalysisRecordModel.id)).group_by(AnalysisRecordModel.verdict)
        ).all()
        verdicts = Counter({verdict: count for verdict, count in verdict_rows})
        type_rows = db.execute(
            select(AnalysisRecordModel.indicator_type, func.count(AnalysisRecordModel.id)).group_by(
                AnalysisRecordModel.indicator_type
            )
        ).all()
        by_type = Counter({item_type: count for item_type, count in type_rows})
        recent = self.list_recent(db, 8)

        records = db.scalars(
            select(AnalysisRecordModel)
            .options(selectinload(AnalysisRecordModel.stats))
            .order_by(AnalysisRecordModel.created_at.asc())
        ).all()

        quick_links = [
            QuickLink(label='Dashboard', tab='dashboard', description='SOC-style overview of recent activity.'),
            QuickLink(label='News', tab='news', description='Latest Hacker News headlines for analyst awareness.'),
            QuickLink(label='Pwned?', tab='hibp', description='Check whether an email appears in known breaches.'),
            QuickLink(label='Analyze URL', tab='url', description='Run a fresh URL check via VirusTotal.'),
            QuickLink(label='Analyze Indicator', tab='indicator', description='Search IPs, domains, and hashes.'),
        ]
        if is_admin:
            quick_links.append(
                QuickLink(label='Admin', tab='admin', description='Manage runtime options, users, and view all analyses.')
            )

        return DashboardOverview(
            total_analyses=total_analyses,
            suspicious_count=verdicts.get('suspicious', 0),
            not_suspicious_count=verdicts.get('not_suspicious', 0),
            unknown_count=verdicts.get('unknown', 0),
            analyses_by_type=dict(by_type),
            analyses_over_time_day=self._analyses_over_time(records, mode='day', periods=14),
            analyses_over_time_week=self._analyses_over_time(records, mode='week', periods=10),
            verdict_distribution=self._verdict_distribution(records),
            recent_analyses=recent,
            quick_links=quick_links,
        )

    def _verdict_distribution(self, records: list[AnalysisRecordModel]) -> list[CountPoint]:
        distribution = Counter({'malicious': 0, 'suspicious': 0, 'harmless': 0, 'unknown': 0})
        for record in records:
            stats = record.stats
            if stats and stats.malicious_count > 0:
                distribution['malicious'] += 1
            elif stats and stats.suspicious_count > 0:
                distribution['suspicious'] += 1
            elif record.verdict == 'not_suspicious':
                distribution['harmless'] += 1
            else:
                distribution['unknown'] += 1
        return [
            CountPoint(label='malicious', count=distribution['malicious']),
            CountPoint(label='suspicious', count=distribution['suspicious']),
            CountPoint(label='harmless', count=distribution['harmless']),
            CountPoint(label='unknown', count=distribution['unknown']),
        ]

    def _analyses_over_time(
        self,
        records: list[AnalysisRecordModel],
        *,
        mode: str,
        periods: int,
    ) -> list[CountPoint]:
        if periods <= 0:
            return []

        now = datetime.now(UTC)
        counts = Counter()
        if mode == 'day':
            start_date = now.date() - timedelta(days=periods - 1)
            for record in records:
                created = self._normalize_datetime(record.created_at)
                if created.date() >= start_date:
                    counts[created.date().isoformat()] += 1
            labels = [(start_date + timedelta(days=index)).isoformat() for index in range(periods)]
        else:
            current_week_start = (now - timedelta(days=now.weekday())).date()
            start_week = current_week_start - timedelta(weeks=periods - 1)
            for record in records:
                created = self._normalize_datetime(record.created_at)
                week_start = (created - timedelta(days=created.weekday())).date()
                if week_start >= start_week:
                    counts[week_start.isoformat()] += 1
            labels = [(start_week + timedelta(weeks=index)).isoformat() for index in range(periods)]

        return [CountPoint(label=label, count=counts.get(label, 0)) for label in labels]

    @staticmethod
    def _normalize_datetime(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    @staticmethod
    def _to_schema(record: AnalysisRecordModel) -> AnalysisRecord:
        return AnalysisRecord(
            id=record.id,
            input_value=record.input_value,
            indicator_type=record.indicator_type,
            verdict=record.verdict,
            username=record.username_snapshot,
            created_at=record.created_at,
            raw_status=record.raw_status,
        )


history_service = AnalysisHistoryService()
