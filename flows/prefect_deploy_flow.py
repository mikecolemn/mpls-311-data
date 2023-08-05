from prefect.filesystems import GitHub
from prefect.deployments import Deployment
from etl_mpls311_gcp import parent_process_data

storage = GitHub.load("gh-mpls311")

github_dep = Deployment.build_from_flow(
    flow=parent_process_data,
    name='Mpls-311-ETL',
    storage=storage,
    parameters={"years":[2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]}
)

github_dep.apply()

if __name__  == "__main__":
    github_dep.apply()