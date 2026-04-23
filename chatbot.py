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
class AgricultureRAGChatbot:
    def __init__(self, use_llm=True):
        """Initialize RAG chatbot with CSV knowledge base and optional LLM paraphrasing"""
        print(" Loading Agriculture RAG Chatbot...")
        self.ps = PorterStemmer()
        self.use_llm = use_llm
        self._llm_loaded = False
        self.model = None
        self.tokenizer = None
        self.device = None
        
        # ========== INTENT CATEGORIES ==========
        self.AGRICULTURE_INTENTS = [
            "Cultivation", "Fertilizer", "Pesticide", "Irrigation", 
            "Soil", "Yield", "Diseases", "Varieties", 
            "MarketPrice", "HarvestTime", "SowingTime", "Weather", "SeedRate", "SeedTreatment", "LandPrep", "WeedControl", "Storage", "Economics"
        ]
        self.INTERACTION_INTENTS = [
            "Greeting", "Wassup", "Wellness", "AskingHelp", "OutOfScope"
        ]
        self.CONFIDENCE_THRESHOLD = 0.6

        # ========== LOAD TRAINED MODELS ==========
        try:
            # Intent models
            self.intent_model = load_model('saved_state/intent_model.h5', compile=False)
            self.intent_cv = pickle.load(open('saved_state/IntentCountVectorizer.sav', 'rb'))
            self.intent_label_map = pickle.load(open('saved_state/intent_label_map.sav', 'rb'))
            self.idx_to_intent = {v: k for k, v in self.intent_label_map.items()}

            # Entity models
            self.entity_model = pickle.load(open('saved_state/entity_model.sav', 'rb'))
            self.entity_cv = pickle.load(open('saved_state/EntityCountVectorizer.sav', 'rb'))
            self.entity_label_map = pickle.load(open('saved_state/entity_label_map.sav', 'rb'))
            self.idx_to_entity = {v: k for k, v in self.entity_label_map.items()}

            print("Intent & Entity models loaded")
        except Exception as e:
            print(f"Warning: Could not load ML models: {e}")
            print("   Will use rule-based fallback only")
            self.intent_model = None

        # ========== LOAD KNOWLEDGE BASE ==========
        self.load_knowledge_base()

        # ========== SETUP EMBEDDINGS FOR RAG ==========
        self.setup_embeddings()

        # ========== LLM WILL BE LOADED LAZILY ON FIRST USE ==========
        if self.use_llm:
            print("LLM paraphrasing enabled (will load on first query)")

    def load_knowledge_base(self):
        """Load Q&A pairs from CSV"""
        try:
            # Try loading the new large dataset first, then fall back
            potential_paths = ["data/agriculture_knowledge_base.csv", "data/agriculture_knowledge_base.csv"]
            path_found = False
            for path in potential_paths:
                if os.path.exists(path):
                    self.df = pd.read_csv(path)
                    print(f"Loaded knowledge base from {path}: {len(self.df)} Q&A pairs")
                    path_found = True
                    break
            
            if not path_found:
                raise FileNotFoundError("No knowledge base CSV found.")

            # Create searchable columns
            self.df['search_text'] = self.df['question'] + " " + self.df['answer'].str[:100]
            self.df['crop'] = self.df['crop'].fillna('')
            self.df['soil'] = self.df['soil'].fillna('')
            self.df['intent'] = self.df['intent'].fillna('')

        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            print("   Creating empty DataFrame")
            self.df = pd.DataFrame(columns=['crop', 'soil', 'intent', 'question', 'answer'])

    def setup_embeddings(self):
        """Create embeddings for semantic search with caching"""
        try:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            
            index_path = 'saved_state/faiss_index.idx'
            embeddings_path = 'saved_state/embeddings.npy'

            if len(self.df) > 0:
                # Simple cache check: if index exists and matches df size, load it
                if os.path.exists(index_path) and os.path.exists(embeddings_path):
                    self.question_embeddings = np.load(embeddings_path)
                    if len(self.question_embeddings) == len(self.df):
                        self.index = faiss.read_index(index_path)
                        print(f"Loaded cached embeddings: {self.question_embeddings.shape}")
                        return

                # Otherwise recompute
                print("Generating embeddings (this may take a minute)...")
                questions = self.df['question'].tolist()
                self.question_embeddings = self.embedder.encode(questions)

                # Create FAISS index
                dimension = self.question_embeddings.shape[1]
                self.index = faiss.IndexFlatIP(dimension)
                faiss.normalize_L2(self.question_embeddings.astype('float32'))
                self.index.add(self.question_embeddings.astype('float32'))
                
                # Save cache
                faiss.write_index(self.index, index_path)
                np.save(embeddings_path, self.question_embeddings)

                print(f"Created and cached embeddings: {self.question_embeddings.shape}")
            else:
                self.index = None

        except Exception as e:
            print(f"Could not create embeddings: {e}")
            self.index = None

    def setup_llm(self):
        """Setup local HuggingFace LLM for paraphrasing (Lazily called)"""
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
        """Use local HuggingFace LLM to make answer conversational"""

        if not getattr(self, "use_llm", False):
            return answer

        # Lazy load the LLM if not already loaded
        if not self._llm_loaded:
            self.setup_llm()

        if not self.model: # If loading failed
            return answer
        import torch

        prompt = f"""
    You are a helpful agriculture assistant for farmers in Pakistan.

    User question:
    "{query}"

    Knowledge base answer:
    "{answer}"

    Rewrite the answer in a friendly, natural way.
    Keep all facts and numbers EXACTLY the same.
    Do NOT add new information.
    Keep it short (2-4 sentences).

    Rewritten answer:
    """

        inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=512
            ).to(self.device)

        with torch.no_grad():
            output = self.model.generate(
                    **inputs,
                    max_new_tokens=120,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            decoded = self.tokenizer.decode(
                output[0],
                skip_special_tokens=True
            )

            # Extract only generated part
            if "Rewritten answer:" in decoded:
                rewritten = decoded.split("Rewritten answer:")[-1].strip()
            else:
                rewritten = decoded.strip()

            return rewritten if rewritten else answer

    def get_intent(self, text):
        """Predict intent with ML model"""
        if not self.intent_model:
            return self.rule_based_intent(text), 0.5

        try:
            # Preprocess
            text = re.sub('[^a-zA-Z]', ' ', text)
            text = text.lower()
            text = text.split()
            text = [self.ps.stem(word) for word in text]
            text = ' '.join(text)

            # Vectorize
            X = self.intent_cv.transform([text]).toarray()

            # Predict
            pred = self.intent_model.predict(X, verbose=0)
            intent_idx = np.argmax(pred[0])
            confidence = np.max(pred[0])

            return self.idx_to_intent.get(intent_idx, "Unknown"), confidence

        except:
            return self.rule_based_intent(text), 0.5

    def rule_based_intent(self, text):
        """Fallback rule-based intent detection"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['hello', 'hi', 'hey', 'namaste']):
            return 'Greeting'
        elif any(word in text_lower for word in ['how are you', 'how do you do']):
            return 'Wellness'
        elif any(word in text_lower for word in ['help', 'assist']):
            return 'AskingHelp'
        elif any(word in text_lower for word in ['fertilizer', 'urea', 'dap', 'npk']):
            return 'Fertilizer'
        elif any(word in text_lower for word in ['pest', 'insect', 'whitefly', 'borer', 'control']):
            return 'Pesticide'
        elif any(word in text_lower for word in ['irrigation', 'water', 'irrigate']):
            return 'Irrigation'
        elif any(word in text_lower for word in ['soil', 'clay', 'sandy', 'loamy']):
            return 'Soil'
        elif any(word in text_lower for word in ['yield', 'production', 'output']):
            return 'Yield'
        elif any(word in text_lower for word in ['disease', 'rust', 'blight', 'virus']):
            return 'Diseases'
        elif any(word in text_lower for word in ['variety', 'varieties', 'type', 'hybrid']):
            return 'Varieties'
        elif any(word in text_lower for word in ['harvest', 'reap', 'picking']):
            return 'HarvestTime'
        elif any(word in text_lower for word in ['sow', 'sowing', 'plant', 'planting']):
            return 'SowingTime'
        elif any(word in text_lower for word in ['price', 'cost', 'rate', 'mandi']):
            return 'MarketPrice'
        elif any(word in text_lower for word in ['how to grow', 'cultivate', 'cultivation']):
            return 'Cultivation'
        elif any(word in text_lower for word in ['who is', 'prime minister', 'president']):
            return 'OutOfScope'
        else:
            return 'Cultivation'  # Default

    def extract_entities(self, text):
        """Extract crops, soil types, etc."""
        text_lower = text.lower()
        entities = []

        # Crop list
        crops = ['wheat', 'rice', 'cotton', 'sugarcane', 'maize', 'potato', 'tomato',
                 'onion', 'mustard', 'gram', 'chickpea', 'sunflower', 'groundnut']

        # Soil types
        soils = ['sandy', 'clay', 'loamy', 'saline', 'black', 'red', 'alluvial']

        # Check for crops
        for crop in crops:
            if crop in text_lower:
                entities.append(('crop', crop))
                break

        # Check for soils
        for soil in soils:
            if soil in text_lower:
                entities.append(('soil', soil))
                break

        return entities

    def search_knowledge_base(self, query, intent, entities, top_k=3):
        """Search knowledge base using multiple strategies"""

        # Strategy 1: Exact match on crop + intent
        crop = None
        soil = None
        for entity_type, entity_value in entities:
            if entity_type == 'crop':
                crop = entity_value
            elif entity_type == 'soil':
                soil = entity_value

        # Try exact matches
        if crop and intent:
            exact_match = self.df[
                (self.df['crop'].str.contains(crop, case=False, na=False)) &
                (self.df['intent'] == intent)
                ]
            if len(exact_match) > 0:
                return exact_match.iloc[0]['answer'], 1.0, 'exact_match'

        # Try soil matches
        if soil and intent == 'Soil':
            soil_match = self.df[
                (self.df['soil'].str.contains(soil, case=False, na=False)) &
                (self.df['intent'] == intent)
                ]
            if len(soil_match) > 0:
                return soil_match.iloc[0]['answer'], 0.95, 'soil_match'

        # Strategy 2: Semantic search with FAISS
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

        # Strategy 3: Keyword search
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

        # Strategy 4: Crop only match
        if crop:
            crop_answers = self.df[self.df['crop'].str.contains(crop, case=False, na=False)]
            if len(crop_answers) > 0:
                return crop_answers.iloc[0]['answer'], 0.6, 'crop_only'

        return None, 0, 'no_match'

    def generate_response(self, query):
        """Main response generation with RAG"""
        if query.lower() in ['quit', 'exit', 'bye', 'q', 'allah hafiz']:
            return {
                'query': query,
                'answer': "Allah Hafiz! Happy farming!",
                'intent': "Closing",}
        # Step 1: Get intent
        intent, intent_conf = self.get_intent(query)
        
        # Detect if it's interactional or out-of-scope
        is_interactional = intent in self.INTERACTION_INTENTS
        is_low_confidence = intent_conf < self.CONFIDENCE_THRESHOLD

        # Step 2: Route based on intent category and confidence
        if is_interactional or (is_low_confidence and intent == "OutOfScope"):
            answer = self.get_intent_based_fallback(intent, [])
            return {
                'query': query,
                'answer': answer,
                'intent': intent,
                'intent_confidence': float(intent_conf),
                'entities': [],
                'match_type': 'interactional',
                'confidence': float(intent_conf)
            }

        # Step 3: Extract entities (Only for agricultural queries)
        entities = self.extract_entities(query)

        # Step 4: Search knowledge base
        answer, confidence, match_type = self.search_knowledge_base(query, intent, entities)

        # Step 5: If no match, use intent-based fallback
        if not answer:
            answer = self.get_intent_based_fallback(intent, entities)
            confidence = 0.5
            match_type = 'fallback'

        # Step 6: Paraphrase with LLM (Only for successful agricultural RAG/Fallback results)
        if self.use_llm and answer and intent in self.AGRICULTURE_INTENTS:
            original_answer = answer
            answer = self.paraphrase_with_llm(query, answer)
            if not answer:  # If paraphrase failed
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

    def get_intent_based_fallback(self, intent, entities):
        """Fallback when no match in knowledge base or for interactional intents"""
        crop = next((v for t, v in entities if t == 'crop'), None)

        fallbacks = {
            'Cultivation': f"For {crop or 'crops'}, focus on soil preparation, quality seeds, balanced fertilizers, proper irrigation, and pest management. Contact your local agriculture department for specific recommendations.",
            'Fertilizer': f"For {crop or 'your crop'}, conduct a soil test first. Generally, apply NPK based on crop requirement. Use organic matter like FYM to improve soil health.",
            'Pesticide': f"Monitor your {crop or 'crop'} regularly. Use recommended pesticides only when pest population reaches economic threshold level. Practice integrated pest management.",
            'Irrigation': f"Water requirement varies by {crop or 'crop'} and growth stage. Use water-efficient methods like drip or sprinkler irrigation. Government provides 60-80% subsidy on these systems.",
            'Soil': "Get your soil tested at the nearest soil testing laboratory. Add organic matter, practice crop rotation, and apply amendments based on soil test recommendations.",
            'Yield': f"Yield depends on variety, soil fertility, water management, and pest control. With best practices, you can achieve {crop or 'crop'} yields 30-50% higher than average.",
            'Diseases': f"Prevent {crop or 'crop'} diseases through resistant varieties, crop rotation, and field hygiene. Contact your local agriculture officer for specific disease management.",
            'HarvestTime': f"Harvest {crop or 'crops'} at proper maturity for best quality and storage life. Timing varies by crop and season.",
            'SowingTime': f"Sow {crop or 'crops'} at the recommended time for your region. Timely sowing can increase yields by 20-30%.",
            'Greeting': "Assalam-o-Alaikum! I am your Kisan Guide Chatbot. How can I help you with your crops today?",
            'Wassup': "I am here to assist Pakistani farmers with their agriculture-related queries. What's on your mind regarding your farm?",
            'AskingHelp': "I'm here to help! You can ask me about crops (wheat, rice, cotton, etc.), fertilizers, pesticides, soil, irrigation, harvesting, and more. What specific information do you need?",
            'Wellness': "I'm doing well, thank you! I'm dedicated to providing the best agricultural advice to help you succeed. What's your question?",
            'OutOfScope': "I am specialized in agriculture in Pakistan. I can't answer general questions about politics, sports, or entertainment. Please ask me something about crops, soil, or farming!"
        }

        return fallbacks.get(intent,
                             f"I understand you're asking about {intent}. While I don't have a specific answer for this, I can help you with other agricultural topics like crop cultivation, fertilizers, or pest control.")

    def chat(self,query):
        """Interactive chat loop"""
        print("\n" + "=" * 70)
        print("Kisan Guide CHATBOT")
        print("=" * 70)
        print(f"Knowledge Base: {len(self.df)} Q&A pairs")
        print(f"LLM Paraphrasing: {'ON' if self.use_llm else 'OFF'}")
        print("=" * 70)
        print("\nAsk me anything about crops, farming, soil, irrigation...")
        print("Type 'quit' to exit\n")

        while True:
            try:

                query = query

                if query.lower() in ['quit', 'exit', 'bye', 'q', 'allah hafiz']:
                    print("\nBot: Allah Hafiz! Happy farming!")
                    break

                if not query:
                    continue

                # Generate response
                response = self.generate_response(query)

                # Print answer
                print(f"\n Bot: {response['answer']}")

                # Show metadata (optional - remove in production)
                print(f"\n    Intent: {response['intent']} ({response['intent_confidence']:.0%})")
                if response['entities']:
                    entities_str = ', '.join([f"{v}({k})" for k, v in response['entities']])
                    print(f"    Entities: {entities_str}")
                print(f"    Match: {response['match_type']} (confidence: {response['confidence']:.0%})")
                print()

            except KeyboardInterrupt:
                print("\n\nBot: Allah Hafiz!")
                break
            except Exception as e:
                print(f"\n Error: {e}")
                print("   Please try again.")


def main(question):
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-llm', action='store_true', help='Disable LLM paraphrasing')
    args = parser.parse_args()

    chatbot = AgricultureRAGChatbot(use_llm=not args.no_llm)
    chatbot.chat(question)


# if __name__ == "__main__":
#     main()