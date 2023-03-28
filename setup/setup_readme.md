
### Table of contents
- [Google Cloud Platform setup](#google-cloud-platform-setup)
    - [Google Cloud Platform](#google-cloud-platform)
    - [Create Project](#create-project)
    - [Create Service Account](#create-service-account)
    - [Generate SSH key](#generate-ssh-key)
    - [Create VM](#create-vm)

# Google Cloud Platform setup

## Google Cloud Platform

[Google Cloud Platform](https://cloud.google.com/)

You can create a trial account on Google's Cloud platform that is free for 90 days and you have $300 (or an equivalent amount of your local currency) worth of credits to use in that time.

Login with a Google account of yours, to the link above.  You can click Start Free in the upper right and follow through the prompts to set up your free trial profile.  You will need to provide credit card information.

## Create Project

[Google Cloud Console](https://console.cloud.google.com/)

We should to create a new project on Google Cloud, to treat this project separately from any other projects you may have worked on. 

Click in the drop down box next to Google Cloud, in the upper right of your screen, and click the New Project link in upper right of the next screen that opens.  Enter a name you want to use and hit Create.

## Create Service Account

We need to create a service account for this project.  This service account will be used to control permissions and be utilized by our Terraform and data pipeline processes.

From the Navigation menu on the left, navigate to IAM And Admin > Service Accounts.  Click Create service account at the top, and enter what you want for the Name, ID, and Description fields listed.  Click Create and Continue.

For Access, you can search for and select each of the following: "BigQuery Admin", "Storage Admin", and "Storage Object Admin".  If you ever want to change any of these, you can update them from the IAM And Admin > IAM screen.  Click the pencil icon (Edit Principal) at the right of the service account, and you can change, add, or remove permissions.

You don't need to enter anything for the Grant Users.

Hit Done.

From the Service Account screen, click the Actions icon to the right of the service account and select "Manage keys".  On the next screen, click the Add Key link, select New Key, then select JSON, and click Create.  This will prompt you to download the .json key being generated.  Save this somewhere on your local computer.  Later, we'll upload this to a VM we create.

## Generate SSH key

[Reference link](https://cloud.google.com/compute/docs/connect/create-ssh-keys)

We need to generate an ssh key, which we'll upload to our Google Cloud project and this will be used for ssh'ing into a VM

On your local computer, open your terminal and run the below command:
`ssh-keygen -t rsa -f ~/.ssh/mpls311_vm -C mpls311 -b 2048`

This will generate an 2048 bit rsa ssh keypair, named `mpls311_vm` and a comment of `mpls311`.  The comment will end up being the user on your VM.

Do a `cat mpls311_vm.pub` to see the contents of the public key, and copy the contents.

Back in Google Cloud Console, navigate to Compute Engine > Metadata.

On the SSH keys tab, you can click Add SSH key and paste in the contents you copied, and hit save.

## Create VM

Finally, we'll create a VM that we can set up and run this project from.

In Google Cloud Console, navigate to Compute Engine > VM instances.  You may have to activate the APi for the Compute Engine when you first come here.

Click the `Create Instance` action towards the top.  On the next screen, you'll want to set the following information:

Name = whatever name you would like to call this VM

Region, Zone = select a region near you, same with Zone

Machine Type = Standard, 4vCPu, 16 GB Memory (e2-standard-4)

Boot Disk section, change the following settings:

Select Ubuntu and Ubuntu 20.04 (x86/64) as the Operation System and Version
Size = 20 GB should be plenty for this project.

Hit Create.  Once the VM is finished getting created, note the external IP address.

In your terminal window, you should now be able to ssh into the VM via the command below, inputing the external IP address of your VM
`ssh -i ~/.ssh/mpls311_vm mpls311@[external IP address]`

You can also update or create a `config` file in your `~/.ssh` folder with the block below, inputing the external IP address of your VM.  This will allow you to just do `ssh gcpvm` to login to your VM
```
Host gcpvm
    Hostname [external IP address]
    User mpls311
    IdentityFile ~/.ssh/mpls311_vm
```

> **Important note: When you're not using your VM, make sure to stop it in your VM Instances screen in Google Cloud Console.  This way it's not up and running, and using up your credits.**
