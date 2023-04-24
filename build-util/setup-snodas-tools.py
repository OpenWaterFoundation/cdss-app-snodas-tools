"""
Check and if necessary create new folders for running SNODAS Tools.
This is useful for setting up new SNODAS Tools environments.  To run:

1.  Create a SNODAS Tools root folder where files will be created.
2.  Copy the 'config/SNODAS-Tools-Config.ini' file from another implementation and edit.
3.  Run this script from the SNODAS Tools root folder.
4.  Fix configuration file issues and created other files as instructed.
"""

import argparse
import logging
import os
from pathlib import Path
import tempfile

# Global data.
program_name = "setup-snodas-tools"
program_version = "1.0.0"
program_version_date = "2023-04-20"

# Root folder for SNODAS Tools production files.
root_folder = None

# Processed data folder, under root.
processed_data_folder = None

# Workflow folder, under root.
workflow_folder = None

# Static data folder, under root.
static_data_folder = None

# Supporting functions, alphabetized.

def check_config_file_exists ( config_file_path: Path ) -> int:
    """
    Check that the configuration file exists.
    """
    # Check that the configuration file exists.
    if not config_file_path.exists():
        # Check that this script is being run from a test folder that includes the configuration file.
        logging.error("")
        logging.error("It does not appear that this script is being run from a SNODAS Tools root folder.")
        logging.error("  The configuration file does not exist:")
        logging.error("    {}".format(config_file_path))
        logging.error("  The root folder should have already been created and contain a valid 'config/SNODAS-Tools-Config.ini' file.")
        logging.error("")
        exit(1)
    return 0


def check_processed_data_folder ( config_file_path: Path ) -> None:
    """
    Check that the processed data folder is defined and exists:
    - the global 'processed_data_folder' global variable will be defined
    """
    global processed_data_folder
    processed_data_folder_prop = get_config_property ( config_file_path, "Folders", "processed_data_folder")

    if not processed_data_folder_prop:
        logging.error("SNODAS Tools processed data folder '[Folders].processed_data_folder' is not defined in the configuration file.")
        exit(1)

    # Set the Path representation of the folder.
    processed_data_folder = Path(processed_data_folder_prop)
    logging.info("SNODAS Tools 'processed_data_folder' from configuration:")
    logging.info("  {}".format(processed_data_folder))

    if processed_data_folder.exists():
      logging.info("  SNODAS Tools processed data folder exists:")
      logging.info("    {}".format(processed_data_folder))
    else:
      logging.info("  SNODAS Tools processed data folder does not exist:")
      logging.info("    {}".format(processed_data_folder))
      processed_data_folder.mkdir(parents = True)
      # TODO smalers 2023-04-22 how to check for error?
      #if ?
      #  logging.error("Error creating processed data folder:")
      #  logging.error("  {}".format(processed_data_folder))
      #  exit(1)
      logging.info("    Created it.")

    # Add a .gitignore in the folder since processed files are dynamic.
    create_gitignore_file(processed_data_folder, indent="    ")

    # Handle processing subfolders similarly:
    # - TODO smalers 2022-04-21 could use the following for all setup folders but some benefit from more care
    # - the following are configuration properties for folders that need to be created
    process_data_folders = [
        "download_snodas_tar_folder",       # Step 1.
        "untar_snodas_tif_folder",          # Step 2.
        "clip_proj_snodas_tif_folder",      # Step 3.
        "create_snowcover_tif_folder",      # Step 4.
        "calculate_stats_folder",           # Step 5.
        "output_stats_by_date_folder",      #   Output from step 5.
        "output_stats_by_basin_folder",     #   Output from step 5.
        "timeseries_folder",                # Step 6.
        "timeseries_graph_png_folder"       #   Output from step 6.
    ]

    for folder_prop_name in process_data_folders:
        folder_prop_value = get_config_property ( config_file_path, "Folders", folder_prop_name)

        if not folder_prop_value:
            logging.error("    SNODAS Tools processed data folder '[Folders].{}' is not defined in the configuration file.".format(folder_prop_name))
            exit(1)

        # Set the Path representation of the folder.
        folder_path = Path(folder_prop_value)
        logging.info("    SNODAS Tools output folder '{}' from configuration:".format(folder_prop_name))
        logging.info("      {}".format(folder_path))

        if folder_path.exists():
          logging.info("    SNODAS Tools process output folder exists:")
          logging.info("      {}".format(folder_path))
        else:
          logging.info("    SNODAS Tools process output folder does not exist:")
          logging.info("      {}".format(folder_path))
          folder_path.mkdir(parents = True)
          # TODO smalers 2023-04-22 how to check for error?
          #if ?
          #  logging.error("Error creating processed data folder:")
          #  logging.error("  {}".format(processed_data_folder))
          #  exit(1)
          logging.info("      Created it.")

    return 0


def check_root_folder(config_file_path: Path) -> int:
    """
    Check that the root folder is defined and exists:
    - the global 'root_folder' variable will be set
    """
    # The root_folder is global to the script.
    global root_folder

    # Get the configuration property.
    root_folder_prop=get_config_property(config_file_path, "Folders", "root_folder")

    if not root_folder_prop:
        logging.error("SNODAS Tools root folder '[Folders].root_folder' property is not defined in the configuration file.")
        exit(1)

    # Set the root folder as a Path.
    root_folder = Path(root_folder_prop)

    logging.info("SNODAS Tools 'root_folder' from configuration:")
    logging.info("  {}".format(root_folder))

    # The current folder should match the root folder.
    if root_folder != current_folder:
        logging.error("  SNODAS Tools configuration 'root_folder' does not match the current folder:")
        logging.error("     configuration: {}".format(root_folder))
        logging.error("           current: {}".format(current_folder))
        exit(1)

    # Success.
    return 0


def check_static_data_folder ( config_file_path: Path ) -> None:
    """
    Check that the static data folder is defined and exists:
    - the global 'static_data_folder' global variable will be defined
    """
    global static_data_folder
    static_data_folder_prop = get_config_property ( config_file_path, "Folders", "static_data_folder")

    if not static_data_folder_prop:
        logging.error("SNODAS Tools static data folder '[Folders].static_data_folder' is not defined in the configuration file.")
        exit(1)

    # Set the Path representation of the folder.
    static_data_folder = Path(static_data_folder_prop)
    logging.info("SNODAS Tools 'static_data_folder' from configuration:")
    logging.info("  {}".format(static_data_folder))

    if static_data_folder.exists():
      logging.info("  SNODAS Tools static data folder exists:")
      logging.info("    {}".format(static_data_folder))
    else:
      logging.info("  SNODAS Tools static data folder does not exist:")
      logging.info("    {}".format(static_data_folder))
      static_data_folder.mkdir(parents = True)
      # TODO smalers 2023-04-22 how to check for error?
      #if ?
      #  logging.error("Error creating static data folder:")
      #  logging.error("  {}".format(static_data_folder))
      #  exit(1)
      logging.info("    Created it.")

    return 0


def check_workflow_folder ( config_file_path: Path ) -> None:
    """
    Check that the workflow folder is defined and exists:
    - the global 'workflow_folder' global variable will be defined
    """
    global workflow_folder
    workflow_folder_prop = get_config_property ( config_file_path, "Folders", "workflow_folder")

    if not workflow_folder_prop:
        logging.error("SNODAS Tools workflow folder '[Folders].workflow_folder' is not defined in the configuration file.")
        exit(1)

    # Set the Path representation of the folder.
    workflow_folder = Path(workflow_folder_prop)
    logging.info("SNODAS Tools 'workflow_folder' from configuration:")
    logging.info("  {}".format(workflow_folder))

    if workflow_folder.exists():
      logging.info("  SNODAS Tools workflow folder exists:")
      logging.info("    {}".format(workflow_folder))
    else:
      logging.info("  SNODAS Tools workflow folder does not exist:")
      logging.info("    {}".format(workflow_folder))
      workflow_folder.mkdir(parents = True)
      # TODO smalers 2023-04-22 how to check for error?
      #if ?
      #  logging.error("Error creating processed data folder:")
      #  logging.error("  {}".format(workflow_folder))
      #  exit(1)
      logging.info("    Created it.")

    # Handle processing subfolders similarly:
    # - TODO smalers 2022-04-21 could use the following for all setup folders but some benefit from more care
    # - the following are configuration properties for folders that need to be created
    workflow_folders = [
        "timeseries_products_workflow_folder"   # TSTool command file to create graph images.
    ]

    for folder_prop_name in workflow_folders:
        folder_prop_value = get_config_property ( config_file_path, "Folders", folder_prop_name)

        if not folder_prop_value:
            logging.error("    SNODAS Tools workflow folder '[Folders].{}' is not defined in the configuration file.".format(folder_prop_name))
            exit(1)

        # Set the Path representation of the folder.
        folder_path = Path(folder_prop_value)
        logging.info("    SNODAS Tools workflow folder '{}' from configuration:".format(folder_prop_name))
        logging.info("      {}".format(folder_path))

        if folder_path.exists():
          logging.info("    SNODAS Tools workflow folder exists:")
          logging.info("      {}".format(folder_path))
        else:
          logging.info("    SNODAS Tools workflow folder does not exist:")
          logging.info("      {}".format(folder_path))
          folder_path.mkdir(parents = True)
          # TODO smalers 2023-04-22 how to check for error?
          #if ?
          #  logging.error("Error creating processed data folder:")
          #  logging.error("  {}".format(workflow_folder))
          #  exit(1)
          logging.info("      Created it.")

    # Make sure that the time series workflow folder contains the TSTool command file to process graphs.
    property_name = "tstool_create_snodas_graphs_command_file"
    command_file_prop = get_config_property ( config_file_path, "ProgramInstall", property_name)

    if not command_file_prop:
        logging.error("SNODAS Tools TSTool command file '[ProgramInstall].{}' is not defined in the configuration file.".format(property_name))
        exit(1)

    logging.info("SNODAS Tools '{}' from configuration:".format(property_name))
    logging.info("  {}".format(command_file_prop))

    tstool_command_file = Path(command_file_prop)
    if tstool_command_file.exists():
      logging.info("  SNODAS Tools TSTool command file exists:")
      logging.info("    {}".format(tstool_command_file))
    else:
      logging.error("  SNODAS Tools TSTool command file does not exist:")
      logging.error("    {}".format(tstool_command_file))
      logging.error("    Need to create it with supporting files.")
      exit(1)

    return 0


def create_gitignore_file(folder: Path, indent: str = "") -> None:
    """
    Create a .gitignore file in the folder.

    Args:
        folder - the folder in which to create the .gitignore file
        indent - spaces to indent logging messages
    """
    gitignore_path = folder / ".gitignore"
    if not gitignore_path.exists():
        # File does not exist so create it.
        fp = open(gitignore_path, 'w')
        fp.write("# Control which files are ignored in the repository:\n")
        fp.write("# - keep this file\n")
        fp.write("# - keep the README.md file\n")
        fp.write("/*\n")
        fp.write("!.gitignore\n")
        fp.write("!README.md*\n")
        logging.info(indent + "Created .gitignore file:")
        logging.info(indent + "  {}".format(gitignore_path))
        fp.close()



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
                continue;
            else:
                # Make sure that the value is a string.
                dict_property_value = str(dict_property_value);
            expanded_property_value = expanded_property_value.replace("${" + property_name + "}", dict_property_value);
    return expanded_property_value


def get_config_property(config_file_path: Path, section_req: str, property_name_req: str) -> str or None:
    """
    Look up a property value as a string for the configuration file.
    """
    cfp = open(config_file_path, 'r')
    section = None
    section_props = None
    property_value = None
    property_value_found = None
    # A dictionary of all properties, with section, after expansion in case need to expand further.
    all_props = {}

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
                continue;
            property_name = line_trimmed[0:pos].strip()
            property_value = line_trimmed[pos + 1:].strip()
            logging.debug("  {} = {}".format(property_name, property_value))
            # Remove surrounding quotes:
            if property_value.startswith("'") or property_value.startswith('"'):
                property_value = property_value[1:]
            if property_value.endswith("'") or property_value.endswith('"'):
                property_value = property_value[0:len(propery_value) - 1]

            # Expand the property value:
            # - first expand only using the sections properties, which don't include the section prefix
            # - then expand using all the properties, which include the section prefix
            property_value = expand_config_property(section_props, property_value)
            property_value = expand_config_property(all_props, property_value)

            if section_req == section and property_name_req == property_name:
                # Found the requested property:
                property_value_found = property_value
                break

            if section:
                # In a section so save the section property and also in the full dictionary.
                section_props[property_name] = property_value
                all_props[section + "." + property_name] = property_value
            else:
                # Not in a section so only save the global property without section in the name.
                all_props[property_name] = property_value

    # Close the input file.
    cfp.close()

    # No property was found.
    return property_value_found



def print_version() -> None:
    """
    Print the program version.
    """
    nl = "\n"
    print(nl
    + program_name + " version " + program_version + " " + program_version_date + nl
    + nl
    +  "SNODAS Tools" + nl
    +  "SNODAS Tools is part of Colorado's Decision Support Systems" + nl
    +  "and has been enhanced by the Open Water Foundation." + nl
    +  "Copyright (C) 1994-2023 Colorado Department of Natural Resources" + nl
    +  "and the Open Water Foundation." + nl
    +  "" + nl
    +  "SNODAS Tools is free software:  you can redistribute it and/or modify" + nl
    +  "    it under the terms of the GNU General Public License as published by" + nl
    +  "    the Free Software Foundation, either version 3 of the License, or" + nl
    +  "    (at your option) any later version." + nl
    +  "" + nl
    +  "    SNODAS Tools is distributed in the hope that it will be useful," + nl
    +  "    but WITHOUT ANY WARRANTY; without even the implied warranty of" + nl
    +  "    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the" + nl
    +  "    GNU General Public License for more details." + nl
    +  "" + nl
    +  "    You should have received a copy of the GNU General Public License" + nl
    +  "    along with SNODAS Tools.  If not, see <https://www.gnu.org/licenses/>." + nl
    + nl)


if __name__ == '__main__':
    """
    Entry point for the this program.
    """
    debug = False
    #if debug:
    #    print_env()

    # Get main folder locations.
    current_folder = Path(os.getcwd())
    config_file_path = current_folder / "config" / "SNODAS-Tools-Config.ini"

    # Parse the command line parameters:
    # - the -h and --help arguments are automatically included so don't need to add below
    # - the default action is "store" which will save a variable with the same name as the option
    # - the --version option has special behavior, as documented in the argparse module documentation,
    #   but use a custom print_version() function so can include the license
    parser = argparse.ArgumentParser(description='setup-snodas-tools')

    # Handle the --debug command line parameter.
    parser.add_argument("--debug", help="Turn on debug.", action="store_true")

    # Handle the --version command line parameter.
    parser.add_argument("--version", help="Print program version.", action="store_true")

    # The following will result in exit if unknown argument.
    # args = parser.parse_args()
    args, unknown_args = parser.parse_known_args()

    if args.debug:
        # Turn debug on.
        debug = True

    if args.version:
        # Print the version.
        print_version()

    # Initialize basic logging:
    # - logging is just to the console so call logging.info(), etc.
    # - if debug is on, will print, otherwise the default is to include only up to INFO
    if debug:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    # Print important information.
    logging.info("")
    logging.info("Running in folder:")
    logging.info("  {}".format(current_folder))
    logging.info("Configuration file (based on the run folder):")
    logging.info("  {}".format(config_file_path))

    # Check that the configuration file exists.
    check_config_file_exists(config_file_path)

    # Check the root folder.
    check_root_folder(config_file_path)

    # Check the static data folder.
    check_static_data_folder(config_file_path)

    # Check the workflow folder.
    check_workflow_folder(config_file_path)

    # Check the processed data folder.
    check_processed_data_folder(config_file_path)

    # Application exit.
    exit(0)
