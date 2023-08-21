import requests
import json
import pandas as pd
import math
from time import time, strftime, gmtime
from datetime import date
from pandas import json_normalize
import os
import yaml
from pathlib import Path
from prefect import flow, task


def api_request(url: str) -> json:
    """Generic function to send API requests"""

    api_response = requests.get(url).json()

    return api_response

@task(name="Query API Featureset")
def query_api_featureset(year: int) -> json:
    """Gather information about API Featureset, will use the maxRecordCount value"""

    url_base = f"https://services.arcgis.com/afSMGVsC7QlRK1kZ/arcgis/rest/services/Public_311_{year}/FeatureServer/0"
    url_respformat = "f=pjson"

    api_response = api_request(url_base + "?" + url_respformat)

    return api_response

@task(name="Query API Recordcount")
def query_api_recordcnt(year: int, last_edit_date: str) -> int:
    """Gather record count of records meeting the criteria in the API Recordset"""

    qry_date = strftime('%Y-%m-%d %H:%M:%S', gmtime(last_edit_date / 1000))

    url_base = f"https://services.arcgis.com/afSMGVsC7QlRK1kZ/arcgis/rest/services/Public_311_{year}/FeatureServer/0"
    url_respformat = "f=pjson"
    url_params = f"/query?where=openeddatetime > DATE '{qry_date}' OR lastupdatedate > DATE '{qry_date}'&outFields=*&outSR=4326&returnCountOnly=true&"

    api_response = api_request(url_base + url_params + url_respformat)

    return api_response

@task(name="Query API records")
def query_api_records(year: int, batch_size: int, record_cnt: int, last_edit_date: str) -> pd.DataFrame:
    """Query the API records"""
    
    qry_date = strftime('%Y-%m-%d %H:%M:%S', gmtime(last_edit_date / 1000))

    # where openeddatetime > DATE '{qry_date}' OR lastupdatedate > DATE '{qry_date}'
    
    offset = 0
    df_all = pd.DataFrame()

    while offset < record_cnt:
        url_base = f"https://services.arcgis.com/afSMGVsC7QlRK1kZ/arcgis/rest/services/Public_311_{year}/FeatureServer/0"
        url_params = f"/query?where=openeddatetime > DATE '{qry_date}' OR lastupdatedate > DATE '{qry_date}'&outFields=*&outSR=4326&resultOffset={offset}&"
        url_respformat = "f=pjson"

        print(url_base + url_params + url_respformat)

        api_response = api_request(url_base + url_params + url_respformat)
        df_curr = pd.json_normalize(api_response, record_path='features')
        df_all = pd.concat([df_all, df_curr])
        
        offset = offset + batch_size

    return df_all


@task(name="Format DataFrame", log_prints=True)
def format_df(df: pd.DataFrame) -> pd.DataFrame:
    """Format DataFrame"""

    with open('flows/load_schema.yaml', 'rb') as f:
        load_schema = yaml.safe_load(f)
        
    field_names = load_schema['field_names']
    data_types = load_schema['data_types']

    df.rename(columns=field_names, inplace=True)
    df = df.astype(data_types)

    print(f"rows: {len(df)}")

    return df

@task(name="Save data to Parquet file")
def write_to_pq(df: pd.DataFrame, year: str) -> Path:
    """Write DataFrame out locally as a parquet file"""

    today = date.today()

    curr_date = today.strftime("%Y%m%d")

    pq_path = Path(f"data/pq/{curr_date}/mpls_311data_{year}_{curr_date}.parquet")
    os.makedirs(os.path.dirname(pq_path), exist_ok=True)
    
    df.to_parquet(pq_path, compression="gzip", index=False)

    return pq_path

if __name__ == '__main__':

    year = "2019"
    
    process_data(year)
