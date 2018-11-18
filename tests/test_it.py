import os
import pvxmlgen
import xml.etree.ElementTree as ET
from functools import cmp_to_key
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
