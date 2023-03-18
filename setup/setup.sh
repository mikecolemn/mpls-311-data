#!/bin/bash

# sudo lvextend -r -l +100%free /dev/ubuntu-vg/ubuntu-lv

# initial updates
sudo apt-get update -y
sudo apt-get upgrade -y

# setup gcloud cli
sudo apt-get install apt-transport-https ca-certificates gnupg -y
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
sudo apt-get update && sudo apt-get install google-cloud-cli

# anaconda setup
wget https://repo.anaconda.com/archive/Anaconda3-2022.10-Linux-x86_64.sh
# User will need to page down past the MORE prompt
echo -ne "ENTER \n yes \n \n yes \n" | bash Anaconda3-2022.10-Linux-x86_64.sh
rm Anaconda3-2022.10-Linux-x86_64.sh

source .bashrc

# Pull repo
git clone https://github.com/mikecolemn/mpls-311-data.git
cd mpls-311-data

# Create conda environment
conda create -n mpls311 python=3.9 -y
conda activate mpls311

pip install -r ./setup/conda_requirements.txt


