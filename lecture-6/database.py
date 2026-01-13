import sqlite3
import datetime

DB_NAME = "weather.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # エリア情報を保存するテーブルを作成します
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS areas (
        area_code TEXT PRIMARY KEY,
        area_name TEXT NOT NULL
    )
    """)
    
    
    # 天気予報情報を保存するテーブルを作成します
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
    
   
    cursor.execute(query, (area_code, *dates))
    rows = cursor.fetchall()
    conn.close()
    
    
    result_map = {}
    for row in rows:
        d = row[0]
        w = row[1]
        if d not in result_map:
            result_map[d] = w
            
    # リクエストされた日付の順序で結果を返します。存在しない場合は空にします
    result = []
    for d in dates:
        if d in result_map:
            result.append({"date": d, "weather": result_map[d]})
            
    return result
