"""Chatbot helper functions - reusable utility functions for chatbot"""

from Model.LandModel import LandModel
from Model.CultivationSessionModel import CultivationSessionModel
from Model.CropModel import CropModel
from Model.NeighbourModel import NeighbourModel
from Model.FarmerModel import FarmerModel
from Model.PerformActivityModel import PerformedActivityModel
from Services.ActivitySuggestionService import ActivitySuggestionService
from Services.WeatherService import get_weather
from Services.CropActivityData import get_activity_name_by_id

# Active session statuses
ACTIVE_STATUSES = ['Active', 'active', 'Running', 'In Progress', 'ACTIVE', 'Sown', 'sown', 'Growing']


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


def format_neighbors(farmer_id, include_names=False):
    """Format neighbor information"""
    neighbor_lands = get_neighbor_info(farmer_id)
    
    if not neighbor_lands or len(neighbor_lands) == 0:
        return "No neighbors found for your lands."
    
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