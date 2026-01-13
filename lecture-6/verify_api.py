from weather_service import fetch_area_list, fetch_weather
import json

def test_area_fetch():
    print("Testing Area Fetch...")
    data = fetch_area_list()
    if not data:
        print("FAIL: No data returned from area fetch")
        return False
    
    if "centers" not in data or "offices" not in data:
        print("FAIL: 'centers' or 'offices' missing in area data")
        return False
    
    print(f"SUCCESS: Fetched {len(data['centers'])} centers.")
    return True

def test_weather_fetch():
    print("Testing Weather Fetch (Tokyo 130000)...")
    
    # 130000は東京です
    data = fetch_weather("130000")
    if not data:
        print("FAIL: No data returned for Tokyo weather")
        return False
    
    # データが期待される形式であることを確認します。具体的には、最初の要素に"timeSeries"キーが存在し、その中に"areas"キーが含まれていることを確認します。
    try:
        report = data[0]
        time_series = report["timeSeries"][0]
        areas = time_series["areas"]
        print(f"SUCCESS: Fetched forecast for {len(areas)} sub-areas.")
        for area in areas:
            print(f" - {area['area']['name']}: {area['weathers'][0]}")
    except Exception as e:
        print(f"FAIL: Error parsing weather data: {e}")
        return False
        
    return True

if __name__ == "__main__":
    if test_area_fetch() and test_weather_fetch():
        print("\nALL TESTS PASSED")
    else:
        print("\nTESTS FAILED")
