# Deployed Environment / TSTool

TSTool is installed in the `/opt` folder on the deployed GCP VM, the default path
when run as root. This section describes how to

* install another TSTool version on the deployed VM
* update the configuration file for integrating TSTool with SNODAS Tools.
* test the installed TSTool version to confirm a successful installation.

## Installing TSTool ##

After the TSTool installer is acquired, perform the following to install on the 
deployed VM:

1. Upload the installer to the GCP cloud console using the kebab button. It will be
installed in the home directory.
2. Type
`gcloud compute scp TSTool-linux-13.04.00.dev.2106091606.run  snodas-tools-1:~ --zone=us-west1-c`
to securely copy the installer from the cloud console to the VM. This command will
also copy it to the user's home directory.
3. Log into the deployed VM and run the installer with the command
`sudo ./TSTool-linux-13.04.00.dev.2106091606.run`. This is an example installing the
13.04.00.dev version. The installer name might not match exactly; the important part
is using sudo, as the default installation folder would be in `/opt/`, instead of
a user folder.
4. A message will appear displaying the default system install folder. Confirm that
the script knows it was run as root, will install under `/opt/`, and press return.
5. A final prompt will ask to create a symbolic link from `/usr/bin/tstool` ->
`/opt/tstool-VERSION`, where VERSION is the TSTool version to be installed. Enter Y
and hit return. The installation is now complete.

## SNODAS Tools Configuration ##

**TODO smalers 2016-12-04 need to describe final configuration of the SNODAS tools once all software components are installed.
This will be similar to the development environment for file structure.**

## Test SNODAS Tools ##

**TODO smalers 2016-12-04 need to describe how to do basic testing to make sure things are working**