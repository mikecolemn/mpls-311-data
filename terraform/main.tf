terraform {
  required_version = ">= 1.0"
  backend "local" {}  # Can change from "local" to "gcs" (for google) or "s3" (for aws), if you would like to preserve your tf-state online
  required_providers {
    google = {
      source  = "hashicorp/google"
    }
  }
}

provider "google" {
  project = var.project
  region = var.region
  # credentials = file(var.credentials)  # Use this if you do not want to set env-var GOOGLE_APPLICATION_CREDENTIALS
}

# Data Lake Bucket
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
resource "google_storage_bucket" "data-lake-bucket" {
  name          = "${local.data_lake_bucket}_${var.project}" # Concatenating DL bucket & Project name for unique naming
  location      = var.region

  # Optional, but recommended settings:
  storage_class = var.storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled     = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30  // days
    }
  }

  force_destroy = true
}

# DWH
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
resource "google_bigquery_dataset" "dataset" {
  count = 3
  dataset_id = var.BQ_DATASET[count.index]
  project    = var.project
  location   = var.region
  delete_contents_on_destroy = true
}

resource "google_bigquery_table" "track_load" {

  dataset_id = "mpls_311_staging"
  table_id = "track_load"
  deletion_protection = false

  schema = <<EOF
[
  {
    "name": "job_start",
    "type": "NUMERIC",
    "mode": "NULLABLE",
    "description": "Epoch time of when the job run started"
  },
  {
    "name": "job_end",
    "type": "NUMERIC",
    "mode": "NULLABLE",
    "description": "Epoch time of when the job run ended"
  },
  {
    "name": "job_runtime",
    "type": "NUMERIC",
    "mode": "NULLABLE",
    "description": "Runtime of this job run"
  },
  {
    "name": "year",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Year of data for the job run"
  },
  {
    "name": "max_record_cnt",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Max record count this years feature set can return"
  },
  {
    "name": "record_cnt",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Count of record in this years featureset that meets the criteria"
  },
  {
    "name": "data_last_edit_date",
    "type": "NUMERIC",
    "mode": "NULLABLE",
    "description": "Data last edit date for this year recordset"
  },
  {
    "name": "pq_path",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Path of Parquet file loaded"
  }

]
EOF

  depends_on = [
    google_bigquery_dataset.dataset
  ]

}

resource "google_bigquery_table" "stg_mpls_311data" {

  dataset_id = "mpls_311_staging"
  table_id = "raw_mpls_311data"
  deletion_protection = false

  time_partitioning {
    field = "open_datetime"
    type = "YEAR"
  }

  schema = <<EOF
[
  {
    "name": "case_id",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Unique identifying number associated with each case"
  },
  {
    "name": "object_id",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Unique identifying number within the original source data set"
  },
  {
    "name": "subject_name",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "This is the top level hierarchy definition of a service request. It is most closely associated with a department designation"
  },
  {
    "name": "reason_name",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "This is the 2nd level classification of a service request and reflects a program name or a division assigned to perform the service request"
  },
  {
    "name": "type_name",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "This is the 3rd level classification describing what the service request specifically is for. It is the most common designation description used in the city"
  },
  {
    "name": "title",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Similar to the Type column, this describes more details about the incident"
  },
  {
    "name": "open_datetime",
    "type": "TIMESTAMP",
    "mode": "NULLABLE",
    "description": "This is the date and time stamp when the department, program, or division assigned to complete the task in a service request starts working that service request"
  },
  {
    "name": "case_status",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "If case status = 0, it means the case is closed. If case status = 1, the case is still considered open. All cases with a case status of 1 should not have a closed date"
  },
  {
    "name": "closed_datetime",
    "type": "timestamp",
    "mode": "NULLABLE",
    "description": "The date a resolving department, division or program completed the service request"
  },
  {
    "name": "coord_x",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "This is the coordinate the city provides of where the service request occurred in the WGS 84 web Mercator auxilliary sphere coordinate system"
  },
  {
    "name": "coord_y",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "This is the coordinate the city provides of where the service request occurred in the WGS 84 web Mercator auxilliary sphere coordinate system"
  },
  {
    "name": "last_update_datetime",
    "type": "timestamp",
    "mode": "NULLABLE",
    "description": "The last time this Service request has been updated"
  },
  {
    "name": "geometry_x",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "Additional geometry data point related to the Service Request"
  },
  {
    "name": "geometry_y",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "Additional geometry data point related to the Service Request"
  }

]
EOF

  depends_on = [
    google_bigquery_dataset.dataset
  ]

}