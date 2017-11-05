import sys
from ._version import __version__


def main(argv=sys.argv[1:]):
    print("pvxmlgen v{}".format(__version__))

if __name__ == "__main__":
    main()
