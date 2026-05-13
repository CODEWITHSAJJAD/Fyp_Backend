from datetime import datetime

from Model.CropModel import CropModel
from db import db
from Model.CultivationSessionModel import CultivationSessionModel
from Model.SuggestedActivityModel import SuggestedActivityModel
from Model.LandModel import LandModel
from Model.CityModel import CityModel
from Model.FarmerModel import FarmerModel
from Model.PerformActivityModel import PerformedActivityModel
from Services.CropActivityData import get_activity_name_by_id
from Services.WeatherService import get_weather, is_weather_suitable_for_activity, get_weather_delay_days
from Services.ActivitySuggestionService import ActivitySuggestionService
from Services.DateUtils import (
     add_days_to_string,days_between, get_month_number,get_human_readable_period, get_year_number
)

class RemindersService:
    @staticmethod
    def get_reminders(land_id):
        try:
            session = CultivationSessionModel.query.filter(CultivationSessionModel.land_id == land_id,
                                                           CultivationSessionModel.session_status != "Harvest").first()
            if not session:
                return {"error": "Session not found"}, 404

            land = LandModel.query.filter(LandModel.land_id == session.land_id).first()
            city_name = None
            reference_date = None
            if land:
                city = CityModel.query.filter(CityModel.city_id == land.city_id).first()
                city_name = city.city_name if city else None
                reference_date = ActivitySuggestionService.get_reference_date_for_land(land.land_id)

            weather = None
            if city_name:
                weather = get_weather(city_name)

            activities = SuggestedActivityModel.query.filter(
                SuggestedActivityModel.cultivation_session_id == session.cultivation_session_id
            ).filter(
                SuggestedActivityModel.status == "pending"
            ).order_by(SuggestedActivityModel.suggested_date).all()

            reminders = []
            if not reference_date:
                return {"error": "Farmer preferred date not found"}, 404

            # Only include activities that are today or tomorrow (day_count <= 1)
            for a in activities:
                activity_name = get_activity_name_by_id(a.activity_id)
                suggested_date = a.suggested_date

                # Calculate day_count using days_between (supports both date formats)
                day_count = days_between(reference_date, suggested_date) if reference_date else 0

                # Only include if activity is today (day_count = 0) or tomorrow (day_count = 1)
                if day_count < 0:
                    continue

                if day_count > 1:
                    continue

                if weather and not weather.get("error"):
                    is_suitable, delay_reason = is_weather_suitable_for_activity(activity_name, weather)
                    if not is_suitable:
                        delay_days = get_weather_delay_days(activity_name, weather)
                        if delay_days > 0:
                            new_date = add_days_to_string(suggested_date, delay_days)
                            new_day_count = days_between(reference_date, new_date) if reference_date else 0

                            if new_day_count <= 1:
                                reminders.append({
                                    "suggested_activity_id": a.suggested_activity_id,
                                    "activity_name": activity_name,
                                    "original_date": suggested_date,
                                    "suggested_date": new_date,
                                    "when": get_human_readable_period(reference_date, suggested_date),
                                    "day_count": get_human_readable_period(reference_date, suggested_date),
                                    "status": "postponed",
                                    "weather_note": delay_reason
                                })
                            continue

                reminders.append({
                    "suggested_activity_id": a.suggested_activity_id,
                    "activity_name": activity_name,
                    "suggested_date": suggested_date,
                    "when": get_human_readable_period(reference_date, suggested_date),
                    "day_count": get_human_readable_period(reference_date, suggested_date),
                    "status": "pending",
                    "weather_note": None
                })

            reminders.sort(key=lambda x: days_between(reference_date,
                                                      x.get("suggested_date", reference_date)) if reference_date else 0)

            return {
                "session_id": session.cultivation_session_id,
                "city": city_name,
                "today": reference_date,
                "weather": {
                    "condition": weather.get("condition") if weather else None,
                    "temperature": weather.get("temperature") if weather else None
                } if weather and not weather.get("error") else None,
                "reminders": reminders[:3]
            }, 200

        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def _get_season_from_preferred_date(prefered_date):
        print(prefered_date)
        if not prefered_date:
            current_month = datetime.now().month
        else:
            current_month = get_month_number(prefered_date)

        if current_month is None:
            current_month = datetime.now().month
        print(current_month)
        if current_month >= 4 and current_month <= 9:
            current_season = 1
            season_name_str = "Kharif"
        else:
            current_season = 0
            season_name_str = "Rabi"

        return current_season
    @staticmethod
    def get_Disease_and_pest_Alerts(land_id):
        try:
            Farmer=db.session.query(FarmerModel.Prefered_Date,LandModel.land_id,FarmerModel.farmer_id).join(FarmerModel,FarmerModel.farmer_id==LandModel.farmer_id).filter(LandModel.land_id == land_id).first()
            farmer_date = Farmer.Prefered_Date
            farmer_date_year = get_year_number(farmer_date)
            performed_activity=PerformedActivityModel.query.filter(PerformedActivityModel.Activity_id==12).all()
            alerts=[]
            for p in performed_activity:
                performed_date=p.activity_date
                performed_date_year=get_year_number(performed_date)
                if performed_date_year == farmer_date_year:
                    performed_season=RemindersService._get_season_from_preferred_date(performed_date)
                    farmer_season=RemindersService._get_season_from_preferred_date(farmer_date)
                    if performed_season == farmer_season:
                        crop=db.session.query(CropModel.crop_name,CropModel.crop_id,CultivationSessionModel.crop_id,CultivationSessionModel.cultivation_session_id).join(CropModel,CropModel.crop_id==CultivationSessionModel.crop_id).filter(CultivationSessionModel.cultivation_session_id==p.cultivation_session_id).first()
                        alerts.append({
                            "alerts":p.Activity_type,
                            "crop":crop.crop_name
                        })
                    return alerts,200
                return {"error": "Alerts not found"},404
        except Exception as e:
            return {"error": str(e)}, 500