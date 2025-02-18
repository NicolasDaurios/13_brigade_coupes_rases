import os
import boto3
import requests
from datetime import datetime


# # # # # # # # # # # # # # # # # # #
# Vérification des données meta data 
# # # # # # # # # # # # # # # # # # # 
def data_update(query: str):
    # Récup api
    url = f"https://zenodo.org/api/records/13685177/files/{query}"
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        data = dict(response.json())
    else:
        raise Exception(f"Erreur lors de la requête : {response.status_code}")
    
    # Parser les données dates
    date_format = "%Y-%m-%dT%H:%M:%S"
    base_date = datetime.strptime("2024-09-13T08:08:10.342532+00:00".split(".")[0], date_format)
    date_extracted = datetime.strptime(data["updated"].split(".")[0], date_format)
    do_update = base_date < date_extracted

    print(f"✅ Inspection de la metadata fait, réponse à mise à jour requise : {do_update}")
    return do_update

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
            filename_without_date = filename.split('-')[0] + ".tif"  
            
            # Vérifier si le fichier sans date est dans S3
            if filename_without_date == "mosaics_tropisco_warnings_france_date.tif":
                return True

    return False
