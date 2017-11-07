import sys
import os.path
from pkg_resources import parse_version
from ._version import __version__
from .core import doxygen_version, DOXYGEN_MIN_VERSION, doxygen_execute, doxygen_parse_classes, paraview_class_xml, merge_class_xml
import argparse
import xml.etree.ElementTree as ET


def indent(elem, indentation=4 * ' ', level=0):
    i = '\n' + level * indentation
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + indentation
        for e in elem:
            indent(e, indentation, level+1)
            if not e.tail or not e.tail.strip():
                e.tail = i + indentation
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
    if len(elem.attrib) > 2:
        elem.attrib = {(i + indentation + k): v for k, v in elem.attrib.items()}


def main():
    parser = argparse.ArgumentParser(prog='pvxmlgen')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(__version__))
    parser.add_argument('files', metavar='<input>', type=str, nargs='+', help='input C++ header file')
    parser.add_argument('-o',    metavar='<output>', type=str, required=True, help='output XML file')
    args = parser.parse_args()

    doxygen = doxygen_version()
    if not doxygen:
        print('Doxygen not found.')
        sys.exit(1)
    if parse_version(DOXYGEN_MIN_VERSION) > doxygen:
        print('Unsupported doxygen version detected: {}'.format(doxygen))
        sys.exit(1)

    output_xml = None
    if (args.o != '-') and os.path.isfile(args.o):
        try:
            output_xml = ET.parse(args.o).getroot()
            if output_xml.tag != 'ServerManagerConfiguration':
                raise ET.ParseError()
        except ET.ParseError:
            print('Output file {} is not a valid server manager xml file.'.format(args.o))
            sys.exit(1)

    nodes = doxygen_execute(args.files)
    defs = doxygen_parse_classes(nodes)
    if not defs:
        print('No classes to process.')
        sys.exit(1)

    for class_name, class_defs in defs.items():
        class_xml = paraview_class_xml(class_name, class_defs)
        if class_xml is None:
            continue
        if output_xml is None:
            output_xml = class_xml
        else:
            merge_class_xml(class_xml, output_xml)

    if output_xml is None:
        print('Got nothing to output.')
        sys.exit(1)

    indent(output_xml)
    output_string = ET.tostring(output_xml, encoding='utf-8').decode('utf-8')

    if args.o == '-':
        print(output_string)
    else:
        with open(args.o, 'w', encoding='utf-8') as f:
            f.write(output_string)


if __name__ == "__main__":
    main()
