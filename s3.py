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
           'Diseases', 'Varieties', 'MarketPrice', 'HarvestTime', 'SowingTime',
           'CropSuitability', 'PastSessions', 'NeighborPastSessions', 'ProfitActivities', 'ProfitablePastCrops']

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
    ],
    'CropSuitability': [
        "is {crop} suitable for my land", "can i grow {crop} on my land",
        "is {crop} good for sandy soil", "is {crop} good for loamy soil",
        "will {crop} grow in my region", "is {crop} suitable for this season",
        "does {crop} suit my soil type", "should i grow {crop} on my land"
    ],
    'PastSessions': [
        "my past cultivation sessions", "previous crops i grew",
        "last season crops", "crop history of my land",
        "what did i cultivate before", "my farming history"
    ],
    'NeighborPastSessions': [
        "neighbor previous crops", "what neighbor grew before",
        "neighbor crop history", "neighbor farming past"
    ],
    'ProfitActivities': [
        "activities for profit", "profitable farming activities",
        "activities for good yield", "best farming practices for profit"
    ],
    'ProfitablePastCrops': [
        "most profitable crops", "crops that earned profit",
        "best earning crops from history", "profitable crops from past"
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
    
    # Add crop suitability patterns for each crop
    intent_data.append([f"is {lower_crop} suitable for me", "CropSuitability"])
    intent_data.append([f"can i grow {lower_crop}", "CropSuitability"])
    intent_data.append([f"is {lower_crop} good for my land", "CropSuitability"])
    intent_data.append([f"should i grow {lower_crop}", "CropSuitability"])
    intent_data.append([f"will {lower_crop} grow on my land", "CropSuitability"])
    intent_data.append([f"is {lower_crop} right for me", "CropSuitability"])
    intent_data.append([f"does my land suit {lower_crop}", "CropSuitability"])
    
    # Add dynamic CropRecommendation patterns for each crop
    intent_data.append([f"should i cultivate {lower_crop}", "CropRecommendation"])
    intent_data.append([f"can i grow {lower_crop}", "CropRecommendation"])
    intent_data.append([f"is {lower_crop} good", "CropRecommendation"])
    intent_data.append([f"should i grow {lower_crop}", "CropRecommendation"])

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
    
    # === FOLLOW-UP QUESTIONS (SHORT VS DETAILED) ===
    # Short questions
    ["just tell me", "Quick"], ["quick", "Quick"], ["brief", "Quick"], ["simple", "Quick"],
    ["just list", "Quick"], ["names only", "Quick"], ["just", "Quick"],
    ["fast", "Quick"], ["in short", "Quick"], ["short", "Quick"],
    
    # Detailed/Explanatory questions
    ["explain", "Explanatory"], ["explain in detail", "Explanatory"], ["detailed", "Explanatory"],
    ["why", "Explanatory"], ["why should i", "Explanatory"], ["tell me why", "Explanatory"],
    ["reason", "Explanatory"], ["reason for", "Explanatory"], ["explaination", "Explanatory"],
    ["how", "Explanatory"], ["what is", "Explanatory"], ["tell me about", "Explanatory"],
    ["describe", "Explanatory"], ["elaborate", "Explanatory"], ["in detail", "Explanatory"],
    ["give me details", "Explanatory"], ["full details", "Explanatory"],
    
    # === FOLLOW-UP PRONOUNS (it, this, that) ===
    ["sow it", "SowingTime"], ["when to sow it", "SowingTime"], ["when should i sow it", "SowingTime"],
    ["grow it", "Cultivation"], ["how to grow it", "Cultivation"], ["how to cultivate it", "Cultivation"],
    ["harvest it", "HarvestTime"], ["when to harvest it", "HarvestTime"], ["when should i harvest it", "HarvestTime"],
    ["fertilize it", "Fertilizer"], ["fertilizer for it", "Fertilizer"],
    ["water it", "Irrigation"], ["irrigation for it", "Irrigation"],
    ["sow this", "SowingTime"], ["sow that", "SowingTime"],
    ["grow this", "Cultivation"], ["grow that", "Cultivation"],
    ["when to plant it", "SowingTime"], ["when to harvest it", "HarvestTime"],
    ["best time for it", "SowingTime"], ["suitable time for it", "SowingTime"],
    
    # === YES/NO QUESTIONS ===
    ["is it good", "Confirm"], ["is this good", "Confirm"], ["is that good", "Confirm"],
    ["should i grow it", "Confirm"], ["should i plant it", "Confirm"],
    ["can i grow it", "Confirm"], ["is it suitable", "Confirm"],
    ["is it best", "Confirm"], ["is this the best", "Confirm"],
    ["will it work", "Confirm"], ["will it grow", "Confirm"],
    ["is it profitable", "Confirm"], ["is this profitable", "Confirm"],
    
    # === CONTEXT-AWARE FOLLOW-UPS ===
    # After getting recommendations - follow up with crop name
    ["tell me about", "Cultivation"], ["more about", "Cultivation"], ["details about", "Cultivation"],
    ["info about", "Cultivation"], ["information about", "Cultivation"],
    ["best variety", "Varieties"], ["which variety", "Varieties"],
    ["recommended variety", "Varieties"], ["popular variety", "Varieties"],
    ["high yielding variety", "Varieties"], ["good variety", "Varieties"],
    
    # === TIME-BASED QUESTIONS ===
    ["now", "SowingTime"], ["this season", "SowingTime"], ["next season", "SowingTime"],
    ["current season", "SowingTime"], ["which month", "SowingTime"], ["what month", "SowingTime"],
    ["suitable season", "SowingTime"], ["right season", "SowingTime"],
    ["best month", "SowingTime"], ["ideal time", "SowingTime"],
    
    # === QUANTITY QUESTIONS ===
    ["how much", "Yield"], ["how many", "Yield"], ["per acre", "Yield"], ["per hectare", "Yield"],
    ["yield per acre", "Yield"], ["production per acre", "Yield"],
    ["how much yield", "Yield"], ["expected yield", "Yield"], ["average yield", "Yield"],
    
    # === REQUIREMENTS QUESTIONS ===
    ["requirements", "Cultivation"], ["what is needed", "Cultivation"], ["what do i need", "Cultivation"],
    ["things needed", "Cultivation"], ["materials needed", "Cultivation"],
    ["tools needed", "Cultivation"], ["equipment needed", "Cultivation"],
    ["what all is required", "Cultivation"], ["full requirements", "Cultivation"],
    
    # === COST/PRICE QUESTIONS ===
    ["cost", "MarketPrice"], ["price", "MarketPrice"], ["rate", "MarketPrice"],
    ["expense", "MarketPrice"], ["budget", "MarketPrice"], ["investment", "MarketPrice"],
    ["how much does it cost", "MarketPrice"], ["what is the price", "MarketPrice"],
    ["current market price", "MarketPrice"], ["today price", "MarketPrice"],
    ["mandi rate", "MarketPrice"], ["wholesale price", "MarketPrice"],
    ["retail price", "MarketPrice"], ["farm gate price", "MarketPrice"],
    
    # === PROBLEM/DISEASE QUESTIONS ===
    ["problem", "Diseases"], ["issues", "Diseases"], ["sick", "Diseases"],
    ["dying", "Diseases"], ["not growing", "Diseases"], ["yellow leaves", "Diseases"],
    ["brown spots", "Diseases"], ["wilted", "Diseases"], ["drooping", "Diseases"],
    ["not fruiting", "Diseases"], ["no yield", "Diseases"], ["low yield", "Diseases"],
    ["attack", "Diseases"], ["infestation", "Diseases"], ["infected", "Diseases"],
    ["pest attack", "Diseases"], ["disease attack", "Diseases"], ["bug attack", "Diseases"],
    ["how to fix", "Diseases"], ["how to solve", "Diseases"], ["treatment", "Diseases"],
    ["remedy", "Diseases"], ["solution", "Diseases"], ["control", "Diseases"],
    ["prevent", "Diseases"], ["prevention", "Diseases"], ["avoid", "Diseases"],
    
    # === COMPARISON QUESTIONS ===
    ["vs", "Cultivation"], ["versus", "Cultivation"], ["compare", "Cultivation"],
    ["difference between", "Cultivation"], ["which is better", "Cultivation"],
    ["between", "Cultivation"], ["or", "Cultivation"],
    
    # === STEP-BY-STEP ===
    ["step by step", "Cultivation"], ["steps", "Cultivation"], ["procedure", "Cultivation"],
    ["process", "Cultivation"], ["method", "Cultivation"], ["technique", "Cultivation"],
    ["guide", "Cultivation"], ["tutorial", "Cultivation"], ["instructions", "Cultivation"],
    ["how does it work", "Cultivation"], ["how should i do", "Cultivation"],
    
    # === LOCAL LANGUAGE (URDU/HINDI) variations ===
    ["kitna pani", "Irrigation"], ["kitna kg", "Yield"], ["kitna money", "MarketPrice"],
    ["kab lagay", "SowingTime"], ["kab kaatna", "HarvestTime"], ["kitna time", "Yield"],
    ["kaisay", "Cultivation"], ["kaise", "Cultivation"], ["kaisa", "Cultivation"],
    ["kon sa", "Varieties"], ["kaun sa", "Varieties"], ["kis mein", "Soil"],
    
    # === CONTEXT-AWARE INTENTS ===
    # MyActivities
    ["my activities", "MyActivities"], ["what are my activities", "MyActivities"],
    ["show my activities", "MyActivities"], ["my tasks", "MyActivities"],
    ["my upcoming activities", "MyActivities"], ["what activities do i have", "MyActivities"],
    ["things to do today", "MyActivities"], ["my farming activities", "MyActivities"],
    ["show my tasks", "MyActivities"], ["what should i do today", "ActivityRecommendation"],
    
    # MyCrops - CRITICAL FIX for "what is cultivated" issue
    ["my crops", "MyCrops"], ["what crops i have", "MyCrops"],
    ["what am i growing", "MyCrops"], ["my cultivation", "MyCrops"],
    ["show my crops", "MyCrops"], ["what is growing on my farm", "MyCrops"],
    ["my current crops", "MyCrops"], ["which crops am i planting", "MyCrops"],
    
    # CRITICAL: These were being misclassified as Cultivation
    ["what is cultivated", "MyCrops"], ["what is cultivated on my land", "MyCrops"],
    ["what is cultivated on it", "MyCrops"], ["what is cultivated on this land", "MyCrops"],
    ["what is grown", "MyCrops"], ["what is grown on my land", "MyCrops"],
    ["what is grown on it", "MyCrops"], ["what is grown on this land", "MyCrops"],
    ["what is planted", "MyCrops"], ["what is planted on my land", "MyCrops"],
    ["what is planted on it", "MyCrops"], ["what is planted on this land", "MyCrops"],
    ["what is on my land", "MyCrops"], ["what is on my farm", "MyCrops"],
    ["what is on it", "MyCrops"], ["what is on this land", "MyCrops"],
    ["currently cultivated", "MyCrops"], ["currently grown", "MyCrops"],
    ["currently planted", "MyCrops"], ["active crop", "MyCrops"],
    ["any crop on land", "MyCrops"], ["any crop grown", "MyCrops"],
    ["cultivated on my lands", "MyCrops"], ["cultivated on my land", "MyCrops"],
    
    # MyLands - with weather (dynamic - not hardcoded)
    ["weather of my land", "MyLands"], ["weather for my land", "MyLands"],
    ["weather of my field", "MyLands"], ["weather for my farm", "MyLands"],
    ["what is weather of my land", "MyLands"], ["tell me weather of my land", "MyLands"],
    ["info of my land", "MyLands"], ["about my land", "MyLands"],
    ["land details", "MyLands"], ["field details", "MyLands"],
    ["my land", "MyLands"], ["my field", "MyLands"], ["my farm", "MyLands"],
    ["land info", "MyLands"], ["field info", "MyLands"], ["farm info", "MyLands"],
    ["my land info", "MyLands"], ["farm details", "MyLands"],
    
    # CRITICAL FIX - Just land name without "cultivate/recommend/grow" should be MyLands
    ["land", "MyLands"], ["fields", "MyLands"],
    
    # MyNeighbors (dynamic - not hardcoded)
    ["neighbors of my land", "MyNeighbors"],
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
    
    # CropRecommendation - MORE variations
    ["which crop should i grow", "CropRecommendation"], ["what should i cultivate", "CropRecommendation"],
    ["recommend a crop", "CropRecommendation"], ["what to grow this season", "CropRecommendation"],
    ["which crop is best", "CropRecommendation"], ["crop suggestion", "CropRecommendation"],
    ["what crop should i plant", "CropRecommendation"], ["recommend crop for my land", "CropRecommendation"],
    ["what to grow on my farm", "CropRecommendation"],
    
    # More CropRecommendation variations
    ["what i should cultivate", "CropRecommendation"], ["most profitable crop", "CropRecommendation"],
    ["profitable crop", "CropRecommendation"], ["which is most profitable", "CropRecommendation"],
    ["what suits my land", "CropRecommendation"], ["recommend me a crop", "CropRecommendation"],
    ["best crop for my land", "CropRecommendation"], ["most profitable crop of my neighbor", "CropRecommendation"],
    ["neighbor profitable crop", "CropRecommendation"], ["what to cultivate after harvesting", "CropRecommendation"],
    ["crop after harvest", "CropRecommendation"], ["next season crop", "CropRecommendation"],
    
    # Additional crop recommendation patterns
    ["what to grow", "CropRecommendation"], ["suggest me a crop", "CropRecommendation"],
    ["give me crop suggestion", "CropRecommendation"], ["what is good to grow", "CropRecommendation"],
    ["which crop grows well", "CropRecommendation"], ["best crop for sandy soil", "CropRecommendation"],
    ["best crop for loam soil", "CropRecommendation"], ["crop for this season", "CropRecommendation"],
    ["what can i grow", "CropRecommendation"],
    
    # CRITICAL FIX - Patterns with land that were being misclassified
    ["what should i cultivate on my land", "CropRecommendation"],
    ["what should i cultivate on it", "CropRecommendation"],
    ["what i should cultivate on my land", "CropRecommendation"],
    ["what i should cultivate on it", "CropRecommendation"],
    ["i should cultivate on my land", "CropRecommendation"],
    ["i should cultivate on it", "CropRecommendation"],
    ["should cultivate on my land", "CropRecommendation"],
    ["should cultivate on it", "CropRecommendation"],
    ["cultivate on my land", "CropRecommendation"],
    ["cultivate on it", "CropRecommendation"],
    ["recommend for my land", "CropRecommendation"], ["best for my soil", "CropRecommendation"],
    ["good crop for my land", "CropRecommendation"], ["which crop is suitable", "CropRecommendation"],
    ["suitable crop for me", "CropRecommendation"], ["what crop fits my land", "CropRecommendation"],
    ["i want to plant", "CropRecommendation"], ["i want to grow", "CropRecommendation"],
    ["planning to grow", "CropRecommendation"], ["thinking to cultivate", "CropRecommendation"],
    ["give me recommendations", "CropRecommendation"], ["your recommendation", "CropRecommendation"],
    ["crop recommendations", "CropRecommendation"], ["suggest crops", "CropRecommendation"],
    ["which crops to grow", "CropRecommendation"], ["what crops can i grow", "CropRecommendation"],
    ["what crops to cultivate", "CropRecommendation"], ["advise me a crop", "CropRecommendation"],
    ["i need crop advice", "CropRecommendation"], ["help me choose crop", "CropRecommendation"],
    
    # Specific follow-ups after getting recommendations
    ["these crops", "CropRecommendation"], ["those crops", "CropRecommendation"],
    ["the crops you mentioned", "CropRecommendation"], ["crops you recommended", "CropRecommendation"],
    ["show me crops", "CropRecommendation"], ["list the crops", "CropRecommendation"],
    ["crop names", "CropRecommendation"], ["what are the crops", "CropRecommendation"],
    
    # === SOWING TIME FOLLOW-UP variations ===
    ["when to sow", "SowingTime"], ["when to plant", "SowingTime"],
    ["when should i sow", "SowingTime"], ["when should i plant", "SowingTime"],
    ["when can i sow", "SowingTime"], ["when can i plant", "SowingTime"],
    ["sowing time", "SowingTime"], ["planting time", "SowingTime"],
    ["best sowing time", "SowingTime"], ["best planting time", "SowingTime"],
    ["suitable time to sow", "SowingTime"], ["suitable time to plant", "SowingTime"],
    ["right time to sow", "SowingTime"], ["right time to plant", "SowingTime"],
    ["when is sowing season", "SowingTime"], ["when is planting season", "SowingTime"],
    ["sowing season", "SowingTime"], ["planting season", "SowingTime"],
    ["what is sowing time", "SowingTime"], ["what is planting time", "SowingTime"],
    
    # === HARVEST TIME FOLLOW-UP variations ===
    ["when to harvest", "HarvestTime"], ["when should i harvest", "HarvestTime"],
    ["when can i harvest", "HarvestTime"], ["harvesting time", "HarvestTime"],
    ["best harvest time", "HarvestTime"], ["right time to harvest", "HarvestTime"],
    ["when is harvest season", "HarvestTime"], ["harvest season", "HarvestTime"],
    ["what is harvest time", "HarvestTime"], ["harvesting season", "HarvestTime"],
    ["ready for harvest", "HarvestTime"], ["when will it be ready", "HarvestTime"],
    ["days to harvest", "HarvestTime"], ["harvest after days", "HarvestTime"],
    ["how many days to harvest", "HarvestTime"], ["time to harvest", "HarvestTime"],
    
    # === FERTILIZER FOLLOW-UP variations ===
    ["fertilizer", "Fertilizer"], ["fertilizers", "Fertilizer"], ["fertilizer for", "Fertilizer"],
    ["what fertilizer", "Fertilizer"], ["which fertilizer", "Fertilizer"],
    ["best fertilizer", "Fertilizer"], ["recommended fertilizer", "Fertilizer"],
    ["fertilizer dose", "Fertilizer"], ["fertilizer amount", "Fertilizer"],
    ["how much fertilizer", "Fertilizer"], ["fertilizer requirement", "Fertilizer"],
    ["npk for", "Fertilizer"], ["urea for", "Fertilizer"], ["dap for", "Fertilizer"],
    ["manure for", "Fertilizer"], ["compost for", "Fertilizer"],
    ["when to apply fertilizer", "Fertilizer"], ["fertilizer timing", "Fertilizer"],
    ["fertilizer application", "Fertilizer"], ["how to apply fertilizer", "Fertilizer"],
    
    # === IRRIGATION FOLLOW-UP variations ===
    ["irrigation", "Irrigation"], ["water requirement", "Irrigation"],
    ["how much water", "Irrigation"], ["watering", "Irrigation"],
    ["when to water", "Irrigation"], ["when to irrigate", "Irrigation"],
    ["irrigation schedule", "Irrigation"], ["watering schedule", "Irrigation"],
    ["how many times to water", "Irrigation"], ["number of irrigations", "Irrigation"],
    ["drip irrigation", "Irrigation"], ["sprinkler irrigation", "Irrigation"],
    ["flood irrigation", "Irrigation"], ["canal water", "Irrigation"],
    ["water source", "Irrigation"], ["drought tolerant", "Irrigation"],
    
    # === SOIL FOLLOW-UP variations ===
    ["soil", "Soil"], ["soil type", "Soil"], ["soil requirement", "Soil"],
    ["best soil", "Soil"], ["suitable soil", "Soil"], ["soil ph", "Soil"],
    ["soil preparation", "Soil"], ["how to prepare soil", "Soil"],
    ["improve soil", "Soil"], ["soil fertility", "Soil"], ["soil health", "Soil"],
    
    # === VARIETIES FOLLOW-UP variations ===
    ["varieties", "Varieties"], ["variety", "Varieties"], ["types", "Varieties"],
    ["which variety", "Varieties"], ["best variety", "Varieties"],
    ["recommended variety", "Varieties"], ["high yielding variety", "Varieties"],
    ["popular variety", "Varieties"], ["local variety", "Varieties"],
    ["hybrid variety", "Varieties"], ["traditional variety", "Varieties"],
    ["new variety", "Varieties"], ["improved variety", "Varieties"],
    
    # === YIELD FOLLOW-UP variations ===
    ["yield", "Yield"], ["production", "Yield"], ["productivity", "Yield"],
    ["how much yield", "Yield"], ["expected yield", "Yield"],
    ["yield per acre", "Yield"], ["production per acre", "Yield"],
    ["yield per hectare", "Yield"], ["average yield", "Yield"],
    ["maximum yield", "Yield"], ["minimum yield", "Yield"],
    
    # === DISEASE/PEST FOLLOW-UP variations ===
    ["pests", "Pesticide"], ["pesticide", "Pesticide"], ["pest control", "Pesticide"],
    ["insects", "Pesticide"], ["insecticide", "Pesticide"],
    ["common pests", "Pesticide"], ["pest attack", "Pesticide"],
    ["diseases", "Diseases"], ["disease", "Diseases"], ["disease control", "Diseases"],
    ["common diseases", "Diseases"], ["disease attack", "Diseases"],
    ["treatment", "Diseases"], ["remedy", "Diseases"], ["solution", "Diseases"],
    ["how to control", "Diseases"], ["prevention", "Diseases"],
    
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
    ["who owned my neighbor land", "NeighborInfo"], ["who is the owner of this land", "NeighborInfo"],
    ["neighbor land owner", "NeighborInfo"], ["owner of neighbor land", "NeighborInfo"],
    ["who is the owner", "NeighborInfo"], ["tell me about owner", "NeighborInfo"],
    
    # === PAST SESSIONS / HISTORY ===
    ["what are my last five crop sessions", "PastSessions"], ["my last five crop sessions", "PastSessions"],
    ["show my past sessions", "PastSessions"], ["my previous cultivation sessions", "PastSessions"],
    ["my crop history", "PastSessions"], ["what crops did i grow before", "PastSessions"],
    ["last crop sessions", "PastSessions"], ["my cultivation history", "PastSessions"],
    ["show my session history", "PastSessions"], ["past crop details", "PastSessions"],
    ["my farming history", "PastSessions"], ["previous seasons crops", "PastSessions"],
    ["last season i grew", "PastSessions"], ["what did i grow last season", "PastSessions"],
    ["my previous growing season", "PastSessions"],
    
    # === NEIGHBOR PAST SESSIONS ===
    ["my neighbor last sessions", "NeighborPastSessions"], ["what did my neighbor grow", "NeighborPastSessions"],
    ["neighbor past crops", "NeighborPastSessions"], ["neighbor cultivation history", "NeighborPastSessions"],
    ["what my neighbor cultivated before", "NeighborPastSessions"], ["neighbor previous crops", "NeighborPastSessions"],
    ["neighbor farming history", "NeighborPastSessions"], ["my neighbor previous sessions", "NeighborPastSessions"],
    
    # === ACTIVITIES FOR PROFIT ===
    ["activities performed for profit", "ProfitActivities"], ["what activities for profit", "ProfitActivities"],
    ["activities done for profitability", "ProfitActivities"], ["profitable activities", "ProfitActivities"],
    ["activities that make profit", "ProfitActivities"], ["how to get profit activities", "ProfitActivities"],
    ["activities for good yield", "ProfitActivities"], ["activities for better production", "ProfitActivities"],
    ["what activities increase profit", "ProfitActivities"], ["best activities for profit", "ProfitActivities"],
    ["tell me profitable sessions", "ProfitActivities"], ["which sessions were profitable", "ProfitActivities"],
    ["profitable sessions of my land", "ProfitActivities"],
    
    # === PROFITABLE CROPS FROM PAST ===
    ["profitable crops from my past", "ProfitablePastCrops"], ["most profitable crop from my history", "ProfitablePastCrops"],
    ["which crop gave me profit before", "ProfitablePastCrops"], ["my profitable crops", "ProfitablePastCrops"],
    ["best crops i grew before", "ProfitablePastCrops"], ["crops that made profit", "ProfitablePastCrops"],
    ["past profitable crops", "ProfitablePastCrops"], ["crops that gave good returns", "ProfitablePastCrops"],
    ["which crop earned me money", "ProfitablePastCrops"], ["most earning crop before", "ProfitablePastCrops"],
    ["profitbake crop of my past", "ProfitablePastCrops"], ["profitable crop from my past", "ProfitablePastCrops"],
    
    # === CROP SUITABILITY QUESTIONS (Dynamic - no specific crop names) ===
    ["is this suitable for me to cultivate", "CropSuitability"], ["is this suitable for me to grow", "CropSuitability"],
    ["is suitable for me to cultivate", "CropSuitability"], ["is suitable for me to grow", "CropSuitability"],
    ["can i grow this on my land", "CropSuitability"], ["can i cultivate this on my land", "CropSuitability"],
    ["will this grow on my land", "CropSuitability"], ["is this good for my soil", "CropSuitability"],
    ["should i grow this", "CropSuitability"], ["is this right for me", "CropSuitability"],
    ["does my land suit this", "CropSuitability"], ["is my land good for this", "CropSuitability"],
    ["suitable crop for my land", "CropSuitability"], ["is this crop suitable", "CropSuitability"],
    ["is it suitable for my land", "CropSuitability"], ["can i grow it on my land", "CropSuitability"],
    ["will it grow on my land", "CropSuitability"], ["should i grow it", "CropSuitability"],
    
    # === PAST SESSIONS / HISTORY ===
    ["what are my last five crop sessions", "PastSessions"], ["my last five crop sessions", "PastSessions"],
    ["show my past sessions", "PastSessions"], ["my previous cultivation sessions", "PastSessions"],
    ["my crop history", "PastSessions"], ["what crops did i grow before", "PastSessions"],
    ["last crop sessions", "PastSessions"], ["my cultivation history", "PastSessions"],
    ["show my session history", "PastSessions"], ["past crop details", "PastSessions"],
    ["my farming history", "PastSessions"], ["previous seasons crops", "PastSessions"],
    ["last season i grew", "PastSessions"], ["what did i grow last season", "PastSessions"],
    ["my previous growing season", "PastSessions"],
    
    # === NEIGHBOR PAST SESSIONS ===
    ["my neighbor last sessions", "NeighborPastSessions"], ["what did my neighbor grow", "NeighborPastSessions"],
    ["neighbor past crops", "NeighborPastSessions"], ["neighbor cultivation history", "NeighborPastSessions"],
    ["what my neighbor cultivated before", "NeighborPastSessions"], ["neighbor previous crops", "NeighborPastSessions"],
    ["neighbor farming history", "NeighborPastSessions"], ["my neighbor previous sessions", "NeighborPastSessions"],
    
    # === ACTIVITIES FOR PROFIT ===
    ["activities performed for profit", "ProfitActivities"], ["what activities for profit", "ProfitActivities"],
    ["activities done for profitability", "ProfitActivities"], ["profitable activities", "ProfitActivities"],
    ["activities that make profit", "ProfitActivities"], ["how to get profit activities", "ProfitActivities"],
    ["activities for good yield", "ProfitActivities"], ["activities for better production", "ProfitActivities"],
    ["what activities increase profit", "ProfitActivities"], ["best activities for profit", "ProfitActivities"],
    
    # === PROFITABLE CROPS FROM PAST ===
    ["profitable crops from my past", "ProfitablePastCrops"], ["most profitable crop from my history", "ProfitablePastCrops"],
    ["which crop gave me profit before", "ProfitablePastCrops"], ["my profitable crops", "ProfitablePastCrops"],
    ["best crops i grew before", "ProfitablePastCrops"], ["crops that made profit", "ProfitablePastCrops"],
    ["past profitable crops", "ProfitablePastCrops"], ["crops that gave good returns", "ProfitablePastCrops"],
    ["which crop earned me money", "ProfitablePastCrops"], ["most earning crop before", "ProfitablePastCrops"],
    
    # More MyCrops variations
    ["what i cultivated", "MyCrops"], ["last crop", "MyCrops"], ["previously grown", "MyCrops"],
    ["what did i grow last", "MyCrops"], ["my previous crops", "MyCrops"],
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