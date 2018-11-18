from .test_it import ComparableElement
import difflib

def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, ComparableElement) and isinstance(right, ComparableElement) and op == "==":
        diff = ''.join(left.xml_diff(right, differ=difflib.ndiff)).splitlines()
        return ['Comparing XML trees'] + diff
