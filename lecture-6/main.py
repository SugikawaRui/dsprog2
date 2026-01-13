import flet as ft
from weather_service import fetch_area_list, fetch_weather
import datetime

def main(page: ft.Page):
    page.title = "Weather App"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Store area data
    area_data = {}
    centers = {}
    offices = {}
    
    # UI Components
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=400,
        group_alignment=-0.9,
        destinations=[],
        on_change=lambda e: update_weather_list(e.control.selected_index)
    )
    
    weather_list = ft.ListView(expand=True, spacing=10, padding=20)
    
    
    from database import init_db, save_area, save_weather_forecast, get_specific_dates_forecast
    init_db()

    def get_weather_detail(e, area_code, area_name):
        """Fetches and displays weather detail using DB strategy."""
        tile = e.control
        if tile.data.get("fetched"):
            return

        if e.data == "true":
            # ローディングを表示
            tile.controls = [ft.ProgressBar()]
            tile.update()
            
            # １　APIから取得
            weather_data = fetch_weather(area_code)
            
            error_msg = None
            if not weather_data:
                error_msg = "Failed to load weather data from API."
            else:


                # 2. DBに保存
                try:
                    report = weather_data[0]
                    time_series = report["timeSeries"][0]
                    time_defines = time_series["timeDefines"]
                    
                    
                    save_area(area_code, area_name)
                    
                    for i, area_weather in enumerate(time_series["areas"]):
                         sub_area_name = area_weather["area"]["name"]
                         weathers = area_weather["weathers"]
                         
                         for j, weather in enumerate(weathers):
                            if j < len(time_defines):
                                dt_str = time_defines[j]
                                dt = datetime.datetime.fromisoformat(dt_str)
                                date_str = dt.strftime("%Y-%m-%d")
                                
                                # Save without temps
                                save_weather_forecast(area_code, date_str, weather)
                                
                except (IndexError, KeyError) as err:
                    error_msg = f"Error parsing/saving data: {err}"

            # 3. 特定の日付の予報を取得
            today = datetime.date.today()
            yesterday = today - datetime.timedelta(days=1)
            tomorrow = today + datetime.timedelta(days=1)
            
            target_dates = [
                yesterday.strftime("%Y-%m-%d"),
                today.strftime("%Y-%m-%d"),
                tomorrow.strftime("%Y-%m-%d")
            ]
            
            db_forecasts = get_specific_dates_forecast(area_code, target_dates)
            
            forecast_map = {item["date"]: item["weather"] for item in db_forecasts}
            
            # 4. UI更新
            forecast_controls = []
            day_forecasts = []
            
            for date_str in target_dates:
                try:
                    forecast_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                    date_label = forecast_date.strftime("%m-%d")
                except ValueError:
                    date_label = date_str

                weather_text = forecast_map.get(date_str, "---") # Default to "---" if missing

                day_forecasts.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"{date_label}", size=12, color="grey"),
                            ft.Text(f"{weather_text}")
                        ], spacing=5),
                        padding=10,
                        border=ft.border.all(1, ft.Colors.OUTLINE),
                        border_radius=5,
                        width=150
                    )
                )
            
            forecast_controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"Forecast", weight="bold"),
                        ft.Row(day_forecasts, wrap=True)
                    ]),
                    margin=ft.margin.only(bottom=10)
                )
            )
            tile.controls = forecast_controls
            tile.data["fetched"] = True
                    
            tile.update()

    def update_weather_list(index):
        weather_list.controls.clear()
        
        # 中心コードを取得
        center_code = list(centers.keys())[index]
        children_codes = centers[center_code]["children"]
        
        for code in children_codes:
            if code in offices:
                office_data = offices[code]
                name = office_data["name"]
                
                # DBに保存
                save_area(code, name)
                
                # オンデマンドで詳細を取得
                tile = ft.ExpansionTile(
                    title=ft.Text(name),
                    subtitle=ft.Text("Click to view forecast"),
                    on_change=lambda e, c=code, n=name: get_weather_detail(e, c, n),
                    data={"fetched": False}, # Track if we fetched already
                    controls=[ft.Container(height=50)] # Placeholder
                )
                weather_list.controls.append(tile)
        
        weather_list.update()

    def load_area_data():
        nonlocal area_data, centers, offices
        data = fetch_area_list()
        if data:
            area_data = data
            centers = data.get("centers", {})
            offices = data.get("offices", {})
            
            # ナビゲーションレールの宛先を設定
            rail.destinations = [
                ft.NavigationRailDestination(
                    icon=ft.Icons.LOCATION_CITY, 
                    selected_icon=ft.Icons.LOCATION_CITY_OUTLINED, 
                    label=center["name"]
                ) for code, center in centers.items()
            ]
            
            #  最初の天気リストを表示
            if centers:
                update_weather_list(0)
            
            page.update()
        else:
            page.add(ft.Text("Failed to load area list.", color="red"))

    # レイアウトの設定
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                weather_list,
            ],
            expand=True,
            height=500 
        )
    )

    load_area_data()

ft.app(target=main)
