"""
Response Builder - Builds responses using data sources + LLM formatting
Ensures all answers come from user's data, not generated
"""

from typing import Dict, Any, Optional
from Services.LLMService import get_llm_service, SystemPrompts
from Services.ChatbotHelper import (
    get_farmer_lands, format_land_info, get_farmer_crops,
    get_neighbor_info, format_neighbors, get_farmer_profile,
    get_upcoming_activities
)
from Services.ChatbotHelper import get_context as _get_context, set_context as _set_context

class ResponseBuilder:
    """Builds responses from data sources with optional LLM enhancement"""
    
    @staticmethod
    def build_response(
        intent: str,
        query: str,
        farmer_id: int,
        session_id: int = None,
        data: Dict[str, Any] = None,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """Build response from data sources"""
        
        # Get context
        context = _get_context(farmer_id, session_id)
        
        # Get system prompt for this intent
        system_prompt = ResponseBuilder._get_system_prompt(intent)
        
        # Build context from data sources
        context_data = ResponseBuilder._build_context_data(intent, farmer_id, context, data)
        
        # If LLM available, use it for formatting
        llm_service = get_llm_service()
        
        if use_llm and llm_service.is_available():
            # Generate natural response from data
            llm_response = llm_service.generate_response(
                query,
                system_prompt=system_prompt,
                context=context_data
            )
            
            if llm_response:
                return {
                    'answer': llm_response,
                    'intent': intent,
                    'source': 'llm_enhanced'
                }
        
        # Fallback to template-based response
        return ResponseBuilder._build_template_response(intent, context_data)
    
    @staticmethod
    def _get_system_prompt(intent: str) -> str:
        """Get system prompt for intent"""
        prompts = {
            'CropRecommendation': SystemPrompts.CROPS_RECOMMENDATION,
            'MyLands': SystemPrompts.MY_LANDS,
            'MyCrops': SystemPrompts.MY_CROPS,
            'Cultivation': SystemPrompts.CULTIVATION,
            'ActivityRecommendation': SystemPrompts.ACTIVITIES,
            'Fertilizer': SystemPrompts.FERTILIZER,
        }
        return prompts.get(intent, SystemPrompts.DEFAULT)
    
    @staticmethod
    def _build_context_data(
        intent: str, 
        farmer_id: int, 
        context: Dict,
        extra_data: Dict = None
    ) -> Dict[str, Any]:
        """Build context from all data sources"""
        
        data = {}
        
        if intent in ['MyLands', 'CropRecommendation', 'MyCrops']:
            lands = get_farmer_lands(farmer_id)
            data['lands'] = [format_land_info(l) for l in lands]
            
            current_land = context.get('current_land')
            if current_land:
                for land in lands:
                    if land.land_id == current_land.get('land_id'):
                        data['current_land'] = format_land_info(land)
                        break
        
        if intent in ['MyCrops', 'MyNeighbors']:
            crops = get_farmer_crops(farmer_id)
            if crops:
                data['crops'] = crops
        
        if intent in ['MyNeighbors', 'NeighborInfo']:
            neighbors = format_neighbors(farmer_id)
            if neighbors:
                data['neighbors'] = neighbors
        
        if intent == 'FarmerInfo':
            profile = get_farmer_profile(farmer_id)
            if profile:
                data['profile'] = profile
        
        if intent in ['ActivityRecommendation', 'MyActivities']:
            activities = get_upcoming_activities(farmer_id)
            if activities:
                data['activities'] = activities
        
        # Add extra data from recommendations
        if extra_data:
            data.update(extra_data)
        
        return data
    
    @staticmethod
    def _build_template_response(intent: str, context_data: Dict) -> Dict[str, Any]:
        """Build response without LLM (fallback)"""
        
        templates = {
            'MyLands': ResponseBuilder._format_lands,
            'MyCrops': ResponseBuilder._format_crops,
            'MyNeighbors': ResponseBuilder._format_neighbors,
            'FarmerInfo': ResponseBuilder._format_profile,
            'ActivityRecommendation': ResponseBuilder._format_activities,
        }
        
        formatter = templates.get(intent)
        if formatter:
            answer = formatter(context_data)
            return {'answer': answer, 'intent': intent, 'source': 'template'}
        
        return {'answer': 'I need more information to help you.', 'intent': intent, 'source': 'fallback'}
    
    @staticmethod
    def _format_lands(data: Dict) -> str:
        lands = data.get('lands', [])
        current = data.get('current_land')
        
        if current:
            return current
        
        if lands:
            return "Your lands: " + ", ".join(lands)
        
        return "No lands found."
    
    @staticmethod
    def _format_crops(data: Dict) -> str:
        crops = data.get('crops', 'No active crops found.')
        return crops
    
    @staticmethod
    def _format_neighbors(data: Dict) -> str:
        neighbors = data.get('neighbors', 'No neighbors found.')
        return neighbors
    
    @staticmethod
    def _format_profile(data: Dict) -> str:
        profile = data.get('profile', 'Profile not found.')
        return profile
    
    @staticmethod
    def _format_activities(data: Dict) -> str:
        activities = data.get('activities', 'No activities scheduled.')
        return activities