"""Repository for Findings and longitudinal trends."""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import LabResult, Entity, Report


class FindingRepository:

    @staticmethod
    def get_lab_results(db: Session, report_internal_id: str) -> List[LabResult]:
        return (
            db.query(LabResult)
            .filter(LabResult.report_id == report_internal_id)
            .all()
        )

    @staticmethod
    def get_entities(db: Session, report_internal_id: str) -> List[Entity]:
        return (
            db.query(Entity)
            .filter(Entity.report_id == report_internal_id)
            .all()
        )

    @staticmethod
    def get_longitudinal_trends(db: Session, user_id: str, current_report_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Collects historical lab results for comparison across reports belonging to the user."""
        all_reports = (
            db.query(Report)
            .filter(Report.user_id == user_id, Report.processing_status.in_(["completed", "analyzed"]))
            .order_by(Report.created_at.asc())
            .all()
        )

        current_report = db.query(Report).filter(Report.report_id == current_report_id).first()
        if not current_report:
            return {}

        current_tests = {
            res.test_name
            for res in db.query(LabResult).filter(LabResult.report_id == current_report.id).all()
        }

        trends: Dict[str, List[Dict[str, Any]]] = {}
        for r in all_reports:
            results = (
                db.query(LabResult)
                .filter(LabResult.report_id == r.id, LabResult.test_name.in_(current_tests))
                .all()
            )
            for res in results:
                trends.setdefault(res.test_name, []).append({
                    "report_id": r.report_id,
                    "date": r.created_at.strftime("%Y-%m-%d"),
                    "value": res.value,
                    "unit": res.unit,
                    "status": res.status,
                })

        return trends
