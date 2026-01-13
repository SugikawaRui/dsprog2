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
    
    # Removed old get_weather_detail as it is redefined below in the new logic block. 
    # However, to be clean, I should've done one big replace. 
    # Since I did the bottom part, I effectively have two get_weather_detail functions now if I paste it at the bottom?
    # No, I replaced update_weather_list and below. 
    # I need to replace the old get_weather_detail with NOTHING or the new one.
    # Actually, I pasted the NEW get_weather_detail inside the previous call? 
    # Let me check the previous call content... 
    # YES, I pasted 'def get_weather_detail...' inside the replacement content of step 93.
    # So I need to DELETE the OLD get_weather_detail which is at lines 27..111.

    # Database init
    from database import init_db, save_area, save_weather_forecast, get_specific_dates_forecast
    init_db()

    def get_weather_detail(e, area_code, area_name):
        """Fetches and displays weather detail using DB strategy."""
        tile = e.control
        if tile.data.get("fetched"):
            return

        if e.data == "true":
            # Show loading
            tile.controls = [ft.ProgressBar()]
            tile.update()
            
            # 1. Fetch from API
            weather_data = fetch_weather(area_code)
            
            error_msg = None
            if not weather_data:
                error_msg = "Failed to load weather data from API."
            else:
                # 2. Parse and Save to DB
                try:
                    report = weather_data[0]
                    time_series = report["timeSeries"][0]
                    time_defines = time_series["timeDefines"]
                    
                    # We save the area name to be sure
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

            # 3. Read from DB to display
            # Target dates: Yesterday, Today, Tomorrow
            today = datetime.date.today()
            yesterday = today - datetime.timedelta(days=1)
            tomorrow = today + datetime.timedelta(days=1)
            
            target_dates = [
                yesterday.strftime("%Y-%m-%d"),
                today.strftime("%Y-%m-%d"),
                tomorrow.strftime("%Y-%m-%d")
            ]
            
            db_forecasts = get_specific_dates_forecast(area_code, target_dates)
            
            # Map for quick lookup
            # db_forecasts is list of dicts: {"date": "YYYY-MM-DD", "weather": "..."}
            forecast_map = {item["date"]: item["weather"] for item in db_forecasts}
            
            # Always build UI from target_dates to ensure 3 columns
            forecast_controls = []
            day_forecasts = []
            
            for date_str in target_dates:
                # Convert date string to date object and format as MM-DD
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
        
        # Get selected center code
        center_code = list(centers.keys())[index]
        children_codes = centers[center_code]["children"]
        
        for code in children_codes:
            if code in offices:
                office_data = offices[code]
                name = office_data["name"]
                
                # Save area info to DB when listing
                save_area(code, name)
                
                # Create ExpansionTile
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
            
            # Populate Rail
            rail.destinations = [
                ft.NavigationRailDestination(
                    icon=ft.Icons.LOCATION_CITY, 
                    selected_icon=ft.Icons.LOCATION_CITY_OUTLINED, 
                    label=center["name"]
                ) for code, center in centers.items()
            ]
            
            # Initial update
            if centers:
                update_weather_list(0)
            
            page.update()
        else:
            page.add(ft.Text("Failed to load area list.", color="red"))

    # Layout
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                weather_list,
            ],
            expand=True,
            height=500 # Explicit height for scrolling
        )
    )

    load_area_data()

ft.app(target=main)
