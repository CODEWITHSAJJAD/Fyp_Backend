from flask import jsonify, request
from Services.ActivitySuggestionService import ActivitySuggestionService
from Services.NotificationService import NotificationService
from Services.WeatherService import get_weather
from Model.CultivationSessionModel import CultivationSessionModel
from Model.SuggestedActivityModel import SuggestedActivityModel
from Model.ActivityModel import ActivityModel
from Model.LandModel import LandModel
from db import db

class ActivitiesSuggestionsController:
    @staticmethod
    def seed_session():
        data = request.get_json(force=True) or {}
        session_id = data.get("session_id")
        if not session_id:
            return jsonify({"error": "session_id required"}), 400
        sowing_date = data.get("sowing_date")
        res, code = ActivitySuggestionService.seed_suggested_activities(session_id, sowing_date)
        return jsonify(res), code

    @staticmethod
    def get_suggested(session_id):
        """Get suggested activities with auto weather check and dynamic day count"""
        res, code = ActivitySuggestionService.get_suggested_activities(session_id)
        return jsonify(res), code

    @staticmethod
    def get_reminders(land_id):
        """Get upcoming activity reminders"""
        res, code = ActivitySuggestionService.get_reminders(land_id)
        return jsonify(res), code

    @staticmethod
    def perform():
        payload = request.get_json(force=True) or {}
        sa_id = payload.get("suggested_activity_id")
        if not sa_id:
            return jsonify({"error":"suggested_activity_id required"}), 400
        
        performed_date = payload.get("performed_date")
        res, code = ActivitySuggestionService.record_performed(sa_id, performed_date)
        return jsonify(res), code

    @staticmethod
    def skip():
        payload = request.get_json(force=True) or {}
        sa_id = payload.get("suggested_activity_id")
        if not sa_id:
            return jsonify({"error":"suggested_activity_id required"}), 400
        reason = payload.get("reason", "Manually skipped")
        res, code = ActivitySuggestionService.skip_activity(sa_id, reason)
        return jsonify(res), code

    @staticmethod
    def adjust_with_weather(session_id):
        res, code = ActivitySuggestionService.adjust_with_weather(session_id)
        return jsonify(res), code

    @staticmethod
    def get_weather(city_name):
        weather = get_weather(city_name)
        if weather.get("error"):
            return jsonify({"error": weather.get("description")}), 500
        return jsonify(weather), 200

    @staticmethod
    def get_notifications(farmer_id):
        res, code = NotificationService.get_notifications(farmer_id)
        return jsonify(res), code

    @staticmethod
    def mark_notification_read(notification_id):
        res, code = NotificationService.mark_as_read(notification_id)
        return jsonify(res), code

    @staticmethod
    def mark_all_notifications_read(farmer_id):
        res, code = NotificationService.mark_all_as_read(farmer_id)
        return jsonify(res), code