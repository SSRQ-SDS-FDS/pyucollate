"""utilities for formatting the datastructures used in pyucollate.

Useful mostly for debugging output.
"""


from collections.abc import Iterable


def hexstrings2int(hexstrings: Iterable[str]) -> list[int]:
    """List of hex strings to list of integers.

    >>> hexstrings2int(["0000", "0001", "FFFF"])
    [0, 1, 65535]
    """
    return [int(hexstring, 16) for hexstring in hexstrings]


def int2hexstrings(numbers: Iterable[int]) -> list[str]:
    """List of integers to list of 4-digit hex strings.

    >>> int2hexstrings([0, 1, 65535])
    ['0000', '0001', 'FFFF']
    """
    return [str(f"{n:04X}") for n in numbers]


def format_collation_elements(collation_elements: list[list[int]] | None) -> str | None:
    """Format collation element array (list of list of integer weights).

    >>> str(format_collation_elements([[1, 2, 3], [4, 5]]))
    '[0001.0002.0003], [0004.0005]'
    >>> format_collation_elements(None)
    """
    if collation_elements is None:
        return None

    return ", ".join(
        "[" + ".".join(int2hexstrings(collation_element)) + "]"
        for collation_element in collation_elements
    )


def format_sort_key(sort_key: list[int]) -> str:
    """Format sort key (list of integers) with | level boundaries
    >>> str(format_sort_key([1, 0, 65535]))
    '0001 | FFFF'.
    """
    return " ".join((f"{x:04X}" if x else "|") for x in sort_key)
