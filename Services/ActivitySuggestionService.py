from db import db
from Model.CultivationSessionModel import CultivationSessionModel
from Model.SuggestedActivityModel import SuggestedActivityModel
from Model.CropModel import CropModel
from Model.LandModel import LandModel
from Model.CityModel import CityModel
from Model.PerformActivityModel import PerformedActivityModel
from Services.CropActivityData import get_activities_for_crop, is_repeating_activity, get_activity_name_by_id
from Services.WeatherService import get_weather, is_weather_suitable_for_activity, get_weather_delay_days
from Services.NotificationService import NotificationService
from Services.DateUtils import (
    date_to_string, string_to_date, add_days_to_string, 
    get_current_date_string, get_current_datetime_string,
    days_until, days_since
)

class ActivitySuggestionService:
    @staticmethod
    def seed_suggested_activities(session_id, sowing_date_str):
        try:
            session = CultivationSessionModel.query.filter(CultivationSessionModel.cultivation_session_id==session_id).first()
            if not session:
                return {"error": "Session not found"}, 404
            
            crop = CropModel.query.filter(CropModel.crop_id==session.crop_id).first()
            if not crop:
                return {"error": "Crop not found"}, 404
            
            crop_activities = get_activities_for_crop(crop.crop_name)
            
            if sowing_date_str is None:
                existing_performed = PerformedActivityModel.query.filter(
                    PerformedActivityModel.cultivation_session_id==session_id,
                    PerformedActivityModel.Activity_id==2
                ).first()
                if existing_performed and existing_performed.activity_date:
                    sowing_date_str = existing_performed.activity_date
                else:
                    sowing_date_str = get_current_date_string()
            
            existing = SuggestedActivityModel.query.filter(SuggestedActivityModel.cultivation_session_id==session_id).count()
            if existing > 0:
                return {"error": "Activities already seeded"}, 400
            
            for act in crop_activities:
                activity_id = act.get("activity_id")
                days_from_sowing = act.get("days_from_sowing")
                suggested_date = add_days_to_string(sowing_date_str, days_from_sowing)
                priority = "high" if days_from_sowing < 0 else ("medium" if days_from_sowing >= 0 and days_from_sowing <= 20 else "low")
                
                sa = SuggestedActivityModel(
                    cultivation_session_id=session_id,
                    activity_id=activity_id,
                    days_from_sowing=days_from_sowing,
                    suggested_date=suggested_date,
                    priority=priority,
                    status="pending",
                    weather_delay_reason=None
                )
                db.session.add(sa)
            
            db.session.commit()
            return {"message": f"Seeded {len(crop_activities)} activities", "count": len(crop_activities)}, 201
        
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    @staticmethod
    def get_suggested_activities(session_id):
        try:
            session = CultivationSessionModel.query.filter(CultivationSessionModel.cultivation_session_id==session_id).first()
            if not session:
                return {"error": "Session not found"}, 404
            
            land = LandModel.query.filter(LandModel.land_id==session.land_id).first()
            city_name = None
            farmer_id = None
            if land:
                city = CityModel.query.filter(CityModel.city_id==land.city_id).first()
                city_name = city.city_name if city else None
                farmer_id = land.farmer_id
            
            weather = None
            if city_name:
                weather = get_weather(city_name)
            
            existing_count = SuggestedActivityModel.query.filter(
                SuggestedActivityModel.cultivation_session_id==session_id
            ).count()
            
            if existing_count == 0:
                ActivitySuggestionService.seed_suggested_activities(session_id, None)
            
            is_harvested = session.session_status and session.session_status == "Harvest"
            
            if is_harvested:
                activities = []
            else:
                activities = SuggestedActivityModel.query.filter(
                    SuggestedActivityModel.cultivation_session_id==session_id
                ).filter(
                    SuggestedActivityModel.status != "completed",
                    SuggestedActivityModel.status != "skipped"
                ).order_by(SuggestedActivityModel.days_from_sowing).all()
            
            result = []
            adjustments_made = []
            
            for a in activities:
                activity_name = get_activity_name_by_id(a.activity_id)
                suggested_date = a.suggested_date
                status = a.status
                reason = a.weather_delay_reason
                day_count = days_until(suggested_date)
                
                if weather and not weather.get("error") and status == "pending":
                    is_suitable, delay_reason = is_weather_suitable_for_activity(activity_name, weather)
                    if not is_suitable:
                        delay_days = get_weather_delay_days(activity_name, weather)
                        if delay_days > 0:
                            new_date = add_days_to_string(a.suggested_date, delay_days)
                            a.suggested_date = new_date
                            a.status = "postponed"
                            a.weather_delay_reason = delay_reason
                            db.session.commit()
                            
                            adjustments_made.append({
                                "activity_id": a.activity_id,
                                "activity_name": activity_name,
                                "reason": delay_reason,
                                "new_date": new_date
                            })
                            suggested_date = new_date
                            status = "postponed"
                            reason = delay_reason
                            day_count = days_until(new_date)
                
                result.append({
                    "suggested_activity_id": a.suggested_activity_id,
                    "activity_id": a.activity_id,
                    "activity_name": activity_name,
                    "days_from_sowing": a.days_from_sowing,
                    "day_count": day_count,
                    "suggested_date": suggested_date,
                    "priority": a.priority,
                    "status": status,
                    "weather_delay_reason": reason
                })
            
            if adjustments_made and farmer_id:
                notif_msg = f" Weather adjusted: " + ", ".join([f"{x['activity_name']} → {x['new_date']}" for x in adjustments_made])
                NotificationService.create_notification(
                    farmer_id=farmer_id,
                    notification_type="weather_adjustment",
                    title="Activity Schedule Updated",
                    message=notif_msg,
                    extra_data={"session_id": session_id, "adjustments": adjustments_made}
                )
            
            return {
                "session_id": session_id,
                "crop": session.crop_id,
                "session_status": session.session_status,
                "city": city_name,
                "weather": {
                    "condition": weather.get("condition") if weather else None,
                    "temperature": weather.get("temperature") if weather else None,
                    "description": weather.get("description") if weather else None
                } if weather and not weather.get("error") else None,
                "activities": result
            }, 200
        
        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def get_reminders(land_id):
        try:
            session = CultivationSessionModel.query.filter(CultivationSessionModel.land_id==land_id,CultivationSessionModel.session_status!="Harvest").first()
            if not session:
                return {"error": "Session not found"}, 404
            
            land = LandModel.query.filter(LandModel.land_id==session.land_id).first()
            city_name = None
            if land:
                city = CityModel.query.filter(CityModel.city_id==land.city_id).first()
                city_name = city.city_name if city else None
            
            weather = None
            if city_name:
                weather = get_weather(city_name)
            
            activities = SuggestedActivityModel.query.filter(
                SuggestedActivityModel.cultivation_session_id==session_id
            ).filter(
                SuggestedActivityModel.status == "pending"
            ).order_by(SuggestedActivityModel.suggested_date).all()
            
            reminders = []
            today = get_current_date_string()
            
            for a in activities:
                activity_name = get_activity_name_by_id(a.activity_id)
                suggested_date = a.suggested_date
                day_count = days_until(suggested_date)
                
                if weather and not weather.get("error"):
                    is_suitable, delay_reason = is_weather_suitable_for_activity(activity_name, weather)
                    if not is_suitable:
                        delay_days = get_weather_delay_days(activity_name, weather)
                        if delay_days > 0:
                            new_date = add_days_to_string(suggested_date, delay_days)
                            new_day_count = days_until(new_date)
                            reminders.append({
                                "suggested_activity_id": a.suggested_activity_id,
                                "activity_name": activity_name,
                                "original_date": suggested_date,
                                "suggested_date": new_date,
                                "day_count": new_day_count,
                                "status": "postponed",
                                "weather_note": delay_reason
                            })
                            continue
                
                reminders.append({
                    "suggested_activity_id": a.suggested_activity_id,
                    "activity_name": activity_name,
                    "suggested_date": suggested_date,
                    "day_count": day_count,
                    "status": "pending",
                    "weather_note": None
                })
            
            reminders.sort(key=lambda x: x["day_count"])
            
            return {
                "session_id": session.session_id,
                "city": city_name,
                "today": today,
                "weather": {
                    "condition": weather.get("condition") if weather else None,
                    "temperature": weather.get("temperature") if weather else None
                } if weather and not weather.get("error") else None,
                "reminders": reminders[:10]
            }, 200
        
        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def record_performed(suggested_activity_id, performed_date_str):
        try:
            sa = SuggestedActivityModel.query.filter_by(suggested_activity_id=suggested_activity_id).first()
            if not sa:
                return {"error": "Suggested activity not found"}, 404
            
            if performed_date_str is None:
                performed_date_str = get_current_date_string()
            
            session = CultivationSessionModel.query.filter(CultivationSessionModel.cultivation_session_id==sa.cultivation_session_id).first()
            farmer_id = None
            if session:
                land = LandModel.query.filter(LandModel.land_id==session.land_id).first()
                farmer_id = land.farmer_id if land else None
            
            activity_name = get_activity_name_by_id(sa.activity_id)
            
            existing = PerformedActivityModel.query.filter(
                PerformedActivityModel.cultivation_session_id==sa.cultivation_session_id,
                PerformedActivityModel.Activity_id==sa.activity_id
            ).first()
            
            if existing:
                existing.activity_date = performed_date_str
                existing.Activity_type = activity_name
            else:
                performed = PerformedActivityModel(
                    cultivation_session_id=sa.cultivation_session_id,
                    Activity_id=sa.activity_id,
                    activity_date=performed_date_str,
                    Activity_type=activity_name
                )
                db.session.add(performed)
            
            sa.status = "completed"
            db.session.commit()
            
            return {"status": "completed", "activity_id": sa.activity_id}, 200
        
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    @staticmethod
    def adjust_with_weather(session_id):
        try:
            session = CultivationSessionModel.query.filter(CultivationSessionModel.cultivation_session_id==session_id).first()
            if not session:
                return {"error": "Session not found"}, 404
            
            land = LandModel.query.filter(LandModel.land_id==session.land_id).first()
            city_name = None
            if land:
                city = CityModel.query.filter(CityModel.city_id==land.city_id).first()
                city_name = city.city_name if city else None
            
            if not city_name:
                return {"error": "City not found for land"}, 404
            
            weather = get_weather(city_name)
            if weather.get("error"):
                return {"error": weather.get("description")}, 500
            
            activities = SuggestedActivityModel.query.filter(
                SuggestedActivityModel.cultivation_session_id==session_id,
                SuggestedActivityModel.status=="pending"
            ).all()
            
            adjustments = []
            for a in activities:
                activity_name = get_activity_name_by_id(a.activity_id)
                is_suitable, delay_reason = is_weather_suitable_for_activity(activity_name, weather)
                
                if not is_suitable:
                    delay_days = get_weather_delay_days(activity_name, weather)
                    a.suggested_date = add_days_to_string(a.suggested_date, delay_days)
                    a.status = "postponed"
                    a.weather_delay_reason = delay_reason
                    adjustments.append({
                        "activity_id": a.activity_id,
                        "activity_name": activity_name,
                        "reason": delay_reason,
                        "new_date": a.suggested_date
                    })
            
            db.session.commit()
            
            return {
                "message": "Weather adjustments complete",
                "city": city_name,
                "weather": weather.get("condition"),
                "adjustments": adjustments
            }, 200
        
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    @staticmethod
    def check_activity_done(session_id, activity_id):
        performed = PerformedActivityModel.query.filter(
            PerformedActivityModel.cultivation_session_id==session_id,
            PerformedActivityModel.Activity_id==activity_id
        ).first()
        return performed is not None

    @staticmethod
    def skip_activity(suggested_activity_id, reason):
        try:
            sa = SuggestedActivityModel.query.filter(SuggestedActivityModel.suggested_activity_id==suggested_activity_id).first()
            if not sa:
                return {"error": "Not found"}, 404
            
            sa.status = "skipped"
            sa.weather_delay_reason = reason or "Manually skipped"
            db.session.commit()
            return {"status": "skipped"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500