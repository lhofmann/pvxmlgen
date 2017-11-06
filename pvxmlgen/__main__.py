import sys
from pkg_resources import parse_version
from ._version import __version__
from .core import doxygen_version, DOXYGEN_MIN_VERSION


def main(argv=sys.argv[1:]):
    print('pvxmlgen version {}'.format(__version__))
    doxygen = doxygen_version()
    if not doxygen:
        print('Doxygen not found.')
        sys.exit(1)
    if parse_version(DOXYGEN_MIN_VERSION) < doxygen:
        print('Unsupported doxygen version detected: {}'.format(doxygen))
        sys.exit(1)
    print('doxygen version {}'.format(doxygen))


if __name__ == "__main__":
    main()
