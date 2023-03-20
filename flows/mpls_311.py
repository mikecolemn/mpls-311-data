import requests
import json
import pandas as pd
import math
from pandas.io.json import json_normalize
import os
from pathlib import Path
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp.bigquery import GcpCredentials, BigQueryWarehouse
from prefect_dbt.cli.commands import DbtCoreOperation


@task(name="Get API data", retries=3, log_prints=True)
def get_data_api(year: str) -> pd.DataFrame:
    """API call to Mpls 311 dataset, create DataFrame"""

    print(f"Year: {year}")

    url_base = f"https://services.arcgis.com/afSMGVsC7QlRK1kZ/arcgis/rest/services/Public_311_{year}/FeatureServer/0/query?"
    url_params = "where=1%3D1&outFields=*&outSR=4326&returnIdsOnly=true&f=json"

    objids_response = requests.get(url_base + url_params).json()
    objids = objids_response["objectIds"]

    df_all = pd.DataFrame()

    start_objid = min(objids)
    end_objid = 0
    max_objid = max(objids)
    batch_size = 1000

    while start_objid < max_objid:
        
        end_objid = start_objid + batch_size

        url_params = f"where=objectID >= {start_objid} AND objectID < {end_objid}&outFields=*&outSR=4326&f=json"
        features_response = requests.get(url_base + url_params).json()
        df_curr = pd.json_normalize(features_response, record_path='features')
        df_all = pd.concat([df_all, df_curr])

        start_objid = end_objid

    return df_all

@task(name="Format DataFrame", log_prints=True)
def format_df(df: pd.DataFrame) -> pd.DataFrame:
    """Format DataFrame"""

    df.rename(columns={'attributes.CASEID': 'case_id',
                        'attributes.OBJECTID': 'object_id',
                        'attributes.SUBJECTNAME': 'subject_name',
                        'attributes.REASONNAME': 'reason_name',
                        'attributes.TYPENAME': 'type_name',
                        'attributes.TITLE': 'title',
                        'attributes.OPENEDDATETIME': 'open_datetime',
                        'attributes.CASESTATUS': 'case_status',
                        'attributes.CLOSEDDATETIME': 'closed_datetime',
                        'attributes.XCOORD': 'coord_x',
                        'attributes.YCOORD': 'coord_y',
                        'attributes.LastUpdateDate': 'last_update_datetime',
                        'geometry.x': 'geometry_x',
                        'geometry.y': 'geometry_y' 
                        }, inplace=True)

    df = df.astype({
                'case_id': 'Int64',
                'object_id': 'Int64',
                'subject_name': 'str',
                'reason_name': 'str',
                'type_name': 'str',
                'title': 'str',
                'open_datetime': 'datetime64[ms]',
                'case_status': 'Int64',
                'closed_datetime': 'datetime64[ms]',
                'coord_x': 'float64',
                'coord_y': 'float64',
                'last_update_datetime': 'datetime64[ms]',
                'geometry_x': 'float64',
                'geometry_y': 'float64'
                })

    print(f"rows: {len(df)}")

    return df

@task(name="Save data to Parquet file")
def write_to_pq(df: pd.DataFrame, year: str) -> Path:
    """Write DataFrame out locally as a parquet file"""

    pq_path = Path(f"data/pq/mpls_311data_{year}.parquet")
    os.makedirs(os.path.dirname(pq_path), exist_ok=True)
    
    df.to_parquet(pq_path, compression="gzip", index=False)

    return pq_path

@task(name="Upload parquet file")
def pq_to_gcs(path: Path) -> None:
    """Upload local parquet file to GCS"""

    gcs_block = GcsBucket.load("mpls311-gcs")
    gcs_block.upload_from_path(from_path=f"{path}",to_path=path)
    return

@task(name="Stage GCS to BQ")
def stage_bq():
    """Stage data in BigQuery"""

    # gcp_credentials_block = GcpCredentials.load("mpls311-gcp-creds")

    with BigQueryWarehouse.load("mpls311-bq") as warehouse:
        operation = """
            CREATE OR REPLACE EXTERNAL TABLE `mpls-311.mpls_311_staging.external_mpls_311data`
            OPTIONS (
                format = 'PARQUET',
                uris = ['gs://data_lake_mpls-311/data/pq/mpls_311data_*.parquet']
            )
        """
        warehouse.execute(operation)

    with BigQueryWarehouse.load("mpls311-bq") as warehouse:
        operation = """
            CREATE OR REPLACE TABLE `mpls-311.mpls_311_staging.mpls_311data_partitioned`
            PARTITION BY
                DATE_TRUNC(open_datetime,YEAR) AS
            SELECT * FROM `mpls-311.mpls_311_staging.external_mpls_311data`
        """
        warehouse.execute(operation)

@task(name="dbt modelling")
def dbt_model():
    """Run dbt models"""

    dbt_path = Path(f"dbt/mpls_311")

    dbt_run = DbtCoreOperation(
                    commands=["dbt deps", "dbt seed", "dbt run -t prod"],
                    project_dir=dbt_path,
                    profiles_dir=dbt_path,
    )

    dbt_run.run()

    return

@flow(name="Process-Data-Subflow")
def process_data(year: int):
    """Main function to process a year of Mpls 311 data"""

    data = get_data_api(year)
    df = format_df(data)
    pq_path = write_to_pq(df, year)
    pq_to_gcs(pq_path)

@flow(name="Process-Data-Parent")
def parent_process_data(years: list[int] = [2023]):
    """Parent process to loop through provided years Mpls 311 data"""

    for year in years:
        process_data(year)

    
if __name__ == '__main__':

    years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]

    parent_process_data(years)

    stage_bq()
    dbt_model()
