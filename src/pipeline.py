import pandas as pd
import geopandas as gpd

crime_df = pd.read_csv("Crimes_-_2025_20260416.csv")

crime = gpd.GeoDataFrame(
    crime_df,
    geometry=gpd.points_from_xy(crime_df.Longitude, crime_df.Latitude),
    crs="EPSG:4326"
)

stations = gpd.read_file("CTA_-_'L'_(Rail)_Stations_20260416.geojson")

crime = crime.to_crs(epsg=3857)
stations = stations.to_crs(epsg=3857)

stations["buff250m"] = stations.geometry.buffer(250)
stations["buff500m"] = stations.geometry.buffer(500)

buff250m = gpd.GeoDataFrame(stations[["station_id"]], geometry=stations["buff250m"], crs=stations.crs)
buff500m = gpd.GeoDataFrame(stations[["station_id"]], geometry=stations["buff500m"], crs=stations.crs)

join250 = gpd.sjoin(crime, buff250m, predicate="within")
join500 = gpd.sjoin(crime, buff500m, predicate="within")

count250 = join250.groupby("station_id").size().reset_index(name="crime_250")
count500 = join500.groupby("station_id").size().reset_index(name="crime_500")

stations = stations.merge(count250, on="station_id", how="left")
stations = stations.merge(count500, on="station_id", how="left")

stations[["crime_250", "crime_500"]] = stations[["crime_250", "crime_500"]].fillna(0)

stations["area_250_km2"] = 3.1416 * (0.25 ** 2)
stations["area_500_km2"] = 3.1416 * (0.5 ** 2)

stations["density_250"] = stations["crime_250"] / stations["area_250_km2"]
stations["density_500"] = stations["crime_500"] / stations["area_500_km2"]

stations["exposure_score"] = (
    stations["density_250"] * 0.7 +
    stations["density_500"] * 0.3
)

def classify(x):
    if x < 10:
        return "Low"
    if x < 50:
        return "Medium"
    elif x < 100:
        return "High"
    else:
        return "Very High"
    


stations["exposure_class"] = stations["exposure_score"].apply(classify)

stations = stations.sort_values("exposure_score", ascending=False)
print(stations[["station_id", "exposure_score", "exposure_class"]].head(10))

# ---------------------------
# CLEAN EXPORT SECTION
# ---------------------------

stations["buff250m"] = stations.geometry.buffer(250)
stations["buff500m"] = stations.geometry.buffer(500)

buf250 = gpd.GeoDataFrame(
    stations[["station_id", "crime_250", "density_250", "exposure_score", "exposure_class"]].copy(),
    geometry=stations["buff250m"],
    crs=stations.crs
)

buf250.to_file("outputs/buffers_250m.gpkg", driver="GPKG")

buf500 = gpd.GeoDataFrame(
    stations[["station_id", "crime_500", "density_500", "exposure_score", "exposure_class"]].copy(),
    geometry=stations["buff500m"],
    crs=stations.crs
)

buf500.to_file("outputs/buffers_500m.gpkg", driver="GPKG")

stations_points = gpd.GeoDataFrame(
    stations.drop(columns=["buff250m", "buff500m"]).copy(),
    geometry=stations.geometry,
    crs=stations.crs
)

stations_points.to_file("outputs/stations_points.gpkg", driver="GPKG")
