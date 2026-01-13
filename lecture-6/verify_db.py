import sqlite3
import os

DB_NAME = "weather.db"

def check_db():
    from database import init_db, save_area, save_weather_forecast, get_latest_forecasts
    
    # Initialize DB for testing
    init_db()
    
    if not os.path.exists(DB_NAME):
        print("FAIL: Database file not found even after init.")
        return False
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables found: {tables}")
    
    if "areas" not in tables or "weather_forecasts" not in tables:
        print("FAIL: Missing tables.")
        return False

    # Check data (assuming main.py ran or we can insert dummy)
    # Since we can't run GUI, we can manually test database.py functions
    from database import save_area, save_weather_forecast, get_latest_forecasts
    
    # Test Insert
    print("Testing Insert...")
    save_area("999999", "Test Area")
    # Insert Yesterday, Today, Tomorrow
    import datetime
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    tomorrow = today + datetime.timedelta(days=1)
    
    save_weather_forecast("999999", yesterday.strftime("%Y-%m-%d"), "Yesterday Weather")
    save_weather_forecast("999999", today.strftime("%Y-%m-%d"), "Today Weather")
    save_weather_forecast("999999", tomorrow.strftime("%Y-%m-%d"), "Tomorrow Weather")
    
    # Test Retrieve Logic
    from database import get_specific_dates_forecast
    
    print("Testing Retrieve Specific Dates...")
    target_dates = [
        yesterday.strftime("%Y-%m-%d"),
        today.strftime("%Y-%m-%d"),
        tomorrow.strftime("%Y-%m-%d")
    ]
    
    forecasts = get_specific_dates_forecast("999999", target_dates)
    if not forecasts:
        print("FAIL: No forecasts retrieved.")
        return False
        
    print(f"Retrieved {len(forecasts)} records.")
    # Check simple presence
    dates_found = [f["date"] for f in forecasts]
    if yesterday.strftime("%Y-%m-%d") in dates_found and \
       today.strftime("%Y-%m-%d") in dates_found:
        print("SUCCESS: Data verification passed.")
        return True
    else:
        print(f"FAIL: Missing expected dates. Found: {dates_found}")
        return False

if __name__ == "__main__":
    if check_db():
        print("DB VERIFICATION PASSED")
    else:
        print("DB VERIFICATION FAILED")
