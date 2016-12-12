# Project Initialization / GitHub

Various files related to the SNODAS Tools software, documentation, tests, etc. are managed in a public GitHub Git repository.
The following sections describe how the repository was initialized during project set-up.

## Prerequisites

Before creating a repository in GitHub and cloning to local files, the following steps must have been completed:

* [Install Git Software](../dev-env/git/)
* [Create Development Folder](dev-folder/)

## Create GitHub Repository

It is assumed that the [Git for Windows software was previously installed](../dev-env/git/).

The Git/GitHub repository was initialized using the following steps:

The [SNODAS Tools Git repository](https://github.com/OpenWaterFoundation/cdss-app-snodas-tools) was first created in GitHub under the Open Water Foundation organization.

* Basic information was defined such as the description and default `README.md` file.
* The repository was defined as public.
* Collaborators were added for the project team.
consistent with [overall project organization](overview#development-folder-structure):

**TODO smalers 2016-12-06 Need to confirm how the State of CO wants to manage the repository -
is OWF repository OK or should it be moved to a State of CO organization? - see the OWF OpenCDSS project**

**TODO smalers 2016-12-06 Need to confirm with the State of CO the license for the software and work products - see the OWF OpenCDSS project**

## Clone the GitHub Repository to Developer Computer

It is assumed that the [project folder structure was previously defined](dev-folder/) on the development computer for the software developer's account,
Additionally, if not already done, create the folder to hold Git repositories (the following illustrates using Windows Command Shell):

```
> C:
> cd \Users\user\cdss-dev\CDSS-SNODAS-Tools
> mkdir git-repos
```

The repository was cloned to the `git-repos` folder:


```
> C:
> cd \Users\user\cdss-dev\CDSS-SNODAS-Tools\cdss-dev
> git clone https://githubUsers\user\cdss-dev\CDSS-SNODAS-Tools\cdss-dev.com/OpenWaterFoundation/cdss-app-snodas-tools.git
```

This created a folder `C:\Users\user\cdss-dev\CDSS-SNODAS-Tools\cdss-dev\cdss-app-snodas-tools`.

## Add files to the Repository

Files were then added to the repository and committed, as described in other documentation.
