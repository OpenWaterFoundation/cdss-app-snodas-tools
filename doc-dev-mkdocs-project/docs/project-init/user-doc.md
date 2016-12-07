# Project Initialization / User Documentation

This documentation describes how the user documentation was initialized.
This user documentation uses the MkDocs software which should have been [previously installed](../dev-env/mkdocs/).

## Create Folder for User Documentation

The SNODAS tools [development folders should have been previously created](dev-folder/) and the [Git repository cloned](github/).
Next, create a MkDocs empty project.  The following uses Windows Command Shell.


```
> C:
> cd C:\Users\user\cdss-dev\CDSS-SNODAS-Tools\git-repos\cdss-app-snodas-tools
> mkdocs new doc-user-makedocs-project
```

This will initialize the folder `C:\Users\user\cdss-dev\CDSS-SNODAS-Tools\git-repos\cdss-app-snodas-tools\doc-user-mkdocs-project`.

## Edit MkDocs Content

Follow the guidance in the [Development Tasks / Documenting](../dev-tasks/doc#user-documentation-website) section for guidelines in editing the documentation.
Some MkDocs files were created from scratch and others were copied from other MkDocs projects and updated.

Documentation files are committed to the repository using normal [Git workflow protocols](../dev-tasks/git/).
