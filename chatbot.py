"""Integrated context-aware chatbot enhancement for AgricultureRAGChatbot"""

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

_context_store = {}
_context_lock = __import__('threading').Lock()

def _load_context_from_chat(farmer_id, session_id):
    """Load context from previous chat history"""
    try:
        from Model.ChatModel import ChatModel
        from Model.ChatSessionModel import ChatSessionModel
        
        # Get recent chats for this session (last 10)
        chats = ChatModel.query.join(ChatSessionModel).filter(
            ChatSessionModel.Farmer_id == farmer_id,
            ChatSessionModel.chat_session_id == session_id
        ).order_by(ChatModel.time_stamp.desc()).limit(10).all()
        
        # Work backwards to find last set context
        for chat in reversed(chats):
            # Check if this was a context-setting intent
            ctx_intents = ['MyLands', 'CropRecommendation', 'MyNeighbors', 'MyCrops']
            if chat.chat_type in ctx_intents:
                # Parse land info from answer - look for numbered lands
                import re
                land_matches = re.findall(r'\d+\.\s*([^\n]+)', chat.answer)
                if land_matches:
                    # Get actual lands
                    from Model.LandModel import LandModel
                    lands = LandModel.query.filter_by(farmer_id=farmer_id, land_Status=1).all()
                    for land in lands:
                        if land.land_name.lower() in chat.answer.lower():
                            return {
                                'state': 'active',
                                'current_land': {'land_id': land.land_id, 'land_name': land.land_name, 'soil_type': land.soil_type},
                                'current_session': None,
                                'pending_question': None
                            }
        
        return None
    except Exception as e:
        print(f"Context load error: {e}")
        return None

def _get_context(farmer_id, session_id=None):
    key = f"chatbot_context_{farmer_id}_{session_id}" if session_id else f"chatbot_context_{farmer_id}"
    
    # Try in-memory first
    context = _context_store.get(key, None)
    if context and context.get('state') != 'none':
        return context
    
    # Try loading from chat history
    if session_id:
        loaded = _load_context_from_chat(farmer_id, session_id)
        if loaded:
            _context_store[key] = loaded
            return loaded
    
    return {
        'state': 'none',
        'current_land': None,
        'current_session': None,
        'pending_question': None
    }

def _set_context(farmer_id, context, session_id=None):
    key = f"chatbot_context_{farmer_id}_{session_id}" if session_id else f"chatbot_context_{farmer_id}"
    with _context_lock:
        _context_store[key] = context

def _reset_context(farmer_id, session_id=None):
    _set_context(farmer_id, {
        'state': 'none',
        'current_land': None,
        'current_session': None,
        'pending_question': None
    }, session_id)

# Singleton instance to prevent reloading on every request
_chatbot_instance = None

def get_chatbot(use_llm=False):
    """Get or create singleton chatbot instance"""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = AgricultureRAGChatbot(use_llm=use_llm)
    return _chatbot_instance

class AgricultureRAGChatbot:
    
    CONTEXT_INTENTS = {
        # Priority: More specific first
        'CropRecommendation': ['what should i grow', 'which crop', 'recommend crop', 'what to cultivate', 'what to grow', 'suggest crop', 'best crop', 'what i should plant', 'what to plant', 'which crop to grow', 'what crop should i', 'what to grow on'],
        'ActivityRecommendation': ['what should i do now', 'what to do today', 'next activity', 'current task', 'what i should do'],
        'MyNeighbors': ['neighbor', 'neighbours', 'neighbors', 'neighbor doing', 'nearby farmers', 'neighbors growing', 'neighbor crops', 'neighbor planted'],
        'MyLands': ['my lands', 'my fields', 'list of lands', 'weather of land'],
        'MyCrops': ['my crops', 'what crops i have', 'what am i growing', 'my cultivation'],
        'MyActivities': ['my activities', 'my tasks', 'things to do'],
    }

    def __init__(self, use_llm=True):
        print(" Loading Agriculture RAG Chatbot...")
        self.ps = PorterStemmer()
        self.use_llm = use_llm
        self._llm_loaded = False
        self.model = None
        self.tokenizer = None
        self.device = None
        
        self.AGRICULTURE_INTENTS = [
            "Cultivation", "Fertilizer", "Pesticide", "Irrigation", 
            "Soil", "Yield", "Diseases", "Varieties", 
            "MarketPrice", "HarvestTime", "SowingTime", "Weather"
        ]
        self.INTERACTION_INTENTS = [
            "Greeting", "Wassup", "Wellness", "AskingHelp", "OutOfScope"
        ]
        self.CONFIDENCE_THRESHOLD = 0.6
        
        self._load_models()
        self.load_knowledge_base()
        self.setup_embeddings()
        if self.use_llm:
            print("LLM paraphrasing enabled (will load on first query)")

    def _load_models(self):
        try:
            self.intent_model = load_model('saved_state/intent_model.h5', compile=False)
            self.intent_cv = pickle.load(open('saved_state/IntentCountVectorizer.sav', 'rb'))
            self.intent_label_map = pickle.load(open('saved_state/intent_label_map.sav', 'rb'))
            self.idx_to_intent = {v: k for k, v in self.intent_label_map.items()}
            
            self.entity_model = pickle.load(open('saved_state/entity_model.sav', 'rb'))
            self.entity_cv = pickle.load(open('saved_state/EntityCountVectorizer.sav', 'rb'))
            self.entity_label_map = pickle.load(open('saved_state/entity_label_map.sav', 'rb'))
            self.idx_to_entity = {v: k for k, v in self.entity_label_map.items()}
            print("Intent & Entity models loaded")
        except Exception as e:
            print(f"Warning: Could not load ML models: {e}")
            self.intent_model = None

    def load_knowledge_base(self):
        try:
            potential_paths = ["data/agriculture_knowledge_base_combined.csv"]
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
        try:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            index_path = 'saved_state/faiss_index.idx'
            embeddings_path = 'saved_state/embeddings.npy'
            
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

    def setup_llm(self):
        if self._llm_loaded:
            return
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            print(" Loading local HuggingFace LLM (TinyLlama)...")
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.llm_model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
            self.tokenizer = AutoTokenizer.from_pretrained(self.llm_model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.llm_model_name,
                dtype=torch.float16 if self.device == "cuda" else torch.float32
            ).to(self.device)
            self.model.eval()
            self._llm_loaded = True
            print(f"Local LLM loaded successfully")
        except Exception as e:
            print(f"Could not load local LLM: {e}")
            self.use_llm = False

    def paraphrase_with_llm(self, query, answer):
        if not getattr(self, "use_llm", False):
            return answer
        if not self._llm_loaded:
            self.setup_llm()
        if not self.model:
            return answer
        import torch
        
        prompt = f"""You are a helpful agriculture assistant for farmers in Pakistan. User question: "{query}". Knowledge base answer: "{answer}". Rewrite the answer in a friendly, natural way. Keep all facts and numbers EXACTLY the same. Do NOT add new information. Keep it short (2-4 sentences). Rewritten answer:"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(self.device)
        with torch.no_grad():
            output = self.model.generate(**inputs, max_new_tokens=120, temperature=0.7, top_p=0.9, do_sample=True, pad_token_id=self.tokenizer.eos_token_id)
            decoded = self.tokenizer.decode(output[0], skip_special_tokens=True)
            if "Rewritten answer:" in decoded:
                rewritten = decoded.split("Rewritten answer:")[-1].strip()
            else:
                rewritten = decoded.strip()
            return rewritten if rewritten else answer

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
            'Greeting': ['hello', 'hi', 'hey', 'namaste'],
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
        text_lower = text.lower()
        
        # Check in prioritized order from CONTEXT_INTENTS
        # More specific intents first
        priority_order = ['CropRecommendation', 'ActivityRecommendation', 'MyNeighbors', 'MyLands', 'MyCrops', 'MyActivities']
        
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
            'OutOfScope': "I am specialized in agriculture in Pakistan. Please ask me about crops, soil, or farming!"
        }
        return fallbacks.get(intent, f"I can help you with agricultural topics like crop cultivation, fertilizers, or pest control.")

    def generate_response(self, query, farmer_id=None, session_id=None):
        """Main response generation - supports both regular and context-aware queries"""
        
        if query.lower() in ['reset', 'clear context']:
            if farmer_id:
                _reset_context(farmer_id, session_id)
            return {'answer': "Context cleared. How can I help you?", 'intent': 'ContextReset', 'requires_context': False}
        
        context = _get_context(farmer_id, session_id) if farmer_id else {'state': 'none', 'current_land': None}
        
        if context.get('state') in ['waiting_for_land', 'waiting_for_session'] and farmer_id:
            result = self._handle_context_response(query, farmer_id, context, session_id)
            if result:
                return result
        
        context_intent = self.detect_context_intent(query)
        
        if context_intent and farmer_id:
            return self._handle_context_intent(query, context_intent, farmer_id, context, session_id)
        
        intent, intent_conf = self.get_intent(query)
        
        # Check if query mentions a specific crop (indicates user wants info about that crop)
        from crop_recommendation import RuleBasedCropEngine
        engine = RuleBasedCropEngine()
        mentioned_crop = None
        query_lower = query.lower()
        for crop in engine.crop_knowledge_base.keys():
            if crop.lower() in query_lower:
                mentioned_crop = crop
                break
        
        # If crop is mentioned AND intent is CropRecommendation, change to Cultivation
        if mentioned_crop and intent == 'CropRecommendation':
            intent = 'Cultivation'
        
        # If ML detected a context intent with high confidence, use it
        context_intents_priority = ['CropRecommendation', 'ActivityRecommendation', 'MyNeighbors', 'MyLands', 'MyCrops', 'MyActivities']
        if farmer_id and intent in context_intents_priority and intent_conf > 0.9:
            return self._handle_context_intent(query, intent, farmer_id, context, session_id)
        
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
        
        if self.use_llm and answer and intent in self.AGRICULTURE_INTENTS:
            original_answer = answer
            answer = self.paraphrase_with_llm(query, answer)
            if not answer:
                answer = original_answer
        
        return {
            'query': query,
            'answer': answer,
            'intent': intent,
            'intent_confidence': float(intent_conf),
            'entities': entities,
            'match_type': match_type,
            'confidence': confidence
        }

    def _handle_context_response(self, query, farmer_id, context, session_id=None):
        """Handle when user responds to a context request"""
        from Model.LandModel import LandModel
        
        waiting_state = context.get('state')
        pending_question = context.get('pending_question')
        
        lands = LandModel.query.filter_by(farmer_id=farmer_id, land_Status=1).all()
        selected_land = None
        for land in lands:
            if land.land_name.lower() in query.lower():
                selected_land = land
                break
        
        if selected_land:
            _set_context(farmer_id, {
                'state': 'active',
                'current_land': {'land_id': selected_land.land_id, 'land_name': selected_land.land_name, 'soil_type': selected_land.soil_type},
                'current_session': None,
                'pending_question': None
            }, session_id)
            
            # Get fresh context and handle the original pending question
            fresh_context = _get_context(farmer_id, session_id)
            return self._handle_context_intent(pending_question or query, self.detect_context_intent(pending_question or query), farmer_id, fresh_context, session_id)
        
        # Check if response is a land number
        query_stripped = query.strip()
        if query_stripped.isdigit():
            idx = int(query_stripped) - 1
            if 0 <= idx < len(lands):
                selected_land = lands[idx]
                _set_context(farmer_id, {
                    'state': 'active',
                    'current_land': {'land_id': selected_land.land_id, 'land_name': selected_land.land_name, 'soil_type': selected_land.soil_type},
                    'current_session': None,
                    'pending_question': None
                }, session_id)
                fresh_context = _get_context(farmer_id, session_id)
                return self._handle_context_intent(pending_question or query, self.detect_context_intent(pending_question or query), farmer_id, fresh_context, session_id)
        
        return {'answer': "I couldn't find that land. Please specify the land name from the list.", 'intent': 'ContextGathering', 'requires_context': True}

    def _handle_context_intent(self, query, intent, farmer_id, context, session_id=None):
        """Handle context-aware intents using EXISTING services"""
        # Debug
        print(f"[DEBUG _handle_context_intent] query={query}, intent={intent}")
        
        from Model.LandModel import LandModel
        from Model.CultivationSessionModel import CultivationSessionModel
        from Model.CropModel import CropModel
        from Model.NeighbourModel import NeighbourModel
        from Services.ActivitySuggestionService import ActivitySuggestionService
        
        print(f"[DEBUG] Loading lands for farmer_id={farmer_id}")
        lands = LandModel.query.filter_by(farmer_id=farmer_id, land_Status=1).all()
        print(f"[DEBUG] Found {len(lands)} lands")
        land_ids = [l.land_id for l in lands]
        
        if intent == 'MyLands':
            # Add debug
            print(f"[DEBUG MyLands] query: {query}, lands count: {len(lands)}")
            
            # Check for weather query first
            is_weather_query = 'weather' in query.lower()
            
            # Try to find specific land from query
            target_land = None
            query_lower = query.lower()
            print(f"[DEBUG] Looking for land in: {query_lower}")
            for land in lands:
                print(f"[DEBUG] Checking land: {land.land_name.lower()}")
                if land.land_name.lower() in query_lower:
                    target_land = land
                    print(f"[DEBUG] Found land: {land.land_name}")
                    break
            
            if target_land:
                # Set context for this land
                _set_context(farmer_id, {
                    'state': 'active',
                    'current_land': {'land_id': target_land.land_id, 'land_name': target_land.land_name, 'soil_type': target_land.soil_type},
                    'current_session': None,
                    'pending_question': None
                }, session_id)
                
                if is_weather_query:
                    # Get weather for this land
                    from Services.WeatherService import WeatherService
                    try:
                        if target_land.city_rls:
                            weather = WeatherService.get_weather(target_land.city_rls.city_name)
                            if weather:
                                response = f"Weather for {target_land.land_name}:\n"
                                response += f"Location: {weather.get('location', target_land.city_rls.city_name)}\n"
                                response += f"Temperature: {weather.get('temperature', 'N/A')}\n"
                                response += f"Condition: {weather.get('condition', 'N/A')}\n"
                                response += f"Humidity: {weather.get('humidity', 'N/A')}\n"
                                response += f"Wind: {weather.get('wind', 'N/A')}\n"
                                return {'answer': response, 'intent': intent}
                    except Exception as e:
                        return {'answer': f"Could not fetch weather: {str(e)}", 'intent': intent}
                
                # Show specific land info
                response = f"Land: {target_land.land_name}\n"
                response += f"Size: {target_land.land_in_acres} acres\n"
                response += f"Soil Type: {target_land.soil_type}\n"
                if target_land.city_rls:
                    response += f"City: {target_land.city_rls.city_name}\n"
                return {'answer': response, 'intent': intent}
            
            # Show all lands
            if not lands:
                return {'answer': "You don't have any lands registered yet.", 'intent': intent}
            response = "Here are your lands:\n"
            for i, land in enumerate(lands, 1):
                response += f"{i}. {land.land_name} ({land.land_in_acres} acres, {land.soil_type} soil)\n"
            response += "\nSpecify a land name for details or weather."
            return {'answer': response, 'intent': intent}
        
        elif intent == 'MyCrops':
            if not land_ids:
                return {'answer': "You don't have any active crops. Start a new cultivation session!", 'intent': intent}
            sessions = CultivationSessionModel.query.filter(CultivationSessionModel.land_id.in_(land_ids)).all()
            if not sessions:
                return {'answer': "You don't have any active cultivation sessions.", 'intent': intent}
            response = "Here are your current crops:\n"
            for i, session in enumerate(sessions, 1):
                land = LandModel.query.get(session.land_id)
                crop = CropModel.query.get(session.crop_id) if session.crop_id else None
                crop_name = crop.crop_name if crop else session.seed_name or 'Unknown'
                status_icon = "✓" if session.session_status == "Active" else "○"
                response += f"{status_icon} {crop_name} on {land.land_name if land else 'Unknown land'} ({session.session_status})\n"
            return {'answer': response, 'intent': intent}
        
        elif intent == 'CropRecommendation':
            current_land = context.get('current_land')
            
            if not lands:
                return {'answer': "You don't have any lands registered to recommend crops for.", 'intent': intent}
            
            if not current_land:
                if len(lands) == 1:
                    land = lands[0]
                    _set_context(farmer_id, {'state': 'active', 'current_land': {'land_id': land.land_id, 'land_name': land.land_name, 'soil_type': land.soil_type}, 'current_session': None, 'pending_question': None}, session_id)
                    return self._get_crop_recommendation(land.land_id)
                
                _set_context(farmer_id, {'state': 'waiting_for_land', 'current_land': None, 'current_session': None, 'pending_question': query}, session_id)
                response = "On which land would you like to grow crops? Here are your lands:\n"
                for i, land in enumerate(lands, 1):
                    response += f"{i}. {land.land_name} ({land.land_in_acres} acres, {land.soil_type} soil)\n"
                return {'answer': response, 'intent': intent, 'requires_context': True}
            
            return self._get_crop_recommendation(current_land['land_id'])
        
        elif intent == 'MyNeighbors':
            current_land = context.get('current_land')
            target_land = None
            
# Try to find land from query first
            if not current_land and lands:
                query_lower = query.lower()
                for land in lands:
                    if land.land_name.lower() in query_lower:
                        target_land = land
                        break
            
            # If no land found in query, ask user to specify
            if not target_land and not current_land:
                if len(lands) == 1:
                    target_land = lands[0]
                else:
                    _set_context(farmer_id, {'state': 'waiting_for_land', 'current_land': None, 'current_session': None, 'pending_question': query}, session_id)
                    response = "Which land's neighbors would you like to know about? Here are your lands:\n"
                    for i, land in enumerate(lands, 1):
                        response += f"{i}. {land.land_name}\n"
                    return {'answer': response, 'intent': intent, 'requires_context': True}
            
            land_id = (target_land.land_id if target_land else current_land['land_id']) if target_land or current_land else None
            
            if not land_id:
                return {'answer': "Please specify which land's neighbors you want to know about.", 'intent': intent}
            
            neighbors = NeighbourModel.query.filter(
                ((NeighbourModel.land_id == land_id) | (NeighbourModel.neighbour_land_id == land_id)),
                NeighbourModel.status == 1
            ).all()
            land_name = target_land.land_name if target_land else current_land.get('land_name', 'this land')
            
            if not neighbors:
                return {'answer': f"No neighbors found for {land_name}.", 'intent': intent}
            
            response = f"Neighbors of {land_name}:\n"
            for i, neighbor in enumerate(neighbors, 1):
                # Check both directions
                other_land_id = neighbor.neighbour_land_id if neighbor.neighbour_land_id != land_id else neighbor.land_id
                neighbor_land = LandModel.query.get(other_land_id)
                
                # Check what crop the neighbor is growing on their land
                neighbor_sessions = CultivationSessionModel.query.filter_by(land_id=other_land_id, session_status='Active').all()
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
            if not land_ids:
                return {'answer': "You don't have any active cultivation sessions. Start a new session first!", 'intent': intent}
            
            sessions = CultivationSessionModel.query.filter(
                CultivationSessionModel.land_id.in_(land_ids),
                CultivationSessionModel.session_status == 'Active'
            ).all()
            
            if not sessions:
                return {'answer': "You don't have any active cultivation sessions.", 'intent': intent}
            
            response = "Here are your upcoming activities:\n"
            has_activities = False
            
            # Use existing ActivitySuggestionService
            for session in sessions[:5]:
                land = LandModel.query.get(session.land_id)
                crop = CropModel.query.get(session.crop_id) if session.crop_id else None
                crop_name = crop.crop_name if crop else session.seed_name or 'Unknown'
                
                # Call existing service to get suggested activities
                result, code = ActivitySuggestionService.get_suggested_activities(session.cultivation_session_id)
                
                if code == 200 and result.get('activities'):
                    has_activities = True
                    response += f"\n{crop_name} on {land.land_name if land else 'Unknown'}:\n"
                    activities = result['activities'][:3]
                    for act in activities:
                        status_icon = "✓" if act.get('status') == 'Performed' else "○"
                        response += f"  {status_icon} {act.get('activity_name')} ({act.get('suggested_date')})\n"
            
            if not has_activities:
                response = "No upcoming activities found. Your crops are all set!"
            
            return {'answer': response, 'intent': intent}
        
        return None

    def _get_crop_recommendation(self, land_id):
        """Use existing crop_recommendation.py RuleBasedCropEngine"""
        from Model.LandModel import LandModel
        from crop_recommendation import RuleBasedCropEngine
        
        land = LandModel.query.get(land_id)
        if not land:
            return {'answer': "Land not found.", 'intent': 'CropRecommendation'}
        
        import datetime
        month = datetime.datetime.now().month
        if month in [3, 4, 5]:
            current_season = "Zaid"
        elif month in [6, 7, 8, 9]:
            current_season = "Kharif"
        else:
            current_season = "Rabi"
        
        # Use existing RuleBasedCropEngine
        engine = RuleBasedCropEngine()
        
        # Create anonymous object to match existing API
        class LandResource:
            def __init__(self, soil, water):
                self.soil_type = soil
                self.water_source = water
        
        land_resource = LandResource(land.soil_type, land.source_of_water)
        recommendations = engine.evaluate_cold_start(land_resource, current_season, "Normal", None)
        
        # If no recommendations for current season, try other seasons
        if not recommendations:
            # Try Rabi for Zaid, or Kharif as fallback
            fallback_seasons = ["Rabi", "Kharif"] if current_season == "Zaid" else ["Rabi", "Kharif"]
            for season in fallback_seasons:
                recs = engine.evaluate_cold_start(land_resource, season, "Normal", None)
                if recs:
                    recommendations = recs
                    current_season = f"{current_season} (or try {season})"
                    break
        
        if not recommendations:
            # Show all available crops from engine
            all_crops = list(engine.crop_rules.keys())
            response = f"Currently no specific recommendations for {land.land_name} ({land.soil_type} soil) in {current_season} season.\n\n"
            response += f"Available crops in our database:\n"
            for i, crop in enumerate(all_crops[:10], 1):
                response += f"{i}. {crop}\n"
            response += "\nFor better recommendations, please specify a season (Kharif or Rabi)."
            return {'answer': response, 'intent': 'CropRecommendation'}
        
        response = f"Based on {land.land_name} ({land.soil_type} soil, {land.source_of_water} water):\n\n"
        for i, rec in enumerate(recommendations[:5], 1):
            response += f"{i}. {rec['crop']} (Confidence: {rec['confidence_score']}%)\n   Why: {rec['rationale']}\n"
        
        return {'answer': response, 'intent': 'CropRecommendation'}

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
