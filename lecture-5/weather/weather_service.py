import requests
import json

AREA_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_BASE_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/"

def fetch_area_list():
    """Fetches the list of areas from the JMA API."""
    try:
        response = requests.get(AREA_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching area list: {e}")
        return None

def fetch_weather(area_code):
    """Fetches the weather forecast for a specific area code."""
    url = f"{FORECAST_BASE_URL}{area_code}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching weather for {area_code}: {e}")
        return None
