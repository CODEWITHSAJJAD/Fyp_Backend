from flask import jsonify
from Services.WeatherService import WeatherService
from Model.CultivationSessionModel import CultivationSessionModel

class WeatherController:
    @staticmethod
    def get_weather(city: str = None, session_id: int = None):
        if not city and session_id:
            sess = CultivationSessionModel.query.filter_by(cultivation_session_id=session_id).first()
            if sess and getattr(sess, 'land_rls', None):
                land = sess.land_rls
                if land and getattr(land, 'city_rls', None):
                    city = land.city_rls.city_name
        if not city:
            return jsonify({"error": "city or session_id required"}), 400
        data = WeatherService.get_weather(city)
        return jsonify(data), 200
