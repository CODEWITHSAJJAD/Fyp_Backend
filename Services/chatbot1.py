"""Integrated context-aware chatbot for AgricultureRAGChatbot"""

import pandas as pd
import numpy as np
import pickle
import re
from sentence_transformers import SentenceTransformer
import faiss
from nltk.stem.porter import PorterStemmer
from tensorflow.keras.models import load_model
import warnings
import os

warnings.filterwarnings('ignore')

from Services.ChatbotHelper import (
    get_context as _get_context,
    set_context as _set_context,
    reset_context as _reset_context,
    get_farmer_lands, find_land_in_query,
    get_active_sessions_for_farmer, get_neighbor_info,
    get_farmer_profile, get_farmer_crops, format_neighbors,
    get_past_activities, get_upcoming_activities, get_neighbor_owner_info,
    get_crop_name, get_crop_sowing_info,
    get_my_past_sessions, get_past_sessions_for_land,
    get_neighbor_past_sessions, get_profitable_past_crops,
    get_activities_for_profitable_sessions, check_crop_suitability,
    get_loss_crops, get_most_profitable_crop, get_activities_for_loss_crops,
    get_harvest_info_for_active_crop, get_irrigation_advice,
    handle_neighbor_past_sessions, get_my_past_sessions_formatted,
    format_crop_suitability_response, get_land_names_response,
    get_remaining_activities
)

_chatbot_instance = None


def get_chatbot(use_llm=False):
    """Get or create singleton chatbot instance"""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = AgricultureRAGChatbot(use_llm=use_llm)
    return _chatbot_instance


class AgricultureRAGChatbot:

    CONTEXT_INTENTS = {
        'CropRecommendation': ['what should i grow', 'which crop', 'recommend crop', 'what to cultivate'],
        'ActivityRecommendation': ['what should i do now', 'what to do today', 'next activity', 'current task', 'what i should do'],
        'MyNeighbors': ['neighbor', 'neighbours', 'neighbors', 'neighbor doing', 'nearby farmers', 'neighbors growing', 'neighbor crops', 'neighbor planted'],
        'MyLands': ['my lands', 'my fields', 'list of lands', 'weather of land',
            'land info', 'land details', 'field info', 'farm info',
            'my land', 'about my land', 'show my land', 'which land',
            'about my field', 'my field details', 'land information'],
        'MyCrops': ['my crops', 'what crops i have', 'what am i growing', 'my cultivation', 'what i cultivated', 'last crop', 'previously grown'],
        'MyActivities': ['my activities', 'my tasks', 'things to do'],
        'PastActivities': ['what activities i performed', 'past activities', 'completed activities', 'how many times', 'did i do', 'performed on', 'history of activities', 'watering done', 'harvesting done'],
        'FarmerInfo': ['what is my name', 'my name', 'who am i', 'my profile', 'my information', 'tell me my name', 'do i know my name', 'what should i know about me', 'my details', 'my account', 'about me', 'my info'],
        'NeighborInfo': ['neighbor name', 'neighbor land', 'neighbor owner', 'who is my neighbor', 'neighbors names', 'who owned', 'owner of this land', 'who is the owner'],
        'PastSessions': ['past sessions', 'last five crop sessions', 'my crop history', 'previous cultivation', 'crop history', 'last season', 'what did i grow before'],
        'NeighborPastSessions': ['neighbor past sessions', 'neighbor crop history', 'neighbor previous crops', 'what did neighbor grow', 'neighbor farming history'],
        'ProfitActivities': ['profitable sessions', 'activities for profit', 'profitable activities', 'activities performed for profit', 'activities that made profit'],
        'ProfitablePastCrops': ['profitable crops', 'profitable past', 'most profitable crop', 'crops that earned profit', 'best earning crops', 'profitbake crop', 'profitable crop of my neighbor', 'neighbor profitable'],
        'CropSuitability': ['suitable for me', 'suitable to cultivate', 'good for my land', 'suitable crop', 'is it suitable', 'does my land suit'],
    }

    def __init__(self, use_llm=True):
        print(" Loading Agriculture RAG Chatbot...")
        self.ps = PorterStemmer()
        self.use_llm = use_llm

        self.AGRICULTURE_INTENTS = [
            "Cultivation", "Fertilizer", "Pesticide", "Irrigation",
            "Soil", "Yield", "Diseases", "Varieties",
            "MarketPrice", "HarvestTime", "SowingTime", "Weather"
        ]
        self.INTERACTION_INTENTS = [
            "Greeting", "Wassup", "Wellness", "AskingHelp", "OutOfScope", "Acknowledgment", "Farewell"
        ]
        self.CONFIDENCE_THRESHOLD = 0.6

        self.ALL_KNOWN_INTENTS = [
            "Cultivation", "Fertilizer", "Pesticide", "Irrigation", "Soil", "Yield",
            "Diseases", "Varieties", "MarketPrice", "HarvestTime", "SowingTime", "Weather",
            "Greeting", "Wassup", "Wellness", "AskingHelp", "OutOfScope", "Acknowledgment", "Farewell",
            "CropRecommendation", "ActivityRecommendation", "MyNeighbors", "MyLands",
            "MyCrops", "MyActivities", "FarmerInfo", "PastActivities", "NeighborInfo",
            "PastSessions", "NeighborPastSessions", "ProfitActivities", "ProfitablePastCrops",
            "CropSuitability", "LandRecommendation", "ContextGathering", "Quick", "Explanatory", "Confirm"
        ]

        self._load_models()
        self.load_knowledge_base()
        self.setup_embeddings()
        if self.use_llm:
            print("LLM paraphrasing enabled (will load on first query)")

    def _load_models(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        saved_path = os.path.join(base_path, '..', 'saved_state')
        try:
            self.intent_model = load_model(os.path.join(saved_path, 'intent_model.h5'), compile=False)
            self.intent_cv = pickle.load(open(os.path.join(saved_path, 'IntentCountVectorizer.sav'), 'rb'))
            self.intent_label_map = pickle.load(open(os.path.join(saved_path, 'IntentCountVectorizer.sav'), 'rb'))
            self.idx_to_intent = {v: k for k, v in self.intent_label_map.items()}

            self.entity_model = pickle.load(open(os.path.join(saved_path, 'entity_model.sav'), 'rb'))
            self.entity_cv = pickle.load(open(os.path.join(saved_path, 'EntityCountVectorizer.sav'), 'rb'))
            self.entity_label_map = pickle.load(open(os.path.join(saved_path, 'entity_label_map.sav'), 'rb'))
            self.idx_to_entity = {v: k for k, v in self.entity_label_map.items()}
            print("Intent & Entity models loaded")
        except Exception as e:
            print(f"Warning: Could not load ML models: {e}")
            self.intent_model = None

    def load_knowledge_base(self):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(base_path, '..', 'data', 'agriculture_knowledge_base_combined.csv')
            potential_paths = [data_path, "data/agriculture_knowledge_base_combined.csv"]
            path_found = False
            for path in potential_paths:
                if os.path.exists(path):
                    self.df = pd.read_csv(path)
                    print(f"Loaded knowledge base from {path}: {len(self.df)} Q&A pairs")
                    path_found = True
                    break

            if not path_found:
                raise FileNotFoundError("No knowledge base CSV found.")

            self.df['search_text'] = self.df['question'] + " " + self.df['answer'].str[:100]
            self.df['crop'] = self.df['crop'].fillna('')
            self.df['soil'] = self.df['soil'].fillna('')
            self.df['intent'] = self.df['intent'].fillna('')
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            self.df = pd.DataFrame(columns=['crop', 'soil', 'intent', 'question', 'answer'])

    def setup_embeddings(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        saved_path = os.path.join(base_path, '..', 'saved_state')
        os.makedirs(saved_path, exist_ok=True)

        try:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            index_path = os.path.join(saved_path, 'faiss_index.idx')
            embeddings_path = os.path.join(saved_path, 'embeddings.npy')

            if len(self.df) > 0:
                if os.path.exists(index_path) and os.path.exists(embeddings_path):
                    self.question_embeddings = np.load(embeddings_path)
                    if len(self.question_embeddings) == len(self.df):
                        self.index = faiss.read_index(index_path)
                        print(f"Loaded cached embeddings: {self.question_embeddings.shape}")
                        return

                print("Generating embeddings...")
                questions = self.df['question'].tolist()
                self.question_embeddings = self.embedder.encode(questions)

                dimension = self.question_embeddings.shape[1]
                self.index = faiss.IndexFlatIP(dimension)
                faiss.normalize_L2(self.question_embeddings.astype('float32'))
                self.index.add(self.question_embeddings.astype('float32'))

                faiss.write_index(self.index, index_path)
                np.save(embeddings_path, self.question_embeddings)
                print(f"Created and cached embeddings: {self.question_embeddings.shape}")
            else:
                self.index = None
        except Exception as e:
            print(f"Could not create embeddings: {e}")
            self.index = None

    def get_intent(self, text):
        if not self.intent_model:
            return self.rule_based_intent(text), 0.5
        try:
            text = re.sub('[^a-zA-Z]', ' ', text).lower()
            text = ' '.join([self.ps.stem(word) for word in text.split()])
            X = self.intent_cv.transform([text]).toarray()
            pred = self.intent_model.predict(X, verbose=0)
            intent_idx = np.argmax(pred[0])
            confidence = np.max(pred[0])
            return self.idx_to_intent.get(intent_idx, "Unknown"), confidence
        except:
            return self.rule_based_intent(text), 0.5

    def rule_based_intent(self, text):
        text_lower = text.lower()
        rules = {
            'Greeting': ['hello', 'hi', 'hey'],
            'Wellness': ['how are you', 'how do you do'],
            'AskingHelp': ['help', 'assist'],
            'Fertilizer': ['fertilizer', 'urea', 'dap', 'npk'],
            'Pesticide': ['pest', 'insect', 'whitefly', 'borer', 'control'],
            'Irrigation': ['irrigation', 'water', 'irrigate'],
            'Soil': ['soil', 'clay', 'sandy', 'loamy'],
            'Yield': ['yield', 'production', 'output'],
            'Diseases': ['disease', 'rust', 'blight', 'virus'],
            'Varieties': ['variety', 'varieties', 'type', 'hybrid'],
            'HarvestTime': ['harvest', 'reap', 'picking'],
            'SowingTime': ['sow', 'sowing', 'plant', 'planting'],
            'MarketPrice': ['price', 'cost', 'rate', 'mandi'],
            'Cultivation': ['how to grow', 'cultivate', 'cultivation'],
            'OutOfScope': ['who is', 'prime minister', 'president']
        }
        for intent, keywords in rules.items():
            if any(word in text_lower for word in keywords):
                return intent
        return 'Cultivation'

    def detect_context_intent(self, text):
        text_lower = text.lower().strip()
        
        if text_lower.isdigit() and len(text_lower) <= 2:
            return None
        
        has_grow_cultivate = any(word in text_lower for word in ['grow', 'cultivate', 'plant', 'sow', 'recommend'])
        has_land_word = any(word in text_lower for word in ['land', 'field', 'farm'])

        if has_grow_cultivate and has_land_word:
            return 'CropRecommendation'

        has_neighbor_word = any(word in text_lower for word in ['neighbor', 'neighbours', 'neighbors', 'nearby'])
        if has_neighbor_word and has_land_word:
            return 'MyNeighbors'

        priority_order = ['FarmerInfo', 'NeighborInfo', 'PastSessions', 'NeighborPastSessions', 'ProfitActivities',
                          'ProfitablePastCrops', 'PastActivities', 'CropSuitability', 'CropRecommendation',
                          'ActivityRecommendation', 'MyNeighbors', 'MyLands', 'MyCrops', 'MyActivities']

        for intent in priority_order:
            keywords = self.CONTEXT_INTENTS.get(intent, [])
            for keyword in keywords:
                if keyword in text_lower:
                    return intent

        return None

    def extract_entities(self, text):
        text_lower = text.lower()
        entities = []
        crops = ['wheat', 'rice', 'cotton', 'sugarcane', 'maize', 'potato', 'tomato', 'onion', 'mustard', 'gram', 'chickpea', 'sunflower', 'groundnut']
        soils = ['sandy', 'clay', 'loamy', 'saline', 'black', 'red', 'alluvial']

        for crop in crops:
            if crop in text_lower:
                entities.append(('crop', crop))
                break
        for soil in soils:
            if soil in text_lower:
                entities.append(('soil', soil))
                break
        return entities

    def search_knowledge_base(self, query, intent, entities, top_k=3):
        crop = None
        soil = None
        for entity_type, entity_value in entities:
            if entity_type == 'crop':
                crop = entity_value
            elif entity_type == 'soil':
                soil = entity_value

        if crop and intent:
            exact_match = self.df[(self.df['crop'].str.contains(crop, case=False, na=False)) & (self.df['intent'] == intent)]
            if len(exact_match) > 0:
                return exact_match.iloc[0]['answer'], 1.0, 'exact_match'

        if soil and intent == 'Soil':
            soil_match = self.df[(self.df['soil'].str.contains(soil, case=False, na=False)) & (self.df['intent'] == intent)]
            if len(soil_match) > 0:
                return soil_match.iloc[0]['answer'], 0.95, 'soil_match'

        if self.index is not None and len(self.df) > 0:
            try:
                query_embedding = self.embedder.encode([query])
                faiss.normalize_L2(query_embedding.astype('float32'))
                scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
                for i, idx in enumerate(indices[0]):
                    if idx < len(self.df) and scores[0][i] > 0.5:
                        row = self.df.iloc[idx]
                        return row['answer'], float(scores[0][i]), 'semantic'
            except:
                pass

        query_words = set(query.lower().split())
        best_score = 0
        best_answer = None
        for _, row in self.df.iterrows():
            question_words = set(row['question'].lower().split())
            overlap = len(query_words & question_words)
            if overlap > best_score and overlap > 1:
                best_score = overlap
                best_answer = row['answer']
        if best_answer:
            return best_answer, 0.7, 'keyword'

        if crop:
            crop_answers = self.df[self.df['crop'].str.contains(crop, case=False, na=False)]
            if len(crop_answers) > 0:
                return crop_answers.iloc[0]['answer'], 0.6, 'crop_only'
        return None, 0, 'no_match'

    def get_intent_based_fallback(self, intent, entities):
        crop = next((v for t, v in entities if t == 'crop'), None)
        fallbacks = {
            'Cultivation': f"For {crop or 'crops'}, focus on soil preparation, quality seeds, balanced fertilizers, proper irrigation, and pest management.",
            'Fertilizer': f"For {crop or 'your crop'}, conduct a soil test first. Generally, apply NPK based on crop requirement.",
            'Pesticide': f"Monitor your {crop or 'crop'} regularly. Use recommended pesticides only when pest population reaches economic threshold level.",
            'Irrigation': f"Water requirement varies by {crop or 'crop'} and growth stage. Use water-efficient methods like drip or sprinkler irrigation.",
            'Soil': "Get your soil tested at the nearest soil testing laboratory. Add organic matter, practice crop rotation.",
            'Yield': f"Yield depends on variety, soil fertility, water management, and pest control.",
            'Diseases': f"Prevent {crop or 'crop'} diseases through resistant varieties, crop rotation, and field hygiene.",
            'HarvestTime': f"Harvest {crop or 'crops'} at proper maturity for best quality and storage life.",
            'SowingTime': f"Sow {crop or 'crops'} at the recommended time for your region.",
            'Greeting': "Assalam-o-Alaikum! I am your Kisan Guide Chatbot. How can I help you with your crops today?",
            'Wassup': "I am here to assist Pakistani farmers with their agriculture-related queries. What's on your mind?",
            'AskingHelp': "I'm here to help! You can ask me about crops, fertilizers, pesticides, soil, irrigation, and more.",
            'Wellness': "I'm doing well, thank you! I'm dedicated to providing the best agricultural advice.",
            'OutOfScope': "I am specialized in agriculture in Pakistan. Please ask me about crops, soil, or farming!",
            'Acknowledgment': "Sure! Is there anything else I can help you with regarding your farming?",
            'Farewell': "Allah Hafiz! Happy farming! Feel free to return anytime you need agriculture advice."
        }
        return fallbacks.get(intent, f"I can help you with agricultural topics like crop cultivation, fertilizers, or pest control.")

    def generate_response(self, query, farmer_id=None, session_id=None):
        """Main response generation"""
        try:
            if query.lower() in ['reset', 'clear context']:
                if farmer_id:
                    _reset_context(farmer_id, session_id)
                return {'answer': "Context cleared. How can I help you?", 'intent': 'ContextReset', 'requires_context': False}

            context = _get_context(farmer_id, session_id) if farmer_id else {'state': 'none', 'current_land': None}

            if context is None:
                context = {'state': 'none', 'current_land': None, 'current_session': None,
                          'pending_question': None, 'last_recommendations': [],
                          'last_mentioned_crop': None, 'last_intent': None,
                          'last_mentioned_neighbor': None, 'last_mentioned_activity': None}

            if context.get('state') in ['waiting_for_land', 'waiting_for_session'] and farmer_id:
                result = self._handle_context_response(query, farmer_id, context, session_id)
                if result:
                    return result

            if farmer_id and query.strip().isdigit() and len(query.strip()) <= 2:
                from Services.ChatbotHelper import get_farmer_lands
                user_lands = get_farmer_lands(farmer_id)
                if user_lands:
                    if context.get('state') in ['waiting_for_land', 'waiting_for_session'] or context.get('current_land'):
                        result = self._handle_context_response(query, farmer_id, context, session_id)
                        if result:
                            return result

                    last_rec = context.get('last_recommendations', [])
                    if last_rec:
                        try:
                            idx = int(query.strip()) - 1
                            if 0 <= idx < len(last_rec):
                                selected_crop = last_rec[idx].get('Name', '')
                                if selected_crop:
                                    _set_context(farmer_id, {
                                        'last_mentioned_crop': selected_crop,
                                        'state': 'active'
                                    }, session_id)
                                    return {'answer': f"You selected {selected_crop}. What would you like to know about it? (sowing time, cultivation details, suitability, etc.)", 'intent': 'CropRecommendation'}
                        except:
                            pass

            intent, intent_conf = self.get_intent(query)

            if intent_conf < 0.7 and farmer_id:
                rule_intent = self.detect_context_intent(query)
                if rule_intent:
                    intent = rule_intent
                    intent_conf = 0.8

            query_lower = query.lower()
            is_explanatory = any(word in query_lower for word in ['why', 'explain', 'detail', 'reason', 'how', 'explaination', 'what is', 'tell me'])
            is_quick = any(word in query_lower for word in ['just', 'quick', 'simple', 'fast', 'brief', 'name', 'list'])

            if farmer_id:
                has_grow_cultivate = any(word in query_lower for word in ['grow', 'cultivate', 'plant', 'sow'])
                has_land_word = any(word in query_lower for word in ['land', 'field', 'farm', 'it'])
                if has_grow_cultivate and has_land_word:
                    intent = 'CropRecommendation'
                    intent_conf = 0.95

                has_neighbor_word = any(word in query_lower for word in ['neighbor', 'neighbours', 'neighbors', 'nearby'])
                if has_neighbor_word and has_land_word:
                    intent = 'MyNeighbors'
                    intent_conf = 0.95

                has_session_word = any(word in query_lower for word in ['session', 'sessions', 'season', 'seasons'])
                has_last_word = any(word in query_lower for word in ['last', 'previous', 'past', 'before'])
                if has_session_word and has_last_word:
                    intent = 'PastSessions'
                    intent_conf = 0.95

                has_profitable_word = any(word in query_lower for word in ['profitable', 'profit', 'earn', 'earning', 'profitbake'])
                has_crop_word = any(word in query_lower for word in ['crop', 'crops'])
                if has_profitable_word and has_crop_word:
                    intent = 'ProfitablePastCrops'
                    intent_conf = 0.95

                is_good_for_me = ('good' in query_lower or 'suitable' in query_lower or 'right' in query_lower) and ('me' in query_lower or 'my' in query_lower or 'it' in query_lower or 'this' in query_lower)
                if is_good_for_me and not any(word in query_lower for word in ['wheat', 'rice', 'cotton', 'bajra', 'corn', 'maize']):
                    intent = 'CropSuitability'
                    intent_conf = 0.95

                if any(word in query_lower for word in ['when', 'time']) and any(word in query_lower for word in ['sow', 'plant']):
                    if context.get('last_mentioned_crop') or context.get('current_land'):
                        intent = 'SowingTime'
                        intent_conf = 0.95

                if any(word in query_lower for word in ['tell me about', 'info about', 'details about', 'what is']):
                    for crop in ['wheat', 'rice', 'cotton', 'bajra', 'bottle gourd', 'bitter gourd', 'chilies', 'cucumber', 'maize', 'corn']:
                        if crop in query_lower:
                            intent = 'Cultivation'
                            intent_conf = 0.95
                            break

                if any(phrase in query_lower for phrase in ['what if i do', 'what if i grow', 'can i do', 'should i do']):
                    for crop in ['wheat', 'rice', 'cotton', 'bajra', 'bottle gourd', 'bitter gourd', 'chilies', 'cucumber', 'maize', 'corn']:
                        if crop in query_lower:
                            intent = 'CropSuitability'
                            intent_conf = 0.95
                            break

                has_rain = any(word in query_lower for word in ['rain', 'rained', 'raining'])
                has_water_question = any(word in query_lower for word in ['water', 'irrigate', 'irrigation'])
                has_should_water = 'should' in query_lower or 'must' in query_lower
                if has_rain and has_water_question and has_should_water:
                    intent = 'Irrigation'
                    intent_conf = 0.95

                has_season = any(word in query_lower for word in ['rabi', 'kharif', 'season', 'next season', 'next rabi', 'next kharif', 'summer', 'winter'])
                has_grow_word = any(word in query_lower for word in ['grow', 'cultivate', 'sow', 'plant'])
                if has_season and has_grow_word:
                    intent = 'CropRecommendation'
                    intent_conf = 0.95

                has_activities = any(word in query_lower for word in ['activities performed', 'activity performed', 'performed on', 'history of'])
                has_most_profitable = 'most profitable' in query_lower or 'most profited' in query_lower
                if has_activities and has_most_profitable:
                    intent = 'PastActivities'
                    intent_conf = 0.95

                has_loss_word = any(word in query_lower for word in ['loss', 'lost', 'negative', 'not profitable', 'no profit', 'deficit'])
                if has_loss_word and has_crop_word:
                    intent = 'ProfitActivities'
                    intent_conf = 0.95

                has_remaining_word = any(word in query_lower for word in ['remaining', 'pending', 'left', 'upcoming', 'next activity'])
                has_activity_word = any(word in query_lower for word in ['activity', 'activities', 'task', 'tasks'])
                if has_remaining_word and (has_activity_word or has_crop_word):
                    intent = 'ActivityRecommendation'
                    intent_conf = 0.95

                has_most_word = any(word in query_lower for word in ['most', 'best', 'highest', 'top'])
                if has_profitable_word and has_crop_word and has_most_word:
                    intent = 'ProfitablePastCrops'
                    intent_conf = 0.95

            context_intents_priority = ['CropRecommendation', 'ActivityRecommendation', 'MyNeighbors', 'MyLands', 'MyCrops', 'MyActivities', 'FarmerInfo', 'PastActivities', 'NeighborInfo', 'PastSessions', 'NeighborPastSessions', 'ProfitActivities', 'ProfitablePastCrops', 'CropSuitability', 'HarvestTime', 'SowingTime', 'Irrigation']
            if farmer_id and intent in context_intents_priority and intent_conf > 0.7:
                return self._handle_context_intent(query, intent, farmer_id, context, session_id, is_quick, is_explanatory)

            if farmer_id and len(query.strip()) < 20:
                from Services.ChatbotHelper import get_farmer_lands, find_land_in_query
                user_lands = get_farmer_lands(farmer_id)
                if user_lands:
                    matched_land = find_land_in_query(query_lower, user_lands)
                    if matched_land:
                        intent = 'MyLands'
                        intent_conf = 0.95
                        return self._handle_context_intent(query, intent, farmer_id, context, session_id, is_quick, is_explanatory)

            mentioned_crop = None
            common_crops = ['wheat', 'rice', 'cotton', 'sugarcane', 'maize', 'potato', 'tomato', 'onion', 'mustard', 'gram', 'barley', 'sunflower', 'groundnut', 'chilies', 'bajra', 'bitter gourd', 'bottle gourd']
            for crop in common_crops:
                if crop in query_lower:
                    mentioned_crop = crop.capitalize()
                    break

            if mentioned_crop and farmer_id:
                _set_context(farmer_id, {
                    'state': context.get('state', 'active'),
                    'current_land': context.get('current_land'),
                    'current_session': context.get('current_session'),
                    'pending_question': context.get('pending_question'),
                    'last_recommendations': context.get('last_recommendations', []),
                    'last_mentioned_crop': mentioned_crop,
                    'last_intent': intent,
                    'last_mentioned_neighbor': context.get('last_mentioned_neighbor'),
                    'last_mentioned_activity': context.get('last_mentioned_activity'),
                    'conversation_history': context.get('conversation_history', [])
                }, session_id)

            goodbye_phrases = ['bye', 'goodbye', 'allah hafiz', 'khuda hafiz', 'see you', 'take care', 'tata', 'exit']
            if any(phrase in query_lower for phrase in goodbye_phrases):
                return {'answer': "Allah Hafiz! Happy farming! Feel free to return anytime you need agriculture advice.", 'intent': 'Farewell', 'intent_confidence': float(intent_conf)}

            acknowledgment_phrases = ['ok', 'okay', 'alright', 'all right', 'sure', 'yeah', 'yes', 'ya', 'okay thank', 'thanks', 'thank you', 'good', 'nice', 'cool', 'great', 'okay then', 'alright then', 'hmm', 'okkk', 'ok ok', 'cool then']
            if any(phrase in query_lower for phrase in acknowledgment_phrases):
                return {'answer': "Sure! Is there anything else I can help you with regarding your farming? Feel free to ask about crops, fertilizers, soil, irrigation, or any other agriculture topic.", 'intent': 'Acknowledgment', 'intent_confidence': float(intent_conf)}

            is_interactional = intent in self.INTERACTION_INTENTS
            is_low_confidence = intent_conf < self.CONFIDENCE_THRESHOLD

            if is_interactional or (is_low_confidence and intent == "OutOfScope"):
                answer = self.get_intent_based_fallback(intent, [])
                return {'answer': answer, 'intent': intent, 'intent_confidence': float(intent_conf), 'match_type': 'interactional'}

            entities = self.extract_entities(query)
            answer, confidence, match_type = self.search_knowledge_base(query, intent, entities)

            if not answer:
                answer = self.get_intent_based_fallback(intent, entities)
                confidence = 0.5
                match_type = 'fallback'

            is_unknown_intent = intent == "Unknown" or intent not in self.ALL_KNOWN_INTENTS
            is_low_confidence = intent_conf < self.CONFIDENCE_THRESHOLD

            if is_unknown_intent or intent == "OutOfScope" or (is_low_confidence and match_type == 'fallback'):
                return {'answer': "I am specialized in agriculture in Pakistan. Please ask me about crops, fertilizers, pesticides, soil, irrigation, farming activities, or your lands!", 'intent': 'OutOfScope', 'intent_confidence': float(intent_conf)}

            non_agri_keywords = ['love', 'hate', 'miss', 'happy', 'sad', 'angry', 'friend', 'family', 'school', 'movie', 'song', 'game', 'cricket', 'football', 'politics']
            if any(word in query_lower for word in non_agri_keywords) and intent in ['Cultivation', 'Unknown']:
                return {'answer': "I am specialized in agriculture in Pakistan. Please ask me about crops, fertilizers, pesticides, soil, irrigation, farming activities, or your lands!", 'intent': 'OutOfScope', 'intent_confidence': float(intent_conf)}

            if self.use_llm and answer and intent in self.AGRICULTURE_INTENTS:
                from Services.LLMService import get_llm_service
                llm = get_llm_service()
                original_answer = answer
                if llm.is_available():
                    try:
                        prompt = f"""You are a helpful agriculture assistant for farmers in Pakistan. User question: "{query}". Knowledge base answer: "{answer}". Rewrite the answer in a friendly, natural way. Keep all facts and numbers EXACTLY the same. Do NOT add new information. Keep it short (2-4 sentences). Rewritten answer:"""
                        answer = llm.generate_response(prompt, system_prompt="You are a helpful agriculture assistant.")
                        if not answer:
                            answer = original_answer
                    except:
                        answer = original_answer
                else:
                    answer = original_answer

            return {
                'query': query,
                'answer': answer,
                'intent': intent,
                'intent_confidence': float(intent_conf),
                'entities': entities,
                'confidence': confidence,
                'match_type': match_type
            }

        except Exception as e:
            import traceback
            print(f"Error in generate_response: {type(e).__name__}: {str(e)}")
            traceback.print_exc()
            return {'answer': "I'm having trouble processing your request. Please try again.", 'intent': 'Error'}

    def _handle_context_response(self, query, farmer_id, context, session_id=None):
        """Handle when user responds to a context request"""
        from Model.LandModel import LandModel
        from Services.ChatbotHelper import find_land_in_query, get_farmer_lands

        pending_question = context.get('pending_question')

        if not pending_question:
            last_intent = context.get('last_intent', 'CropRecommendation')
            if last_intent == 'CropRecommendation':
                pending_question = "what crops should I grow"
            elif last_intent == 'ActivityRecommendation':
                pending_question = "what activities should I do"
            elif last_intent == 'MyNeighbors':
                pending_question = "show my neighbors"
            else:
                pending_question = f"show my {last_intent.lower()}"

        last_intent = context.get('last_intent', 'CropRecommendation')
        if last_intent == 'MyNeighbors':
            resolved_intent = 'MyNeighbors'
        elif last_intent == 'ActivityRecommendation':
            resolved_intent = 'ActivityRecommendation'
        elif last_intent == 'MyLands':
            resolved_intent = 'MyLands'
        else:
            resolved_intent = 'CropRecommendation'

        user_lands = get_farmer_lands(farmer_id)
        selected_land = find_land_in_query(query.lower(), user_lands)

        query_lower = query.lower()
        is_pronoun = any(word in query_lower for word in ['it', 'this', 'that', 'these', 'those'])
        stored_land = context.get('current_land')

        if selected_land:
            _set_context(farmer_id, {
                'state': 'active',
                'current_land': {'land_id': selected_land.land_id, 'land_name': selected_land.land_name, 'soil_type': selected_land.soil_type},
                'current_session': None,
                'pending_question': None
            }, session_id)

            fresh_context = _get_context(farmer_id, session_id)
            return self._handle_context_intent(pending_question, resolved_intent, farmer_id, fresh_context, session_id)

        query_stripped = query.strip()
        if query_stripped.isdigit():
            idx = int(query_stripped) - 1
            if 0 <= idx < len(user_lands):
                selected_land = user_lands[idx]
                _set_context(farmer_id, {
                    'state': 'active',
                    'current_land': {'land_id': selected_land.land_id, 'land_name': selected_land.land_name, 'soil_type': selected_land.soil_type},
                    'current_session': None,
                    'pending_question': None
                }, session_id)
                fresh_context = _get_context(farmer_id, session_id)
                return self._handle_context_intent(pending_question, resolved_intent, farmer_id, fresh_context, session_id)

        if is_pronoun and stored_land:
            _set_context(farmer_id, {
                'state': 'active',
                'current_land': stored_land,
                'current_session': None,
                'pending_question': None
            }, session_id)
            fresh_context = _get_context(farmer_id, session_id)
            return self._handle_context_intent(pending_question, resolved_intent, farmer_id, fresh_context, session_id)

        return {'answer': "I couldn't find that land. Please specify the land name from the list.", 'intent': 'ContextGathering', 'requires_context': True}

    def _handle_context_intent(self, query, intent, farmer_id, context, session_id=None, is_quick=False, is_explanatory=False):
        """Handle context-aware intents"""
        from Services.ChatbotHelper import format_land_info, format_weather
        from Model.LandModel import LandModel
        from Model.NeighbourModel import NeighbourModel
        from Model.CultivationSessionModel import CultivationSessionModel
        from Model.CropModel import CropModel

        user_lands = get_farmer_lands(farmer_id)
        query_lower = query.lower()

        mentioned_crop = None
        all_crops = CropModel.query.all()
        for crop in all_crops:
            if crop.crop_name.lower() in query_lower:
                mentioned_crop = crop.crop_name
                break

        mentioned_land = find_land_in_query(query_lower, user_lands)
        if mentioned_land and 'land' in query_lower:
            intent = 'MyLands'

        if mentioned_crop:
            _set_context(farmer_id, {
                'state': context.get('state', 'active'),
                'current_land': context.get('current_land'),
                'current_session': context.get('current_session'),
                'pending_question': context.get('pending_question'),
                'last_recommendations': context.get('last_recommendations', []),
                'last_mentioned_crop': mentioned_crop
            }, session_id)
            context = _get_context(farmer_id, session_id)

        last_rec = context.get('last_recommendations', [])
        if last_rec and any(word in query_lower for word in ['bajra', 'bitter gourd', 'bottle gourd', 'chilies', 'crop', 'recommend']):
            if is_quick:
                crop_list = ", ".join([r['Name'] for r in last_rec[:4]])
                return {'answer': f"Recommended crops: {crop_list}", 'intent': intent}
            elif is_explanatory:
                return self._get_crop_recommendation(context.get('current_land', {}).get('land_id'), is_quick=is_quick, is_explanatory=is_explanatory, farmer_id=farmer_id, session_id=session_id)
            else:
                crop_list = ", ".join([r['Name'] for r in last_rec[:4]])
                return {'answer': f"Based on your land, I recommend: {crop_list}. These suit your soil and water conditions.", 'intent': intent}

        crop_followup_keywords = ['when', 'sow', 'plant', 'cultivate', 'grow', 'season', 'time', 'start', 'prepare']
        has_crop_followup = any(word in crop_followup_keywords for word in query_lower.split())

        crop_name = None
        if last_rec:
            for rec in last_rec:
                rec_name = rec.get('Name', '').lower()
                if rec_name in query_lower:
                    crop_name = rec.get('Name', '')
                    break

        if not crop_name:
            has_pronoun = any(word in query_lower for word in ['it', 'this', 'that', 'these', 'those'])
            if has_pronoun and has_crop_followup:
                if last_rec:
                    crop_name = last_rec[0].get('Name', '')
                elif context.get('last_mentioned_crop'):
                    crop_name = context.get('last_mentioned_crop')

        if not crop_name:
            for crop in all_crops:
                if crop.crop_name.lower() in query_lower:
                    crop_name = crop.crop_name
                    break

        if crop_name and has_crop_followup:
            sowing_info = get_crop_sowing_info(crop_name)
            if sowing_info:
                if is_quick:
                    return {'answer': f"{crop_name} is usually sown in {sowing_info.get('season', 'the appropriate season')}.", 'intent': 'CropSowingTime'}
                elif is_explanatory:
                    details = f"{crop_name} should be cultivated during {sowing_info.get('season', 'the appropriate season')}. "
                    details += f"The ideal time is {sowing_info.get('sowing_time', 'when weather conditions are suitable')}. "
                    details += f"Key tips: {sowing_info.get('tips', 'Follow recommended farming practices')}"
                    return {'answer': details, 'intent': 'CropSowingTime'}
                else:
                    return {'answer': f"You should sow {crop_name} in {sowing_info.get('season', 'the appropriate season')}. {sowing_info.get('tips', '')}", 'intent': 'CropSowingTime'}

        if has_crop_followup and not crop_name:
            for crop in all_crops:
                if crop.crop_name.lower() in query_lower:
                    crop_name = crop.crop_name
                    break
            if crop_name:
                sowing_info = get_crop_sowing_info(crop_name)
                if sowing_info:
                    if is_quick:
                        return {'answer': f"{crop_name} is usually sown in {sowing_info.get('season', 'the appropriate season')}.", 'intent': 'CropSowingTime'}
                    elif is_explanatory:
                        details = f"{crop_name} should be cultivated during {sowing_info.get('season', 'the appropriate season')}. "
                        details += f"The ideal time is {sowing_info.get('sowing_time', 'when weather conditions are suitable')}. "
                        details += f"Key tips: {sowing_info.get('tips', 'Follow recommended farming practices')}"
                        return {'answer': details, 'intent': 'CropSowingTime'}
                    else:
                        return {'answer': f"You should sow {crop_name} in {sowing_info.get('season', 'the appropriate season')}. {sowing_info.get('tips', '')}", 'intent': 'CropSowingTime'}

        if intent == 'MyLands':
            target_land = find_land_in_query(query_lower, user_lands)
            if target_land:
                _set_context(farmer_id, {
                    'state': 'active',
                    'current_land': {'land_id': target_land.land_id, 'land_name': target_land.land_name, 'soil_type': target_land.soil_type},
                    'current_session': None,
                    'pending_question': None
                }, session_id)

                if 'weather' in query_lower:
                    weather_response = format_weather(target_land)
                    if weather_response:
                        return {'answer': weather_response, 'intent': intent}
                    return {'answer': f"Could not fetch weather for {target_land.land_name}.", 'intent': intent}

                return {'answer': format_land_info(target_land), 'intent': intent}

            if not user_lands:
                return {'answer': "You don't have any lands registered yet.", 'intent': intent}

            return {'answer': get_land_names_response(user_lands), 'intent': intent}

        elif intent == 'MyCrops':
            crops_response = get_farmer_crops(farmer_id)
            if not crops_response:
                return {'answer': "You don't have any active crops. Start a new cultivation session!", 'intent': intent}
            return {'answer': crops_response, 'intent': intent}

        elif intent == 'CropRecommendation':
            current_land = context.get('current_land')

            if not current_land and user_lands:
                if len(user_lands) == 1:
                    land = user_lands[0]
                    _set_context(farmer_id, {'state': 'active', 'current_land': {'land_id': land.land_id, 'land_name': land.land_name, 'soil_type': land.soil_type}, 'current_session': None, 'pending_question': None}, session_id)
                    return self._get_crop_recommendation(land.land_id, is_quick=is_quick, is_explanatory=is_explanatory)
                else:
                    for land in user_lands:
                        if land.land_name.lower() in query_lower:
                            _set_context(farmer_id, {'state': 'active', 'current_land': {'land_id': land.land_id, 'land_name': land.land_name, 'soil_type': land.soil_type}, 'current_session': None, 'pending_question': None}, session_id)
                            return self._get_crop_recommendation(land.land_id, is_quick=is_quick, is_explanatory=is_explanatory, farmer_id=farmer_id, session_id=session_id)

            if not user_lands:
                return {'answer': "You don't have any lands registered to recommend crops for.", 'intent': intent}

            if not current_land:
                _set_context(farmer_id, {'state': 'waiting_for_land', 'current_land': None, 'current_session': None, 'pending_question': query, 'last_intent': intent}, session_id)
                response = "On which land would you like to grow crops? Here are your lands:\n"
                for i, land in enumerate(user_lands, 1):
                    response += f"{i}. {land.land_name} ({land.land_in_acres} acres, {land.soil_type} soil)\n"
                return {'answer': response, 'intent': intent, 'requires_context': True}

            return self._get_crop_recommendation(current_land['land_id'], is_quick=is_quick, is_explanatory=is_explanatory)

        elif intent == 'MyNeighbors':
            user_lands_all = LandModel.query.filter_by(farmer_id=farmer_id).all()

            target_land = None
            for land in user_lands_all:
                if land.land_name.lower() in query_lower:
                    target_land = land
                    break

            if not target_land and context.get('current_land'):
                stored_land_name = context.get('current_land', {}).get('land_name', '').lower()
                for land in user_lands_all:
                    if land.land_name.lower() == stored_land_name:
                        target_land = land
                        break

            if not target_land:
                if len(user_lands_all) == 1:
                    target_land = user_lands_all[0]
                else:
                    _set_context(farmer_id, {
                        'state': 'waiting_for_land',
                        'current_land': None,
                        'current_session': None,
                        'pending_question': query,
                        'last_intent': intent
                    }, session_id)
                    response = "Which of YOUR lands' neighbors would you like to know about? Here are your lands:\n"
                    for i, land in enumerate(user_lands_all, 1):
                        response += f"{i}. {land.land_name}\n"
                    return {'answer': response, 'intent': intent, 'requires_context': True}

            land_id = target_land.land_id

            neighbors = NeighbourModel.query.filter(
                ((NeighbourModel.land_id == land_id) | (NeighbourModel.neighbour_land_id == land_id)),
                NeighbourModel.status == 1
            ).all()

            if not neighbors:
                return {'answer': f"No neighbors found for {target_land.land_name}.", 'intent': intent}

            response = f"Neighbors of {target_land.land_name}:\n"
            for i, neighbor in enumerate(neighbors, 1):
                other_land_id = neighbor.neighbour_land_id if neighbor.neighbour_land_id != land_id else neighbor.land_id
                neighbor_land = LandModel.query.get(other_land_id)

                neighbor_sessions = CultivationSessionModel.query.filter_by(land_id=other_land_id, session_status='Sown', is_public=1).all()
                neighbor_crops = []
                for session in neighbor_sessions:
                    if session.crop_id:
                        crop = CropModel.query.get(session.crop_id)
                        if crop:
                            neighbor_crops.append(crop.crop_name)
                    if session.seed_name:
                        neighbor_crops.append(session.seed_name)

                crops_str = ", ".join(neighbor_crops) if neighbor_crops else "No active crop"
                response += f"{i}. {neighbor_land.land_name if neighbor_land else 'Unknown'}: {crops_str}\n"

            return {'answer': response, 'intent': intent}

        elif intent == 'ActivityRecommendation' or intent == 'MyActivities':
            target_land = find_land_in_query(query_lower, user_lands)
            specific_land = target_land.land_name if target_land else None
            response = get_remaining_activities(farmer_id, specific_land)
            return {'answer': response, 'intent': intent}

        elif intent == 'PastActivities':
            has_most_profitable = 'most profitable' in query_lower or 'most profited' in query_lower
            if has_most_profitable:
                response = get_profitable_past_crops(farmer_id)
                return {'answer': response, 'intent': intent}

            has_loss = any(word in query_lower for word in ['loss', 'lost', 'negative', 'not profitable', 'unprofitable'])
            if has_loss:
                response = get_activities_for_loss_crops(farmer_id)
                return {'answer': response, 'intent': intent}

            response = get_past_activities(farmer_id, None)
            return {'answer': response, 'intent': intent}

        elif intent == 'FarmerInfo':
            response = get_farmer_profile(farmer_id)
            if not response:
                return {'answer': "Farmer not found.", 'intent': intent}
            return {'answer': response, 'intent': intent}

        elif intent == 'NeighborInfo':
            neighbor_land_name = None
            for nl in get_neighbor_info(farmer_id):
                if nl.land_name.lower() in query_lower:
                    neighbor_land_name = nl.land_name
                    break
            if neighbor_land_name:
                response = get_neighbor_owner_info(farmer_id, neighbor_land_name)
            else:
                active_sessions = get_active_sessions_for_farmer(farmer_id)
                active_land_ids = set(s.land_id for s in active_sessions)
                user_lands_filtered = [l for l in user_lands if l.land_id in active_land_ids]
                include_names = 'name' in query_lower or 'owner' in query_lower or 'who' in query_lower
                response = format_neighbors(farmer_id, include_names, user_lands_filtered if user_lands_filtered else None)
            return {'answer': response, 'intent': intent}

        elif intent == 'PastSessions':
            target_land = find_land_in_query(query_lower, user_lands)
            if target_land:
                response = get_my_past_sessions_formatted(farmer_id, target_land.land_id)
                if not response:
                    return {'answer': f"No past sessions found for {target_land.land_name}.", 'intent': intent}
                return {'answer': response, 'intent': intent}
            else:
                response = get_my_past_sessions_formatted(farmer_id)
                if not response:
                    return {'answer': "No past crop sessions found for your lands.", 'intent': intent}
                return {'answer': response, 'intent': intent}

        elif intent == 'NeighborPastSessions':
            response = handle_neighbor_past_sessions(farmer_id, query_lower)
            return {'answer': response, 'intent': intent}

        elif intent == 'ProfitActivities':
            has_loss = any(word in query_lower for word in ['loss', 'lost', 'negative', 'not profitable', 'no profit', 'deficit'])
            has_activities_req = 'activity' in query_lower or 'perform' in query_lower

            if has_loss and has_activities_req:
                response = get_activities_for_loss_crops(farmer_id)
                return {'answer': response, 'intent': intent}

            if has_loss:
                response = get_loss_crops(farmer_id)
                return {'answer': response, 'intent': intent}

            if has_activities_req:
                target_land = find_land_in_query(query_lower, user_lands)
                land_name = target_land.land_name if target_land else None
                response = get_activities_for_profitable_sessions(farmer_id, land_name)
                return {'answer': response, 'intent': intent}

            target_land = find_land_in_query(query_lower, user_lands)
            land_name = target_land.land_name if target_land else None
            response = get_activities_for_profitable_sessions(farmer_id, land_name)
            return {'answer': response, 'intent': intent}

        elif intent == 'ProfitablePastCrops':
            if 'neighbor' in query_lower:
                sessions = get_neighbor_past_sessions(farmer_id, limit=5)
                profitable = [s for s in sessions if s.get('is_profit') == 1]
                if not profitable:
                    return {'answer': "No profitable crops found for your neighbors.", 'intent': intent}
                response = "Your neighbors' profitable crops from past sessions:\n"
                for i, s in enumerate(profitable, 1):
                    response += f"  • {s['crop_name']} on {s['land_name']}"
                    if s.get('amount_per_acre'):
                        response += f" (Earned: {s['amount_per_acre']})"
                    response += "\n"
                return {'answer': response, 'intent': intent}

            has_most_word = any(word in query_lower for word in ['most', 'single', 'only', 'best', 'highest', 'top'])
            has_activities_word = 'activities' in query_lower or 'activity' in query_lower

            if has_most_word and not has_activities_word:
                response = get_profitable_past_crops(farmer_id)
                lines = response.split('\n')
                profitable_lines = [l for l in lines if 'Earned:' in l]
                if profitable_lines:
                    first_crop = profitable_lines[0].strip()
                    return {'answer': f"Your most profitable crop: {first_crop}", 'intent': intent}
                return {'answer': response, 'intent': intent}

            if has_activities_word and has_most_word:
                response = get_activities_for_profitable_sessions(farmer_id, None)
                return {'answer': response, 'intent': intent}

            response = get_profitable_past_crops(farmer_id)
            return {'answer': response, 'intent': intent}

        elif intent == 'CropSuitability':
            current_land = context.get('current_land')
            if not current_land:
                current_land_obj = find_land_in_query(query_lower, user_lands)
                if current_land_obj:
                    current_land = {'land_id': current_land_obj.land_id, 'land_name': current_land_obj.land_name, 'soil_type': current_land_obj.soil_type}

            if not current_land:
                if len(user_lands) == 1:
                    land = user_lands[0]
                    current_land = {'land_id': land.land_id, 'land_name': land.land_name, 'soil_type': land.soil_type}
                else:
                    _set_context(farmer_id, {'state': 'waiting_for_land', 'current_land': None, 'current_session': None, 'pending_question': query, 'last_intent': intent}, session_id)
                    response = "On which land would you like to check crop suitability? Here are your lands:\n"
                    for i, land in enumerate(user_lands, 1):
                        response += f"{i}. {land.land_name} ({land.soil_type} soil)\n"
                    return {'answer': response, 'intent': intent, 'requires_context': True}

            crop_name = None
            for crop in all_crops:
                if crop.crop_name.lower() in query_lower:
                    crop_name = crop.crop_name
                    break

            if not crop_name and context.get('last_mentioned_crop'):
                crop_name = context.get('last_mentioned_crop')

            if not crop_name and context.get('last_recommendations'):
                for rec in context.get('last_recommendations'):
                    if rec.get('Name', '').lower() in query_lower:
                        crop_name = rec.get('Name', '')
                        break

            if not crop_name:
                return {'answer': "Which crop would you like to check suitability for? Please specify the crop name.", 'intent': intent}

            result = check_crop_suitability(current_land['land_id'], crop_name)
            if not result:
                return {'answer': f"Could not check suitability for {crop_name}. Please try another crop.", 'intent': intent}

            response = format_crop_suitability_response(current_land, crop_name, result)

            _set_context(farmer_id, {
                'state': 'active',
                'current_land': current_land,
                'last_mentioned_crop': crop_name
            }, session_id)

            return {'answer': response, 'intent': intent}

        elif intent == 'HarvestTime':
            crop_name = None
            for crop in all_crops:
                if crop.crop_name.lower() in query_lower:
                    crop_name = crop.crop_name
                    break
            if not crop_name:
                crop_name = context.get('last_mentioned_crop')

            response = get_harvest_info_for_active_crop(farmer_id, crop_name)
            if response:
                return {'answer': response, 'intent': intent}
            return {'answer': self.get_intent_based_fallback(intent, []), 'intent': intent}

        elif intent == 'Irrigation':
            response = get_irrigation_advice(farmer_id, query_lower)
            if response:
                return {'answer': response, 'intent': intent}
            return {'answer': self.get_intent_based_fallback(intent, []), 'intent': intent}

        return None

    def _get_crop_recommendation(self, land_id, is_quick=False, is_explanatory=False, farmer_id=None, session_id=None):
        """Use RecommendationController for crop recommendations"""
        from Model.LandModel import LandModel
        from Model.CityModel import CityModel
        from flask import json
        from Controller.RecommendationController import RecommendationController

        land = LandModel.query.get(land_id)
        if not land:
            return {'answer': "Land not found.", 'intent': 'CropRecommendation'}

        if farmer_id:
            _set_context(farmer_id, {
                'state': 'active',
                'current_land': {'land_id': land.land_id, 'land_name': land.land_name, 'soil_type': land.soil_type},
                'current_session': None,
                'pending_question': None,
                'last_recommendations': []
            }, session_id)

        try:
            city_name = None
            province_name = None
            if land.city_id:
                city = CityModel.query.get(land.city_id)
                if city:
                    city_name = city.city_name
                    if city.province_rls:
                        province_name = city.province_rls.province_name

            response, status_code = RecommendationController.get_recommendations(land_id)

            if status_code != 200:
                return {'answer': "Could not get recommendations.", 'intent': 'CropRecommendation'}

            data = json.loads(response.data)

            if not data.get('data') or not data['data'].get('recommendations'):
                return {'answer': f"No crop recommendations available for this land in current season.", 'intent': 'CropRecommendation'}

            recommendations = data['data']['recommendations']
            land_profile = data['data'].get('land_profile', {})
            season = data['data'].get('environmental_context', {}).get('Season', 'Current')

            if is_quick:
                crop_list = []
                for rec in recommendations[:4]:
                    crop_name = rec.get('Name', rec.get('crop_name', 'Unknown'))
                    rationale = rec.get('rationale', '')
                    reasons = [r.strip() for r in rationale.split('|') if r.strip()]
                    brief_reason = reasons[0] if reasons else "Suitable for your land"
                    crop_list.append(f"{crop_name} ({brief_reason})")

                response_text = f"Based on your land in {city_name or 'your area'}, I recommend: {', '.join(crop_list)}."
                if farmer_id:
                    _set_context(farmer_id, {'last_recommendations': recommendations[:4]}, session_id)
                return {'answer': response_text, 'intent': 'CropRecommendation', 'recommendations': recommendations[:4]}

            if is_explanatory:
                location_info = f"{city_name}" if city_name else ""
                if province_name:
                    location_info += f", {province_name}"

                response_text = f"🌾 Crop Recommendations for {land.land_name}\n"
                response_text += f"   📍 Location: {location_info if location_info else 'N/A'}\n"
                response_text += f"   🌍 Soil: {land.soil_type}\n"
                response_text += f"   💧 Water: {land.source_of_water}\n"
                response_text += f"   📅 Season: {season}\n"

                if land_profile.get('previous_crop'):
                    response_text += f"   🌱 Previous Crop: {land_profile['previous_crop']}\n"

                response_text += "\n" + "="*50 + "\n"

                for i, rec in enumerate(recommendations[:4], 1):
                    crop_name = rec.get('Name', rec.get('crop_name', 'Unknown'))
                    confidence = rec.get('confidence_score', 0)
                    rationale = rec.get('rationale', '')

                    stars = "⭐" * (confidence // 20)

                    response_text += f"\n{i}. {crop_name} {stars}\n"
                    response_text += f"   Confidence: {confidence}%\n"

                    reasons = [r.strip() for r in rationale.split('|') if r.strip()]
                    if reasons:
                        response_text += "   Why: "
                        key_reasons = reasons[:3]
                        response_text += " • ".join(key_reasons) + "\n"

                    if rec.get('suggested_actions'):
                        response_text += f"   💡 Tip: {rec['suggested_actions'][0]}\n"

                response_text += "\n" + "="*50
                response_text += "\n\nFor more details about any crop, just ask!"

                if farmer_id:
                    _set_context(farmer_id, {'last_recommendations': recommendations[:4]}, session_id)
                return {'answer': response_text, 'intent': 'CropRecommendation', 'recommendations': recommendations[:4]}

            response_text = f"Here are the best crops for your land '{land.land_name}' in {province_name or 'your region'}:\n\n"

            for i, rec in enumerate(recommendations[:4], 1):
                crop_name = rec.get('Name', rec.get('crop_name', 'Unknown'))
                confidence = rec.get('confidence_score', 0)
                rationale = rec.get('rationale', '')

                reasons = [r.strip() for r in rationale.split('|') if r.strip()]
                main_reason = reasons[0] if reasons else "Suitable for your conditions"

                if main_reason.startswith('Region'):
                    main_reason = main_reason.replace('Region suitable: ', '').replace('.', '')
                    main_reason = f"This crop grows well in {main_reason}."
                elif main_reason.startswith('Ideal'):
                    main_reason = main_reason.replace('Ideal soil match', 'Your soil type is ideal')

                response_text += f"{i}. {crop_name} - {main_reason}\n"

                if rec.get('suggested_actions'):
                    response_text += f"   💡 {rec['suggested_actions'][0]}\n"
                response_text += "\n"

            response_text += "Ask me about any specific crop for more details!"

            if farmer_id:
                _set_context(farmer_id, {'last_recommendations': recommendations[:4]}, session_id)
            return {'answer': response_text, 'intent': 'CropRecommendation', 'recommendations': recommendations[:4]}

        except Exception as e:
            return {'answer': f"Could not generate recommendations: {str(e)}", 'intent': 'CropRecommendation'}

    def chat(self, query):
        print("\n" + "=" * 70)
        print("Kisan Guide CHATBOT")
        print("=" * 70)
        print(f"Knowledge Base: {len(self.df)} Q&A pairs")
        print("=" * 70)

        if query.lower() in ['quit', 'exit', 'bye', 'q', 'allah hafiz']:
            print("\nBot: Allah Hafiz! Happy farming!")
            return

        response = self.generate_response(query)
        print(f"\n Bot: {response['answer']}")
        print(f"\n    Intent: {response['intent']}")


def main(question):
    chatbot = AgricultureRAGChatbot(use_llm=False)
    chatbot.chat(question)