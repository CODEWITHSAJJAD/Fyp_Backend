from flask import jsonify, request
from copy import deepcopy
from Services.WeatherService import get_weather
from Model import CityModel
from url import imageurl
from Model.LandModel import LandModel
from Model.CropModel import CropModel
from Model.CityModel import CityModel
from Model.CultivationSessionModel import CultivationSessionModel
from Model.NeighbourModel import NeighbourModel
from db import db
from datetime import datetime

class RecommendationController:

    # Static knowledge base for crops 
    # Mapped roughly to the project's CropModel where season_name=0 is Rabi, season_name=1 is Kharif
    CROP_KNOWLEDGE_BASE = {
        # RABI CROPS (season_name=0)
        "Wheat": {"soil": ["Loamy", "Clay", "Alluvial", "Clay Loam"], "water": "Moderate", "season_name": 0, "type": "Cereal"},
        "Barley": {"soil": ["Sandy Loam", "Loamy", "Alluvial"], "water": "Low", "season_name": 0, "type": "Cereal"},
        "Gram": {"soil": ["Sandy", "Loamy", "Sandy Loam"], "water": "Low", "season_name": 0, "type": "Legume"},
        "Mustard": {"soil": ["Sandy", "Loamy"], "water": "Low", "season_name": 0, "type": "Oilseed"},
        "Beans": {"soil": ["Loamy", "Sandy Loam"], "water": "Moderate", "season_name": 0, "type": "Legume"},
        "Beets (Chakandar)": {"soil": ["Loamy", "Sandy Loam"], "water": "Moderate", "season_name": 0, "type": "Vegetable"},
        "Cabbage": {"soil": ["Clay Loam", "Loamy", "Sandy Loam"], "water": "High", "season_name": 0, "type": "Vegetable"},
        "Carrot": {"soil": ["Sandy Loam", "Loamy"], "water": "Moderate", "season_name": 0, "type": "Vegetable"},
        "Cauliflower": {"soil": ["Clay Loam", "Loamy"], "water": "High", "season_name": 0, "type": "Vegetable"},
        "Coriander": {"soil": ["Loamy", "Clay Loam"], "water": "Moderate", "season_name": 0, "type": "Spice"},
        "Fennogreek (Methi)": {"soil": ["Loamy", "Sandy Loam"], "water": "Moderate", "season_name": 0, "type": "Vegetable"},
        "Garlic": {"soil": ["Loamy", "Sandy Loam"], "water": "Moderate", "season_name": 0, "type": "Spice"},
        "Lettuce (Salad)": {"soil": ["Sandy Loam", "Loamy"], "water": "High", "season_name": 0, "type": "Vegetable"},
        "Linseed": {"soil": ["Clay Loam", "Loamy"], "water": "Low", "season_name": 0, "type": "Oilseed"},
        "Mattar (Green)": {"soil": ["Loamy", "Sandy Loam", "Alluvial"], "water": "Moderate", "season_name": 0, "type": "Legume"},
        "Onion": {"soil": ["Loamy", "Sandy Loam"], "water": "Moderate", "season_name": 0, "type": "Vegetable"},
        "Potato": {"soil": ["Sandy Loam", "Loamy"], "water": "Moderate", "season_name": 0, "type": "Vegetable"},
        "Radish": {"soil": ["Sandy Loam", "Loamy"], "water": "Moderate", "season_name": 0, "type": "Vegetable"},
        "Spinach": {"soil": ["Sandy Loam", "Loamy", "Clay Loam"], "water": "High", "season_name": 0, "type": "Vegetable"},
        "Sweet Potato": {"soil": ["Sandy Loam", "Loamy"], "water": "Moderate", "season_name": 0, "type": "Vegetable"},
        "Tobacco": {"soil": ["Sandy Loam", "Loamy"], "water": "Moderate", "season_name": 0, "type": "Cash"},
        "Tomato": {"soil": ["Loamy", "Sandy Loam", "Clay Loam"], "water": "Moderate", "season_name": 0, "type": "Vegetable"},
        "Turnip": {"soil": ["Sandy Loam", "Loamy"], "water": "Moderate", "season_name": 0, "type": "Vegetable"},

        # KHARIF CROPS (season_name=1)
        "Cotton": {"soil": ["Sandy", "Loamy", "Sandy Loam", "Clay Loam"], "water": "High", "season_name": 1, "type": "Cash"},
        "Sugarcane": {"soil": ["Clay", "Alluvial", "Clay Loam", "Loamy"], "water": "Very High", "season_name": 1, "type": "Cash"},
        "Rice": {"soil": ["Clay", "Clay Loam"], "water": "Very High", "season_name": 1, "type": "Cereal"},
        "Maize": {"soil": ["Loamy", "Sandy Loam", "Alluvial"], "water": "Moderate", "season_name": 1, "type": "Cereal"},
        "Mung Bean": {"soil": ["Alluvial", "Loamy", "Sandy", "Sandy Loam"], "water": "Low", "season_name": 1, "type": "Legume"},
        "Bajra": {"soil": ["Sandy", "Sandy Loam", "Loamy"], "water": "Low", "season_name": 1, "type": "Cereal"},
        "Jowar": {"soil": ["Sandy Loam", "Loamy", "Clay Loam"], "water": "Low", "season_name": 1, "type": "Cereal"},
        "Brinjal": {"soil": ["Loamy", "Sandy Loam", "Clay Loam"], "water": "Moderate", "season_name": 1, "type": "Vegetable"},
        "Bitter Gourd": {"soil": ["Sandy Loam", "Loamy"], "water": "Moderate", "season_name": 1, "type": "Vegetable"},
        "Bottle Gourd": {"soil": ["Sandy Loam", "Loamy"], "water": "Moderate", "season_name": 1, "type": "Vegetable"},
        "Chilies": {"soil": ["Loamy", "Sandy Loam", "Clay Loam"], "water": "Moderate", "season_name": 1, "type": "Spice"},
        "Cucumber": {"soil": ["Sandy Loam", "Loamy"], "water": "Moderate", "season_name": 1, "type": "Vegetable"},
        "Groundnut": {"soil": ["Sandy", "Sandy Loam", "Loamy"], "water": "Low", "season_name": 1, "type": "Oilseed"},
        "Lady Finger": {"soil": ["Loamy", "Sandy Loam", "Clay Loam"], "water": "Moderate", "season_name": 1, "type": "Vegetable"},
        "Long Melon": {"soil": ["Sandy Loam", "Loamy"], "water": "Moderate", "season_name": 1, "type": "Vegetable"},
        "Luffa": {"soil": ["Sandy Loam", "Loamy"], "water": "Moderate", "season_name": 1, "type": "Vegetable"},
        "Musk Melon": {"soil": ["Sandy Loam", "Loamy", "Sandy"], "water": "Moderate", "season_name": 1, "type": "Fruit"},
        "Pumpkin": {"soil": ["Sandy Loam", "Loamy"], "water": "Moderate", "season_name": 1, "type": "Vegetable"},
        "Safflower": {"soil": ["Clay Loam", "Loamy", "Sandy Loam"], "water": "Low", "season_name": 1, "type": "Oilseed"},
        "Sesamum": {"soil": ["Sandy Loam", "Loamy"], "water": "Low", "season_name": 1, "type": "Oilseed"},
        "Soybean": {"soil": ["Loamy", "Clay Loam"], "water": "Moderate", "season_name": 1, "type": "Legume"},
        "Sunflower": {"soil": ["Loamy", "Sandy Loam", "Clay Loam"], "water": "Moderate", "season_name": 1, "type": "Oilseed"},
        "Tinda": {"soil": ["Sandy Loam", "Loamy"], "water": "Moderate", "season_name": 1, "type": "Vegetable"},
        "Turmeric (Haldi)": {"soil": ["Loamy", "Clay Loam", "Alluvial"], "water": "High", "season_name": 1, "type": "Spice"},
        "Watermelon": {"soil": ["Sandy", "Sandy Loam", "Loamy"], "water": "Moderate", "season_name": 1, "type": "Fruit"},
    }

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
            "Groundnut": {"Ensure loose soil for peg penetration.", "Apply gypsum at flowering.", "Do not irrigate near maturity stage."},
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
    def get_recommendations(id):
        try:
            land_id = id
            current_month = datetime.now().month
            if current_month >= 4 and current_month <= 9:
                current_season = 1
                season_name_str = "Kharif"
            else:
                current_season = 0
                season_name_str = "Rabi"
            cityname=db.session.query(LandModel.city_id,CityModel.city_name).join(CityModel,CityModel.city_id==LandModel.city_id).filter(LandModel.land_id==land_id).first()

            current_weather = get_weather(cityname)
            if not land_id:
                return jsonify({"error": "land_id is required in JSON body"}), 400
            land = LandModel.query.filter(LandModel.land_id==land_id).first()
            if not land:
                return jsonify({"error": "Land resource not found"}), 404

            last_session = CultivationSessionModel.query.filter(CultivationSessionModel.land_id==land.land_id)\
                .order_by(CultivationSessionModel.cultivation_session_id.desc()).first()
            
            last_crop_name = None
            if last_session and last_session.crop_rls:
                last_crop_name = last_session.crop_rls.crop_name
            neighbors = NeighbourModel.query.filter(NeighbourModel.land_id==land.land_id, NeighbourModel.status==1).all()
            highly_successful_neighbor_crop = None
            for n in neighbors:
                n_session = CultivationSessionModel.query.filter(CultivationSessionModel.land_id==n.neighbour_land_id, CultivationSessionModel.is_profit==1)\
                    .order_by(CultivationSessionModel.cultivation_session_id.desc()).first()
                if n_session and n_session.crop_rls and n_session.crop_rls.season_name == current_season:
                    highly_successful_neighbor_crop = n_session.crop_rls.crop_name
                    break

            available_crops = CropModel.query.filter(CropModel.season_name==current_season).all()
            if not available_crops:
                return jsonify({"message": "No crops found for the current season in the database."}), 200
            recommendations = []

            for db_crop in available_crops:
                c_name = db_crop.crop_name
                if highly_successful_neighbor_crop and c_name == highly_successful_neighbor_crop:
                    recommendations.append({
                        "crop_id": db_crop.crop_id,
                        "crop_name": c_name,
                        "crop_image": imageurl+db_crop.crop_image,
                        "confidence_score": 90,
                        "rationale": "High success (profitable yield) observed recently in immediate neighboring farms with similar conditions.",
                        "suggested_actions": RecommendationController._get_suggested_actions(c_name) + ["Consult neighbor for hyper-local tips."]
                    })
                    continue
                score = 30
                rationale = []
                reqs = RecommendationController.CROP_KNOWLEDGE_BASE.get(c_name)
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
                    for accepted_soil in reqs['soil']:
                        if accepted_soil.lower() in user_soil_variants or any(variant in accepted_soil.lower() for variant in user_soil_variants):
                            soil_matched = True
                            break

                    if soil_matched:
                        score += 40
                        rationale.append(f"Ideal soil match ({land.soil_type}).")
                    else:
                        score -= 20
                        rationale.append(f"Sub-optimal soil ({land.soil_type}), may require amendments.")

                    water_src = land.source_of_water.strip().lower() if land.source_of_water else ""

                    if "rainfed" in water_src and reqs['water'] in ["High", "Very High"]:
                        score -= 20
                        rationale.append("Warning: Crop requires high water but source is primarily rainfed.")
                    elif any(w in water_src for w in ["canal", "both", "tube", "well"]) and reqs['water'] in ["High", "Very High", "Moderate"]:
                        score += 30
                        rationale.append(f"Sufficient water available ({land.source_of_water}).")
                    else:
                        score += 20
                        rationale.append("Water resources are adequate for this crop.")

                    if last_crop_name:
                        last_reqs = RecommendationController.CROP_KNOWLEDGE_BASE.get(last_crop_name)
                        if last_reqs:
                            last_type = last_reqs.get('type')
                            if last_type in ["Cash", "Cereal"] and reqs['type'] == "Legume":
                                score += 20
                                rationale.append(f"Excellent rotation choice after {last_crop_name}; will restore soil nitrogen.")
                            elif last_crop_name == c_name:
                                score -= 15
                                rationale.append("Consecutive planting of the same crop may deplete nutrients and increase pest risks.")

                    if current_weather == "Expected Heavy Rain" and reqs['water'] == "Low":
                        score -= 10
                        rationale.append("Warning: Heavy rain expected, ensure good drainage.")

                confidence = max(0, min(score, 100))

                if confidence >= 85:
                    recommendations.append({
                        "id": db_crop.crop_id,
                        "Name": c_name,
                        "Image": imageurl+db_crop.crop_image,
                        "Season":"Rabi" if db_crop.season_name==0 else "Kharif",
                        "confidence_score": confidence,
                        "rationale": " | ".join(rationale),
                        "suggested_actions": RecommendationController._get_suggested_actions(c_name)
                    })

            recommendations = sorted(recommendations, key=lambda x: x['confidence_score'], reverse=True)

            final_recommendations = recommendations[:5]

            return jsonify({
                "status": "success",
                "data": {
                    "land_profile": {
                        "soil_type": land.soil_type,
                        "water_source": land.source_of_water,
                        "previous_crop": last_crop_name
                    },
                    "environmental_context": {
                        "Season": season_name_str,
                        "weather": current_weather
                    },
                    "recommendations": final_recommendations
                }
            }), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500
