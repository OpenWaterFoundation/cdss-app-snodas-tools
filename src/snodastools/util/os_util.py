"""
This module provides utility functions for operating system information.
"""

import os


def is_linux_os () -> bool:
    """
    Indicate whether the operating system is Linux.

    Returns:  True if Linux operating system, False if not.
    """
    if os.name.upper() == 'POSIX':
        return True
    else:
        return False
