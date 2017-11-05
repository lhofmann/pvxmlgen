import pvxmlgen


def test_doxygen():
    assert pvxmlgen.doxygen_version() is not None
