### Table of contents
- [Project Purpose](#project-purpose)
- [Technologies](#technologies)
- [Data Pipeline](#data-pipeline)
- [Reproducing this project](#reproducing-this-project)
- [Results](#results)
- [Future Development](#future-development)


## Project purpose

![Mpls 311](images/311-promo.jpg)

This repository is the final project of the [DataTalksClub Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp).  I selected data from the city of Minneapolis's OpenData set, for their 311 Department, as the dataset to explore and build a project around.  I had a rough idea of what the 311 Department helped support, but not a full grasp of the all the different types of requests involved or the volume of them.

The 311 Department is the primary source of contact for the city of Minneapolis, for non-emergecy information and service requests.  Part of their responsibilities are to start service requests for other departments to resolve.

The final dashboard will help answer questions of:

1) What types of service requests does the city of Minneapolis support?
2) What is the breakdown of service requests categories?
3) What is the volume of requests throughout the year?  Does the volume vary among categories of requests?

## Updates 10/2023

After completing the Zoomcamp, I've continued to work on some of the future development ideas I've had.  I'm now using a more current version of Prefect, which is run within docker containers.  I've also implemented some tracking tables for the pipeline executions, along with a revamp of my pipeline to retrieve and load incremental data changes.  This required a pretty significant revamp to the python code, implementing an additional set of dbt incremental models, the Prefect setup/config, along with changes to the Terraform code.

## Technologies

This project utilizes the following technologies and tools:

* Google Cloud Platform 
    * Google Storage buckets as Data Lake
    * Google Bigquery datasets as Data Warehouse
    * Google Looker Studio reports for Data Visualization
    * Google Compute Engine, if you use a VM on Google's Cloud Platform
* Terraform as Infrastructure as Code, to deploy Buckets and Datasets on Google Cloud Platform, including some tables in our Staging dataset
* Python script acts as the data pipeline, from initial retrieveal of the data staging it in BigQuery, and to running the dbt models
* Prefect as the orchestration tool.  A local instance of the Prefect Orion server is used, to make it easy for peer reviews.
* Docker, for running Prefect in containers
* dbt for some data quality testing, data modelling and transformation, and promotion of data to Production BigQuery dataset.  A local instance of dbt core is used to make it easy for peer reviews.
* Parquet columnar data files
* Piperider during development to assist with reviewing dbt model changes

## Data Pipeline

![data pipeline](images/mpls_311data_diagram.png)

The data pipeline will do the following:

1) Loop through each year passed to the pipeline.

2) Query a load tracking table for the last edit date of data previously processed for that year.  

3) Query the Minneaplis 311 dataset via API for that year to get the last edit date, and the maximum number of records that this dataset can return at a time.  There are separate data sets for each year, and each only return a certain amount of records per API request.  Anywhere from 1,000 to 32,000 records for each request.

4) If the dataset's last data edit date is after our tracked last edit date, it will then query the dataset for a count of records where the open date or the update date are after our tracked last edit date.

5) Query the Minneapolis 311 datasets again, pulling the actual service request records, in batches based on the maxmimum number of records that dataset can return at a time.  

6) The API returns results in a nested .json format.  As each batch of records are returned, the appropriate values from the .json file that have the data fields are placed in a Pandas DataFrame, and then appended into a consolidated DataFrame.

7) Once all the records are returned for a year, the DataFrame has data types applied to each field and field names are updated to more meaningful names.

8) The Pandas DataFrame is saved as a Parquet file locally, and then uploaded to the Google Storage Bucket acting as a data lake, that the Terraform process created.

9) Once the data is in our Google Storage Bucket, then it is loaded into a raw staging table in our BigQuery Staging dataset.  This raw staging table is truncated at the beginning of every run of the pipeline.

    During the initial project development, with this data set being fairly small, I was thinking that not partitioning would be the way to go.  However, testing my dbt models with non-partitioned, partitioned, clustered, and finally partitioned and clustered showed that I was getting the fastest results when using tables that were both partitioned and clustered.  The process's performance was about 33% better than the other options.

    For this setup with incremental loads, this raw staging table is built by terraform and is partitioned on YEAR(open_datetime).  This is the most efficient, based on time and cost, for both the initial pipline and then incremental pipeline runs, when testing options of non-partitioned, partitioned, clustered, and partitioned and clustered.  

10) Once the data is loaded, then a tracking record is written to our tracking table, recording specific useful pieces of information.

11) Once all years are processed and all the data is staged into BigQuery, then the dbt models are run.  The dbt models involve the following:

  * A seed file that I manually prepared, that standardizes some of the values for the layers of categorization.  In the original data, there are categories that are similar, but slightly different based on the source of the service request.  For example, if you submit a service request through the Open311 app vs calling the 311 phone number, the categories are named slightly different but for a similar request.

  * The dbt models are run.  There's a staging model, and then some dimension models for dates, categories and geography information, there's a fact model, and then a reporting model with aggregated data that will support the dashboard I create.  The fact and geography dimension models are incremental models, all the others are views or tables that get fully re-built with each run.  The date dimension model is partioned on the year of the open_datetime.

  * Some dbt tests that I prepared are run with the models.  They are all set with a severity of warn, which will just warn you of any tests that fail.  You should expect to see a few warnings about non-unique values in case_id, some warnings about the open_datetime being after closed_datetime, and now a warning about a new category showing up in the data.


## Reproducing this project

Reproducing this project has been tested on an Ubuntu 20.04 LTS VM, in both Google Cloud and a Proxmox homelab.  This project will require a similar VM, a Google Cloud account, a project on Google Cloud, and a service account with appropriate permissions for the project.

1) If you need to set up a VM, an account, project, or service account on Google Cloud, see [Setup Readme](https://github.com/mikecolemn/mpls-311-data/blob/main/setup/setup_readme.md) for more detailed instructions.

2) On your VM, clone the repo, `git clone https://github.com/mikecolemn/mpls-311-data.git`, and then `cd` into the repo folder

3) If you need to install Google Cloud CLI, unzip, Docker (and Docker-Compose), Anaconda, and Terraform, you can run a bash script with this command, `bash ./setup/setup.sh`, which will perform the following actions:

    * Apply initial updates, and install unzip, docker, docker-compose
    * Install Google Cloud cli application
    * Setup Anaconda and Terraform.

    * (Note) This may take a little time to process and if you see any prompts from updates, you can hit OK on the prompts and `f` for the MORE prompt for the Anaconda setup

4) Setup your Anaconda virtual environment with the following commands:

    * `source ~/.bashrc` - (if you just installed Anaconda above, and haven't restarted your shell session)
    * `conda create -n mpls311 python=3.9 -y`
    * `conda activate mpls311`
    * `pip install -r ./setup/conda_requirements.txt`

5) Run `docker-compose -f docker/docker-compose.yml up -d` to start the docker containers for Prefect and its underlying Postgres database 

6) Save your Google Cloud service account .json file to the ./creds folder.  You can sftp the file from your local computer to that location.  You could even just open the file on your local computer, copy the contents of the file and do `nano ./creds/[filename].json` on the VM and paste in the contents into this new blank file, and then do CTRL + X, and then `Y` and ENTER, to save and exit the file.

7) Set an environment variable for your service account file that you just saved with this command: `export GOOGLE_APPLICATION_CREDENTIALS="<absolute path to the json file in the ./creds folder>"`

8) Update the GOOGLE_APPLICATION_CREDENTIALS environment variable in the ./.env file, using the same absolute path to the .json service account file

9) Run `gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS` to authenticate with Google Cloud, with your service account .json file.

10) Run Terraform to deploy your infrastructure to your Google Cloud Project.  Run the following commands:

    * `terraform -chdir="./terraform" init` - to initialize terraform
    * `terraform -chdir="./terraform" plan -var="project=<project id here>"`, replacing <project id here> with your Google Project ID.  This will build a deployment plan that you can review.
    * `terraform -chdir="./terraform" apply -var="project=<project id here>"`, replacing <project id here> with your Google Project ID.  This will apply the deployment plan and deploy the infrastructure

11) Run the following commands to set up a local Prefect profile

    * `prefect profile create mpls311`
    * `prefect profile use mpls311`
    * `prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api`

12) If you are using VS Code and have made a remote SSH connectiono to your VM through it, and forwarded port 4200, you could now go to http://localhost:4200 to access your Prefect server instance

13) Create blocks in Prefect to store credentials and setups for Google Cloud and DBT core, running: `python setup/prefect_setup_blocks_gcp.py`

14) Edit the prefect.yaml in the root of this repository, you can do `nano prefect.yaml`.  Find and edit the line that currently says `bucket: data_lake_[project name]`, replacing the `[project name]` with your GCP Project name

15) Run the following two commands to deploy the pipeline to Prefect and then run it for all years of data

    * `prefect deploy --name Mpls311ETL`
    * `prefect deployment run 'Process-Data-Parent/Mpls311ETL'`

    This may take 5-10 minutes to run the full pipeline.  You can switch to the terminal session for the work queue to watch the progress if you like.

    If you were to immediately run the deployment again, no additional records would get pulled from the API, and the dbt models would run, rebuild some tables, but make no additions to the fact or georgraphy dimension tables.  If you were to run a day later, the process will pick up new records and updated records from the API, and process them through the full pipeline.

16) > **Important note: Once you're done evaluating this project, make sure to stop and remove any cloud resources.  If you're using a cloud VM, make sure to stop it in your VM Instances screen in Google Cloud Console, and potentially delete it if you no longer want it.  This way it's not up and running, and using up your credits.  In addition, you can use Terraform to destroy your buckets and datasets, with `terraform -chdir="./terraform" destroy -var="project=<project id here>"`**



## Results

Below is an example dashboard I've put together based on this data.  

![Dashboard Example](images/mpls_311data_dashboard_example.png)

As I look through the reports, there are a number of things that jump out at me:

1) There are a small number of major categories of service requests, 13 of them.  Below those categories though, there are 178 different minor categories of requests they coordinate.

1) Over the years, the major category with the most service requests is Vehicles and Commuting.  That category also has the top two minor categories for Parking Violations and Abandoned Vehicles.  I'm surprised there are so many requests related to abandoned vehicles.

2) Some variations in certain categories throughout the year make sense.  For example, service requests related to Sidewalk Snow or Ice issues or Street Snow and Ice issues are typically November through April, given the winter here.  Similarly, service requests for exterior nuisance complaints are highest from May through September, when people here are outside more and no longer hibernating.  There's also a very noticable spike related to Pothole and Sewer Issue service requests in March specifically, likely related to Winter ending.


## Future development

I currently plan on continuing to refine this project and pipeline, expanding out my knowledge and experience.  Some things that immediately come to mind that I think are worth exploring:

1) ~~Dockerizing the Prefect Orion server, so the server and worker queue can just run in the background as a docker container~~ **Implemented**

2) ~~Refining my API functionality, such as implementing functionality to check the json response for information, error handling and checking for the parameter indicating the return record count limits~~ **Implemented**

3) ~~Implementing some tracking table(s), tracking each run of the pipeline, tracking information such as date run, record counts, parameters used, etc.~~ **Implemented**

4) Alter the process to allow for a full data process, and also incremental updates.  This would likely include changes to the dbt models, changes to the API functionality, and utilizing the tracking table(s) referenced above

5) There's a lot more analysis that can be performed on this data set.  One interesting idea that comes to mind is looking at the time it takes for service requests to be completed, defining KPIs or SLAs based on prior year's data as benchmarks, and evaulating the next year's data against those benchmarks.  It would also be interesting to explore how to utilize the geography coordinates in the data, to evaluate the data against neighborhoods or locations in the city.

6) Building additional functionality allowing the process to be run on a variety of systems.  For example, building functionality for local storage and local postgres or duckdb database instances, or utilizing other cloud services, such as with AWS.

7) Implementing Continuous Integration / Continuous Deployment (CI/CD)