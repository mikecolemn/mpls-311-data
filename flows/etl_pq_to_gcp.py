from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp.bigquery import BigQueryWarehouse, bigquery_load_cloud_storage
from prefect_dbt.cli.commands import DbtCliProfile, DbtCoreOperation
from etl_api_to_pq import *

def get_bucket(block: str):
    gcs_block = GcsBucket.load(block)
    
    return gcs_block


@task(name="Check-Prior-load")
def gcp_prior_load(year: int, bq_block) -> int:
    """Retrieves information about prior load, to limit next processing to only new or updated records"""

    last_edit_stmt = f"SELECT COALESCE(MAX(data_last_edit_date),0) as last_date FROM mpls_311_staging.track_load WHERE year = {year}"

    with BigQueryWarehouse.load(bq_block) as warehouse:
        operation = last_edit_stmt
        result = warehouse.fetch_one(operation)

        last_edit_date = result[0]

    return last_edit_date

@task(name="Truncate_Staging_Table")
def gcp_truncate_stage(bq_block) -> None:
    """Truncates Staging table of previously processed data"""

    truncate_stmt = "TRUNCATE TABLE mpls_311_staging.raw_mpls_311data"

    with BigQueryWarehouse.load(bq_block) as warehouse:
        operation = truncate_stmt
        warehouse.execute(operation)

    return 


@task(name="Upload parquet file")
def pq_to_gcs(path: Path, gcs_block: GcsBucket) -> None:
    """Upload local parquet file to GCS"""

    gcs_block.upload_from_path(from_path=f"{path}",to_path=path)
    return


@flow(name="Stage GCS to BQ")
def stage_bq(bucket, year):
    """Stage data in BigQuery"""

    #gcp_credentials = GcpCredentials(project="mpls-311")
    gcp_credentials = GcpCredentials.load("gcp-mpls311")

    job_config = {'write_disposition': 'WRITE_APPEND',
                  'source_format': 'PARQUET'}

    result = bigquery_load_cloud_storage(
                    dataset = "mpls_311_staging",
                    table = "raw_mpls_311data",
                    uri = f"gs://{bucket}/data/pq/mpls_311data_{year}.parquet",
                    gcp_credentials = gcp_credentials,
                    job_config=job_config,
                    location=''
                )

    return result

@task(name="dbt modelling")
def dbt_model():
    """Run dbt models"""

    dbt_cli_profile = DbtCliProfile.load("dbt-cli-profile-dev")

    dbt_path = Path(f"dbt/mpls_311_incremental")

    dbt_run = DbtCoreOperation(
                commands=["dbt deps", 
                            "dbt seed", 
                            "dbt build"],
                project_dir=dbt_path,
                dbt_cli_profile=dbt_cli_profile,
                overwrite_profiles=True
    )

    dbt_run.run()

    return

@task(name="Track-Load")
def track_load_gcs(track: dict, bq_block):
    """Stores a record, tracking information about the dataset loaded"""

    track["job_end"] = time()
    track["job_runtime"] = track["job_end"] - track["job_start"]

    # df_track = pd.DataFrame([track])
    

    track_stmt = f"""INSERT INTO mpls_311_staging.track_load
            (job_start, job_end, job_runtime, year, max_record_cnt, record_cnt, data_last_edit_date, pq_path, parameter)
            VALUES({track['job_start']},
                    {track['job_end']},
                    {track['job_runtime']},
                    {track['year']},
                    {track['max_record_cnt']},
                    {track['record_cnt']},
                    {track['data_last_edit_date']},
                    '{track['pq_path']}',
                    '{track['parameter']}')"""

    print(track_stmt)

    with BigQueryWarehouse.load(bq_block) as warehouse:
        operation = track_stmt
        warehouse.execute(operation)


if __name__ == '__main__':

    years = [2023]
    # years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
    
    parent_process_data(years)