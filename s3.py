# setup_training_data.py - Auto-generates training data for ALL 47 crops
import pandas as pd
import numpy as np
import os
from nltk.stem.porter import PorterStemmer

print("=" * 60)
print("SETTING UP AGRICULTURE CHATBOT TRAINING DATA")
print("=" * 60)

os.makedirs("datasets", exist_ok=True)
os.makedirs("saved_state", exist_ok=True)
ps = PorterStemmer()

# Get all crops from uploads/crops folder
def get_all_crops():
    crops = []
    crops_base = "uploads/crops"
    
    for season_folder in ['Kharif', 'Rabi']:
        season_path = os.path.join(crops_base, season_folder)
        if os.path.exists(season_path):
            for file in os.listdir(season_path):
                if file.endswith('.jpg') or file.endswith('.png'):
                    # Clean crop name (remove extension, parentheses content)
                    crop_name = file.replace('.jpg', '').replace('.png', '').strip()
                    crop_name = crop_name.split(' (')[0].strip()  # Remove content in parentheses
                    if crop_name.lower() not in [c.lower() for c in crops]:
                        crops.append(crop_name)
    
    return crops

ALL_CROPS = get_all_crops()
print(f"Found {len(ALL_CROPS)} crops: {ALL_CROPS}")

# Intent categories
INTENTS = ['Cultivation', 'Fertilizer', 'Pesticide', 'Irrigation', 'Soil', 'Yield', 
           'Diseases', 'Varieties', 'MarketPrice', 'HarvestTime', 'SowingTime']

# Template patterns for each intent
TEMPLATES = {
    'Cultivation': [
        "how to grow {crop}", "how to cultivate {crop}", "i want to grow {crop}",
        "tell me about {crop} cultivation", "information about {crop}",
        "details about {crop} farming", "{crop} growing guide",
        "how to plant {crop}", "steps to grow {crop}",
        "method to grow {crop}", "what is the process of growing {crop}",
        "can you tell me about {crop}", "{crop} farming tips"
    ],
    'Fertilizer': [
        "fertilizer for {crop}", "what fertilizer to use for {crop}",
        "best fertilizer for {crop}", "how much fertilizer for {crop}",
        "npk ratio for {crop}", "urea for {crop}", "manure for {crop}",
        "fertilizer dose for {crop}", "fertilizer recommendation for {crop}",
        "which fertilizer is best for {crop}", "how to apply fertilizer to {crop}"
    ],
    'Pesticide': [
        "pesticide for {crop}", "pests in {crop}", "insects in {crop}",
        "how to control pests in {crop}", "pest management in {crop}",
        "insecticide for {crop}", "pest control for {crop}",
        "common pests of {crop}", "pest attack in {crop}"
    ],
    'Irrigation': [
        "water requirement for {crop}", "how much water for {crop}",
        "irrigation for {crop}", "how many irrigations for {crop}",
        "drip irrigation for {crop}", "sprinkler irrigation for {crop}",
        "when to irrigate {crop}", "critical stages for irrigation in {crop}",
        "watering schedule for {crop}"
    ],
    'Soil': [
        "soil for {crop}", "best soil for {crop}", "soil type for {crop}",
        "soil ph for {crop}", "how to improve soil for {crop}",
        "soil preparation for {crop}", "suitable soil for {crop}"
    ],
    'Yield': [
        "yield of {crop}", "average yield of {crop}", "how much yield from {crop}",
        "{crop} production per acre", "how to increase {crop} yield",
        "{crop} yield per hectare", "productivity of {crop}"
    ],
    'Diseases': [
        "diseases in {crop}", "common diseases of {crop}", "diseases of {crop}",
        "how to control diseases in {crop}", "{crop} disease control",
        "treatments for {crop} diseases", "{crop} plant diseases"
    ],
    'Varieties': [
        "{crop} varieties", "best {crop} variety", "high yielding {crop} variety",
        "types of {crop}", "popular {crop} varieties", "which {crop} variety to grow"
    ],
    'MarketPrice': [
        "price of {crop}", "{crop} market price", "cost of {crop}",
        "{crop} rate today", "mandi price of {crop}", "current price of {crop}",
        "selling price of {crop}"
    ],
    'HarvestTime': [
        "when to harvest {crop}", "{crop} harvesting time",
        "how to harvest {crop}", "harvesting method of {crop}",
        "right time to harvest {crop}", "when is {crop} ready for harvest"
    ],
    'SowingTime': [
        "when to sow {crop}", "when to plant {crop}",
        "{crop} sowing season", "best time to sow {crop}",
        "sowing time for {crop}", "planting season for {crop}"
    ]
}

# Generate intent data for all crops
intent_data = []

# 1. Add crop-specific intents for ALL crops
for crop in ALL_CROPS:
    lower_crop = crop.lower()
    
    for intent, templates in TEMPLATES.items():
        for template in templates:
            query = template.format(crop=lower_crop)
            intent_data.append([query, intent])

# 2. Add existing static intents (greetings, help, etc.)
static_intents = [
    # === WEATHER ===
    ["weather today", "Weather"], ["weather tomorrow", "Weather"], ["weather this week", "Weather"],
    ["will it rain", "Weather"], ["rain forecast", "Weather"], ["temperature today", "Weather"],
    ["climate today", "Weather"], ["weather condition", "Weather"],
    
    # === GREETINGS ===
    ["hello", "Greeting"], ["hi", "Greeting"], ["hey", "Greeting"], ["Salam", "Greeting"],
    ["good morning", "Greeting"], ["good evening", "Greeting"], ["Assalam-o-Alaikum", "Greeting"],
    ["wassup", "Wassup"], ["whats up", "Wassup"], ["how are you", "Wellness"], 
    ["how are you doing", "Wellness"], ["are you okay", "Wellness"], ["how is it going", "Wellness"],
    
    # === HELP ===
    ["i need help", "AskingHelp"], ["need help", "AskingHelp"], ["help me", "AskingHelp"],
    ["can you help me", "AskingHelp"], ["i need assistance", "AskingHelp"], ["please help", "AskingHelp"],
    ["help", "AskingHelp"],
    
    # === OUT OF SCOPE ===
    ["who is the president", "OutOfScope"], ["who is the prime minister", "OutOfScope"],
    ["what is your name", "OutOfScope"], ["who created you", "OutOfScope"],
    ["are you a bot", "OutOfScope"], ["how old are you", "OutOfScope"],
    ["do you have a girlfriend", "OutOfScope"], ["are you married", "OutOfScope"],
    ["cricket match", "OutOfScope"], ["football", "OutOfScope"], ["movie", "OutOfScope"],
    ["song", "OutOfScope"], ["recipe", "OutOfScope"], ["cooking", "OutOfScope"],
    
    # === CONTEXT-AWARE INTENTS ===
    # MyActivities
    ["my activities", "MyActivities"], ["what are my activities", "MyActivities"],
    ["show my activities", "MyActivities"], ["my tasks", "MyActivities"],
    ["my upcoming activities", "MyActivities"], ["what activities do i have", "MyActivities"],
    ["things to do today", "MyActivities"], ["my farming activities", "MyActivities"],
    ["show my tasks", "MyActivities"], ["what should i do today", "ActivityRecommendation"],
    
    # MyCrops
    ["my crops", "MyCrops"], ["what crops i have", "MyCrops"],
    ["what am i growing", "MyCrops"], ["my cultivation", "MyCrops"],
    ["show my crops", "MyCrops"], ["what is growing on my farm", "MyCrops"],
    ["my current crops", "MyCrops"], ["which crops am i planting", "MyCrops"],
    
    # MyLands - with weather
    ["weather of my land", "MyLands"], ["weather for my land", "MyLands"],
    ["weather of my field", "MyLands"], ["weather for my farm", "MyLands"],
    ["weather of khoo aly", "MyLands"], ["weather of my land khoo aly", "MyLands"],
    ["what is weather of my land", "MyLands"], ["tell me weather of my land", "MyLands"],
    ["info of my land", "MyLands"], ["about my land", "MyLands"],
    ["land details", "MyLands"], ["field details", "MyLands"],
    ["my land info", "MyLands"], ["farm details", "MyLands"],
    
    # MyNeighbors - with land names  
    ["neighbors of my land", "MyNeighbors"], ["neighbors of khoo aly", "MyNeighbors"],
    ["who are my neighbors", "MyNeighbors"], ["neighbors nearby", "MyNeighbors"],
    ["neighbor details", "MyNeighbors"], ["neighbor info", "MyNeighbors"],
    ["neighbor lands", "MyNeighbors"], ["neighbor farms", "MyNeighbors"],
    
    # MyCrops
    ["my growing crops", "MyCrops"], ["crops on my land", "MyCrops"],
    ["current crops", "MyCrops"], ["active crops", "MyCrops"],
    ["what am i planting", "MyCrops"], ["what i planted", "MyCrops"],
    ["crops details", "MyCrops"],
    
    # Weather queries with location
    ["weather in punjab", "Weather"], ["weather in sindh", "Weather"],
    ["weather lahore", "Weather"], ["weather karachi", "Weather"],
    ["weather today in my city", "Weather"], ["current weather", "Weather"],
    
    # MyNeighbors
    ["what is my neighbor growing", "MyNeighbors"], ["neighbors crops", "MyNeighbors"],
    ["nearby farmers", "MyNeighbors"], ["what are neighbors growing", "MyNeighbors"],
    ["my neighbor is planting", "MyNeighbors"], ["tell me about my neighbor", "MyNeighbors"],
    ["neighbor farming", "MyNeighbors"], ["what my neighbor cultivated", "MyNeighbors"],
    ["neighbor crops details", "MyNeighbors"],
    
    # CropRecommendation
    ["which crop should i grow", "CropRecommendation"], ["what should i cultivate", "CropRecommendation"],
    ["recommend a crop", "CropRecommendation"], ["what to grow this season", "CropRecommendation"],
    ["which crop is best", "CropRecommendation"], ["crop suggestion", "CropRecommendation"],
    ["what crop should i plant", "CropRecommendation"], ["recommend crop for my land", "CropRecommendation"],
    ["what to grow on my farm", "CropRecommendation"],
    
    # LandRecommendation
    ["which land should i use", "LandRecommendation"], ["which field to use", "LandRecommendation"],
    ["recommend a land", "LandRecommendation"], ["which land is best", "LandRecommendation"],
    ["compare my lands", "LandRecommendation"],
    
    # ActivityRecommendation
    ["what should i do now", "ActivityRecommendation"], ["what to do on farm", "ActivityRecommendation"],
    ["recommend activities", "ActivityRecommendation"], ["farm tasks for today", "ActivityRecommendation"],
    ["suggest farming activities", "ActivityRecommendation"],
    
    # ContextGathering
    ["on my land", "ContextGathering"], ["on my field", "ContextGathering"],
    ["for my farm", "ContextGathering"], ["for my land", "ContextGathering"],
    
    # FarmerInfo
    ["what is my name", "FarmerInfo"], ["my name", "FarmerInfo"], ["who am i", "FarmerInfo"],
    ["my profile", "FarmerInfo"], ["my information", "FarmerInfo"], ["my details", "FarmerInfo"],
    ["about me", "FarmerInfo"], ["my account", "FarmerInfo"], ["my info", "FarmerInfo"],
    
    # PastActivities
    ["what activities i performed", "PastActivities"], ["past activities", "PastActivities"],
    ["completed activities", "PastActivities"], ["how many times", "PastActivities"],
    ["did i do", "PastActivities"], ["performed on", "PastActivities"], ["history of activities", "PastActivities"],
    ["watering done", "PastActivities"], ["harvesting done", "PastActivities"],
    ["activities i did", "PastActivities"], ["my activity history", "PastActivities"],
    ["what did i do on my farm", "PastActivities"], ["list my activities", "PastActivities"],
    
    # NeighborInfo
    ["neighbor name", "NeighborInfo"], ["neighbor land", "NeighborInfo"], ["neighbor owner", "NeighborInfo"],
    ["who is my neighbor", "NeighborInfo"], ["neighbors names", "NeighborInfo"],
    ["neighbor farmer name", "NeighborInfo"], ["who owns neighbor land", "NeighborInfo"],
    ["my neighbor details", "NeighborInfo"], ["neighbor farm owner", "NeighborInfo"],
    
    # More MyCrops variations
    ["what i cultivated", "MyCrops"], ["last crop", "MyCrops"], ["previously grown", "MyCrops"],
    ["what did i grow last", "MyCrops"], ["my previous crops", "MyCrops"],
    
    # More CropRecommendation variations
    ["what i should cultivate", "CropRecommendation"], ["most profitable crop", "CropRecommendation"],
    ["profitable crop", "CropRecommendation"], ["which is most profitable", "CropRecommendation"],
    ["what suits my land", "CropRecommendation"], ["should i cultivate barley", "CropRecommendation"],
    ["should i cultivate wheat", "CropRecommendation"], ["recommend me a crop", "CropRecommendation"],
    ["best crop for my land", "CropRecommendation"], ["most profitable crop of my neighbor", "CropRecommendation"],
    ["neighbor profitable crop", "CropRecommendation"], ["what to cultivate after harvesting", "CropRecommendation"],
    ["crop after harvest", "CropRecommendation"], ["next season crop", "CropRecommendation"],
]

intent_data.extend(static_intents)

# Create DataFrame and save
df_intents = pd.DataFrame(intent_data, columns=["Query", "Intent"])
df_intents.to_csv("datasets/intents.csv", index=False, header=False)
print(f"\n[OK] Created intents.csv with {len(df_intents)} samples")
print(f"   Unique intents: {df_intents['Intent'].nunique()}")
print(f"   Intent distribution (top 15):")
print(df_intents['Intent'].value_counts().head(15).to_string())

# ============================================
# ENTITY DATASET - All crops + common entities
# ============================================

# Clean crop names for entity list
crop_entities = []
for crop in ALL_CROPS:
    # Add main name
    crop_lower = crop.lower()
    crop_entities.append([crop_lower, "CROP"])
    
    # Add common variations
    if ' ' in crop:
        # Split compound names
        parts = crop.split()
        for part in parts:
            if len(part) > 3:
                crop_entities.append([part.lower(), "CROP"])
    
    # Special variations
    if 'rice' in crop_lower:
        crop_entities.append(['paddy', "CROP"])
    if 'corn' not in crop_lower and 'maize' in crop_lower:
        crop_entities.append(['corn', "CROP"])
    if 'lady finger' in crop_lower:
        crop_entities.append(['okra', "CROP"])
    if 'brinjal' in crop_lower:
        crop_entities.append(['eggplant', "CROP"])
    if 'methi' in crop_lower:
        crop_entities.append(['fenugreek', "CROP"])

# Static entity data
entity_data = crop_entities + [
    # === SOIL TYPES ===
    ["soil", "SOIL"], ["red soil", "SOIL"], ["black soil", "SOIL"], ["clay soil", "SOIL"],
    ["sandy soil", "SOIL"], ["loamy soil", "SOIL"], ["alluvial soil", "SOIL"],
    ["laterite soil", "SOIL"], ["red", "SOIL"], ["black", "SOIL"], ["clay", "SOIL"],
    ["sandy", "SOIL"], ["loamy", "SOIL"], ["alluvial", "SOIL"], ["saline", "SOIL"],
    ["kallar", "SOIL"], ["waterlogged", "SOIL"],
    
    # === FERTILIZERS ===
    ["fertilizer", "FTLZ"], ["fertiliser", "FTLZ"], ["manure", "FTLZ"], ["compost", "FTLZ"],
    ["urea", "FTLZ"], ["dap", "FTLZ"], ["npk", "FTLZ"], ["potash", "FTLZ"],
    ["phosphate", "FTLZ"], ["potassium", "FTLZ"], ["nitrogen", "FTLZ"], ["zinc", "FTLZ"],
    ["gypsum", "FTLZ"], ["fym", "FTLZ"], ["farm yard manure", "FTLZ"], ["green manure", "FTLZ"],
    
    # === PESTICIDES / PESTS ===
    ["pesticide", "PEST"], ["insecticide", "PEST"], ["fungicide", "PEST"], ["herbicide", "PEST"],
    ["pest", "PEST"], ["insect", "PEST"], ["whitefly", "PEST"], ["bollworm", "PEST"],
    ["aphid", "PEST"], ["stem borer", "PEST"], ["root borer", "PEST"], ["termite", "PEST"],
    ["armyworm", "PEST"], ["caterpillar", "PEST"], ["thrips", "PEST"], ["mite", "PEST"],
    ["weed", "PEST"], ["weeds", "PEST"],
    
    # === DISEASES ===
    ["disease", "DISEASE"], ["rust", "DISEASE"], ["blast", "DISEASE"], ["blight", "DISEASE"],
    ["wilt", "DISEASE"], ["mildew", "DISEASE"], ["curl", "DISEASE"], ["virus", "DISEASE"],
    ["fungal", "DISEASE"], ["bacterial", "DISEASE"], ["rot", "DISEASE"], ["smut", "DISEASE"],
    ["leaf curl", "DISEASE"], ["yellow rust", "DISEASE"], ["brown rust", "DISEASE"],
    
    # === IRRIGATION ===
    ["irrigation", "IRR"], ["water", "WTR"], ["irrigate", "IRR"], ["drip", "IRR"],
    ["sprinkler", "IRR"], ["flood", "IRR"], ["furrow", "IRR"], ["rain", "RAIN"],
    ["rainfall", "RAIN"], ["precipitation", "RAIN"],
    
    # === YIELD / HARVEST ===
    ["yield", "YLD"], ["production", "YLD"], ["productivity", "YLD"], ["output", "YLD"],
    ["harvest", "REAP"], ["reap", "REAP"],
    
    # === PRICE / COST ===
    ["price", "COST"], ["cost", "COST"], ["rate", "COST"], ["market price", "COST"],
    ["mandi", "COST"], ["rate today", "COST"],
    
    # === TIME / SEASON ===
    ["season", "TIME"], ["time", "TIME"], ["month", "TIME"], ["today", "TIME"],
    ["tomorrow", "TIME"], ["week", "TIME"], ["rabi", "TIME"], ["kharif", "TIME"],
    ["spring", "TIME"], ["summer", "TIME"], ["winter", "TIME"], ["autumn", "TIME"],
    ["zaid", "TIME"],
    
    # === LOCATION ===
    ["punjab", "LOC"], ["sindh", "LOC"], ["kpk", "LOC"], ["balochistan", "LOC"],
    ["pakistan", "LOC"], ["region", "LOC"], ["district", "LOC"], ["area", "LOC"],
    
    # === ACTIONS ===
    ["grow", "CUL"], ["cultivate", "CUL"], ["plant", "CUL"], ["sow", "SOW"],
    
    # === VARIETIES ===
    ["variety", "TYPE"], ["varieties", "TYPE"], ["type", "TYPE"], ["hybrid", "TYPE"],
    
    # === QUANTITY ===
    ["kg", "MSR"], ["kilogram", "MSR"], ["acre", "MSR"], ["hectare", "MSR"],
    ["ton", "MSR"], ["quintal", "MSR"], ["maund", "MSR"], ["per acre", "MSR"],
    
    # === QUESTION WORDS ===
    ["how", "QW"], ["what", "QW"], ["when", "QW"], ["where", "QW"], ["which", "QW"],
    ["why", "QW"], ["who", "QW"], ["can", "QW"], ["will", "QW"], ["tell", "QW"],
    
    # === STOP WORDS ===
    ["the", "SW"], ["a", "SW"], ["an", "SW"], ["is", "SW"], ["are", "SW"],
    ["to", "SW"], ["for", "SW"], ["of", "SW"], ["in", "SW"], ["on", "SW"],
    ["at", "SW"], ["by", "SW"], ["with", "SW"], ["from", "SW"], ["about", "SW"],
    ["i", "USR"], ["me", "USR"], ["my", "USR"], ["you", "USR"], ["your", "USR"],
    ["our", "USR"],
]

# Create DataFrame and save
df_entities = pd.DataFrame(entity_data, columns=["Word", "Tag"])
df_entities = df_entities.drop_duplicates(subset=["Word"])
df_entities.to_csv("datasets/data-tags.csv", index=False)
print(f"\n[OK] Created data-tags.csv with {len(df_entities)} unique entity samples")
print(f"   Unique entity tags: {df_entities['Tag'].nunique()}")

print("\n" + "=" * 60)
print(f"[OK] TRAINING DATA CREATED SUCCESSFULLY!")
print(f"   Total crop-specific queries: {len(ALL_CROPS)} crops × {len(INTENTS)} intents = {len(ALL_CROPS) * len(INTENTS) * 11}")
print(f"   Total static queries: {len(static_intents)}")
print(f"   Total entities: {len(df_entities)}")
print("=" * 60)
print("\nNext step: Run train_model.py or use this data to train your chatbot")