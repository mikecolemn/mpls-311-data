locals {
  data_lake_bucket = "data_lake"
}

variable "project" {
  description = "Your GCP Project ID"
}

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default = "us-central1"
  type = string
}

variable "storage_class" {
  description = "Storage class type for your bucket. Check official docs for more info."
  default = "STANDARD"
}

variable "BQ_DATASET" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  # type = string
  # default = "mpls_311_staging"
  type = list
  default = ["mpls_311_staging", "mpls_311_development", "mpls_311_production"]
}

variable "bq_staging" {
  description = "The BQ staging dataset, for the table schema creation"
  type = string
  default = "mpls_311_staging"
  
}