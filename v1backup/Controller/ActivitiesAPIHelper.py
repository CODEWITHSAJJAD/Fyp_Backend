from flask import jsonify
from Services.ActivitySuggestionService import ActivitySuggestionService

def ensure_seed(session_id):
    res, code = ActivitySuggestionService.seed_suggested_activities(session_id)
    return jsonify(res), code
