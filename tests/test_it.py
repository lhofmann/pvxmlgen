import os
import pvxmlgen
import xml.etree.ElementTree as ET
from glob import glob
import difflib


class ComparableElement(object):
    def __init__(self, element):
        self.element = element
        pvxmlgen.indent(self.element)

    def xml_diff(self, other, differ=difflib.context_diff):
        left_str = ET.tostring(self.element, encoding='utf-8').decode('utf-8')
        right_str = ET.tostring(other.element, encoding='utf-8').decode('utf-8')

        left_str = left_str.splitlines(keepends=True)
        right_str = right_str.splitlines(keepends=True)

        return list(differ(left_str, right_str))

    def __eq__(self, other):
        return len(self.xml_diff(other)) == 0


def test_parsing():
    test_dir = os.path.dirname(os.path.realpath(__file__))
    test_dir = os.path.join(test_dir, 'testcases')

    for filename in glob(os.path.join(test_dir, '*.h')):
        with open(filename, 'r') as f:
            contents = f.read()
        xml = pvxmlgen.generate_xml(contents)
        ground_truth = ET.parse(filename + '.xml').getroot()
        assert ComparableElement(xml) == ComparableElement(ground_truth)


def test_cpp_parsing():
    def output(type_, name, num_elements, defaults):
        return {
            'name': name,
            'type': type_,
            'number_of_elements': num_elements,
            'default_values': defaults
        }

    test_cases = [
        ('  double   x   = 3;', output('double', 'x', 1, 3)),
        ('  double   x   { 3 } ;', output('double', 'x', 1, 3)),
        ('  long int  my_var[5]   { 3, 4, 5, 6, 7 } ;', output('long int', 'my_var', 5, (3, 4, 5, 6, 7))),
        ('  bool b = false;', output('bool', 'b', 1, False)),
        (' \t\t bool \tvar\t  {true } ;', output('bool', 'var', 1, True)),
        ('  float fs[3] = {1.0, 2, 3.0};', output('float', 'fs', 3, (1.0, 2, 3.0))),
        (' class X', {'class': 'X'}),
        (' class myclass : public Y, private Z', {'class': 'myclass'}),
        (' class __attribute__ ((visibility("default"))) myclass {', {'class': 'myclass'}),
        ('  class some_cls : public other {  ', {'class': 'some_cls'}),
    ]

    for string, result in test_cases:
        assert pvxmlgen.parse_declaration(string) == result
