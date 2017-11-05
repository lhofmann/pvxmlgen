import sys
from ._version import __version__
from .core import doxygen_version


def main(argv=sys.argv[1:]):
    print("pvxmlgen version {}".format(__version__))
    doxygen = doxygen_version()
    if not doxygen:
        sys.exit(1)
    print("doxygen version {}".format(doxygen))


if __name__ == "__main__":
    main()
