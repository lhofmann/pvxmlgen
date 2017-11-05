import os
import pvxmlgen


def test_doxygen():
    assert pvxmlgen.doxygen_version() is not None


def test_parsing():
    test_dir = os.path.dirname(os.path.realpath(__file__))

    nodes = pvxmlgen.core.doxygen_execute([os.path.join(test_dir, 'testcases', 'minimal.h')])
    defs = pvxmlgen.core.doxygen_parse_classes(nodes)
    assert 'vtkMinimal' in defs.keys()
