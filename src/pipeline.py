import pandas as pd
import geopandas as gpd

# -------------------------
# 1. LOAD DATA
# -------------------------

crime_df = pd.read_csv("Crimes_-_2025_20260416.csv")

crime = gpd.GeoDataFrame(
    crime_df,
    #turns coordinates into geometry (CSV file so no geometry)
    geometry=gpd.points_from_xy(crime_df.Longitude, crime_df.Latitude),
    #convert to 4326 bc its longitutde and latitude
    crs="EPSG:4326"
)

stations = gpd.read_file("CTA_-_'L'_(Rail)_Stations_20260416.geojson")


# -------------------------
# 2. CONVERT TO METERS
# -------------------------

crime = crime.to_crs(epsg=3857)
stations = stations.to_crs(epsg=3857)


# -------------------------
# 3. CREATE BUFFERS
# -------------------------

stations["buff250m"] = stations.geometry.buffer(250)
stations["buff500m"] = stations.geometry.buffer(500)


# -------------------------
# 4. SPATIAL JOINS
# -------------------------

#Creates new data set where the geometry is the buffer around the station
# station_name for labeling map 
#station_id for joins
buff250 = gpd.GeoDataFrame(
    stations[["station_id", "station_name"]],
    geometry=stations["buff250m"],
    crs=stations.crs
)

buff500 = gpd.GeoDataFrame(
    stations[["station_id"]],
    geometry=stations["buff500m"],
    crs=stations.crs
)
#Finds all crime within the buffers
join250 = gpd.sjoin(crime, buff250, predicate="within")
join500 = gpd.sjoin(crime, buff500, predicate="within")


# -------------------------
# 5. COUNT CRIMES PER STATION
# -------------------------

#grouby groups all crimes near station
#size() counts them
#reset_index turns it back into a normal table
count250 = join250.groupby("station_id").size().reset_index(name="crime_250")
count500 = join500.groupby("station_id").size().reset_index(name="crime_500")

#attatch counts back to stations
stations = stations.merge(count250, on="station_id", how="left")
stations = stations.merge(count500, on="station_id", how="left")

#fills in missing values with 0 

stations[["crime_250", "crime_500"]] = stations[["crime_250", "crime_500"]].fillna(0)


# -------------------------
# 6. NORMALIZE AREA (km²)
# -------------------------

#calculates radius of circle
stations["area_250_km2"] = 3.1416 * (0.25 ** 2)
stations["area_500_km2"] = 3.1416 * (0.5 ** 2)

#converts counts to densitiy
stations["density_250"] = stations["crime_250"] / stations["area_250_km2"]
stations["density_500"] = stations["crime_500"] / stations["area_500_km2"]


# -------------------------
# 7. EXPOSURE SCORE
# -------------------------
#weighing how important exporsure is 
#close (250m crime is 70%)  is more important
#far (500m crime is 30%) because its less important
stations["exposure_score"] = (
    stations["density_250"] * 0.7 +
    stations["density_500"] * 0.3
)


# -------------------------
# 8. CLASSIFICATION
# -------------------------
#.apply means run classify on stations exposure scores
#store it in exposure class 

def classify(x):
    if x < 10:
        return "Low"
    elif x < 50:
        return "Medium"
    elif x < 100:
        return "High"
    else:
        return "Very High"


stations["exposure_class"] = stations["exposure_score"].apply(classify)


# -------------------------
# 9. SORT + PREVIEW
# -------------------------
#sorts for highest scores to come first
stations = stations.sort_values("exposure_score", ascending=False)

print(stations[[
    "station_id",
    "exposure_score",
    "exposure_class"

    #prints top 10 worst scores 
]].head(10))


# -------------------------
# CLEAN POINT EXPORT
# -------------------------
#removes buffer columns because they are not needed/allowed for the final export layer
#the copy is so we dont mess up OG data
stations_points = stations.drop(columns=["buff250m", "buff500m"]).copy()

#use station points as geometry 
stations_points = stations_points.set_geometry("geometry")

#export to GIS file
stations_points.to_file(
    "outputs/stations_points.gpkg",
    driver="GPKG"
)


# -------------------------
# 250m BUFFER EXPORT
# -------------------------
#only selecting important columns 
buf250 = stations[["station_id", "crime_250", "density_250", "exposure_score", "exposure_class"]].copy()

#attatch 250m buffers as map shape
buf250 = gpd.GeoDataFrame(
    buf250,
    geometry=stations["buff250m"],
    crs=stations.crs
)

#exporting to GIS file
buf250.to_file("outputs/buffers_250m.gpkg", driver="GPKG")


# -------------------------
# 500m BUFFER EXPORT
# -------------------------

buf500 = stations[["station_id", "crime_500", "density_500", "exposure_score", "exposure_class"]].copy()

buf500 = gpd.GeoDataFrame(
    buf500,
    geometry=stations["buff500m"],
    crs=stations.crs
)

buf500.to_file("outputs/buffers_500m.gpkg", driver="GPKG")
