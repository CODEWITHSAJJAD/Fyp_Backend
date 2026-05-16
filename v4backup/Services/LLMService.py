"""
LLM Service - Local LLM via HuggingFace for response generation
Uses existing data sources (KB, DB, modules) to build context, then generates natural response
"""

from typing import Optional, Dict, Any
import torch


class LLMService:
    _instance = None
    _llm_available = False
    _llm_loaded = False
    model = None
    tokenizer = None
    device = "cpu"
    
    # Model options - choose one:
    llm_model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # 1.1B - Fast, low memory
    # llm_model_name = "microsoft/Phi-2"  # 2.7B - Best quality/size ratio (~6GB RAM)
    # llm_model_name = "mistralai/Mistral-7B-Instruct-v0.2"  # 7B - Best quality (~14GB RAM)
    # llm_model_name = "microsoft/Phi-2"  # Default: Phi-2
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._load_llm()
    
    def _load_llm(self):
        """Load HuggingFace TinyLlama model"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            print("Loading local HuggingFace LLM (TinyLlama)...")
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.tokenizer = AutoTokenizer.from_pretrained(self.llm_model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.llm_model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            ).to(self.device)
            self.model.eval()
            self._llm_loaded = True
            self._llm_available = True
            print(f"Local LLM loaded successfully on {self.device}")
            
        except Exception as e:
            print(f"Could not load local LLM: {e}")
            self._llm_available = False
            self._llm_loaded = False
    
    def is_available(self) -> bool:
        return getattr(self, '_llm_available', False)
    
    def generate_response(
        self, 
        prompt: str, 
        system_prompt: str = None,
        context: Dict[str, Any] = None
    ) -> str:
        """Generate response using local LLM"""
        
        if not self.is_available():
            return None
        
        # Build full prompt with context
        full_prompt = self._build_prompt(prompt, system_prompt, context)
        
        try:
            inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=150,
                    temperature=0.3,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the response part
            if "Assistant:" in response:
                response = response.split("Assistant:")[-1].strip()
            
            return response.strip()
                
        except Exception as e:
            print(f"[LLM] Generation error: {e}")
            return None
    
    def _build_prompt(self, user_prompt: str, system_prompt: str, context: Dict) -> str:
        """Build prompt with context from data sources"""
        
        prompt_parts = []
        
        if system_prompt:
            prompt_parts.append(f"System: {system_prompt}")
        
        if context:
            if context.get('land_info'):
                prompt_parts.append(f"Land Information: {context['land_info']}")
            if context.get('recommendations'):
                prompt_parts.append(f"Crop Recommendations: {context['recommendations']}")
            if context.get('activities'):
                prompt_parts.append(f"Activities: {context['activities']}")
            if context.get('crops'):
                prompt_parts.append(f"Current Crops: {context['crops']}")
            if context.get('neighbors'):
                prompt_parts.append(f"Neighbor Info: {context['neighbors']}")
            if context.get('profile'):
                prompt_parts.append(f"Farmer Profile: {context['profile']}")
        
        prompt_parts.append(f"User: {user_prompt}")
        prompt_parts.append("Assistant:")
        
        return "\n\n".join(prompt_parts)
    
    def get_embeddings(self, texts: list) -> Optional[list]:
        """Get text embeddings using sentence transformers"""
        try:
            from sentence_transformers import SentenceTransformer
            
            model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            embeddings = model.encode(texts)
            return embeddings.tolist()
            
        except Exception as e:
            print(f"[LLM] Embedding error: {e}")
            return None


# ============================================
# SYSTEM PROMPTS PER INTENT
# ============================================

class SystemPrompts:
    CROPS_RECOMMENDATION = """You are Kisan Guide, an agricultural expert for Pakistani farmers.
Your responses MUST come ONLY from the provided crop recommendations data.
Never make up information. If data is not available, say so clearly.

Format your response in clear, simple language suitable for farmers."""

    MY_LANDS = """You are a land management specialist for Kisan Guide.
Your responses MUST come ONLY from the provided land data.
Provide details about soil, water, location only from the data given.
Never add information not in the provided data."""

    MY_CROPS = """You are a crop monitoring expert for Kisan Guide.
Your responses MUST come ONLY from the provided cultivation data.
Only mention crops, activities, and timings that are in the provided data."""

    CULTIVATION = """You are a farming expert for Kisan Guide.
Your responses MUST come ONLY from the knowledge base cultivation guidelines.
Use only the crop-specific information provided in the data."""

    ACTIVITIES = """You are a farming activities advisor for Kisan Guide.
Your responses MUST come ONLY from the suggested activities data.
Only mention activities and timings from the provided schedule."""

    FERTILIZER = """You are an agronomist for Kisan Guide.
Your responses MUST come ONLY from the fertilizer guidelines in the knowledge base.
Never suggest fertilizers not in the data."""

    DEFAULT = """You are Kisan Guide, a helpful agricultural assistant for Pakistani farmers.
Your role is to provide helpful information from the provided data only.
Never make up information. Always use data from the knowledge base, database, or recommendations."""


# Singleton instance
_llm_service = None

def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def enhance_with_llm(response: dict, query: str, farmer_id: int = None) -> dict:
    """Optionally enhance response with LLM for more natural formatting."""
    llm = get_llm_service()

    if not llm.is_available():
        return response

    if response.get('recommendations'):
        return response

    intent = response.get('intent', 'DEFAULT')
    system_prompt = {
        'CropRecommendation': SystemPrompts.CROPS_RECOMMENDATION,
        'MyLands': SystemPrompts.MY_LANDS,
        'MyCrops': SystemPrompts.MY_CROPS,
        'Cultivation': SystemPrompts.CULTIVATION,
        'ActivityRecommendation': SystemPrompts.ACTIVITIES,
        'FarmerInfo': SystemPrompts.DEFAULT,
        'MyNeighbors': SystemPrompts.DEFAULT,
    }.get(intent, SystemPrompts.DEFAULT)

    current_answer = response.get('answer', '')
    if len(current_answer) > 200:
        return response

    try:
        enhanced = llm.generate_response(
            f"Reformat this response to be more natural and helpful: {current_answer}",
            system_prompt=system_prompt,
            context={'original_query': query}
        )
        if enhanced and len(enhanced) > len(current_answer):
            response['answer'] = enhanced
            response['source'] = 'llm_enhanced'
    except:
        pass

    return response