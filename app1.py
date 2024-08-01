from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import folium
import requests
import pandas as pd

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Change this to your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/map", response_class=HTMLResponse)
def get_map():
    m = folium.Map((45.5236, -122.6750), tiles="cartodb positron")
    m = folium.Map([45.35, -121.6972], zoom_start=12)
    folium.Marker(
        location=[45.3288, -121.6625],
        tooltip="Click me!",
        popup="Mt. Hood Meadows",
        icon=folium.Icon(icon="cloud"),
    ).add_to(m)
    folium.Marker(
        location=[45.3311, -121.7113],
        tooltip="Click me!",
        popup="Timberline Lodge",
        icon=folium.Icon(color="green"),
    ).add_to(m)
    return m._repr_html_()

@app.get("/vector", response_class=HTMLResponse)
def get_vector():
    m = folium.Map(location=[-71.38, -73.9], zoom_start=11)
    trail_coordinates = [
        (-71.351871840295871, -73.655963711222626),
        (-71.374144382613707, -73.719861619751498),
        (-71.391042575973145, -73.784922248007007),
        (-71.400964450973134, -73.851042243124397),
        (-71.402411391077322, -74.050048183880477),
    ]
    folium.PolyLine(trail_coordinates, tooltip="Coast").add_to(m)
    return m._repr_html_()

@app.get("/group", response_class=HTMLResponse)
def get_group():
    m = folium.Map((0, 0), zoom_start=7)
    group_1 = folium.FeatureGroup("first group").add_to(m)
    folium.Marker((0, 0), icon=folium.Icon("red")).add_to(group_1)
    folium.Marker((1, 0), icon=folium.Icon("red")).add_to(group_1)
    group_2 = folium.FeatureGroup("second group").add_to(m)
    folium.Marker((0, 1), icon=folium.Icon("green")).add_to(group_2)
    folium.LayerControl().add_to(m)
    return m._repr_html_()

@app.get("/geojson", response_class=HTMLResponse)
def get_geojson():
    m = folium.Map(tiles="cartodbpositron")
    geojson_data = requests.get(
        "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/world_countries.json"
    ).json()
    folium.GeoJson(geojson_data, name="hello world").add_to(m)
    folium.LayerControl().add_to(m)
    return m._repr_html_()

@app.get("/choropleth", response_class=HTMLResponse)
def get_choropleth():
    state_geo = requests.get(
        "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_states.json"
    ).json()
    state_data = pd.read_csv(
        "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_unemployment_oct_2012.csv"
    )
    m = folium.Map(location=[48, -102], zoom_start=3)
    folium.Choropleth(
        geo_data=state_geo,
        name="choropleth",
        data=state_data,
        columns=["State", "Unemployment"],
        key_on="feature.id",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Unemployment Rate (%)",
    ).add_to(m)
    folium.LayerControl().add_to(m)
    return m._repr_html_()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
