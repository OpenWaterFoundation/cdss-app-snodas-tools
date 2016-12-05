# Development Environment / MkDocs

MkDocs is a Python add-on package that creates static website content from Markdown input.
See the installation instructions on the [MkDocs website](http://www.mkdocs.org/).

Before installing MkDocs, it is necessary that [Python is installed](python) and [`pip` is installed](pip).

## Install MkDocs

To install MkDocs, open a Windows Command Shell and run the following.
This assumes that Python was installed and Python environment variables were set.

To check whether MkDocs is installed:


```
py -m mkdocs
```

If not installed, install with the Python 3 version (actually no need to specify `-3` but do to illustrate installing for specific Python version):

```
py -3 -m pip install mkdocs
```

Check whether installed by running:

```
py -m mkdocs 
```

or simply:

```
mkdocs
```

If installed, the usage will be shown, similar to:

```
Usage: mkdocs [OPTIONS] COMMAND [ARGS]...

MkDocs - Project documentation with Markdown.

Options:
    -V, --version  Show the version and exit.
    -q, --quiet    Silence warnings
    -v, --verbose  Enable verbose output
    -h, --help     Show this message and exit.

Commands:
  build      Build the MkDocs documentation
  gh-deploy  Deploy your documentation to GitHub Pages
  json       Build the MkDocs documentation to JSON files...
  new        Create a new MkDocs project
  serve      Run the builtin development server
```
