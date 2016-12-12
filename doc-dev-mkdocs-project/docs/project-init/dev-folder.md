# Project Initialization / Create Development Folder

A standard development folder structure is desirable to ensure consistency and to allow standard documentation to be prepared.
See the [discussion of development project folder structure](overview#development-folder-structure).

The following steps will create a standard development folder structure for the SNODAS tools.
Steps can be skipped if the steps have already been performed.

## Create Folder Structure with Git BASH

If Git BASH is available from [installing Git](../dev-env/git/), then Git BASH can be used to create development folders.
Lines beginning with `#` are comments that should not need to be entered.
In the following `user` is the software developer account.

```bash
$ cd /c/Users/user
# Create umbrella folder for organization development project, in this case a CDSS software project
$ mkdir cdss-dev
$ cd cdss-dev
# Create folder for development project
$ mkdir CDSS-SNODAS-Tools
```

## Create Folder Structure with Windows Command Shell

A Windows Command Shell can also be used to perform the following steps.
Lines beginning with `#` are comments that should not need to be entered.
In the following `user` is the software developer account.


```com
> C:
> cd \Users\user
# Create umbrella folder for organization development project, in this case a CDSS software project
> mkdir cdss-dev
> cd cdss-dev
# Create folder for development project
> mkdir CDSS-SNODAS-Tools
```

## Next Step

The next step is to configure the Git/GitHub repository so that files can be added to the software project for tracking.
