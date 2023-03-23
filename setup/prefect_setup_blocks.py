from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp.bigquery import BigQueryWarehouse
import os
import json
from dotenv import load_dotenv

load_dotenv()

gcp_account_file = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

with open(os.environ['GOOGLE_APPLICATION_CREDENTIALS'], 'r') as creds:
    json_creds = json.load(creds)
    gcp_project_name = json_creds['project_id']


# alternative to creating GCP blocks in the UI
# copy your own service_account_info dictionary from the json file you downloaded from google
# IMPORTANT - do not store credentials in a publicly available repository!

credentials_block = GcpCredentials(
    service_account_file=f"{gcp_account_file}"  # point to your credentials .json file
)
credentials_block.save("mpls311-gcp-creds", overwrite=True)


bucket_block = GcsBucket(
    gcp_credentials=GcpCredentials.load("mpls311-gcp-creds"),
    bucket=f"data_lake_{gcp_project_name}",  # insert your GCS bucket name
)

bucket_block.save("mpls311-gcs", overwrite=True)

bq_block = BigQueryWarehouse(
    gcp_credentials=GcpCredentials.load("mpls311-gcp-creds"),
    fetch_size = 1
)

bq_block.save("mpls311-bq", overwrite=True)