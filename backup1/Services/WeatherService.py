import requests
from url import OPENWEATHER_BASE_URL,OPENWEATHER_API_KEY

def get_weather(city_name):
    try:
        params = {
            "q": city_name,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        response = requests.get(OPENWEATHER_BASE_URL, params=params, timeout=10)

        if response.status_code != 200:
            return {
                "condition": "unknown",
                "temperature": None,
                "humidity": None,
                "rain_probability": 0,
                "description": f"API error: {response.status_code}",
                "error": True
            }
        
        data = response.json()
        weather = data.get("weather", [{}])[0]
        main = data.get("main", {})
        
        condition = map_weather_condition(weather.get("main", ""), weather.get("id", 0), data.get("wind", {}).get("speed", 0))
        
        rain_prob = 0
        if "rain" in data:
            rain_prob = 100 if data["rain"].get("1h", 0) > 0 or data["rain"].get("3h", 0) > 0 else 0
        
        return {
            "condition": condition,
            "temperature": main.get("temp"),
            "humidity": main.get("humidity"),
            "rain_probability": rain_prob,
            "description": weather.get("description", ""),
            "wind_speed": data.get("wind", {}).get("speed", 0),
            "city": city_name,
            "raw_data": data
        }
    
    except Exception as e:
        return {
            "condition": "unknown",
            "temperature": None,
            "humidity": None,
            "rain_probability": 0,
            "description": str(e),
            "error": True
        }

def map_weather_condition(weather_main, weather_id, wind_speed):

    if weather_id >= 200 and weather_id < 300:
        return "rainy"
    elif weather_id >= 300 and weather_id < 600:
        return "rainy"
    elif weather_id >= 600 and weather_id < 700:
        return "snowy"
    elif weather_id >= 700 and weather_id < 800:
        return "foggy"
    elif weather_id == 800:
        return "sunny"
    elif weather_id > 800:
        return "cloudy"
    
    if wind_speed > 10:
        return "windy"
    
    return "sunny"

def is_weather_suitable_for_activity(activity_name, weather):
    condition = weather.get("condition", "unknown")
    rain_prob = weather.get("rain_probability", 0)
    humidity = weather.get("humidity", 0)
    wind_speed = weather.get("wind_speed", 0)
    
    activity_lower = activity_name.lower()
    
    if "watering" in activity_lower or "water" in activity_lower:
        if condition == "rainy" or rain_prob > 50:
            return False, "Rain expected - skip watering"
        return True, ""
    
    if "fertilizer" in activity_lower or "fertilizer" in activity_lower:
        if condition == "rainy" or rain_prob > 40:
            return False, "Rain expected - delay fertilizer application"
        if wind_speed > 15:
            return False, "High wind - delay fertilizer application"
        return True, ""
    
    if "spray" in activity_lower or "spraying" in activity_lower:
        if condition == "rainy" or rain_prob > 30:
            return False, "Rain expected - delay spraying"
        if wind_speed > 15:
            return False, "High wind - delay spraying"
        if humidity > 85:
            return False, "High humidity - delay spraying"
        return True, ""

    if "harvest" in activity_lower or "harvesting" in activity_lower:
        if condition == "rainy" or rain_prob > 30:
            return False, "Rain expected - delay harvesting"
        if humidity > 80:
            return False, "High humidity - delay harvesting"
        return True, ""

    if "weeding" in activity_lower:
        if condition == "rainy" or rain_prob > 40:
            return False, "Rain expected - delay weeding"
        return True, ""
    return True, ""

def get_weather_delay_days(activity_name, weather):
    condition = weather.get("condition", "unknown")
    rain_prob = weather.get("rain_probability", 0)
    if condition == "rainy" or rain_prob > 50:
        return 1
    elif condition == "cloudy" and rain_prob > 20:
        return 1
    return 0

