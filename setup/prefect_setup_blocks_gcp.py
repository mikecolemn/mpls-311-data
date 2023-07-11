from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp.bigquery import BigQueryWarehouse
from prefect_dbt.cli import BigQueryTargetConfigs, DbtCliProfile
import os
import json
from dotenv import load_dotenv

# pulls in information from environment variables and service account file
load_dotenv()

gcp_account_file = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

with open(os.environ['GOOGLE_APPLICATION_CREDENTIALS'], 'r') as creds:
    json_creds = json.load(creds)
    gcp_project_name = json_creds['project_id']

# Creates block for GCP credentials
credentials_block = GcpCredentials(
    service_account_info=json_creds  # point to your credentials .json file
)
credentials_block.save("gcp-mpls311", overwrite=True)

# Creates block for GCS bucket
bucket_block = GcsBucket(
    gcp_credentials=GcpCredentials.load("gcp-mpls311"),
    bucket=f"data_lake_{gcp_project_name}",  # insert your GCS bucket name
)

bucket_block.save("gcs-mpls311", overwrite=True)

# Creates block for Bigquery
bq_block = BigQueryWarehouse(
    gcp_credentials=GcpCredentials.load("gcp-mpls311"),
    fetch_size = 1
)

bq_block.save("bq-mpls311", overwrite=True)


# Creates block for gcp target for dbt models
credentials = GcpCredentials.load("gcp-mpls311")
target_configs = BigQueryTargetConfigs(
    schema="mpls_311_production",  # GCP dataset
    credentials=credentials,
)
target_configs.save("dbt-gcp-target-config", overwrite=True)

# Creates block for dbt profile
dbt_cli_profile = DbtCliProfile(
    name="mpls_311",
    target="prod",
    target_configs=target_configs,
)
dbt_cli_profile.save("dbt-cli-profile-dev", overwrite=True)