# Development Tasks / Documenting

The SNODAS tools software developer should recognize that good developer and user documentation
is one of the most important contributions to the software project.

Low quality or incomplete developer documentation will result in wasted effort later when another developer tries to understand the software
for maintenance and enhancement.

Low quality or incomplete user documentation will result in users not understanding how to run the software and use generated products.

## Python Code Documentation

Python code documentation should follow Python "docstring" conventions, as per the following resources:

* [Docstring on Wikipedia](https://en.wikipedia.org/wiki/Docstring) - general introduction to docstring concepts
* [Python docstring conventions](https://www.python.org/dev/peps/pep-0257/) - recommendations for Python documentation

## Configuration File Documentation

Configuration files should include documentation in the appropriate form.

* Text files should use `#` or other comments describing the data.
* Excel files should include worksheets documenting the workbook contents and versions,
and use comments in table header cells to describe the contents of columns.

## Data File Documentation

* GIS layers should include standard metadata file for the format.
* **TODO smalers 2016-12-06 need to evaluate how to do for GeoJSON, etc.**

## Developer Documentation Website

Developer documentation (this documentation) is created using MkDocs and results in a static website,
currently accessible from the
[Open Water Foundation SNOTEL Tools project website](http://projects.openwaterfoundation.org/owf-proj-co-cwcb-2016-snodas/index.html) and the
[Open Water Foundation software website](http://software.openwaterfoundation.org).
MkDocs should have been [installed previously](../dev-env/mkdocs/).  See the following resources for MkDocs and MarkDown:

* [MkDocs - Writing your docs](http://www.mkdocs.org/user-guide/writing-your-docs/)
* [Markdown cheatsheet - GitHub, adap-p](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)

### Folder Structure

Create all developer documentation under the `doc-dev-markdown-project` folder in the Git repository as per MkDocs.
Edit the `mkdocs.yml` file to create the documentation outline and then create content in the `docs` folder.
Guidelines for the content are:

* Create a limited number of top-level folders (should already be in place).
* Create Markdown files for each page, for example `myfile.md`.
* If images are needed, create a parallel folder for images, for example `myfile-images`.
* Create PNG images, for example using GIMP software and save in the images folder.

### Markdown Conventions

The reader of developer documentation is expected to have some skill in software development and installation.
However, content should provide background and context where appropriate and not assume that the reader is an expert in GIS or Python.

## User Documentation Website

User documentation is created using a similar approach to the developer documentation.

User documentation is created using MkDocs and results in a static website,
currently accessible from the
[Open Water Foundation SNOTEL Tools project website](http://projects.openwaterfoundation.org/owf-proj-co-cwcb-2016-snodas/index.html) and the
[Open Water Foundation software website](http://software.openwaterfoundation.org).
MkDocs should have been [installed previously](../dev-env/mkdocs/).

### Folder Structure

Create all user documentation under the `doc-user-markdown-project` folder in the Git repository as per MkDocs.
Edit the `mkdocs.yml` file to create the documentation outline and then create content in the `docs` folder.
Guidelines for files are the same as for developer documentation.

### Markdown Conventions

Markdown conventions for user documentation are the same as for developer documentation.
The target for documentation is EVERYONE so writing should be very clear and not assume technical background.
