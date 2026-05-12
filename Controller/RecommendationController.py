from flask import jsonify, request
from copy import deepcopy
from Services.WeatherService import get_weather
from Services.DateUtils import get_month_number
from url import imageurl
from Model.LandModel import LandModel
from Model.CropModel import CropModel
from Model.CityModel import CityModel
from Model.FarmerModel import FarmerModel
from Model.CultivationSessionModel import CultivationSessionModel
from Model.NeighbourModel import NeighbourModel
from Model.ProvinceModel import ProvinceModel
from db import db
from datetime import datetime
import json
import os

class CropKnowledgeBase:
    _instance = None
    _kb = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CropKnowledgeBase, cls).__new__(cls)
            cls._instance._load_knowledge_base()
        return cls._instance

    def _load_knowledge_base(self):
        kb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "CropsInformation.json")
        try:
            with open(kb_path, 'r', encoding='utf-8') as f:
                self._kb = json.load(f)
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            self._kb = {}

    def get_crop_info(self, crop_name):
        return self._kb.get(crop_name, {})

    def is_crop_grown_in_region(self, crop_name, province_id, city_id):
        crop_info = self._kb.get(crop_name, {})
        
        suitable_provinces = crop_info.get("suitable_provinces", [])
        suitable_cities = crop_info.get("suitable_cities", [])
        
        if city_id in suitable_cities:
            return True
        
        if province_id in suitable_provinces:
            return True
        
        return False

kb = CropKnowledgeBase()

class RecommendationController:

    @staticmethod
    def _get_suggested_actions(crop_name: str) -> list:
        actions = {
            "Wheat": ["Prepare seedbed finely", "Sow early November for best yield", "Apply first irrigation at CRI stage (21 days)."],
            "Barley": ["Sow in mid-November", "Requires less water; good for late sowing.", "First irrigation at 25-30 days."],
            "Gram": ["Treat seeds with Rhizobium before sowing.", "Avoid excess irrigation.", "Pinch terminal shoots at 35-40 days for branching."],
            "Mustard": ["Thinning is essential at 20 days.", "Apply first irrigation at flowering stage.", "Monitor for Aphids attacks."],
            "Beans": ["Provide staking for trailing varieties.", "Keep soil moist but avoid waterlogging.", "Harvest pods while tender."],
            "Potato": ["Use disease-free tubers.", "Earthing up should be done twice (25 and 45 days).", "Maintain continuous moisture during tuber formation."],
            "Onion": ["Transplant seedlings at 6-8 weeks.", "Stop irrigation 10-15 days before harvesting.", "Cure bulbs in shade after harvest."],
            "Garlic": ["Plant cloves 5-7 cm deep.", "Keep weed-free during early growth.", "Stop watering when tops begin to fall."],
            "Tomato": ["Stake plants to prevent fruit rot.", "Apply mulch to retain moisture.", "Watch out for fruit borer insects."],
            "Spinach": ["Requires rich nitrogen fertilizer.", "Can be harvested multiple times.", "Sow in successions for continuous supply."],
            "Cabbage": ["Transplant robust seedlings.", "Keep soil consistently moist.", "Check for Diamondback moth caterpillars."],
            "Cauliflower": ["Tie inner leaves over the curd (blanching) to keep it white.", "Requires high nitrogen.", "Watch for stem rot."],
            "Carrot": ["Deep ploughing is essential for root development.", "Thin out young seedlings.", "Avoid heavy manuring right before sowing."],
            "Cotton": ["Ensure deep ploughing.", "Monitor for bollworm from square formation stage.", "Stop irrigation after first picking."],
            "Sugarcane": ["Plant setts in deep trenches.", "Requires frequent and heavy irrigation.", "Earthing up prevents lodging."],
            "Rice": ["Ensure field is puddled properly.", "Maintain 2-3 inches of standing water.", "Apply nitrogen in three splits."],
            "Maize": ["Sow on ridges to avoid waterlogging.", "Apply urea at knee-high and tasseling stages.", "Susceptible to stem borer in early stage."],
            "Bajra": ["Highly drought-resistant.", "Sow with onset of monsoon.", "Susceptible to ergot disease in wet conditions."],
            "Groundnut": ["Ensure loose soil for peg penetration.", "Apply gypsum at flowering.", "Do not irrigate near maturity stage."],
            "Soybean": ["Inoculate seeds to boost nitrogen.", "Needs good drainage; sensitive to waterlogging.", "Control weeds in first 30 days."],
            "Sunflower": ["Needs well-drained soil.", "Place bee hives nearby to improve pollination.", "Harvest when back of head turns lemon yellow."],
            "Chilies": ["Transplant 4-6 week old seedlings.", "Sensitive to waterlogging.", "High potassium requirement for good fruit colour."],
            "Turmeric (Haldi)": ["Plant on ridges for good drainage.", "Requires heavy mulching.", "Long duration crop requiring regular moisture."],
            "Watermelon": ["Sow on raised beds.", "Stop irrigation a week before harvest for sugar accumulation.", "Protect from fruit fly."]
        }
        return actions.get(crop_name, [
            "Prepare soil with appropriate tillage.",
            "Apply basic fertilizers before sowing.",
            "Follow standard local agricultural practices for this crop."
        ])

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
        
        return current_season, season_name_str, current_month

    @staticmethod
    def get_recommendations(id):
        try:
            land_id = id
            
            farmer_data = db.session.query(FarmerModel.Prefered_Date, LandModel.land_id).join(
                FarmerModel, FarmerModel.farmer_id == LandModel.farmer_id
            ).filter(LandModel.land_id == land_id).first()
            
            prefered_date = farmer_data.Prefered_Date
            current_season, season_name_str, current_month = RecommendationController._get_season_from_preferred_date(prefered_date)
            
            land_city = db.session.query(LandModel.city_id, CityModel.city_name).join(
                CityModel, CityModel.city_id == LandModel.city_id
            ).filter(LandModel.land_id == land_id).first()
            
            if not land_city:
                return jsonify({"error": "City not found for this land"}), 404
            
            city_name = land_city.city_name
            city_id = land_city.city_id
            
            city_obj = CityModel.query.get(city_id)
            province_id = None
            province_name = None
            if city_obj and city_obj.province_rls:
                province_id = city_obj.province_rls.province_id
                province_name = city_obj.province_rls.province_name
            
            current_weather = get_weather(city_name)
            
            if not land_id:
                return jsonify({"error": "land_id is required in JSON body"}), 400
            
            land = LandModel.query.filter(LandModel.land_id == land_id).first()
            if not land:
                return jsonify({"error": "Land resource not found"}), 404
            
            last_session = CultivationSessionModel.query.filter(
                CultivationSessionModel.land_id == land.land_id,
                CultivationSessionModel.is_public == 1
            ).order_by(CultivationSessionModel.cultivation_session_id.desc()).first()

            last_crop_name = None
            if last_session and last_session.crop_rls:
                last_crop_name = last_session.crop_rls.crop_name
            
            farmer_profitable_crops = []
            farmer_unprofitable_crops = []
            all_farmer_sessions = CultivationSessionModel.query.filter(
                CultivationSessionModel.land_id == land.land_id,
                CultivationSessionModel.is_public == 1
            ).all()
            
            for session in all_farmer_sessions:
                if session.crop_rls:
                    crop_name = session.crop_rls.crop_name
                    if session.is_profit == 1 and crop_name not in farmer_profitable_crops:
                        farmer_profitable_crops.append(crop_name)
                    elif session.is_profit == 0 and crop_name not in farmer_unprofitable_crops:
                        farmer_unprofitable_crops.append(crop_name)
            
            from sqlalchemy import or_
            neighbors = NeighbourModel.query.filter(
                or_(
                    NeighbourModel.land_id == land.land_id,
                    NeighbourModel.neighbour_land_id == land.land_id
                ),
                NeighbourModel.status == 1
            ).all()
            
            neighbor_profitable_crops = []
            neighbor_crops = []
            
            for n in neighbors:
                if n.land_id == land.land_id:
                    neighbor_land_id = n.neighbour_land_id
                else:
                    neighbor_land_id = n.land_id
                
                n_sessions = CultivationSessionModel.query.filter(
                    CultivationSessionModel.land_id == neighbor_land_id,
                    CultivationSessionModel.is_public == 1
                ).order_by(CultivationSessionModel.cultivation_session_id.desc()).all()
                
                for n_session in n_sessions:
                    if n_session.crop_rls:
                        crop_name = n_session.crop_rls.crop_name
                        if crop_name not in neighbor_crops:
                            neighbor_crops.append(crop_name)
                        if n_session.is_profit == 1 and crop_name not in neighbor_profitable_crops:
                            neighbor_profitable_crops.append(crop_name)
                
                if len(neighbor_profitable_crops) >= 3:
                    break
            
            available_crops = CropModel.query.filter(CropModel.season_name == current_season).all()
            if not available_crops:
                return jsonify({"message": "No crops found for the current season in the database."}), 200
            
            recommendations = []

            for db_crop in available_crops:
                c_name = db_crop.crop_name
                reqs = kb.get_crop_info(c_name)
                
                score = 30
                rationale = []
                
                region_suitable = False
                if province_id is not None and city_id is not None:
                    region_suitable = kb.is_crop_grown_in_region(c_name, province_id, city_id)
                    if region_suitable:
                        score += 35
                        if province_name and city_name:
                            rationale.append(f"Region suitable: {c_name} grows well in {city_name}, {province_name}.")
                        else:
                            rationale.append(f"Region suitable: {c_name} is suitable for this region.")
                    else:
                        score -= 25
                        rationale.append(f"Region not suitable: {c_name} is not recommended for this region.")
                else:
                    score += 10
                    rationale.append("Region data not available, using general recommendations.")
                
                if not reqs:
                    score += 55
                    rationale.append("Standard crop available for this season.")
                else:
                    user_soil = land.soil_type.strip().lower() if land.soil_type else ""
                    if "loam" in user_soil and "loamy" not in user_soil:
                        user_soil_variants = [user_soil, user_soil.replace('loam', 'loamy')]
                    elif "loamy" in user_soil and "loam" not in user_soil:
                        user_soil_variants = [user_soil, user_soil.replace('loamy', 'loam')]
                    else:
                        user_soil_variants = [user_soil]
                    
                    soil_matched = False
                    for accepted_soil in reqs.get('soil', []):
                        if accepted_soil.lower() in user_soil_variants or any(variant in accepted_soil.lower() for variant in user_soil_variants):
                            soil_matched = True
                            break

                    if soil_matched:
                        score += 25
                        rationale.append(f"Ideal soil match ({land.soil_type}).")
                    else:
                        score -= 15
                        rationale.append(f"Sub-optimal soil ({land.soil_type}), may require amendments.")

                    water_src = land.source_of_water.strip().lower() if land.source_of_water else ""
                    req_water = reqs.get('water', 'Moderate')

                    if "rainfed" in water_src and req_water in ["High", "Very High"]:
                        score -= 20
                        rationale.append("Warning: Crop requires high water but source is primarily rainfed.")
                    elif any(w in water_src for w in ["canal", "both", "tube", "well"]) and req_water in ["High", "Very High", "Moderate"]:
                        score += 20
                        rationale.append(f"Sufficient water available ({land.source_of_water}).")
                    else:
                        score += 10
                        rationale.append("Water resources are adequate for this crop.")
                    
                    if c_name in neighbor_profitable_crops:
                        score += 25
                        rationale.append("Profitable in neighboring farms recently.")
                    
                    if c_name in farmer_profitable_crops:
                        score += 20
                        rationale.append(f"You have grown {c_name} profitably before.")
                    elif c_name in farmer_unprofitable_crops:
                        score -= 10
                        rationale.append(f"Warning: You had losses with {c_name} before.")
                    
                    if last_crop_name:
                        last_crop_info = kb.get_crop_info(last_crop_name)
                        if last_crop_info:
                            last_type = last_crop_info.get('type')
                            current_type = reqs.get('type')
                            if last_type in ["Cash", "Cereal"] and current_type == "Legume":
                                score += 15
                                rationale.append(f"Excellent rotation choice after {last_crop_name}; will restore soil nitrogen.")
                            elif last_crop_name == c_name:
                                score -= 10
                                rationale.append("Consecutive planting of the same crop may deplete nutrients and increase pest risks.")

                    if current_weather == "Expected Heavy Rain" and req_water == "Low":
                        score -= 10
                        rationale.append("Warning: Heavy rain expected, ensure good drainage.")

                confidence = max(0, min(score, 100))

                if confidence >= 70:
                    recommendations.append({
                        "id": db_crop.crop_id,
                        "Name": c_name,
                        "Image": imageurl + db_crop.crop_image,
                        "Season": "Rabi" if db_crop.season_name == 0 else "Kharif",
                        "confidence_score": confidence,
                        "rationale": " | ".join(rationale),
                        "suggested_actions": RecommendationController._get_suggested_actions(c_name),
                        "previous_crop": last_crop_name
                    })

            recommendations = sorted(recommendations, key=lambda x: x['confidence_score'], reverse=True)

            final_recommendations = recommendations[:4]

            return jsonify({
                "status": "success",
                "data": {
                    "land_profile": {
                        "soil_type": land.soil_type,
                        "water_source": land.source_of_water,
                        "previous_crop": last_crop_name,
                        "city_id": city_id,
                        "city_name": city_name,
                        "province_id": province_id,
                        "province_name": province_name
                    },
                    "environmental_context": {
                        "Season": season_name_str,
                        "month": current_month,
                        "weather": current_weather
                    },
                    "farmer_history": {
                        "profitable_crops": farmer_profitable_crops,
                        "unprofitable_crops": farmer_unprofitable_crops
                    },
                    "neighbor_insights": {
                        "profitable_crops": neighbor_profitable_crops,
                        "crops_grown": neighbor_crops
                    },
                    "recommendations": final_recommendations
                }
            }), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500