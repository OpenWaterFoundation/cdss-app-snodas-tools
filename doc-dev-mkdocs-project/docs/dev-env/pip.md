# Development Environment / pip

**TODO SAM 2016-12-11 need to determine what version of `pip` is installed with QGIS Python.**

It may be necessary to install add-on packages that extend the basic Python functionality.
For example, the MkDocs software used to prepare this documentation is an add-on package.

## `pip` Background

The [`pip` software](https://pip.pypa.io/en/stable/) is used to install Python packages and is the preferred installation tool since older tools such as `easy_install`
do not support current conventions.  Therefore, in order to install third-party packages, install `pip` first.
See the following resources:

* [Installing Packages](https://packaging.python.org/installing/) - should use `pip` if possible
* [Stack Overflow article on using `pip` when multiple Python versions are installed](http://stackoverflow.com/questions/10919569/how-to-install-a-module-use-pip-for-specific-version-of) -
it is possible

In summary:

* Add-on packages should install into a location consistent with the Python software install location.
* The `pip` utility should be used to install add-on packages.
* It is possible to use `pip` to install modules when multiple versions of Python are installed.
See the examples below for specific operating systems.

## Install `pip` on Windows

The following uses a Windows Command Shell.  To check for whether pip is already installed,:

```com
py -2 -m pip --version
pip 7.0.1 from C:\Python27\lib\site-packages (python 2.7)

py -3 -m pip --version
pip 8.1.2 from C:\Users\sam\AppData\Local\Programs\Python\Python35-32\lib\site-packages (python 3.5)

```

If not installed, install with the following, repeating for each Python installation:

```com
py -2 -m ensurepip

py -3 -m ensurepip
```
