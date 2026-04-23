"""
Kisan Guide: Rule-Based Crop Recommendation System

=========================================
1) ACTIONABLE PLAN & WORKING FLOW
=========================================
Data Flow:
1. Chatbot/Client sends an API request (e.g., via Controller) with User ID, Land ID, or current context.
2. Controller fetches real-time parameters from the Database Models (User Profile, Land, Soil, Weather, Neighbors).
3. Data is passed to the CropRecommendationEngine (Rule-Based Inference Engine).
4. Engine checks for Neighbor Data rules. If none exist (Cold-Start), it falls back to Resource/Environmental rules.
5. Filtered rule outputs are scored, generating a ranked list of crops with rationales.
6. Controller returns JSON response with ranked recommendations, confidence scores, and action plans.

Decision Rules Strategy:
- Neighbor-based Rule (Warm-Start): If neighbor land with similar soil has high yield for Crop X recently, increase Crop X score.
- Cold-Start Rule:
  1. Soil Match: Crop must be compatible with land's soil type (e.g., Loamy -> Wheat, Cotton).
  2. Water Resources: Crop's water requirement must be <= available water resources (e.g., Rainfed vs Canal).
  3. Seasonality & Weather: Crop sowing season must align with current season and expected weather.
  4. Crop History (Rotation): If previous crop was heavy nutrient-depleting (e.g., Sugarcane), recommend a legume (e.g., Mung bean) to restore soil health.

=========================================
2) SAMPLE CODE GENERATION
=========================================
"""

import datetime
from typing import List, Dict, Any, Optional
from flask import Blueprint, request, jsonify

# Assuming standard SQLAlchemy usage in your project
from db import db

# ==========================================
# @Model Layer: Database Schema Definition
# ==========================================

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    region = db.Column(db.String(100))

class LandResource(db.Model):
    __tablename__ = 'land_resources'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_profiles.id'))
    size_acres = db.Column(db.Float)
    soil_type = db.Column(db.String(50))   # e.g., Alluvial, Clay, Loamy, Sandy
    water_source = db.Column(db.String(50)) # e.g., Canal, Tube-well, Rainfed

class CropHistory(db.Model):
    __tablename__ = 'crop_histories'
    id = db.Column(db.Integer, primary_key=True)
    land_id = db.Column(db.Integer, db.ForeignKey('land_resources.id'))
    crop_name = db.Column(db.String(50))
    season = db.Column(db.String(50)) # e.g., Rabi, Kharif, Zaid
    year = db.Column(db.Integer)
    yield_amount_kg = db.Column(db.Float)

class NeighborData(db.Model):
    __tablename__ = 'neighbor_data'
    id = db.Column(db.Integer, primary_key=True)
    land_id = db.Column(db.Integer, db.ForeignKey('land_resources.id'))
    neighbor_crop = db.Column(db.String(50))
    success_rating = db.Column(db.Float) # 0.0 to 10.0

# ==========================================
# Rule-Based Inference Engine
# ==========================================

class RuleBasedCropEngine:
    def __init__(self):
        # Base knowledge base for cold-start evaluations
        self.crop_knowledge_base = {
            "Wheat": {"soil": ["Loamy", "Clay", "Alluvial"], "water": "Moderate", "season": "Rabi", "type": "Cereal"},
            "Cotton": {"soil": ["Sandy", "Loamy"], "water": "High", "season": "Kharif", "type": "Cash"},
            "Mung Bean": {"soil": ["Alluvial", "Loamy", "Sandy"], "water": "Low", "season": "Kharif", "type": "Legume"},
            "Sugarcane": {"soil": ["Clay", "Alluvial"], "water": "Very High", "season": "Kharif", "type": "Cash"},
            "Mustard": {"soil": ["Sandy", "Loamy"], "water": "Low", "season": "Rabi", "type": "Oilseed"}
        }

    def evaluate_cold_start(self, land: LandResource, current_season: str, current_weather: str, last_crop: Optional[str]) -> List[Dict]:
        recommendations = []
        
        for crop, reqs in self.crop_knowledge_base.items():
            score = 0
            rationale = []
            
            # Rule 1: Seasonality Check (Crucial)
            if reqs['season'] != current_season:
                continue # Skip if completely out of season
            
            # Rule 2: Soil Compatibility
            if land.soil_type in reqs['soil']:
                score += 40
                rationale.append(f"Ideal soil match ({land.soil_type}).")
            else:
                score -= 20
                rationale.append(f"Sub-optimal soil ({land.soil_type}), requires amendments.")

            # Rule 3: Water Availability Mapping
            # (Simplified heuristics: Rainfed = Low, Tube-well = Moderate, Canal = High)
            if land.water_source == "Rainfed" and reqs['water'] in ["High", "Very High"]:
                continue # Discard if water extremely insufficient
            elif land.water_source == "Canal" and reqs['water'] in ["High", "Very High", "Moderate"]:
                score += 30
                rationale.append("Sufficient canal water available.")
            elif land.water_source in ["Tube-well", "Rainfed"] and reqs['water'] == "Low":
                score += 35
                rationale.append("Low water requirement fits current water source perfectly.")

            # Rule 4: Crop Rotation & History
            if last_crop:
                last_type = self.crop_knowledge_base.get(last_crop, {}).get('type')
                if last_type in ["Cash", "Cereal"] and reqs['type'] == "Legume":
                    score += 20
                    rationale.append(f"Excellent rotation choice after {last_crop}; will restore soil nitrogen.")
                elif last_crop == crop:
                    score -= 15
                    rationale.append("Consecutive planting of the same crop may increase pest risks.")

            # Weather modifiers
            if current_weather == "Expected Heavy Rain" and reqs['water'] == "Low":
                score -= 10
                rationale.append("Warning: Heavy rain expected, ensure good drainage.")

            if score > 0:
                confidence = min(score, 100)
                recommendations.append({
                    "crop": crop,
                    "confidence_score": confidence,
                    "rationale": " | ".join(rationale),
                    "suggested_actions": self._get_suggested_actions(crop)
                })
                
        return sorted(recommendations, key=lambda x: x['confidence_score'], reverse=True)

    def _get_suggested_actions(self, crop: str) -> List[str]:
        actions = {
            "Wheat": ["Prepare seedbed finely", "Sow early November for best yield", "Apply first irrigation at CRI stage (21 days)"],
            "Mung Bean": ["Inoculate seeds with Rhizobium", "Sow at 2-3 cm depth"],
            "Cotton": ["Ensure deep ploughing", "Monitor for bollworm from square formation stage"]
        }
        return actions.get(crop, ["Follow standard agricultural practices for your region."])


# ==========================================
# @Controller Layer: API Endpoint / Service
# ==========================================

recommendation_bp = Blueprint('crop_recommendation', __name__)

@recommendation_bp.route('/url.py/v1/recommend-crop', methods=['GET'])
def get_recommendations():
    """
    Kisan Guide Endpoint to get real-time recommendations based on contextual data.
    Query parameters: user_id, land_id, current_season, weather_forecast
    """
    user_id = request.args.get('user_id', type=int)
    land_id = request.args.get('land_id', type=int)
    current_season = request.args.get('current_season', default="Rabi")
    current_weather = request.args.get('weather_forecast', default="Normal")
    
    if not user_id or not land_id:
        return jsonify({"error": "user_id and land_id are required"}), 400

    # 1. Fetch real-time data from Database Models
    land = LandResource.query.filter_by(id=land_id, user_id=user_id).first()
    if not land:
        return jsonify({"error": "Land resource not found"}), 404

    # Fetch last crop history
    last_hist = CropHistory.query.filter_by(land_id=land.id).order_by(CropHistory.year.desc()).first()
    last_crop = last_hist.crop_name if last_hist else None

    # Fetch neighbor data as proxy for collaborative filtering
    neighbors = NeighborData.query.filter_by(land_id=land.id).all()
    
    engine = RuleBasedCropEngine()
    final_recommendations = []

    # 2. Apply Rule Strategy
    # If Neighbor Data is rich and highly successful (> 8.0) we prioritize (Warm-Start)
    highly_successful_neighbor = next((n for n in neighbors if n.success_rating >= 8.0), None)
    
    if highly_successful_neighbor:
        # Neighbor-based influence overrides or heavily supplements cold start
        crop = highly_successful_neighbor.neighbor_crop
        final_recommendations.append({
            "crop": crop,
            "confidence_score": 85,
            "rationale": f"High success rate ({highly_successful_neighbor.success_rating}/10) observed in immediate neighboring farms with similar conditions.",
            "suggested_actions": engine._get_suggested_actions(crop) + ["Consult neighbor for hyper-local tips."]
        })
    else:
        # Fallback to Cold-Start Rule Strategy
        final_recommendations = engine.evaluate_cold_start(
            land=land, 
            current_season=current_season, 
            current_weather=current_weather, 
            last_crop=last_crop
        )

    # 3. Return structured transparent reasoning
    return jsonify({
        "status": "success",
        "data": {
            "land_profile": {
                "soil_type": land.soil_type,
                "water_source": land.water_source,
                "previous_crop": last_crop
            },
            "environmental_context": {
                "season": current_season,
                "weather": current_weather
            },
            "recommendations": final_recommendations
        }
    }), 200
