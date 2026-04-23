# dataset_generator.py
import json
import random
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime


class AgricultureDatasetGenerator:
    def __init__(self):
        self.crop_types = {

            "wheat": {
                "season": ["rabi"],
                "soil": ["loamy", "clay loam", "well-drained"],
                "ph": ["6.0-7.5"],
                "temp": ["10-25°C"],
                "water": ["moderate", "450-650mm annually"],
                "regions": ["Punjab", "Sindh", "KPK", "Balochistan"],
                "varieties": ["Sehar-2006", "Faisalabad-2008", "Galaxy-2013", "Inqalab-91"],
                "diseases": ["rust", "smut", "powdery mildew"],
                "pests": ["aphids", "armyworm", "termites"],
                "fertilizers": ["NPK 120:60:40", "urea", "DAP"],
                "duration": ["110-130 days"]
            },

            "rice": {
                "season": ["kharif"],
                "soil": ["clay", "clay loam", "water-retentive"],
                "ph": ["5.5-7.0"],
                "temp": ["20-35°C"],
                "water": ["high", "1200-2000mm"],
                "regions": ["Punjab", "Sindh"],
                "varieties": ["Super Basmati", "Basmati-385", "IRRI-6", "KS-282"],
                "diseases": ["blast", "bacterial blight", "sheath blight"],
                "pests": ["stem borer", "brown plant hopper", "leaf folder"],
                "fertilizers": ["NPK 100:50:50", "urea", "MOP"],
                "duration": ["90-150 days"]
            },

            "maize": {
                "season": ["kharif", "spring"],
                "soil": ["well-drained loamy", "sandy loam"],
                "ph": ["5.8-7.5"],
                "temp": ["18-27°C"],
                "water": ["moderate", "500-800mm"],
                "regions": ["Punjab", "KPK"],
                "varieties": ["Azam", "Jalal", "Pioneer hybrids"],
                "diseases": ["leaf blight", "stalk rot", "rust"],
                "pests": ["stem borer", "armyworm", "shoot fly"],
                "fertilizers": ["NPK 150:75:75", "urea", "SSP"],
                "duration": ["90-110 days"]
            },

            "cotton": {
                "season": ["kharif"],
                "soil": ["well-drained loamy", "black soil"],
                "ph": ["6.0-8.0"],
                "temp": ["21-35°C"],
                "water": ["moderate", "600-1200mm"],
                "regions": ["Punjab", "Sindh"],
                "varieties": ["BT-121", "MNH-886", "CIM-602"],
                "diseases": ["leaf curl virus", "bacterial blight", "verticillium wilt"],
                "pests": ["bollworm", "whitefly", "aphids"],
                "fertilizers": ["NPK 80:40:40", "urea", "zinc sulphate"],
                "duration": ["150-180 days"]
            },

            "sugarcane": {
                "season": ["spring", "autumn"],
                "soil": ["deep fertile loamy", "well-drained"],
                "ph": ["6.5-7.5"],
                "temp": ["20-35°C"],
                "water": ["high", "1500-2500mm"],
                "regions": ["Punjab", "Sindh", "KPK"],
                "varieties": ["CPF-248", "CPF-247", "HSF-240"],
                "diseases": ["red rot", "smut", "rust"],
                "pests": ["top borer", "root borer", "scale insect"],
                "fertilizers": ["NPK 250:115:115", "urea", "organic manure"],
                "duration": ["10-16 months"]
            },

            "gram (chickpea)": {
                "season": ["rabi"],
                "soil": ["sandy loam", "well-drained"],
                "ph": ["6.0-8.0"],
                "temp": ["15-25°C"],
                "water": ["low", "300-500mm"],
                "regions": ["Punjab", "Sindh", "Balochistan"],
                "varieties": ["Desi", "Kabuli", "Noor-91"],
                "diseases": ["ascochyta blight", "wilt"],
                "pests": ["pod borer", "cutworm"],
                "fertilizers": ["DAP", "organic manure"],
                "duration": ["90-120 days"]
            },

            "mustard": {
                "season": ["rabi"],
                "soil": ["loamy", "sandy loam"],
                "ph": ["6.0-7.5"],
                "temp": ["10-25°C"],
                "water": ["low to moderate"],
                "regions": ["Punjab", "Sindh"],
                "varieties": ["Raya Anmol", "Punjab Sarson"],
                "diseases": ["white rust", "downy mildew"],
                "pests": ["aphids", "painted bug"],
                "fertilizers": ["NPK 60:40:40", "urea"],
                "duration": ["110-130 days"]
            },

            "potato": {
                "season": ["rabi", "autumn"],
                "soil": ["sandy loam", "well-drained"],
                "ph": ["5.5-6.5"],
                "temp": ["15-20°C"],
                "water": ["moderate"],
                "regions": ["Punjab", "KPK"],
                "varieties": ["Desiree", "Cardinal", "Sante"],
                "diseases": ["late blight", "early blight"],
                "pests": ["potato tuber moth", "aphids"],
                "fertilizers": ["NPK 200:100:100", "FYM"],
                "duration": ["90-120 days"]
            },
            "tomato": {
                "season": ["rabi", "kharif"],
                "soil": ["sandy loam", "well-drained"],
                "ph": ["6.0-6.8"],
                "temp": ["18-30°C"],
                "water": ["moderate"],
                "regions": ["Punjab", "Sindh", "KPK", "Balochistan"],
                "varieties": ["Roma", "Money Maker", "Rio Grande"],
                "diseases": ["early blight", "late blight", "leaf curl"],
                "pests": ["whitefly", "fruit borer", "aphids"],
                "fertilizers": ["NPK 120:60:60", "FYM"],
                "duration": ["70-90 days"]
            },
            "brinjal": {
                "season": ["kharif", "spring"],
                "soil": ["loamy", "well-drained"],
                "ph": ["5.5-7.5"],
                "temp": ["22-30°C"],
                "water": ["moderate"],
                "regions": ["Punjab", "Sindh"],
                "varieties": ["Black Beauty", "Purple Long"],
                "diseases": ["bacterial wilt", "phomopsis blight"],
                "pests": ["shoot borer", "whitefly"],
                "fertilizers": ["NPK 100:60:60"],
                "duration": ["100-120 days"]
            },

            "chili": {
                "season": ["kharif"],
                "soil": ["sandy loam"],
                "ph": ["6.0-7.0"],
                "temp": ["20-30°C"],
                "water": ["moderate"],
                "regions": ["Punjab", "Sindh"],
                "varieties": ["Longi", "Mirch-444"],
                "diseases": ["anthracnose", "leaf curl"],
                "pests": ["thrips", "mites"],
                "fertilizers": ["NPK 120:60:60"],
                "duration": ["90-120 days"]
            },

            "okra (ladyfinger)": {
                "season": ["kharif"],
                "soil": ["loamy"],
                "ph": ["6.0-7.5"],
                "temp": ["25-35°C"],
                "water": ["moderate"],
                "regions": ["Punjab", "Sindh"],
                "varieties": ["Sabz Pari", "Green Star"],
                "diseases": ["yellow vein mosaic"],
                "pests": ["jassids", "whitefly"],
                "fertilizers": ["NPK 80:40:40"],
                "duration": ["50-60 days"]
            },

            "cabbage": {
                "season": ["rabi"],
                "soil": ["loamy"],
                "ph": ["6.0-7.5"],
                "temp": ["15-20°C"],
                "water": ["moderate"],
                "regions": ["Punjab", "KPK", "Balochistan"],
                "varieties": ["Golden Acre", "Copenhagen Market"],
                "diseases": ["black rot", "downy mildew"],
                "pests": ["cabbage worm", "aphids"],
                "fertilizers": ["NPK 120:80:60"],
                "duration": ["90-120 days"]
            },

            "cauliflower": {
                "season": ["rabi"],
                "soil": ["loamy"],
                "ph": ["6.0-7.0"],
                "temp": ["15-20°C"],
                "water": ["moderate"],
                "regions": ["Punjab", "KPK"],
                "varieties": ["Snowball", "Early Kunwari"],
                "diseases": ["black rot", "club root"],
                "pests": ["diamondback moth"],
                "fertilizers": ["NPK 100:60:60"],
                "duration": ["90-120 days"]
            },

            "carrot": {
                "season": ["rabi"],
                "soil": ["sandy loam"],
                "ph": ["6.0-7.0"],
                "temp": ["16-20°C"],
                "water": ["moderate"],
                "regions": ["Punjab", "KPK"],
                "varieties": ["T-29", "Nantes"],
                "diseases": ["leaf blight"],
                "pests": ["aphids"],
                "fertilizers": ["NPK 60:40:40"],
                "duration": ["90-110 days"]
            },

            "radish": {
                "season": ["rabi"],
                "soil": ["sandy loam"],
                "ph": ["6.0-7.5"],
                "temp": ["10-20°C"],
                "water": ["low to moderate"],
                "regions": ["Punjab", "Sindh", "KPK"],
                "varieties": ["White Icicle", "Desi Long"],
                "diseases": ["downy mildew"],
                "pests": ["aphids"],
                "fertilizers": ["NPK 50:40:40"],
                "duration": ["40-60 days"]
            },

            "spinach": {
                "season": ["rabi"],
                "soil": ["loamy"],
                "ph": ["6.0-7.5"],
                "temp": ["15-20°C"],
                "water": ["moderate"],
                "regions": ["All regions"],
                "varieties": ["Local Green"],
                "diseases": ["downy mildew"],
                "pests": ["leaf miner"],
                "fertilizers": ["NPK 60:40:40"],
                "duration": ["30-45 days"]
            },

            "cucumber": {
                "season": ["kharif", "spring"],
                "soil": ["sandy loam"],
                "ph": ["6.0-7.0"],
                "temp": ["20-30°C"],
                "water": ["moderate"],
                "regions": ["Punjab", "Sindh"],
                "varieties": ["Marketmore", "Local Hybrid"],
                "diseases": ["powdery mildew"],
                "pests": ["fruit fly", "aphids"],
                "fertilizers": ["NPK 80:40:40"],
                "duration": ["50-70 days"]
            },

            "peas": {
                "season": ["rabi"],
                "soil": ["loamy"],
                "ph": ["6.0-7.5"],
                "temp": ["10-20°C"],
                "water": ["moderate"],
                "regions": ["Punjab", "KPK"],
                "varieties": ["Climax", "Meteor"],
                "diseases": ["powdery mildew"],
                "pests": ["pod borer"],
                "fertilizers": ["DAP", "organic manure"],
                "duration": ["90-110 days"]
            },

            "garlic": {
                "season": ["rabi"],
                "soil": ["sandy loam"],
                "ph": ["6.0-7.0"],
                "temp": ["12-25°C"],
                "water": ["moderate"],
                "regions": ["Punjab", "Sindh"],
                "varieties": ["Chinese White", "Local White"],
                "diseases": ["white rot"],
                "pests": ["thrips"],
                "fertilizers": ["NPK 100:50:50"],
                "duration": ["120-150 days"]
            },

            "pumpkin": {
                "season": ["kharif"],
                "soil": ["sandy loam"],
                "ph": ["6.0-7.5"],
                "temp": ["20-30°C"],
                "water": ["moderate"],
                "regions": ["Punjab", "Sindh"],
                "varieties": ["Local Round"],
                "diseases": ["powdery mildew"],
                "pests": ["fruit fly"],
                "fertilizers": ["NPK 80:40:40"],
                "duration": ["90-120 days"]
            },

            "bitter gourd": {
                "season": ["kharif"],
                "soil": ["loamy"],
                "ph": ["6.0-7.0"],
                "temp": ["25-30°C"],
                "water": ["moderate"],
                "regions": ["Punjab", "Sindh"],
                "varieties": ["Palee", "Faisalabad Long"],
                "diseases": ["downy mildew"],
                "pests": ["fruit fly"],
                "fertilizers": ["NPK 80:40:40"],
                "duration": ["60-80 days"]
            },

            "bottle gourd": {
                "season": ["kharif"],
                "soil": ["loamy"],
                "ph": ["6.0-7.5"],
                "temp": ["22-30°C"],
                "water": ["moderate"],
                "regions": ["Punjab", "Sindh"],
                "varieties": ["Anmol"],
                "diseases": ["powdery mildew"],
                "pests": ["fruit fly"],
                "fertilizers": ["NPK 80:40:40"],
                "duration": ["60-75 days"]
            },

            "turnip": {
                "season": ["rabi"],
                "soil": ["sandy loam"],
                "ph": ["6.0-7.5"],
                "temp": ["10-20°C"],
                "water": ["moderate"],
                "regions": ["Punjab", "KPK"],
                "varieties": ["Purple Top"],
                "diseases": ["downy mildew"],
                "pests": ["aphids"],
                "fertilizers": ["NPK 60:40:40"],
                "duration": ["60-80 days"]
            },
            "onion": {
                "season": ["rabi"],
                "soil": ["sandy loam", "loamy"],
                "ph": ["6.0-7.0"],
                "temp": ["13-24°C"],
                "water": ["moderate"],
                "regions": ["Punjab", "Sindh", "Balochistan"],
                "varieties": ["Phulkara", "Swat-1"],
                "diseases": ["purple blotch", "downy mildew"],
                "pests": ["thrips", "onion fly"],
                "fertilizers": ["NPK 100:50:50"],
                "duration": ["100-150 days"]
            }

        }
        self.soil_types = {
            "sandy": {
                "texture": "coarse",
                "drainage": "excellent",
                "nutrients": "low",
                "water_holding": "poor",
                "ph": ["6.0-8.0"],
                "suitable_crops": ["groundnut", "watermelon", "carrot", "potato", "sunflower"],
                "improvement": ["add organic matter", "use mulch", "frequent irrigation", "green manure"],
                "problems": ["nutrient leaching", "dries quickly", "low fertility"]
            },
            "clay": {
                "texture": "fine",
                "drainage": "poor",
                "nutrients": "high",
                "water_holding": "excellent",
                "ph": ["5.5-7.5"],
                "suitable_crops": ["rice", "wheat", "soybean", "cabbage", "spinach"],
                "improvement": ["add sand", "gypsum application", "deep ploughing", "add lime"],
                "problems": ["compaction", "poor aeration", "slow drainage"]
            },
            "loamy": {
                "texture": "medium",
                "drainage": "good",
                "nutrients": "moderate",
                "water_holding": "good",
                "ph": ["6.0-7.5"],
                "suitable_crops": ["most crops", "vegetables", "fruits", "cereals", "pulses"],
                "improvement": ["maintain organic content", "crop rotation", "balanced fertilization"],
                "problems": ["erosion if not managed", "requires regular organic addition"]
            },
            "black": {
                "texture": "clayey",
                "drainage": "poor when wet",
                "nutrients": "high in calcium/magnesium",
                "water_holding": "good",
                "ph": ["7.0-8.5"],
                "suitable_crops": ["cotton", "sugarcane", "wheat", "sorghum", "citrus"],
                "improvement": ["add organic matter", "contour bunding", "subsoiling", "gypsum"],
                "problems": ["cracks when dry", "hard to work when wet", "alkaline nature"]
            }
        }

        self.question_templates = {
            "crop_general": [
                "How do I grow {crop}?",
                "What are the requirements for {crop} cultivation?",
                "Tell me about {crop} farming.",
                "Best practices for {crop}?",
                "{crop} cultivation guide",
                "How to cultivate {crop} successfully?",
                "What should I know about growing {crop}?"
            ],
            "crop_specific": [
                "What soil is best for {crop}?",
                "Ideal temperature for {crop}?",
                "Water requirements for {crop}?",
                "Common diseases of {crop}?",
                "Pests affecting {crop}?",
                "Which season is good for {crop}?",
                "Popular varieties of {crop}?",
                "Fertilizer recommendation for {crop}?",
                "How long does {crop} take to grow?",
                "In which regions is {crop} grown?",
                "How to increase {crop} yield?",
                "What is the ideal pH for {crop}?"
            ],
            "soil_general": [
                "Tell me about {soil} soil",
                "Characteristics of {soil} soil",
                "How to improve {soil} soil?",
                "Crops suitable for {soil} soil",
                "Problems with {soil} soil",
                "What is {soil} soil good for?",
                "How to manage {soil} soil?",
                "pH range of {soil} soil",
                "Water retention in {soil} soil"
            ],
            "comparison_crop": [
                "Difference between {crop1} and {crop2}",
                "Which is better for {soil} soil: {crop1} or {crop2}?",
                "Compare {crop1} and {crop2} cultivation",
                "{crop1} vs {crop2}: which requires more water?",
                "Should I grow {crop1} or {crop2}?"
            ],
            "comparison_soil": [
                "Difference between {soil1} and {soil2} soil",
                "Compare {soil1} and {soil2} soils",
                "Which is better: {soil1} or {soil2} soil?",
                "{soil1} vs {soil2}: which has better drainage?",
                "Water holding capacity: {soil1} vs {soil2}"
            ],
            "practical": [
                "How to test soil quality?",
                "When to harvest {crop}?",
                "How much fertilizer for {crop}?",
                "Organic farming methods for {crop}",
                "How to prepare land for {crop}?",
                "Irrigation methods for {crop}",
                "How to store {crop} after harvest?",
                "Cost of cultivating {crop} per acre"
            ]
        }

    def generate_crop_answer(self, crop: str, question_type: str) -> str:
        """Generate detailed answer for crop questions"""
        crop_info = self.crop_types.get(crop.lower(), {})

        if not crop_info:
            return f"I don't have information about {crop}. Please ask about wheat, rice, maize, cotton, or sugarcane."

        if "soil" in question_type.lower():
            return f"""{crop.title()} grows best in {', '.join(crop_info['soil'])} soil.
• Ideal pH: {crop_info['ph'][0]}
• Temperature: {crop_info['temp'][0]}
• Water: {crop_info['water'][0]}
• Soil should be well-prepared with proper drainage."""

        elif "disease" in question_type.lower():
            diseases = crop_info['diseases']
            prevention = "Use disease-resistant varieties, practice crop rotation, and maintain field hygiene."
            return f"""Common diseases in {crop}:
• {', '.join(diseases)}
Prevention: {prevention}
Recommended varieties: {', '.join(crop_info['varieties'][:2])}"""

        elif "pest" in question_type.lower():
            pests = crop_info['pests']
            control = "Use integrated pest management (IPM) with biological controls, pheromone traps, and judicious pesticide use."
            return f"""Major pests affecting {crop}:
• {', '.join(pests)}
Control measures: {control}"""

        elif "season" in question_type.lower():
            return f"""{crop.title()} Season Information:
• Growing season: {crop_info['season'][0]}
• Best planted: Depends on region
• Main growing regions: {', '.join(crop_info['regions'])}
• Duration: {crop_info['duration'][0]}"""

        elif "variety" in question_type.lower():
            return f"""Popular varieties of {crop}:
• {', '.join(crop_info['varieties'])}
Choose based on your region and soil type. Local agriculture departments can provide specific recommendations."""

        elif "fertilizer" in question_type.lower():
            return f"""Fertilizer recommendation for {crop}:
• Basic: {crop_info['fertilizers'][0]}
• Additional: {', '.join(crop_info['fertilizers'][1:])}
• Apply in split doses
• Conduct soil test for precise recommendation"""

        elif "water" in question_type.lower() or "irrigation" in question_type.lower():
            return f"""Water requirements for {crop}:
• {crop_info['water'][0]} water: {crop_info['water'][1]}
• Critical stages: Flowering and grain filling
• Irrigation methods: Drip/sprinkler for water efficiency
• Avoid waterlogging"""

        elif "temperature" in question_type.lower():
            return f"""Temperature requirements for {crop}:
• Ideal: {crop_info['temp'][0]}
• Minimum for growth: Varies by variety
• Sensitive to frost: Yes, requires protection
• Heat stress above: 35°C (depends on variety)"""

        elif "duration" in question_type.lower() or "days" in question_type.lower() or "time" in question_type.lower():
            return f"""{crop.title()} Growth Duration:
• From planting to harvest: {crop_info['duration'][0]}
• Varies by variety and growing conditions
• Quick maturing varieties available"""

        elif "region" in question_type.lower():
            return f"""{crop.title()} Growing Regions:
• Main regions: {', '.join(crop_info['regions'])}
• Suitable in similar climatic zones
• Consult local agriculture office for suitability in your area"""

        elif "yield" in question_type.lower():
            return f"""To increase {crop} yield:
1. Use high-yielding varieties: {', '.join(crop_info['varieties'][:2])}
2. Follow recommended fertilizer schedule
3. Ensure proper irrigation at critical stages
4. Implement integrated pest management
5. Practice timely sowing and harvesting
Average yield: 2-4 tons/acre (varies by variety and management)"""

        else:  # General info
            return f"""🌱 {crop.title()} COMPLETE CULTIVATION GUIDE 🌱

📅 SEASON & DURATION:
• Growing season: {crop_info['season'][0]}
• Duration: {crop_info['duration'][0]}

🌱 SOIL REQUIREMENTS:
• Best soil: {', '.join(crop_info['soil'])}
• Ideal pH: {crop_info['ph'][0]}

🌡️ CLIMATIC CONDITIONS:
• Temperature: {crop_info['temp'][0]}
• Water: {crop_info['water'][0]}

📍 MAJOR GROWING REGIONS:
• {', '.join(crop_info['regions'])}

🎯 RECOMMENDED VARIETIES:
• {', '.join(crop_info['varieties'])}

💊 FERTILIZER RECOMMENDATION:
• {crop_info['fertilizers'][0]}
• Additional: {', '.join(crop_info['fertilizers'][1:])}

🐛 PEST MANAGEMENT:
• Common pests: {', '.join(crop_info['pests'])}
• Control: Use IPM, biological controls

🦠 DISEASE CONTROL:
• Common diseases: {', '.join(crop_info['diseases'])}
• Prevention: Resistant varieties, crop rotation

💧 WATER MANAGEMENT:
• Critical stages: Flowering, grain filling
• Avoid waterlogging

📈 YIELD IMPROVEMENT:
• Timely operations
• Balanced fertilization
• Proper pest control
• Optimal planting density"""

    def generate_soil_answer(self, soil: str, question_type: str) -> str:
        """Generate detailed answer for soil questions"""
        soil_info = self.soil_types.get(soil.lower(), {})

        if not soil_info:
            return f"I don't have information about {soil} soil. Please ask about sandy, clay, loamy, or black soil."

        if "improve" in question_type.lower():
            return f"""How to improve {soil} soil:
1. {soil_info['improvement'][0]}
2. {soil_info['improvement'][1]}
3. {soil_info['improvement'][2]}
4. {soil_info['improvement'][3] if len(soil_info['improvement']) > 3 else 'Regular soil testing'}

Characteristics:
• Texture: {soil_info['texture']}
• Drainage: {soil_info['drainage']}
• pH range: {soil_info['ph'][0]}"""

        elif "crop" in question_type.lower() or "suitable" in question_type.lower():
            return f"""Crops suitable for {soil} soil:
• {', '.join(soil_info['suitable_crops'])}

Soil properties:
• Texture: {soil_info['texture']}
• Drainage: {soil_info['drainage']}
• Water holding: {soil_info['water_holding']}
• Nutrients: {soil_info['nutrients']}
• pH: {soil_info['ph'][0]}"""

        elif "problem" in question_type.lower():
            problems = soil_info.get('problems', ['None specific'])
            return f"""Problems with {soil} soil:
• {', '.join(problems)}
• Texture: {soil_info['texture']}
• Drainage: {soil_info['drainage']}

Solutions:
• {', '.join(soil_info['improvement'][:2])}"""

        elif "water" in question_type.lower() or "retention" in question_type.lower():
            return f"""Water characteristics of {soil} soil:
• Water holding capacity: {soil_info['water_holding']}
• Drainage: {soil_info['drainage']}
• Texture: {soil_info['texture']}

Management tips:
• Irrigation frequency: {'High' if soil_info['water_holding'] == 'poor' else 'Moderate'}
• Mulching recommended: {'Yes, essential' if soil_info['water_holding'] == 'poor' else 'Beneficial'}"""

        elif "ph" in question_type.lower():
            return f"""pH information for {soil} soil:
• Typical pH range: {soil_info['ph'][0]}
• Texture: {soil_info['texture']}
• Most crops prefer pH 6.0-7.5
• Test soil regularly for accurate pH"""

        else:  # General info
            return f"""🌍 {soil.title()} SOIL COMPLETE PROFILE 🌍

📊 BASIC PROPERTIES:
• Texture: {soil_info['texture']}
• Drainage: {soil_info['drainage']}
• Nutrient content: {soil_info['nutrients']}
• Water holding capacity: {soil_info['water_holding']}
• pH range: {soil_info['ph'][0]}

🌱 SUITABLE CROPS:
• {', '.join(soil_info['suitable_crops'])}

⚠️ COMMON PROBLEMS:
• {', '.join(soil_info.get('problems', ['Requires proper management']))}

🔧 IMPROVEMENT METHODS:
1. {soil_info['improvement'][0]}
2. {soil_info['improvement'][1]}
3. {soil_info['improvement'][2]}
{'4. ' + soil_info['improvement'][3] if len(soil_info['improvement']) > 3 else ''}

💧 WATER MANAGEMENT:
• Irrigation frequency: {'High (dries quickly)' if soil_info['water_holding'] == 'poor' else 'Moderate'}
• Best irrigation: {'Drip/sprinkler' if soil_info['water_holding'] == 'poor' else 'Any efficient method'}

🌾 FERTILIZER STRATEGY:
• {'Frequent light applications' if soil_info['nutrients'] == 'low' else 'Balanced applications'}
• Organic matter: Essential for improvement
• Soil testing: Recommended annually"""

    def generate_comparison_answer(self, item1: str, item2: str, is_soil: bool = False) -> str:
        """Generate comparison between two crops or soils"""
        if is_soil:
            info1 = self.soil_types.get(item1.lower(), {})
            info2 = self.soil_types.get(item2.lower(), {})

            if not info1 or not info2:
                return "I can only compare sandy, clay, loamy, or black soils."

            return f"""📊 COMPARISON: {item1.title()} vs {item2.title()} Soil

{item1.title()} Soil:
• Texture: {info1['texture']}
• Drainage: {info1['drainage']}
• Water holding: {info1['water_holding']}
• Nutrients: {info1['nutrients']}
• Suitable crops: {', '.join(info1['suitable_crops'][:3])}

{item2.title()} Soil:
• Texture: {info2['texture']}
• Drainage: {info2['drainage']}
• Water holding: {info2['water_holding']}
• Nutrients: {info2['nutrients']}
• Suitable crops: {', '.join(info2['suitable_crops'][:3])}

🎯 RECOMMENDATION:
• Choose {item1} for: {'better drainage' if info1['drainage'] == 'excellent' else 'specific crops'}
• Choose {item2} for: {'water retention' if info2['water_holding'] == 'excellent' else 'different needs'}
• Most versatile: {'Loamy soil is generally best for most crops' if 'loamy' in [item1, item2] else 'Depends on crop requirements'}"""

        else:
            info1 = self.crop_types.get(item1.lower(), {})
            info2 = self.crop_types.get(item2.lower(), {})

            if not info1 or not info2:
                return "I can only compare wheat, rice, maize, cotton, or sugarcane."

            return f"""🌾 COMPARISON: {item1.title()} vs {item2.title()}

{item1.title()}:
• Season: {info1['season'][0]}
• Soil: {info1['soil'][0]}
• Water: {info1['water'][0]}
• Duration: {info1['duration'][0]}
• Main regions: {', '.join(info1['regions'][:2])}

{item2.title()}:
• Season: {info2['season'][0]}
• Soil: {info2['soil'][0]}
• Water: {info2['water'][0]}
• Duration: {info2['duration'][0]}
• Main regions: {', '.join(info2['regions'][:2])}

📈 KEY DIFFERENCES:
• Water requirement: {'Higher' if 'high' in info1['water'][0].lower() and 'moderate' in info2['water'][0].lower() else 'Similar'}
• Season: {'Different' if info1['season'][0] != info2['season'][0] else 'Similar'}
• Duration: {'Shorter' if info1['duration'][0] < info2['duration'][0] else 'Longer' if info1['duration'][0] > info2['duration'][0] else 'Similar'}

💡 CHOICE DEPENDS ON:
• Your soil type
• Water availability
• Market demand
• Season in your region"""

    def generate_practical_answer(self, crop: str, question_type: str) -> str:
        """Generate practical farming advice"""
        crop_info = self.crop_types.get(crop.lower(), {})

        if "harvest" in question_type.lower():
            return f"""Harvesting {crop}:
• Timing: When grains are hard and moisture is 20-25%
• Signs: Yellowing of leaves, hard grains
• Method: Manual or combine harvester
• Post-harvest: Dry to 12-14% moisture before storage
• Storage: Clean, dry, rodent-proof containers"""

        elif "fertilizer amount" in question_type.lower() or "how much fertilizer" in question_type.lower():
            return f"""Fertilizer amount for {crop}:
• Basic recommendation: {crop_info['fertilizers'][0]}
• Apply in 3 splits: Basal, vegetative, reproductive stages
• Soil test based: Adjust based on soil test results
• Organic option: 10-15 tons farmyard manure per acre
• Micronutrients: Zinc, boron based on deficiency symptoms"""

        elif "organic" in question_type.lower():
            return f"""Organic farming for {crop}:
• Soil preparation: Green manure, compost addition
• Varieties: Use traditional or organic-certified varieties
• Pest control: Neem-based products, biological controls
• Disease control: Bio-fungicides, resistant varieties
• Certification: Requires 3-year conversion period
• Yield: May be 10-20% lower initially"""

        elif "prepare land" in question_type.lower():
            return f"""Land preparation for {crop}:
1. Clear previous crop residues
2. Plough 2-3 times for fine tilth
3. Level the field properly
4. Add basal fertilizer: {crop_info['fertilizers'][0].split(':')[0]} if available
5. Make irrigation channels
6. Pre-sowing irrigation if needed
Time required: 10-15 days before sowing"""

        elif "irrigation method" in question_type.lower():
            return f"""Irrigation methods for {crop}:
• Traditional: Flood irrigation (higher water use)
• Efficient: Drip irrigation (saves 30-50% water)
• Sprinkler: Good for light soils
• Critical stages: {'Tillering, flowering, grain filling' if crop.lower() in ['wheat', 'rice'] else 'Vegetative, flowering'}
• Interval: {'3-5 days' if crop_info['water'][0] == 'high' else '7-10 days'}"""

        elif "cost" in question_type.lower():
            return f"""Cost of cultivating {crop} (per acre approx):
• Seeds: ₹2000-4000
• Fertilizers: ₹3000-5000
• Pesticides: ₹1500-3000
• Irrigation: ₹2000-4000
• Labor: ₹5000-8000
• Machinery: ₹2000-3000
• Total cost: ₹15,000-25,000
• Expected yield: 2-4 tons
• Net profit: ₹20,000-40,000 (varies by market price)"""

        elif "test soil" in question_type.lower():
            return """How to test soil quality:
1. Collect samples from 10-15 spots in field
2. Take from 0-6 inch depth
3. Mix samples thoroughly
4. Send to soil testing lab
5. Test for: pH, NPK, organic carbon, micronutrients
6. Frequency: Before each cropping season
7. Home kits available for basic pH testing"""

        else:
            return f"""Practical advice for {crop}:
• Start with soil testing
• Use certified seeds
• Follow recommended spacing
• Monitor regularly for pests/diseases
• Keep records of inputs and yields
• Consult local agriculture officer for specific advice"""

    def generate_qna_pair(self) -> Dict[str, str]:
        """Generate a single Q&A pair"""
        q_type = random.choice(list(self.question_templates.keys()))

        try:
            if q_type in ["crop_general", "crop_specific", "practical"]:
                crop = random.choice(list(self.crop_types.keys()))
                template = random.choice(self.question_templates[q_type])

                # Handle different template placeholders
                if "{crop}" in template:
                    question = template.format(crop=crop)
                else:
                    # For practical questions without crop placeholder
                    question = template

                if q_type == "practical":
                    answer = self.generate_practical_answer(crop, template)
                else:
                    answer = self.generate_crop_answer(crop, q_type)

            elif q_type == "soil_general":
                soil = random.choice(list(self.soil_types.keys()))
                template = random.choice(self.question_templates[q_type])
                question = template.format(soil=soil)
                answer = self.generate_soil_answer(soil, q_type)

            elif q_type == "comparison_crop":
                crop1, crop2 = random.sample(list(self.crop_types.keys()), 2)
                template = random.choice(self.question_templates[q_type])

                # Check which placeholders are in template
                if "{crop1}" in template and "{crop2}" in template:
                    question = template.format(crop1=crop1, crop2=crop2)
                elif "{crop1}" in template and "{soil}" in template:
                    soil = random.choice(list(self.soil_types.keys()))
                    question = template.format(crop1=crop1, soil=soil)
                else:
                    question = template.format(crop1=crop1, crop2=crop2)

                answer = self.generate_comparison_answer(crop1, crop2, is_soil=False)

            elif q_type == "comparison_soil":
                soil1, soil2 = random.sample(list(self.soil_types.keys()), 2)
                template = random.choice(self.question_templates[q_type])
                question = template.format(soil1=soil1, soil2=soil2)
                answer = self.generate_comparison_answer(soil1, soil2, is_soil=True)

            return {
                "question": question,
                "answer": answer,
                "type": q_type,
                "entities": self.extract_entities(question),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            # Fallback to simple question if error occurs
            crop = random.choice(list(self.crop_types.keys()))
            question = f"How to grow {crop}?"
            answer = self.generate_crop_answer(crop, "crop_general")

            return {
                "question": question,
                "answer": answer,
                "type": "crop_general",
                "entities": [crop],
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def extract_entities(self, text: str) -> List[str]:
        """Extract crop and soil entities from text"""
        entities = []
        text_lower = text.lower()

        for crop in self.crop_types:
            if crop in text_lower:
                entities.append(crop)

        for soil in self.soil_types:
            if soil in text_lower:
                entities.append(soil)

        return list(set(entities))  # Remove duplicates

    def generate_dataset(self, num_samples: int = 1000) -> List[Dict[str, Any]]:
        """Generate complete dataset"""
        dataset = []

        print(f"Generating {num_samples} Q&A pairs...")
        for i in range(num_samples):
            if i % 100 == 0:
                print(f"Generated {i}/{num_samples} pairs...")

            try:
                qna_pair = self.generate_qna_pair()
                dataset.append(qna_pair)
            except Exception as e:
                print(f"Error generating pair {i}: {e}")
                # Add a simple fallback pair
                crop = random.choice(list(self.crop_types.keys()))
                dataset.append({
                    "question": f"How to grow {crop}?",
                    "answer": self.generate_crop_answer(crop, "crop_general"),
                    "type": "crop_general",
                    "entities": [crop],
                    "timestamp": datetime.now().isoformat()
                })

        print(f"Successfully generated {len(dataset)} pairs!")
        return dataset

    def save_dataset(self, dataset: List[Dict], filename: str = "data/full_dataset.json"):
        """Save dataset to JSON file"""
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)

        print(f"Dataset saved to {filename}")
        print(f"Total samples: {len(dataset)}")

        # Also save as CSV for analysis
        try:
            df = pd.DataFrame(dataset)
            csv_filename = filename.replace('.json', '.csv')
            df.to_csv(csv_filename, index=False, encoding='utf-8')
            print(f"CSV version saved to {csv_filename}")

            # Print statistics
            self.print_statistics(df)

            return df
        except Exception as e:
            print(f"Could not save CSV: {e}")
            return None

    def print_statistics(self, df):
        """Print dataset statistics"""
        print("\n" + "=" * 50)
        print("DATASET STATISTICS")
        print("=" * 50)
        print(f"Total samples: {len(df)}")

        # Question type distribution
        print("\nQuestion Type Distribution:")
        type_counts = df['type'].value_counts()
        for qtype, count in type_counts.items():
            percentage = (count / len(df)) * 100
            print(f"  {qtype}: {count} ({percentage:.1f}%)")

        # Entity distribution
        print("\nTop 10 Most Frequent Entities:")
        all_entities = []
        for entities in df['entities']:
            all_entities.extend(entities)

        from collections import Counter
        entity_counts = Counter(all_entities)
        for entity, count in entity_counts.most_common(10):
            print(f"  {entity}: {count}")

        # Average question length
        avg_q_len = df['question'].apply(len).mean()
        avg_a_len = df['answer'].apply(len).mean()
        print(f"\nAverage question length: {avg_q_len:.1f} characters")
        print(f"Average answer length: {avg_a_len:.1f} characters")
        print("=" * 50)

    def generate_out_of_domain_samples(self, num_samples: int = 200) -> List[Dict]:
        """Generate out-of-domain questions"""
        out_domain_questions = [
            "What's the weather today?",
            "Who won the cricket match yesterday?",
            "Tell me a funny joke",
            "What is quantum physics?",
            "Who is the president of India?",
            "Best movies to watch in 2024?",
            "How to code in Python?",
            "Stock market news today",
            "Football match results",
            "Recommend some good music",
            "History of ancient Rome",
            "Cooking recipes for dinner",
            "Car maintenance tips",
            "Best travel destinations",
            "Latest fashion trends",
            "Gaming news and updates",
            "Political news today",
            "Celebrity gossip latest",
            "Medical advice for cold",
            "Legal advice for property",
            "How to learn swimming?",
            "What is artificial intelligence?",
            "Tell me about space exploration",
            "How does the stock market work?",
            "What are black holes?",
            "Explain blockchain technology",
            "How to invest in mutual funds?",
            "Best smartphone to buy",
            "How to lose weight fast?",
            "Yoga exercises for beginners",
            "What is global warming?",
            "How to make coffee?",
            "Tell me about World War 2",
            "What is machine learning?",
            "How to bake a cake?",
            "What are cryptocurrencies?",
            "How to meditate properly?",
            "Tell me about Indian history",
            "What is climate change?",
            "How to tie a tie?",
            "Best books to read",
            "How to start a business?",
            "What is photosynthesis?",
            "How to paint a room?",
            "Tell me about dinosaurs",
            "What is the internet?",
            "How to play chess?",
            "What is democracy?",
            "How to write a resume?",
            "What is gravity?"
        ]

        response = "I specialize only in agriculture-related topics. Please ask about crops, soil types, farming practices, irrigation methods, pest control, harvest techniques, or any other agriculture subject."

        return [
            {
                "question": q,
                "answer": response,
                "type": "out_of_domain",
                "entities": [],
                "timestamp": datetime.now().isoformat()
            }
            for q in random.sample(out_domain_questions, min(num_samples, len(out_domain_questions)))
        ]


def main():
    """Main function to generate dataset"""
    print("🌾 Agriculture Dataset Generator 🌱")
    print("=" * 50)

    # Create data directory
    import os
    os.makedirs("data", exist_ok=True)

    # Initialize generator
    generator = AgricultureDatasetGenerator()

    # Ask for dataset size
    while True:
        try:
            agri_samples = int(input("How many agriculture Q&A pairs to generate? (500-2000): "))
            if 500 <= agri_samples <= 20000:
                break
            print("Please enter a number between 500 and 20000")
        except ValueError:
            print("Please enter a valid number")

    while True:
        try:
            out_domain_samples = int(input("How many out-of-domain samples? (100-500): "))
            if 100 <= out_domain_samples <= 5000:
                break
            print("Please enter a number between 100 and 5000")
        except ValueError:
            print("Please enter a valid number")

    print("\n" + "=" * 50)
    print("Generating dataset...")
    print("=" * 50)

    # Generate agriculture Q&A pairs
    agriculture_data = generator.generate_dataset(num_samples=agri_samples)

    # Generate out-of-domain samples
    print("\nGenerating out-of-domain samples...")
    out_of_domain_data = generator.generate_out_of_domain_samples(num_samples=out_domain_samples)

    # Combine datasets
    full_dataset = agriculture_data + out_of_domain_data

    # Shuffle the dataset
    random.shuffle(full_dataset)

    # Save the dataset
    filename = f"data/agriculture_dataset_{len(full_dataset)}.json"
    df = generator.save_dataset(full_dataset, filename)

    # Also save a smaller version for testing
    if len(full_dataset) > 1000:
        test_dataset = random.sample(full_dataset, 1000)
        generator.save_dataset(test_dataset, "data/test_dataset.json")
        print("\nTest dataset (1000 samples) saved to data/test_dataset.json")

    print("\n✅ Dataset generation complete!")
    print(f"📁 Main dataset: {filename}")
    print(f"📊 Total samples: {len(full_dataset)}")
    print(f"🌾 Agriculture samples: {len(agriculture_data)}")
    print(f"🚫 Out-of-domain samples: {len(out_of_domain_data)}")

    return df


if __name__ == "__main__":
    main()