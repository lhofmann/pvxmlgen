from hypothesis import given
import hypothesis.strategies as st
import os
import pvxmlgen
from pkg_resources import parse_version


def test_doxygen():
    assert pvxmlgen.doxygen_version() >= parse_version(pvxmlgen.core.DOXYGEN_MIN_VERSION)


def test_parsing():
    test_dir = os.path.dirname(os.path.realpath(__file__))

    nodes = pvxmlgen.core.doxygen_execute([os.path.join(test_dir, 'testcases', 'minimal.h')])
    defs = pvxmlgen.core.doxygen_parse_classes(nodes)
    assert 'vtkMinimal' in defs.keys()
    assert pvxmlgen.core.paraview_class_xml('vtkMinimal', defs['vtkMinimal'])


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
