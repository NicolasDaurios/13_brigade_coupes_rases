import io
import os
import boto3 
import shutil
import rasterio
import numpy as np
import pandas as pd
from tqdm import tqdm
import geopandas as gpd
from pathlib import Path
from dotenv import load_dotenv
from osgeo import gdal, ogr, osr
from datetime import datetime


def load_from_S3(bucket_name, s3_key, download_path):
    if "temp_tif" not in os.listdir():
        os.makedirs("temp_tif", exist_ok=True)

    # Téléchargement du fichier depuis S3
    s3 = boto3.client('s3')
    try:
        with open(download_path, 'wb') as f:
            s3.download_fileobj(bucket_name, s3_key, f)
        print(f'✅ Fichier téléchargé depuis S3 {download_path}')
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement du fichier depuis S3: {e}")


# REPRISE D'UNE FONCTION EXISTANTE
def regroup_sufosat_days(
    input_tif_filepath: str | Path,
    output_tif_filepath: str | Path,
    start_day: pd.Timestamp,
    end_day: pd.Timestamp,
) -> None:
    sufosat_start_day = pd.Timestamp(year=2014, month=4, day=3)
    start_days = (start_day - sufosat_start_day).days
    end_days = (end_day - sufosat_start_day).days

    # Open the input TIFF file
    with rasterio.open(input_tif_filepath) as src:
        # Copy metadata
        profile = src.profile
        profile.update(dtype=rasterio.uint8)

        # Open the output TIFF file
        with rasterio.open(output_tif_filepath, "w", **profile) as dst:
            # Read the data as a generator (window-by-window) to avoid out Of memory issues
            # since the total grid contains billions of points
            for _, window in tqdm(
                src.block_windows(),
                total=src.width
                * src.height
                // (src.block_shapes[0][0] * src.block_shapes[0][1]),
            ):
                # Read the block data for the first and only band
                data = src.read(1, window=window)

                # Apply the date filter to create binary image (0 or 1)
                binary_data = ((data >= start_days) & (data <= end_days)).astype(np.uint8)

                # Write processed block to new file
                dst.write(binary_data, 1, window=window)
                
    print("✅ Fichier tif regroupé")


def extract_raster_as_geodataframe(raster_path, vector_path):    
    os.makedirs(os.path.dirname(vector_path), exist_ok=True)

    # Ouvrir le raster
    raster_ds = gdal.Open(raster_path)
    if raster_ds is None:
        raise ValueError(f"Échec de l'ouverture du raster : {raster_path}")
    else:
        print("✅ Raster ouvert avec Gdal")

    srs = osr.SpatialReference()
    srs.ImportFromWkt(raster_ds.GetProjectionRef())

    driver = ogr.GetDriverByName("ESRI Shapefile")
    if driver is None:
        raise RuntimeError("Pilote Shapefile non disponible.")
    if os.path.exists(vector_path):
        driver.DeleteDataSource(vector_path)
    vector_ds = driver.CreateDataSource(vector_path)
    if vector_ds is None:
        raise RuntimeError(f"Échec de la création du Shapefile : {vector_path}")
    layer = vector_ds.CreateLayer("polygons", srs=srs, geom_type=ogr.wkbPolygon)
    if layer is None:
        raise RuntimeError("Échec de la création de la couche.")

    field_dn = ogr.FieldDefn("DN", ogr.OFTInteger)
    layer.CreateField(field_dn)

    band = raster_ds.GetRasterBand(1)
    mask_band = band

    # Appliquer la fonction Polygonize avec la bonne configuration
    result = gdal.Polygonize(band, mask_band, layer, 0, ["8CONNECTED=YES"])
    if result != 0:
        raise RuntimeError("Échec de la polygonisation.")

    # Nettoyer et fermer les fichiers
    layer = None
    vector_ds = None
    raster_ds = None
    
    # Afficher les logs en print 
    print("✅ Fichier shapefile créé")
    print("✅ Couche SRS créée")
    print("✅ Polygonisation du raster réussie")


def transform_raster(sufosat_2024):
    gdata = sufosat_2024.drop(columns="DN")
    # Opération géographiques sur le geodataframe sans jointure geo 
    gdata["area_ha"] = gdata.to_crs(epsg=3395).geometry.area / 10000
    print("✅ Calcul de la surface en hectares")
    gdata["coordonnees"] = gdata.to_crs(epsg=3395).geometry.centroid
    print("✅ Calcul des coordonnées")

    return gdata


def convert_geometries_to_wkt(sufosat_2024):
    for col in sufosat_2024.columns:
            if col != "geometry" and sufosat_2024[col].dtype.name == "geometry":
                sufosat_2024[col] = sufosat_2024[col].apply(lambda geom: geom.wkt if geom else None)
    print("✅ Conversion des géométries en WKT")

    geojson_str = sufosat_2024.to_json()
    geojson_bytes = io.BytesIO(geojson_str.encode("utf-8"))
    print("✅ Conversion bytes GEOJSON")

    shutil.rmtree("temp_tif")
    shutil.rmtree("temp_shape")
    
    return geojson_bytes


def upload_geodataframe_to_s3(geojson_bytes, bucket_name, s3):
    current_date = datetime.now().strftime("%Y-%m-%d")
    s3.upload_fileobj(
        geojson_bytes, 
        bucket_name, 
        f"to_api/clear_cut_processed_{current_date}.geojson"
    )
    print("✅ Fichier GeoJSON upload sur S3")
