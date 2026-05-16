import json
import os
from datetime import timedelta
import re

CROPS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "crop_activities_template.json")

def load_crop_activities():
    with open(CROPS_FILE, "r") as f:
        data = json.load(f)
    return data.get("crop_activities", {})

CROP_ACTIVITIES = load_crop_activities()

def get_activities_for_crop(crop_name):
    key = crop_name.lower().replace(" ", "_").replace("-", "_")
    # Remove parentheses and their contents, or clean them
    key = re.sub(r'[\(\)]', '', key)  # Removes both ( and )
    
    crop_data = None
    for crop_key, activities in CROP_ACTIVITIES.items():
        if crop_key.lower() == key:
            crop_data = activities
            break
    
    if not crop_data:
        for crop_key, activities in CROP_ACTIVITIES.items():
            if key in crop_key.lower() or crop_key.lower() in key:
                crop_data = activities
                break
    
    if not crop_data:
        return None
    
    activities = crop_data.get("activities", [])
    expanded = []
    
    for act in activities:
        activity_id = act.get("activity_id")
        days_from_sowing = act.get("days_from_sowing")
        is_cycle = act.get("is_cycle", False)
        cycle_count = act.get("cycle_count", 1)
        cycle_interval = act.get("cycle_interval_days", 0)
        
        if is_cycle and cycle_count > 1:
            for i in range(cycle_count):
                cycle_day = days_from_sowing + (i * cycle_interval)
                expanded.append({
                    "name": act.get("activity_name"),
                    "activity_id": activity_id,
                    "days_from_sowing": cycle_day,
                    "is_cycle": True,
                    "cycle_number": i + 1,
                    "total_cycles": cycle_count
                })
        else:
            expanded.append({
                "name": act.get("activity_name"),
                "activity_id": activity_id,
                "days_from_sowing": days_from_sowing,
                "is_cycle": False,
                "cycle_number": 1,
                "total_cycles": 1
            })
    
    expanded.sort(key=lambda x: x["days_from_sowing"])
    return expanded

def get_activity_name_by_id(activity_id):
    activity_map = {
        1: "Land Preparation",
        2: "Sowing",
        3: "Watering",
        4: "Fertilizer",
        5: "Weeding",
        6: "Spray",
        7: "Harvesting",
        8: "Threshing",
        9: "Pruning",
        10: "Soil Testing",
        11: "Mulching"
    }
    return activity_map.get(activity_id, f"Activity_{activity_id}")

def is_repeating_activity(activity_id):
    repeating_activities = [3, 5, 6]
    return activity_id in repeating_activities