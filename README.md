# 🚇 Chicago CTA Crime Exposure Analysis


## 🗺️ Overview

This project analyzes **reported crime around Chicago Transit Authority (CTA) rail stations** using spatial data analysis.

Using Chicago crime records and CTA station locations, the project identifies crime incidents within **250m and 500m** of each station, calculates crime density, and combines the results into a weighted **Crime Exposure Score**.

---

### What the map shows

The final GIS outputs allow station-level crime exposure to be visualized geographically.

* 📍 **Station points** represent individual CTA rail stations.
* 🔵 **250m buffers** represent the immediate area surrounding each station.
* 🟣 **500m buffers** represent the broader surrounding area.
* 🎨 **Exposure classifications** show the calculated exposure category for each station.
* 📊 **Exposure scores** combine crime density from both buffer distances.
---

## 📍 How It Works

Chicago Crime Data
        │
        ▼
  Create GeoPoints
        │
        ▼
   CTA Stations
        │
        ▼
   Create Buffers
    ┌─────┴─────┐
    ▼           ▼
  250m        500m
    │           │
    └─────┬─────┘
          ▼
    Spatial Join
          │
          ▼
     Count Crime
          │
          ▼
    Crime Density
          │
          ▼
   Exposure Score
          │
          ▼
    GIS Visualization

---

## 📊 Exposure Score

Crime is measured at two distances from each station.

| Distance | Weight | Purpose                        |
| :------: | :----: | :----------------------------- |
| **250m** |   70%  | Immediate station surroundings |
| **500m** |   30%  | Broader surrounding area       |

```text
Exposure Score =
(250m Crime Density × 0.70)
+
(500m Crime Density × 0.30)
```

### Classification

|    Score   | Classification |
| :--------: | :------------- |
|  `0–9.99`  | 🟢 Low         |
| `10–49.99` | 🟡 Medium      |
| `50–99.99` | 🟠 High        |
|   `100+`   | 🔴 Very High   |

---

## 🔎 Methodology

### 01 · Load the Data

Two datasets are used:

**Chicago Crime Data**

```text
Crimes_-_2025_20260416.csv
```

**CTA Rail Stations**

```text
CTA_-_'L'_(Rail)_Stations_20260416.geojson
```

Crime latitude and longitude coordinates are converted into geographic point geometries using GeoPandas.

### 02 · Create Station Buffers

Two circular areas are generated around every CTA station:

```python
stations["buff250m"] = stations.geometry.buffer(250)
stations["buff500m"] = stations.geometry.buffer(500)
```

### 03 · Spatial Join

Crime points are matched to the station buffers.

```python
join250 = gpd.sjoin(
    crime,
    buff250,
    predicate="within"
)

join500 = gpd.sjoin(
    crime,
    buff500,
    predicate="within"
)
```

### 04 · Calculate Crime Density

```text
Crime Density = Crime Count ÷ Buffer Area
```

This produces crime density values for both the 250m and 500m areas.

### 05 · Calculate Exposure

```python
stations["exposure_score"] = (
    stations["density_250"] * 0.7 +
    stations["density_500"] * 0.3
)
```

Each station is then assigned an exposure classification.

---

## 🧰 Tech Stack

**Data Analysis**

* Python
* Pandas

**Geospatial Analysis**

* GeoPandas
* Spatial joins
* Buffer analysis
* Coordinate Reference Systems

**GIS**

* QGIS
* GeoPackage
* GeoJSON

---

## 📁 Project Structure

```text
📦 chicago-cta-crime-analysis
│
├── 📄 analysis.py
├── 📄 README.md
│
├── 📊 Crimes_-_2025_20260416.csv
├── 🗺️ CTA_-_'L'_(Rail)_Stations_20260416.geojson
│
├── 📂 images
│   └── 🖼️ results-preview.png
│
└── 📂 outputs
    ├── 📍 stations_points.gpkg
    ├── 🔵 buffers_250m.gpkg
    └── 🟣 buffers_500m.gpkg
```

---

## ⚠️ Limitations

The **Exposure Score is an analytical metric**, not a definitive measure of station safety.

The analysis depends on modeling choices including:

* 250m and 500m buffer sizes
* 70% / 30% weighting
* Classification thresholds
* Geographic coordinates of reported incidents

It does not currently account for:

* CTA ridership
* Time of day
* Crime severity
* Population density
* Pedestrian traffic
* Weekday vs. weekend differences

---

## 🔮 Future Improvements

* 🚉 Incorporate CTA station ridership
* ⏰ Analyze crime by time of day
* 📅 Compare weekday vs. weekend crime
* 🔎 Analyze individual crime categories
* 📈 Incorporate multiple years of data
* 🗺️ Build an interactive web map
* 📊 Create a crime exposure dashboard
* ⚖️ Test alternative weighting methods

---
