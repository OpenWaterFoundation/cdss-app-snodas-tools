# Project Initialization / PyCharm Workspace

PyCharm provides extensive functionality for editing and running Python Programs.

Because the SNODAS tools source code are stored in the Git repository it is necessary to make PyCharm
aware of the repository.  Resources include:

* [Using GitHub Integration](https://www.jetbrains.com/help/pycharm/2016.2/using-github-integration.html)

Important considerations include:

* PyCharm files for a specific developer should not be stored in the Git repository because they will conflict with other developers.
Some developer files will reside with the local PyCharm software installation or other user files, which are not in the repository.
* Definitely do not want to store GitHub account password or any other security information in the public repository.
* PyCharm Git integration will likely be used for Python code, but Git BASH might be used for other files such as MkDocs markdown.

**TODO smalers 2016-12-05 need to figure out PyCharm Git integration and whether to use or Git BASH/GUI**
