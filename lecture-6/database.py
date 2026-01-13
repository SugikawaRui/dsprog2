import sqlite3
import datetime

DB_NAME = "weather.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create areas table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS areas (
        area_code TEXT PRIMARY KEY,
        area_name TEXT NOT NULL
    )
    """)
    
    # Create weather_forecasts table
    # Removed temp columns as per request
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather_forecasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        area_code TEXT,
        forecast_date TEXT,
        weather TEXT,
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (area_code) REFERENCES areas (area_code)
    )
    """)
    
    conn.commit()
    conn.close()

def save_area(area_code, area_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO areas (area_code, area_name)
    VALUES (?, ?)
    """, (area_code, area_name))
    conn.commit()
    conn.close()

def save_weather_forecast(area_code, forecast_date, weather):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # We want to replace if same area and date? Or keep history?
    # Schema doesn't enforce unique area+date. 
    # But usually we want the latest fetch for a date.
    # We can just insert, and the select query handles getting the latest fetched_at.
    cursor.execute("""
    INSERT INTO weather_forecasts (area_code, forecast_date, weather, fetched_at)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """, (area_code, forecast_date, weather))
    conn.commit()
    conn.close()

def get_latest_forecasts(area_code, limit=3):
    """Gets the latest fetch of forecasts for an area."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT forecast_date, weather 
    FROM weather_forecasts 
    WHERE area_code = ? 
    ORDER BY fetched_at DESC, forecast_date ASC
    LIMIT ?
    """, (area_code, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        result.append({
            "date": row[0],
            "weather": row[1]
        })
    return result

def get_specific_dates_forecast(area_code, dates):
    """
    Gets the latest forecast for specific dates for an area.
    dates: list of date strings 'YYYY-MM-DD'
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    placeholders = ','.join('?' for _ in dates)
    query = f"""
    SELECT forecast_date, weather
    FROM weather_forecasts
    WHERE area_code = ? AND forecast_date IN ({placeholders})
    ORDER BY fetched_at DESC
    """
    
    # This query might return multiple entries for the same date (different fetch times).
    # We need to filter in python or upgrade query to group by date.
    # Let's do a simple select and filter in python for latest fetched_at per date.
    
    cursor.execute(query, (area_code, *dates))
    rows = cursor.fetchall()
    conn.close()
    
    # Process checks: we want one entry per date, the one with max fetched_at (implied by ORDER BY fetched_at DESC in pure select? No, ORDER BY applies to the set.)
    # Actually, simply iterating and keeping the first occurrence of each date works if ordered by fetched_at DESC.
    
    result_map = {}
    for row in rows:
        d = row[0]
        w = row[1]
        if d not in result_map:
            result_map[d] = w
            
    # Return list in order of requested dates, or empty if missing
    result = []
    for d in dates:
        if d in result_map:
            result.append({"date": d, "weather": result_map[d]})
            
    return result
