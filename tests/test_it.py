import os
import pvxmlgen
import xml.etree.ElementTree as ET
from functools import cmp_to_key
from glob import glob


# from https://stackoverflow.com/a/18488548
def cmp_el(a, b):
    if a.tag < b.tag:
        return -1
    elif a.tag > b.tag:
        return 1

    # compare attributes
    aitems = list(a.attrib.items())
    aitems.sort()
    bitems = list(b.attrib.items())
    bitems.sort()
    if aitems < bitems:
        return -1
    elif aitems > bitems:
        return 1

    # compare child nodes
    achildren = list(a)
    achildren.sort(key=cmp_to_key(cmp_el))
    bchildren = list(b)
    bchildren.sort(key=cmp_to_key(cmp_el))

    for achild, bchild in zip(achildren, bchildren):
        cmpval = cmp_el(achild, bchild)
        if cmpval < 0:
            return -1
        elif cmpval > 0:
            return 1

    # must be equal
    return 0


def test_parsing():
    test_dir = os.path.dirname(os.path.realpath(__file__))
    test_dir = os.path.join(test_dir, 'testcases')

    for filename in glob(os.path.join(test_dir, '*.h')):
        with open(filename, 'r') as f:
            contents = f.read()
        xml = pvxmlgen.generate_xml(contents)
        ground_truth = ET.parse(filename + '.xml').getroot()
        assert cmp_el(xml, ground_truth) == 0
