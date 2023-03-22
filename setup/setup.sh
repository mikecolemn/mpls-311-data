#!/bin/bash

# initial updates
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install unzip -y

# setup gcloud cli
sudo apt-get install apt-transport-https ca-certificates gnupg -y
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
sudo apt-get update && sudo apt-get install google-cloud-cli

# anaconda setup
wget https://repo.anaconda.com/archive/Anaconda3-2022.10-Linux-x86_64.sh
# User will need to page down or hit f to get past the MORE prompt
echo -ne "ENTER \n yes \n \n yes \n" | bash Anaconda3-2022.10-Linux-x86_64.sh
rm Anaconda3-2022.10-Linux-x86_64.sh

# terraform
wget https://releases.hashicorp.com/terraform/1.4.2/terraform_1.4.2_linux_amd64.zip
sudo unzip terraform_1.4.2_linux_amd64.zip -d /usr/bin
rm terraform_1.4.2_linux_amd64.zip
