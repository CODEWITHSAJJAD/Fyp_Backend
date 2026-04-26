from datetime import date, timedelta
from flask import jsonify
from Model.SuggestedActivityModel import SuggestedActivityModel
from Model.CultivationSessionModel import CultivationSessionModel
from Model.LandModel import LandModel
from Model.CityModel import CityModel
from Model.CropModel import CropModel
from db import db

class DashboardController:
    @staticmethod
    def upcoming_by_crop_and_region(region: str = None, days: int = 7):
        # Build base query for pending activities in the upcoming window
        q = (
            db.session.query(
                SuggestedActivityModel.suggested_date,
                SuggestedActivityModel.activity_id,
                CropModel.crop_name.label('crop_name'),
                LandModel.land_name.label('land_name'),
            )
            .join(CultivationSessionModel, SuggestedActivityModel.cultivation_session_id == CultivationSessionModel.cultivation_session_id)
            .join(CropModel, CultivationSessionModel.crop_id == CropModel.crop_id)
            .join(LandModel, CultivationSessionModel.land_id == LandModel.land_id)
        )
        today = date.today()
        future = today + timedelta(days=days)
        q = q.filter(SuggestedActivityModel.status == 'pending')
        q = q.filter(SuggestedActivityModel.suggested_date >= today, SuggestedActivityModel.suggested_date <= future)
        if region:
            q = q.join(CityModel, LandModel.city_id == CityModel.city_id).filter(CityModel.city_name.ilike(f"%{region}%"))
        rows = q.all()
        summary = {}
        for r in rows:
            crop = r.crop_name or 'Unknown'
            summary[crop] = summary.get(crop, 0) + 1
        result = [{"crop": c, "upcoming_count": cnt} for c, cnt in summary.items()]
        return jsonify({"region": region or "All", "days": days, "summary": result}) , 200
