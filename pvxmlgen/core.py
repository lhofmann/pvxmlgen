from pkg_resources import parse_version
from subprocess import check_output

DOXYGEN_EXECUTABLE = 'doxygen'
DOXYGEN_MIN_VERSION = '1.8'


def doxygen_version():
    try:
        doxygen_version = check_output([DOXYGEN_EXECUTABLE, "-v"]).decode('utf-8')
    except OSError:
        return None
    doxygen_version = parse_version(doxygen_version)
    if doxygen_version < parse_version(DOXYGEN_MIN_VERSION):
        return None
    return doxygen_version
