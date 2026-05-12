"""Chatbot helper functions - reusable utility functions for chatbot"""

from datetime import datetime
from Model.LandModel import LandModel
from Model.CultivationSessionModel import CultivationSessionModel
from Model.CropModel import CropModel
from Model.NeighbourModel import NeighbourModel
from Model.FarmerModel import FarmerModel
from Model.PerformActivityModel import PerformedActivityModel
from Model.CityModel import CityModel
from Services.ActivitySuggestionService import ActivitySuggestionService
from Services.WeatherService import get_weather
from Services.CropActivityData import get_activity_name_by_id

# Active session statuses
ACTIVE_STATUSES = ['Active', 'active', 'Running', 'In Progress', 'ACTIVE', 'Sown', 'sown', 'Growing']

# ============================================
# CONTEXT MANAGEMENT FUNCTIONS
# ============================================

_context_store = {}
_context_lock = __import__('threading').Lock()


def load_context_from_chat(farmer_id, session_id):
    """Load context from previous chat history"""
    try:
        # Check if we have app context
        from flask import has_request_context
        if not has_request_context():
            print("[Context] No request context, skipping context load")
            return None
        from Model.ChatModel import ChatModel
        from Model.ChatSessionModel import ChatSessionModel
        from Model.LandModel import LandModel
        
        lands = LandModel.query.filter_by(farmer_id=farmer_id, land_Status=1).all()
        land_map = {land.land_name.lower(): land for land in lands}
        
        crop_rec_chats = ChatModel.query.join(ChatSessionModel).filter(
            ChatSessionModel.Farmer_id == farmer_id,
            ChatModel.chat_type == 'CropRecommendation'
        ).order_by(ChatModel.time_stamp.desc()).limit(5).all()
        
        for chat in crop_rec_chats:
            answer_lower = chat.answer.lower()
            for land_name, land in land_map.items():
                if land_name in answer_lower:
                    return {
                        'state': 'active',
                        'current_land': {'land_id': land.land_id, 'land_name': land.land_name, 'soil_type': land.soil_type},
                        'current_session': None,
                        'pending_question': None,
                        'source': 'crop_recommendation'
                    }
        
        land_chats = ChatModel.query.join(ChatSessionModel).filter(
            ChatSessionModel.Farmer_id == farmer_id,
            ChatModel.chat_type == 'MyLands'
        ).order_by(ChatModel.time_stamp.desc()).limit(3).all()
        
        for chat in land_chats:
            answer_lower = chat.answer.lower()
            for land_name, land in land_map.items():
                if land_name in answer_lower:
                    return {
                        'state': 'active',
                        'current_land': {'land_id': land.land_id, 'land_name': land.land_name, 'soil_type': land.soil_type},
                        'current_session': None,
                        'pending_question': None,
                        'source': 'my_lands'
                    }
        
        if len(lands) == 1:
            return {
                'state': 'active',
                'current_land': {'land_id': lands[0].land_id, 'land_name': lands[0].land_name, 'soil_type': lands[0].soil_type},
                'current_session': None,
                'pending_question': None,
                'source': 'single_land_fallback'
            }
        
        return None
    except Exception as e:
        print(f"Context load error: {e}")
        return None


def get_context(farmer_id, session_id=None):
    """Get context for a farmer - with full memory"""
    key = f"chatbot_context_{farmer_id}_{session_id}" if session_id else f"chatbot_context_{farmer_id}"
    
    context = _context_store.get(key, None)
    if context and context.get('state') != 'none':
        return context
    
    # Return default context structure with FULL memory support
    return {
        'state': 'none',
        'current_land': None,           # Last selected land
        'current_session': None,         # Last cultivation session
        'pending_question': None,        # Waiting for user input
        'last_recommendations': [],      # Last crop recommendations
        'last_mentioned_crop': None,     # Last crop user asked about
        'last_intent': None,             # Last intent type
        'last_mentioned_neighbor': None,# Last neighbor land asked about
        'last_mentioned_activity': None,# Last activity type asked about
        'conversation_history': [],     # Last 10 Q&A for context
    }


def set_context(farmer_id, context, session_id=None):
    """Set context for a farmer - PRESERVES memory (merges with existing)"""
    key = f"chatbot_context_{farmer_id}_{session_id}" if session_id else f"chatbot_context_{farmer_id}"
    with _context_lock:
        # Get existing to preserve memory
        existing = _context_store.get(key, {
            'state': 'none', 'current_land': None, 'current_session': None,
            'pending_question': None, 'last_recommendations': [],
            'last_mentioned_crop': None, 'last_intent': None,
            'last_mentioned_neighbor': None, 'last_mentioned_activity': None,
            'conversation_history': []
        })
        
        # Handle conversation history - append new Q&A
        if 'conversation_history' in context:
            # Add to existing history, keep last 10
            new_history = existing.get('conversation_history', [])
            new_history.append(context['conversation_history'])
            if len(new_history) > 10:
                new_history = new_history[-10:]
            context['conversation_history'] = new_history
        
        # Merge new values with existing memory
        existing.update(context)
        _context_store[key] = existing


def reset_context(farmer_id, session_id=None):
    """Reset context for a farmer"""
    set_context(farmer_id, {
        'state': 'none',
        'current_land': None,
        'current_session': None,
        'pending_question': None,
        'last_recommendations': [],
        'last_mentioned_crop': None,
        'last_intent': None,
        'last_mentioned_neighbor': None,
        'last_mentioned_activity': None,
        'conversation_history': []
    }, session_id)


def handle_crop_followup(query_lower, context, last_rec, session_id, farmer_id, is_quick, is_explanatory):
    """Handle follow-up questions about crops (sowing time, cultivation, etc.)"""
    crop_followup_keywords = ['when', 'sow', 'plant', 'cultivate', 'grow', 'season', 'time', 'start', 'prepare']
    has_crop_followup = any(word in crop_followup_keywords for word in query_lower.split())
    
    crop_name = None
    
    # Check if crop is explicitly mentioned
    if last_rec:
        for rec in last_rec:
            rec_name = rec.get('Name', '').lower()
            if rec_name in query_lower:
                crop_name = rec.get('Name', '')
                break
    
    # Check for pronouns (it, this, that)
    if not crop_name:
        has_pronoun = any(word in query_lower for word in ['it', 'this', 'that', 'these', 'those'])
        last_crop = context.get('last_mentioned_crop')
        if has_pronoun and last_crop and has_crop_followup:
            crop_name = last_crop
    
    # Check database for crop name
    if not crop_name:
        all_crops = CropModel.query.all()
        for crop in all_crops:
            if crop.crop_name.lower() in query_lower:
                crop_name = crop.crop_name
                break
    
    if crop_name and has_crop_followup:
        sowing_info = get_crop_sowing_info(crop_name)
        if sowing_info:
            if is_quick:
                return f"{crop_name} is usually sown in {sowing_info.get('season', 'the appropriate season')}."
            elif is_explanatory:
                details = f"{crop_name} should be cultivated during {sowing_info.get('season', 'the appropriate season')}. "
                details += f"The ideal time is {sowing_info.get('sowing_time', 'when weather conditions are suitable')}. "
                details += f"Key tips: {sowing_info.get('tips', 'Follow recommended farming practices')}"
                return details
            else:
                return f"You should sow {crop_name} in {sowing_info.get('season', 'the appropriate season')}. {sowing_info.get('tips', '')}"
    
    return None


def get_farmer_lands(farmer_id):
    """Get all lands for a farmer"""
    return LandModel.query.filter_by(farmer_id=farmer_id).all()


def get_farmer_land_ids(farmer_id):
    """Get list of land IDs for a farmer"""
    lands = get_farmer_lands(farmer_id)
    return [l.land_id for l in lands]


def find_land_in_query(query_lower, lands):
    """Find a land mentioned in the query that belongs to the farmer"""
    for land in lands:
        if land.land_name.lower() in query_lower:
            return land
    return None


def get_active_sessions_for_farmer(farmer_id):
    """Get all active cultivation sessions for a farmer's lands"""
    user_land_ids = get_farmer_land_ids(farmer_id)
    if not user_land_ids:
        return []
    
    all_sessions = CultivationSessionModel.query.filter(
        CultivationSessionModel.land_id.in_(user_land_ids)
    ).all()
    
    return [s for s in all_sessions if s.session_status in ACTIVE_STATUSES]


def get_session_by_land(land_id):
    """Get active session for a specific land"""
    return CultivationSessionModel.query.filter(
        CultivationSessionModel.land_id == land_id
    ).filter(
        CultivationSessionModel.session_status.in_(ACTIVE_STATUSES)
    ).first()


def get_last_session_for_land(land_id):
    """Get the most recent session for a land"""
    return CultivationSessionModel.query.filter(
        CultivationSessionModel.land_id == land_id
    ).order_by(CultivationSessionModel.cultivation_session_id.desc()).first()


def get_crop_name(session):
    """Get crop name from a session"""
    if not session:
        return None
    if session.crop_id:
        crop = CropModel.query.get(session.crop_id)
        if crop:
            return crop.crop_name
    return session.seed_name


def format_land_info(land):
    """Format land information as a string"""
    response = f"Land: {land.land_name}\n"
    response += f"Size: {land.land_in_acres} acres\n"
    response += f"Soil Type: {land.soil_type}\n"
    response += f"Water Source: {land.source_of_water}\n"
    if land.city_rls:
        response += f"City: {land.city_rls.city_name}\n"
    return response


def format_weather(land):
    """Get formatted weather for a land"""
    if not land or not land.city_rls:
        return None
    
    weather = get_weather(land.city_rls.city_name)
    if weather and not weather.get('error'):
        return f"Weather for {land.land_name}:\n" \
               f"Location: {weather.get('city', land.city_rls.city_name)}\n" \
               f"Temperature: {weather.get('temperature', 'N/A')}°C\n" \
               f"Condition: {weather.get('condition', 'N/A')}\n" \
               f"Humidity: {weather.get('humidity', 'N/A')}%\n" \
               f"Wind Speed: {weather.get('wind_speed', 'N/A')} m/s\n"
    return None


def get_farmer_profile(farmer_id):
    """Get farmer profile information"""
    farmer = FarmerModel.query.get(farmer_id)
    if not farmer:
        return None
    
    lands = get_farmer_lands(farmer_id)
    
    response = f"Farmer Profile:\n"
    response += f"Name: {farmer.farmer_name or 'Not set'}\n"
    response += f"Phone: {farmer.phone or 'Not set'}\n"
    response += f"Total Lands: {len(lands)}\n"
    
    if lands:
        response += "\nYour Lands:\n"
        for land in lands:
            response += f"  • {land.land_name} ({land.land_in_acres} acres, {land.soil_type} soil)\n"
    
    return response


def get_farmer_crops(farmer_id):
    """Get all active crops for a farmer"""
    user_lands = get_farmer_lands(farmer_id)
    user_land_ids = [l.land_id for l in user_lands]
    
    if not user_land_ids:
        return None
    
    sessions = CultivationSessionModel.query.filter(
        CultivationSessionModel.land_id.in_(user_land_ids)
    ).filter(
        CultivationSessionModel.session_status.in_(ACTIVE_STATUSES)
    ).all()
    
    if not sessions:
        return None
    
    response = "Here are your current crops:\n"
    for session in sessions:
        land = next((l for l in user_lands if l.land_id == session.land_id), None)
        crop_name = get_crop_name(session)
        status_icon = "✓" if session.session_status in ACTIVE_STATUSES else "○"
        response += f"{status_icon} {crop_name} on {land.land_name if land else 'Unknown land'} ({session.session_status})\n"
    
    return response


def get_neighbor_info(farmer_id):
    """Get neighbor information for farmer's lands - checks both directions"""
    user_lands = get_farmer_lands(farmer_id)
    user_land_ids = [l.land_id for l in user_lands]
    
    # Query both directions: user's land can be in land_id OR neighbour_land_id
    neighbors = NeighbourModel.query.filter(
        ((NeighbourModel.land_id.in_(user_land_ids)) | (NeighbourModel.neighbour_land_id.in_(user_land_ids))),
        NeighbourModel.status == 1
    ).all()
    
    if not neighbors:
        return []
    
    neighbor_land_ids = set()
    for n in neighbors:
        if n.land_id in user_land_ids:
            neighbor_land_ids.add(n.neighbour_land_id)
        elif n.neighbour_land_id in user_land_ids:
            neighbor_land_ids.add(n.land_id)
    
    return LandModel.query.filter(LandModel.land_id.in_(neighbor_land_ids)).all()


def format_neighbors(farmer_id, include_names=False, active_lands=None):
    """Format neighbor information"""
    neighbor_lands = get_neighbor_info(farmer_id)
    
    if not neighbor_lands or len(neighbor_lands) == 0:
        return "No neighbors found for your lands."
    
    if active_lands:
        active_land_ids = set(l.land_id for l in active_lands)
        neighbor_lands = [nl for nl in neighbor_lands if nl.land_id in active_land_ids]
    
    if not neighbor_lands:
        return "No neighbors found for your active lands."
    
    if include_names:
        response = "Your Neighbors:\n"
        for nl in neighbor_lands[:10]:
            if nl.farmer_rls:
                response += f"  • {nl.farmer_rls.farmer_name or 'Unknown'}: Owns {nl.land_name}\n"
            else:
                response += f"  • Owner of {nl.land_name}: Not registered\n"
    else:
        response = "Your Neighbor Lands:\n"
        for nl in neighbor_lands[:10]:
            neighbor_sessions = CultivationSessionModel.query.filter(
                CultivationSessionModel.land_id == nl.land_id,
                CultivationSessionModel.session_status.in_(ACTIVE_STATUSES)
            ).all()
            crops = []
            for ns in neighbor_sessions:
                if ns.crop_id:
                    crop = CropModel.query.get(ns.crop_id)
                    if crop:
                        crops.append(crop.crop_name)
            crops_str = ", ".join(crops) if crops else "No active crop"
            response += f"  • {nl.land_name}: {crops_str}\n"
    
    return response


def get_past_activities(farmer_id, specific_activity_type=None):
    """Get past performed activities for farmer"""
    user_lands = get_farmer_lands(farmer_id)
    user_land_ids = [l.land_id for l in user_lands]
    
    if not user_land_ids:
        return None
    
    sessions = CultivationSessionModel.query.filter(
        CultivationSessionModel.land_id.in_(user_land_ids)
    ).all()
    
    if not sessions:
        return "No cultivation history found."
    
    session_ids = [s.cultivation_session_id for s in sessions]
    performed_activities = PerformedActivityModel.query.filter(
        PerformedActivityModel.cultivation_session_id.in_(session_ids)
    ).all()
    
    if not performed_activities:
        return "No activities have been performed yet on your lands."
    
    activity_counts = {}
    for pa in performed_activities:
        act_name = get_activity_name_by_id(pa.Activity_id) if pa.Activity_id else pa.Activity_type
        if act_name:
            activity_counts[act_name] = activity_counts.get(act_name, 0) + 1
    
    if specific_activity_type:
        count = activity_counts.get(specific_activity_type, 0)
        return f"You have performed {specific_activity_type} {count} time(s) on your lands."
    
    response = "Here are your performed activities:\n"
    for act_name, count in activity_counts.items():
        response += f"  • {act_name}: {count} time(s)\n"
    
    return response


def get_upcoming_activities(farmer_id, specific_land_name=None):
    """Get upcoming activities for farmer's sessions"""
    user_lands = get_farmer_lands(farmer_id)
    user_land_ids = [l.land_id for l in user_lands]
    
    if not user_land_ids:
        return "You don't have any lands registered. Add a land first!", None
    
    # Find specific land if mentioned
    target_land = None
    if specific_land_name:
        query_lower = specific_land_name.lower()
        for land in user_lands:
            if land.land_name.lower() in query_lower:
                target_land = land
                break
    
    if target_land:
        # Get session for specific land
        session = get_session_by_land(target_land.land_id)
        
        if not session:
            # No active session on this land
            last_session = get_last_session_for_land(target_land.land_id)
            last_crop_name = get_crop_name(last_session) if last_session else None
            
            response = f"No active session on {target_land.land_name}.\n"
            if last_crop_name:
                response += f"Last crop grown: {last_crop_name}\n"
            response += "To check activities, you need to start a cultivation session first."
            return response, None
        
        # Get activities for this session
        result, code = ActivitySuggestionService.get_suggested_activities(session.cultivation_session_id)
        
        if code == 200 and result.get('activities'):
            crop_name = result.get('crop', 'Unknown')
            response = f"Upcoming activities for {crop_name} on {target_land.land_name}:\n"
            for act in result['activities'][:5]:
                status_icon = "✓" if act.get('status') == 'Performed' else "○"
                response += f"  {status_icon} {act.get('activity_name')} ({act.get('suggested_date')})\n"
            return response, 'single'
        return f"No activities found for {target_land.land_name}.", None
    
    # No specific land - show all active sessions
    sessions = get_active_sessions_for_farmer(farmer_id)
    
    if not sessions:
        return "You don't have any active cultivation sessions on your lands. Start a new session first!", None
    
    response = "Here are your upcoming activities:\n"
    has_activities = False
    
    for session in sessions[:5]:
        land = next((l for l in user_lands if l.land_id == session.land_id), None)
        crop_name = get_crop_name(session)
        
        result, code = ActivitySuggestionService.get_suggested_activities(session.cultivation_session_id)
        
        if code == 200 and result.get('activities'):
            has_activities = True
            response += f"\n{crop_name} on {land.land_name if land else 'Unknown'}:\n"
            for act in result['activities'][:3]:
                status_icon = "✓" if act.get('status') == 'Performed' else "○"
                response += f"  {status_icon} {act.get('activity_name')} ({act.get('suggested_date')})\n"
    
    if not has_activities:
        response = "No upcoming activities found. Your crops are all set!"
    
    return response, 'multiple'


def get_crop_sowing_info(crop_name):
    """Get sowing information for a specific crop"""
    from Controller.RecommendationController import CropKnowledgeBase
    
    kb = CropKnowledgeBase()
    crop_info = kb.get_crop_info(crop_name)
    
    if not crop_info:
        # Fallback to basic crop data from database
        crop = CropModel.query.filter(CropModel.crop_name.ilike(f"%{crop_name}%")).first()
        if crop:
            season_map = {0: "Rabi", 1: "Kharif", 2: "Zaid"}
            return {
                'season': season_map.get(crop.season_name, "Current season"),
                'sowing_time': "Follow local agricultural calendar",
                'tips': "Consult local agriculture extension for best practices"
            }
        return None
    
    # Map season code to name
    season_code = crop_info.get('season_name', 0)
    season_map = {0: "Kharif (Summer)", 1: "Rabi (Winter)", 2: "Zaid (Spring)"}
    season = season_map.get(season_code, "Current season")
    
    # Get suggested actions as tips
    from Controller.RecommendationController import CropKnowledgeBase
    actions = CropKnowledgeBase._get_suggested_actions(crop_name) if hasattr(CropKnowledgeBase, '_get_suggested_actions') else []
    tips = actions[0] if actions else "Follow recommended farming practices"
    
    return {
        'season': season,
        'sowing_time': f"Plant during {season.lower()}",
        'tips': tips
    }


def get_past_sessions_for_land(land_id, limit=5):
    """Get past cultivation sessions for a specific land"""
    sessions = CultivationSessionModel.query.filter(
        CultivationSessionModel.land_id == land_id
    ).order_by(CultivationSessionModel.cultivation_session_id.desc()).limit(limit).all()
    
    if not sessions:
        return []
    
    result = []
    for session in sessions:
        crop_name = get_crop_name(session)
        result.append({
            'session_id': session.cultivation_session_id,
            'crop_name': crop_name,
            'status': session.session_status,
            'is_profit': session.is_profit,
            'amount_per_acre': session.amount_per_acre,
            'seed_name': session.seed_name
        })
    return result


def get_my_past_sessions(farmer_id, limit=5, land_name=None):
    """Get past cultivation sessions for all user's lands"""
    user_lands = get_farmer_lands(farmer_id)
    if not user_lands:
        return []
    
    # Filter by land name if provided
    if land_name:
        user_lands = [l for l in user_lands if land_name.lower() in l.land_name.lower()]
    
    if not user_lands:
        return []
    
    user_land_ids = [l.land_id for l in user_lands]
    
    sessions = CultivationSessionModel.query.filter(
        CultivationSessionModel.land_id.in_(user_land_ids)
    ).order_by(CultivationSessionModel.cultivation_session_id.desc()).limit(limit).all()
    
    if not sessions:
        return []
    
    result = []
    land_map = {l.land_id: l.land_name for l in user_lands}
    for session in sessions:
        crop_name = get_crop_name(session)
        result.append({
            'session_id': session.cultivation_session_id,
            'crop_name': crop_name,
            'land_name': land_map.get(session.land_id, 'Unknown'),
            'status': session.session_status,
            'is_profit': session.is_profit,
            'amount_per_acre': session.amount_per_acre
        })
    return result


def get_neighbor_past_sessions(farmer_id, limit=5, neighbor_land_name=None):
    """Get past cultivation sessions for neighbor's lands"""
    user_lands = get_farmer_lands(farmer_id)
    user_land_ids = [l.land_id for l in user_lands]
    
    if not user_land_ids:
        return []
    
    neighbors = NeighbourModel.query.filter(
        ((NeighbourModel.land_id.in_(user_land_ids)) | (NeighbourModel.neighbour_land_id.in_(user_land_ids))),
        NeighbourModel.status == 1
    ).all()
    
    if not neighbors:
        return []
    
    neighbor_land_ids = set()
    for n in neighbors:
        if n.land_id in user_land_ids:
            neighbor_land_ids.add(n.neighbour_land_id)
        elif n.neighbour_land_id in user_land_ids:
            neighbor_land_ids.add(n.land_id)
    
    neighbor_lands = LandModel.query.filter(LandModel.land_id.in_(neighbor_land_ids)).all()
    
    # Filter by neighbor land name if provided
    if neighbor_land_name:
        neighbor_lands = [l for l in neighbor_lands if neighbor_land_name.lower() in l.land_name.lower()]
    
    if not neighbor_lands:
        return []
    
    neighbor_land_ids = [l.land_id for l in neighbor_lands]
    
    sessions = CultivationSessionModel.query.filter(
        CultivationSessionModel.land_id.in_(neighbor_land_ids)
    ).order_by(CultivationSessionModel.cultivation_session_id.desc()).limit(limit).all()
    
    if not sessions:
        return []
    
    result = []
    land_map = {l.land_id: l.land_name for l in neighbor_lands}
    for session in sessions:
        crop_name = get_crop_name(session)
        result.append({
            'session_id': session.cultivation_session_id,
            'crop_name': crop_name,
            'land_name': land_map.get(session.land_id, 'Unknown'),
            'status': session.session_status,
            'is_profit': session.is_profit,
            'amount_per_acre': session.amount_per_acre
        })
    return result


def get_profitable_sessions(farmer_id, land_name=None):
    """Get sessions that were profitable"""
    user_lands = get_farmer_lands(farmer_id)
    if not user_lands:
        return []
    
    if land_name:
        user_lands = [l for l in user_lands if land_name.lower() in l.land_name.lower()]
    
    if not user_lands:
        return []
    
    user_land_ids = [l.land_id for l in user_lands]
    
    sessions = CultivationSessionModel.query.filter(
        CultivationSessionModel.land_id.in_(user_land_ids),
        CultivationSessionModel.is_profit == 1
    ).order_by(CultivationSessionModel.cultivation_session_id.desc()).all()
    
    if not sessions:
        return []
    
    result = []
    land_map = {l.land_id: l.land_name for l in user_lands}
    for session in sessions:
        crop_name = get_crop_name(session)
        result.append({
            'session_id': session.cultivation_session_id,
            'crop_name': crop_name,
            'land_name': land_map.get(session.land_id, 'Unknown'),
            'amount_per_acre': session.amount_per_acre
        })
    return result


def get_activities_for_profitable_sessions(farmer_id, land_name=None):
    """Get activities performed for profitable sessions"""
    user_lands = get_farmer_lands(farmer_id)
    if not user_lands:
        return None
    
    if land_name:
        user_lands = [l for l in user_lands if land_name.lower() in l.land_name.lower()]
    
    if not user_lands:
        return None
    
    user_land_ids = [l.land_id for l in user_lands]
    
    # Get profitable sessions
    profitable_sessions = CultivationSessionModel.query.filter(
        CultivationSessionModel.land_id.in_(user_land_ids),
        CultivationSessionModel.is_profit == 1
    ).all()
    
    if not profitable_sessions:
        return "No profitable sessions found for your lands."
    
    session_ids = [s.cultivation_session_id for s in profitable_sessions]
    performed_activities = PerformedActivityModel.query.filter(
        PerformedActivityModel.cultivation_session_id.in_(session_ids)
    ).all()
    
    if not performed_activities:
        return "No activities recorded for your profitable sessions."
    
    activity_counts = {}
    for pa in performed_activities:
        act_name = get_activity_name_by_id(pa.Activity_id) if pa.Activity_id else pa.Activity_type
        if act_name:
            activity_counts[act_name] = activity_counts.get(act_name, 0) + 1
    
    land_map = {l.land_id: l.land_name for l in user_lands}
    
    response = "Activities performed for profitable sessions:\n"
    for session in profitable_sessions:
        crop_name = get_crop_name(session)
        land_name_str = land_map.get(session.land_id, 'Unknown')
        
        session_activities = [pa for pa in performed_activities if pa.cultivation_session_id == session.cultivation_session_id]
        if session_activities:
            response += f"\n{crop_name} on {land_name_str}:\n"
            for pa in session_activities:
                act_name = get_activity_name_by_id(pa.Activity_id) if pa.Activity_id else pa.Activity_type
                response += f"  • {act_name}\n"
    
    return response


def get_profitable_past_crops(farmer_id):
    """Get list of profitable crops from past sessions"""
    user_lands = get_farmer_lands(farmer_id)
    if not user_lands:
        return None
    
    user_land_ids = [l.land_id for l in user_lands]
    
    profitable_sessions = CultivationSessionModel.query.filter(
        CultivationSessionModel.land_id.in_(user_land_ids),
        CultivationSessionModel.is_profit == 1
    ).all()
    
    if not profitable_sessions:
        return "No profitable crops found in your history."
    
    profitable_crops = {}
    land_map = {l.land_id: l.land_name for l in user_lands}
    
    for session in profitable_sessions:
        crop_name = get_crop_name(session)
        if crop_name:
            if crop_name not in profitable_crops:
                profitable_crops[crop_name] = []
            profitable_crops[crop_name].append({
                'land_name': land_map.get(session.land_id, 'Unknown'),
                'amount': session.amount_per_acre
            })
    
    if not profitable_crops:
        return "No profitable crops found."
    
    response = "Your profitable crops from past sessions:\n"
    for crop, details in profitable_crops.items():
        lands = ", ".join([d['land_name'] for d in details])
        amounts = [d['amount'] for d in details if d['amount']]
        amount_str = f" (Earned: {', '.join(amounts)})" if amounts else ""
        response += f"  • {crop} on {lands}{amount_str}\n"
    
    return response


def get_neighbor_owner_info(farmer_id, neighbor_land_name=None):
    """Get owner information for neighbor lands"""
    user_lands = get_farmer_lands(farmer_id)
    user_land_ids = [l.land_id for l in user_lands]
    
    if not user_land_ids:
        return "You don't have any lands registered."
    
    neighbors = NeighbourModel.query.filter(
        ((NeighbourModel.land_id.in_(user_land_ids)) | (NeighbourModel.neighbour_land_id.in_(user_land_ids))),
        NeighbourModel.status == 1
    ).all()
    
    if not neighbors:
        return "No neighbors found for your lands."
    
    neighbor_land_ids = set()
    for n in neighbors:
        if n.land_id in user_land_ids:
            neighbor_land_ids.add(n.neighbour_land_id)
        elif n.neighbour_land_id in user_land_ids:
            neighbor_land_ids.add(n.land_id)
    
    neighbor_lands = LandModel.query.filter(LandModel.land_id.in_(neighbor_land_ids)).all()
    
    # Filter by name if provided
    if neighbor_land_name:
        neighbor_lands = [l for l in neighbor_lands if neighbor_land_name.lower() in l.land_name.lower()]
    
    if not neighbor_lands:
        return "No matching neighbor land found."
    
    response = "Neighbor Land Owners:\n"
    for nl in neighbor_lands:
        owner_name = nl.farmer_rls.farmer_name if nl.farmer_rls else "Unknown"
        response += f"  • {nl.land_name}: Owned by {owner_name}\n"
    
    return response


def check_crop_suitability(land_id, crop_name):
    """Check if a crop is suitable for a land with reasons"""
    from Controller.RecommendationController import CropKnowledgeBase
    
    land = LandModel.query.get(land_id)
    if not land:
        return None
    
    kb = CropKnowledgeBase()
    crop_info = kb.get_crop_info(crop_name)
    
    if not crop_info:
        return None
    
    reasons = []
    
    # Check soil compatibility
    land_soil = land.soil_type.lower() if land.soil_type else ""
    suitable_soils = crop_info.get("suitable_soils", [])
    if suitable_soils:
        soil_match = any(s.lower() in land_soil or land_soil in s.lower() for s in suitable_soils)
        if soil_match:
            reasons.append(f"Your soil type ({land.soil_type}) is suitable for {crop_name}")
        else:
            reasons.append(f"Note: {crop_name} prefers {', '.join(suitable_soils)} soil")
    
    # Check water source compatibility
    water_source = land.source_of_water.lower() if land.source_of_water else ""
    water_requirements = crop_info.get("water_requirement", "")
    if water_requirements:
        if "less" in water_requirements.lower() or "low" in water_requirements.lower():
            reasons.append(f"{crop_name} requires less water - suitable for your water source")
        elif "moderate" in water_requirements.lower():
            reasons.append(f"{crop_name} needs moderate water - matches your irrigation")
        elif "high" in water_requirements.lower():
            reasons.append(f"Note: {crop_name} requires high water - ensure adequate irrigation")
    
    # Check season compatibility
    current_month = datetime.now().month
    if current_month >= 4 and current_month <= 9:
        current_season = "Kharif"
    else:
        current_season = "Rabi"
    
    suitable_seasons = crop_info.get("suitable_seasons", [])
    if suitable_seasons:
        season_match = current_season in suitable_seasons
        if season_match:
            reasons.append(f"{crop_name} grows well in {current_season} season (current)")
        else:
            reasons.append(f"Note: {crop_name} is best in {', '.join(suitable_seasons)} seasons")
    
    # Check region suitability
    if land.city_id:
        city = CityModel.query.get(land.city_id)
        if city and city.province_id:
            province_id = city.province_id
            is_suitable = kb.is_crop_grown_in_region(crop_name, province_id, land.city_id)
            if is_suitable:
                reasons.append(f"{crop_name} is suitable for your region")
            else:
                reasons.append(f"Note: Check if {crop_name} grows in your specific area")
    
    if not reasons:
        reasons.append(f"{crop_name} may be grown with proper management")
    
    return {
        'crop': crop_name,
        'land': land.land_name,
        'suitable': True,
        'reasons': reasons
    }