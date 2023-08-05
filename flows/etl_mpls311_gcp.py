from pathlib import Path
from time import time
from etl_api_to_pq import *
from etl_pq_to_gcp import *


@flow(name="Process-Data-Subflow")
def process_data(year: int, last_edit_date: int, gcs_block, bq_block) -> None:
    """Main function to process a year of Mpls 311 data"""

    track = {}
    track["job_start"] = time()

    feature_set = query_api_featureset(year)
    track["max_record_cnt"] = feature_set["maxRecordCount"]
    track["data_last_edit_date"] = feature_set["editingInfo"]["dataLastEditDate"]

    if track["data_last_edit_date"] > last_edit_date:
        print("Newer last edit date")

        record_set = query_api_recordcnt(year, last_edit_date)
        record_cnt = record_set["count"]
        track["record_cnt"] = record_set["count"]

        data = query_api_records(year, track["max_record_cnt"], record_cnt, last_edit_date)
        df = format_df(data)
        pq_path = write_to_pq(df, year)

        track["year"] = year
        track["data_last_edit_date"] = feature_set["editingInfo"]["dataLastEditDate"]
        track["pq_path"] = str(pq_path)
        track["parameter"] = ""

        pq_to_gcs(Path(track["pq_path"]), gcs_block)
        stage_bq(gcs_block.bucket, year)



        track_load_gcs(track, bq_block)        

    else:
        print("No newer data")

@flow(name="Process-Data-Parent")
def parent_process_data(years: list[int]):
    """Parent process to loop through provided years Mpls 311 data"""

    bq_block = "bq-mpls311"
    block_name = "gcs-mpls311"
    gcs_block = get_bucket(block_name)

    gcp_truncate_stage(bq_block)

    for year in years:

        last_edit_date = gcp_prior_load(year, bq_block)
        process_data(year, last_edit_date, gcs_block, bq_block)

    dbt_model()


if __name__ == '__main__':

    years = [2023]
    
    parent_process_data(years)
