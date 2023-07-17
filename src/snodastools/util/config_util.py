"""
Configuration file utilities.
"""

import logging
import os
from pathlib import Path

# A dictionary of all configuration file properties, with section, after expansion:
# - for example a configuration property in [Folders] static_data_folder = ${root_folder}/staticData
#   would have a value in the dictionary as the expanded value
# - the configuration is read with 'read_config_file' and then use 'get_config_prop' to look up specific properties
# - this can be used by utility code and programs
config_dict = {}


def expand_config_property(config_property_dict: dict, property_value: str ) -> str or None:
    """
    Expand ${Property} notation in property values.
    This does not handle nested properties.
    """
    if not property_value:
        return property_value
    elif not config_property_dict:
        return property_value
    else:
        # Have input to work with.
        expanded_property_value = property_value
        for property_name in config_property_dict:
            dict_property_value = config_property_dict[property_name]
            if not dict_property_value:
                continue
            else:
                # Make sure that the value is a string.
                dict_property_value = str(dict_property_value)
            expanded_property_value = expanded_property_value.replace("${" + property_name + "}", dict_property_value)
    return expanded_property_value


def find_config_file ( command_line_snodas_root: Path or None) -> Path or None:
    """
    Find the absolute path to the configuration file given the current folder and optional command line SNODAS root.
    :param command_line_snodas_root: Absolute path to the SNODAS root.
    :return: path to the configuration file or None if cannot determine
    """
    config_file_path = None
    current_folder = Path(os.getcwd())
    print("Current folder:")
    print("  {}".format(current_folder))

    # Old case must now either run from the SNODAS Tools implementation root folder or specify on the command line.
    #if Path('{}/../test-CDSS/config/SNODAS-Tools-Config.ini'.format(current_folder)).exists():
    #   config_file_path = Path('../test-CDSS/config/SNODAS-Tools-Config.ini')

    if command_line_snodas_root:
        # Path to the SNODAS implementation root has been specified on the command line so use it:
        # - check for existence in the calling code so that a user-friendly message can be displayed
        print("Command line specified SNODAS root:")
        print("  {}".format(command_line_snodas_root))
        if command_line_snodas_root.startswith("."):
            # SNODAS root was specified with path relative to the starting folder.
            config_file_path = current_folder / command_line_snodas_root / "config" / "SNODAS-Tools-Config.ini"
            print("  Specified path is relative so append to the current folder.  Config file path:")
        else:
            # SNODAS root was specified with an abslute path.
            print("  Specified path is absolute.  Config file path:")
            config_file_path = Path(command_line_snodas_root) / "config" / "SNODAS-Tools-Config.ini"
        print("    {}".format(config_file_path))
        return Path(config_file_path)

    # Running in the root folder (config will be a sub-folder).
    config_file_path = Path(current_folder) / "config/SNODAS-Tools-Config.ini"
    print("Checking for configuration file as if running in the SNODAS tools root folder:")
    print("  {}".format(config_file_path))
    if config_file_path.exists():
        return config_file_path
    else:
        print("  Configuration file was not found.")

    # Running in the production scripts folder (*venv/ folder same level as config/).
    #    config_file_path = Path('{}/../../config/SNODAS-Tools-Config.ini'.format(current_folder))
    config_file_path = Path(current_folder) / "../../config/SNODAS-Tools-Config.ini"
    print("Checking for configuration file as if running in the SNODAS Tools 'scripts' folder:")
    print("  {}".format(config_file_path))
    if config_file_path.exists():
        return config_file_path
    else:
        print("  Configuration file was not found.")

    # Running in the production scripts folder.
    #    config_file_path = Path('{}/../config/SNODAS-Tools-Config.ini'.format(current_folder))
    config_file_path = Path(current_folder) / "../config/SNODAS-Tools-Config.ini"
    print("Checking for configuration file as if running in the SNODAS Tools 'scripts' folder:")
    print("  {}".format(config_file_path))
    if config_file_path.exists():
        return config_file_path
    else:
        print("  Configuration file was not found.")

    # Could not find the configuration file.
    return None


def get_config_prop(property_name: str) -> str or None:
    """
    Lookup a property value from the name.
    :param config_map_dict: dictionary of configuration properties
    :param property_name: property name to lookup
    :return: the property value if found in the dictionary or None if not found
    """
    global config_dict

    try:
        # Return the value from the global configuration dictionary if found.
        return config_dict[property_name]
    except KeyError:
        # Not found so return None.
        return None


def read_config_file(config_file_path: Path) -> None:
    """
    Read the configuration file into a dictionary of properties.
    :param config_file_path: path to the configuration file
    """
    cfp = open(config_file_path, 'r')

    global config_dict

    section = None
    section_props = None
    property_value = None
    property_value_found = None

    while True:
        line = cfp.readline()
        if not line:
            # End of file.
            break
        line_trimmed = line.strip()
        #logging.debug("line_trimmed={}".format(line_trimmed))
        if (len(line_trimmed) == 0) or line_trimmed.startswith("#") or line_trimmed.startswith(";"):
            # Empty line or comment. Read the next line.
            continue
        elif line_trimmed.startswith("[") and line_trimmed.endswith("]"):
            # Found a [Section].
            section = line_trimmed[1:len(line_trimmed) - 1]
            logging.debug("Found section: {}".format(section))
            # Start a new dictionary for properties within the section.
            section_props = {}
        else:
            # Possibly a PropertyName=PropertyValue line.
            pos = line_trimmed.find("=")
            if pos < 0:
                # No equals. Ignore and read the next line.
                continue
            property_name = line_trimmed[0:pos].strip()
            property_value = line_trimmed[pos + 1:].strip()
            logging.debug("  {} = {}".format(property_name, property_value))
            # Remove surrounding quotes:
            if property_value.startswith("'") or property_value.startswith('"'):
                property_value = property_value[1:]
            if property_value.endswith("'") or property_value.endswith('"'):
                property_value = property_value[0:len(property_value) - 1]

            # Check special values.
            if property_value == 'PARENT_FOLDER':
                logging.info("Found configuration file special value 'PARENT_FOLDER'.")
                logging.info("  Configuration file path is:")
                logging.info("    {}".format(config_file_path))
                logging.info("    Parent is:")
                logging.info("      {}".format(config_file_path.parent.absolute()))
                property_value = Path(config_file_path).parent.absolute()
            elif property_value == 'PARENT_PARENT_FOLDER':
                logging.info("Found configuration file special value 'PARENT_PARENT_FOLDER'.")
                logging.info("  Configuration file path is:")
                logging.info("    {}".format(config_file_path))
                logging.info("    Parent of parent is:")
                logging.info("      {}".format(config_file_path.parent.parent.absolute()))
                property_value = Path(config_file_path).parent.parent.absolute()

            # Expand the property value:
            # - first expand only using the sections properties, which don't include the section prefix
            # - then expand using all the properties, which include the section prefix
            property_value = expand_config_property(section_props, property_value)
            property_value = expand_config_property(config_dict, property_value)

            if section:
                # In a section so save the section property.
                section_props[property_name] = property_value
                # Save the global property without section in the name.
                config_dict[section + "." + property_name] = property_value
            else:
                # Not in a section so only save the global property without section in the name.
                config_dict[property_name] = property_value

    # Close the input file.
    cfp.close()
