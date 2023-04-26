# version - version information for the SNODAS Tools applications

# Put in separate file to minimize commits to main application files when only version changes but no
# other code changes.
app_name = "SNODAS Tools"

# The following parts are used to create a full version:
# - the strings are also used in build process scripts
# - set the `app-version_mod` to something like 'dev`' for a development release that may be used while cumulative
#   development occurs
app_version_major = 2
app_version_minor = 1
app_version_micro = 0
app_version_mod = ""

# Use 'str' for the version string.
if app_version_mod == "":
    app_version = "{}.{}.{}".format(app_version_major, app_version_minor, app_version_micro)
else:
    app_version = "{}.{}.{}.{}".format(app_version_major, app_version_minor, app_version_micro, app_version_mod)
app_version_date = "2023-04-22"


def version_uses_new_config () -> bool:
    """
    Return True if the version uses the new configuration file with ${Property} notation.
    :return: True if the version uses the new configuration file with ${Property} notation.
    """
    if app_version_major < 2:
        return False
    else:
        if app_version_minor < 1:
            return False
        else:
            return True