# Deployed Environment / Install and Run SNODAS Tools #

The next few sections describe how to install the production/deployed tarball file
onto the Google Cloud Platform (GCP) VM instance, followed by how to run SNODAS
Tools, and any other pertinent information about the software.

## Installing SNODAS Tools on the GCP VM instance ##

Steps for creating the tarball on the development VM, installing the tar on the
deployed VM, and extracting from the tar file are as follows:

1. From the development VM's repository top-level file (`cdss-app-snodas-tools`),
`cd` into `build-util/`.
2. Type `./create-installer-tar.bash` to create the tarball.
    * If the error message `-bash: ./create-installer-tar.bash: Permission denied`
    displays, update the file permissions by typing
    `chmod +x create-installer-tar.bash`.
    * Can confirm tarball was created by typing `cd builds` and `ls` to see
    `cdss-tools-VERSION.tar.gz` where VERSION is the version number of SNODAS Tools.
3. Copy the tarball onto the host OS so it can be uploaded to the GCP cloud terminal.
The OWF development structure has a shared folder to an external drive, connected
through the path `/media/SNODAS2/` on the VirtualBox Linux VM. For example, the
tarball would be copied to that file so the GCP terminal can find it on the host OS
when uploading.
4. In the GCP Compute Engine VM instances tab, click the terminal icon the upper
right part of the screen to open up Cloud Shell.
5. Click the kebab menu (three vertical dots) in the upper right part of the cloud
terminal and choose **Upload File**. Choose the tarball, which will be put in the
cloud terminal's home directory.
6. Use `scp` to securely transfer the tar file from the cloud terminal to the VM
home directory by using the command
`gcloud compute scp cdss-tools-2.0.0.tar.gz snodas-tools-1:~ --zone=us-west1-c`.
> **NOTE:** All commands dealing with SNODAS Tools on the GCP VM instance must use
sudo since manipulating folders and files in `/var/opt/`. Therefore, the user must
have sudo privileges to finish the installation.
7. Move the tar into the SNODAS version 2.* top-level file by typing
`sudo mv cdss-tools-VERSION.tar.gz /var/opt/snodas-tools/`.
8. Type `sudo tar -xzvf cdss-tools-VERSION.tar.gz`

## Automating SNODAS Tools using CRON ##

A cron table is used to automate running a bash script that runs
the `SNODASDaily_Automated.py` script. The crontab is owned by root,
as is all folders and files in the `snodas-tools-1/` directory. This
contains the older QGIS and Python version 2 code, but was used as
a template for the installation of the newer version 3 code.

## Running SNODAS Tools ##

**TODO: jpkeahey - Insert link to XWindows set up. This is needed to be done before
any of the SNODAS Tools scripts are run, or else there will be a QT xcb plugin error.**

### Running a range of dates ###

To run SNODAS Tools over a range of dates, perform the following:

1. Log into the GCP VM