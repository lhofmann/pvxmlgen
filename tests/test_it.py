from hypothesis import given
import hypothesis.strategies as st
import os
import pvxmlgen
from pkg_resources import parse_version
import xml.etree.ElementTree as ET
from functools import cmp_to_key


def test_doxygen():
    assert pvxmlgen.doxygen_version() >= parse_version(pvxmlgen.core.DOXYGEN_MIN_VERSION)


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

    nodes = pvxmlgen.core.doxygen_execute([os.path.join(test_dir, 'testcases', 'minimal.h')])
    defs = pvxmlgen.core.doxygen_parse_classes(nodes)
    assert 'vtkMinimal' in defs.keys()
    class_xml = pvxmlgen.core.paraview_class_xml('vtkMinimal', defs['vtkMinimal'])
    assert class_xml
    class_xml_groundtruth = ET.parse(os.path.join(test_dir, 'testcases', 'minimal.out.xml')).getroot()
    # import pdb
    # pdb.set_trace()
    assert cmp_el(class_xml, class_xml_groundtruth) == 0


def test_argsstring():
    passing = ['[{}]', '[ {}]', '[{}  ]', ' [ {} ] ']
    for s in passing:
        assert pvxmlgen.core.parse_argsstring(s.format(1)) == 1
        assert pvxmlgen.core.parse_argsstring(s.format(3)) == 3
        assert pvxmlgen.core.parse_argsstring(s.format(10)) == 10
        assert pvxmlgen.core.parse_argsstring(s.format('010')) == 10
    failing = ['[-{}]', '[ {},]', '[{} 1]', ' [ {} + 2 ] ', '[ {}', '{}]', '{} ]']
    for s in failing:
        assert pvxmlgen.core.parse_argsstring(s.format(1)) is None
        assert pvxmlgen.core.parse_argsstring(s.format(3)) is None
        assert pvxmlgen.core.parse_argsstring(s.format(10)) is None
        assert pvxmlgen.core.parse_argsstring(s.format('010')) is None

    assert pvxmlgen.core.parse_argsstring('[0]') is None
    assert pvxmlgen.core.parse_argsstring('[1,2,3]') is None


@given(st.integers())
def test_int_initializer(n):
    passing = ['={}', '={{{}}}', '{{{}}}', ' =  {}  ', '  {{{}  }}', '    = {{ {}  }}']
    for s in passing:
        assert pvxmlgen.core.parse_initializer(s.format(n), 'int', 1) == str(n)
    passing = ['={{{},{}}}', '{{{},{}}}', '  {{{}  , {}}}', '    = {{ {},{} }}']
    for s in passing:
        assert pvxmlgen.core.parse_initializer(s.format(n, 3*n), 'int', 2) == str(n) + ' ' + str(3*n)
    failing = ['= {} ', '{},{}}}', '={{{},{}', '    {},{} ']
    for s in failing:
        assert pvxmlgen.core.parse_initializer(s.format(n, 3*n), 'int', 2) is None
