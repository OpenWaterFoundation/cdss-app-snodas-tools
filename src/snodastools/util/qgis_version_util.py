"""
This module contains functions that deal with checking the QGIS version.
The functions can be called to determine which modules to import.
"""

from qgis.core import Qgis


def get_qgis_version_int(part: int = 0) -> int:
    """
    Returns the version (int) of the initiated QGIS software.
    If the part is not specified the entire version is returned as an integer.

    Example:
        21809

    Args:
        part The part of the version to return (0=full integer, 1=major, 2=minor, 3=patch)

    Returns:
        The QGIS version (int).
    """

    # TODO smalers 2018-05-28 the following was version 2.
    # return qgis.utils.QGis.QGIS_VERSION_INT

    # Version 3 uses the following.
    if part == 0:
        return Qgis.QGIS_VERSION_INT
    else:
        return int(get_qgis_version_str().split(".")[part - 1])


def get_qgis_version_name() -> str:
    """
    Returns the version name of the initiated QGIS software.

    Example:
        Las Palmas

    Returns:
        The QGIS version name (string).
    """

    # TODO smalers 2018-05-28 the following was version 2.
    # return qgis.utils.QGis.QGIS_RELEASE_NAME
    return Qgis.QGIS_RELEASE_NAME


def get_qgis_version_str() -> str:
    """
    Returns the version (string) of the initiated QGIS software.

    Example:
        "3.26.3"

    Returns:
        The QGIS version (string).
    """

    # TODO smalers 2018-05-28 the following was version 2.
    # return qgis.utils.QGis.QGIS_VERSION

    # The following is for version 3.
    return Qgis.version()