import pytest
from pyucollate.utils import (
    format_collation_elements,
    format_sort_key,
    hexstrings2int,
    int2hexstrings,
)


@pytest.mark.parametrize(
    ("input_strings", "expected_result"), [(["0000", "0001", "FFFF"], [0, 1, 65535])]
)
def test_hexstrings2int(input_strings, expected_result):
    result = hexstrings2int(input_strings)
    assert result == expected_result


@pytest.mark.parametrize(
    ("input_ints", "expected_result"), [([0, 1, 65535], ["0000", "0001", "FFFF"])]
)
def test_int2hexstrings(input_ints, expected_result):
    result = int2hexstrings(input_ints)
    assert result == expected_result


@pytest.mark.parametrize(
    ("input_elements", "expected_result"),
    [([[1, 2, 3], [4, 5]], "[0001.0002.0003], [0004.0005]"), (None, None)],
)
def test_format_collation_elements(input_elements, expected_result):
    result = format_collation_elements(input_elements)
    assert result == expected_result


@pytest.mark.parametrize(("input_ints", "expected_result"), [([0, 1, 65535], "| 0001 FFFF")])
def test_format_sort_key(input_ints, expected_result):
    result = format_sort_key(input_ints)
    assert result == expected_result
