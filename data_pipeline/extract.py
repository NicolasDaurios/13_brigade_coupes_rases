import os
import gzip
import json
import boto3
import shutil
import requests
from tqdm import tqdm
from datetime import datetime


# # # # # # # # # # # #
# Update de la metadata
# # # # # # # # # # # #
def update_metadata(meta_data, bucket_name, s3_key, incr_version=0.0):
    meta_data = {
        "version": 1.0 + incr_version,
        "s3_key": s3_key,
        "bucket_name": bucket_name,
        "data_source_link": meta_data['links']['self'],
        "date_source": meta_data['updated'],
        "file_name": meta_data['key'],
        "date_extract": datetime.now().strftime("%Y-%m-%d"),
        "size": meta_data['size'],
        "mimetype": meta_data['mimetype'],
        "metadata": {
            "width": meta_data['metadata']['width'],
            "height": meta_data['metadata']['height']
        }
    }
    
    return meta_data

# # # # # # # # # # # # # # # # # # #
# Vérification des données meta data 
# # # # # # # # # # # # # # # # # # # 
def data_update(query: str, bucket_name: str, s3_key_metadata: str, s3_key: str):
    url = f"https://zenodo.org/api/records/13685177/files/{query}"
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        data = response.json()
    else:
        raise Exception(f"Erreur lors de la requête API : {response.status_code}")

    s3 = boto3.client("s3")
    metadata_object = s3.get_object(Bucket=bucket_name, Key=s3_key_metadata)
    metadata_content = metadata_object["Body"].read().decode("utf-8")
    metadata = json.loads(metadata_content)

    date_format = "%Y-%m-%dT%H:%M:%S"
    base_date = datetime.strptime(metadata["date_source"].split(".")[0], date_format)
    date_extracted = datetime.strptime(data["updated"].split(".")[0], date_format)

    do_update = base_date < date_extracted
    if do_update:
        metadata = update_metadata(data, bucket_name, s3_key, 0.1)

    print(f"✅ Inspection de la metadata effectuée, mise à jour requise : {do_update}")

    return (metadata, do_update) if not do_update else (metadata, True)

# # # # # # # # # # # # #
# Upload du tif sur S3 
# # # # # # # # # # # # #
def extract_tif_data_and_upload(url: str, s3_key: str, s3:str):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        s3.upload_fileobj(r.raw, "brc-poc-etl", s3_key)

    print(f"✅ Fichier uploadé avec succès sur S3: {s3_key}")

# # # # # # # # # # # # # # # # # #
# Présence du fichier dans le S3
# # # # # # # # # # # # # # # # # # 
def check_tif_in_s3(bucket_name, s3_key_prefix):
    s3 = boto3.client('s3')
    result = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_key_prefix)

    if "Contents" in result:
        for obj in result["Contents"]:
            filename = obj["Key"].split("/")[-1]  
            
            # Vérifier si le fichier sans date est dans S3
            if filename == "mosaics_tropisco_warnings_france_date.tif":
                return True

    return False

# # # # # # # # # # # # # # # # # #
# Récupération des données cadastres
# # # # # # # # # # # # # # # # # # 
def download_file(url, filename):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024  # 1 KB
    progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)

    with open(filename, "wb") as f:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            f.write(data)

    progress_bar.close()
    print(f"📥 Téléchargement terminé : {filename}")

# ✅ Décompression du fichier .gz
def decompress_gz(input_file, output_file):
    with gzip.open(input_file, "rb") as f_in:
        with open(output_file, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    print(f"📂 Décompression terminée : {output_file}")