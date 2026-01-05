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
    
    def get_weather_detail(e, area_code, area_name):
        """Fetches and displays weather detail in the ExpansionTile."""
        # Only fetch if we rely on on_change or explicit action, 
        # but ExpansionTile doesn't have a simple 'on_expand' callback that fetches *content* dynamically 
        # without pre-building controls. 
        # However, we can prepopulate with a loader and replace it content?
        # Simpler approach: Fetch on click of a "Load Forecast" button inside the tile, 
        # or just pre-fetch basic info?
        # User requirement 4: "Select region -> Display weather". 
        # Let's try to fetch when the specific tile is expanded if possible, or just add a button.
        # Actually, ExpansionTile has on_change (expanded check).
        
        tile = e.control
        if tile.data.get("fetched"):
            return

        if e.data == "true":
            # Show loading
            tile.controls = [ft.ProgressBar()]
            tile.update()
            
            weather_data = fetch_weather(area_code)
            
            if not weather_data:
                tile.controls = [ft.Text("Failed to load weather data.", color="red")]
            else:
                # Parse weather data
                # Usually [0] is the 3-day forecast
                try:
                    report = weather_data[0]
                    time_series = report["timeSeries"][0]
                    
                    # Extract time defines to get dates
                    time_defines = time_series["timeDefines"]
                    
                    forecast_controls = []
                    
                    for i, area_weather in enumerate(time_series["areas"]):
                        area_name_sub = area_weather["area"]["name"]
                        weathers = area_weather["weathers"]
                        
                        # Create a row of forecasts for this sub-area
                        day_forecasts = []
                        
                        # Loop through available weathers (up to 2 days: Today, Tomorrow)
                        for j, weather in enumerate(weathers):
                            if j >= 2: break # Limit to 2 days
                            
                            # Format date for this specific forecast
                            date_label = ""
                            if j < len(time_defines):
                                dt = datetime.datetime.fromisoformat(time_defines[j])
                                date_label = dt.strftime("%m月%d日")

                            day_forecasts.append(
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(f"{date_label}", size=12, color="grey"),
                                        ft.Text(f"{weather}")
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
                                    ft.Text(f"{area_name_sub}", weight="bold"),
                                    ft.Row(day_forecasts, wrap=True)
                                ]),
                                margin=ft.margin.only(bottom=10)
                            )
                        )
                    
                    tile.controls = forecast_controls
                    tile.data["fetched"] = True
                    
                except (IndexError, KeyError) as err:
                    tile.controls = [ft.Text(f"Error parsing data: {err}", color="red")]
                    
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
        )
    )

    load_area_data()

ft.app(target=main)
