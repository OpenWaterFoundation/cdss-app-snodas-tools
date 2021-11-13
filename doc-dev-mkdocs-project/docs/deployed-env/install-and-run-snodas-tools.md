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
    * Can verify tarball was created by typing `cd builds` and `ls` to see
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
    * Optionally remove the compressed tar file by typing `sudo rm cdss-tools-VERSION.tar.gz`
9. Change the ownership and group of all the untarred files and folders by running
`sudo chown -R snodas:snodas *`.

## Automating SNODAS Tools using CRON ##

A cron table is used to automate running a bash script that runs the `SNODASDaily_Automated.py`
script. The crontab is owned by root, as is all folders and files in the `snodas-tools-1/`
directory. This contains the older QGIS and Python version 2 code, but was used
as a template for the installation of the newer version 3 code.

## Running SNODAS Tools ##

TSTool uses Java Swing components for its user interface, and Swing uses the
[X Window system](https://en.wikipedia.org/wiki/X_Window_System) (X-Windows) when
run on a Linux computer. X-Windows allows a program to be run on one computer and
display on a different computer. To display on a Windows computer, the computer
must be running an X-Windows server. Even though it won't be used, it is still
necessary to set up an X Window server on an OS that supports graphics.

If X Window has previously been set up, only steps 2 and 3 are necessary. The steps
to running SNODAS Tools on the GCP VM are:

1. Confirm an X server is running on another, graphics-implemented computer and
connect it to the GCP VM. More details can be found at [Setting Up an X Server](#setting-up-an-x-server).
2. SSH into the GCP VM: `ssh -Y user@IP_ADDRESS`.
  * Testing with any basic `x` programs can be done, e.g. trying to run `xclock`.
3. Change directories to the SNODAS Tools top-level folder and run either
```bash
python3 SNODASDaily_Interactive.py
```

for selecting a single or range of dates, or

```bash
python3 SNODASDaily_Automated.py
```

for updating the dates to the most recent day.

See [X Window Troubleshooting](troubleshooting#x-window) for help.

## Setting Up an X Server ##

The following instructions used Cygwin on Windows 10 Pro. **Maybe add link to more
X Window documentation that covers Git Bash, etc.**

1. Confirm the X Window server and xhost packages are installed for Cygwin. Run
the Cygwin installer `.exe` file again, or visit the [cygwin.com install](https://cygwin.com/install.html)
web page and run the setup file from there. More information can be found on the
[Cygwin/X documentation](https://x.cygwin.com/docs/ug/setup.html) page.
> **NOTE: ** The packages `xterm`, `xeyes`, or `xclock` can also be downloaded
for testing purposes.
2. In a separate Cygwin terminal, start the X Window server by running `startxwin -- -listen tcp`.
3. In the Cygwin terminal that will be used to ssh into the GCP VM, set the `DISPLAY`
environment variable to use the Windows display by running `export DISPLAY=localhost:0.0`.
  * Confirmation that the server is running can be tested by starting `xclock`, `xeyes`, etc.
  on the terminal.
4. Add the GCP VM to the xhost access control list: `xhost +IP_ADDRESS`, where `IP_ADDRESS`
is the VM's external IP Address.
