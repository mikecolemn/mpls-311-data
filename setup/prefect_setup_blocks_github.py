from prefect.filesystems import GitHub

block = GitHub(
    repository="https://github.com/mikecolemn/mpls-311-data/",
    reference="dev" # Can refer to a branch
    #access_token=<my_access_token> # only required for private repos
)
block.get_directory("flows") # specify a subfolder of repo
block.save("gh-mpls311", overwrite=True)