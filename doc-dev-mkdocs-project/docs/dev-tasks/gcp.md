# Initial Project Setup / Google Cloud Platform #

## Introduction ##



## Connecting to SNODAS Tools VM ##

Using the Cloud Shell in GCP works just fine, but a simple ssh connection can be
performed through a terminal. Each VM listed under the VM instances section contains
the VM's external IP address that can be used by ssh. Using the following command
will connect to the VM using the `EXTERNAL_IP_ADDRESS` as the `USERNAME` user.

```
ssh USERNAME@EXTERNAL_IP_ADDRESS
```

## Authenticating to Google Cloud Platform ##

### SNODAS Tools (Back End) ###

When dealing with this repository's back end code, logging into the GCP VM instance
is generally enough to authenticate and push to the GCP bucket. Use the command

```
gcloud info
```

to display the Google Cloud SDK information. It will display whether there is an
active account and project in use. These can be updated / changed at Google's
[Cloud SDK: Command Line Interface](https://cloud.google.com/sdk/gcloud/reference)
documentation.

Another useful command is use is

```
gsutil version -l
```

This will show detailed information about the installed gsutil package, and the
path to the boto configuration file. This is the file that's created by Google
when a user has successfully authenticated.

### SNODAS Angular Application (Front End) ###

When pushing the front end application up to the GCP bucket, it will most likely
be done from a completely separate computer that has not been authenticated. Run
the command

```
gcloud auth login --no-launch-browser
```

to display a link that can be copy-pasted into a browser. From there, the desired
account can be selected and authenticated. Running `gcloud info` should display
updated values for the project and account.

