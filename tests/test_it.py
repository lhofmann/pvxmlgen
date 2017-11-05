from subprocess import check_output


def test_doxygen():
    doxygen_version = check_output(["doxygen", "-v"]).decode('utf-8')
    doxygen_version = doxygen_version.split('.')
    assert len(doxygen_version) == 3
    assert int(doxygen_version[0]) == 1
