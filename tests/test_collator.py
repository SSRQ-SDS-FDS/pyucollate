from pathlib import Path

import pytest
from pyucollate import Collator
from pyucollate.collator import (
    Collator_5_2_0,
    Collator_6_3_0,
    Collator_8_0_0,
    Collator_9_0_0,
    Collator_10_0_0,
)


def load_collation_test(version: str) -> list[str]:
    test_file = (
        Path(__file__).parent / "collation_tests" / version / "CollationTest_NON_IGNORABLE.txt"
    )
    with test_file.open() as f:
        return f.readlines()


@pytest.fixture()
def collator():
    return Collator()


@pytest.mark.parametrize(
    ("input_strings", "expected_result"),
    [
        (["cafe", "caff", "café"], ["cafe", "café", "caff"]),
        (["Apfelbaum", "Äpfel", "Apfelsaft"], ["Äpfel", "Apfelbaum", "Apfelsaft"]),
    ],
)
def test_sorting_with_simple_examples(
    collator: Collator, input_strings: list[str], expected_result: list[str]
):
    sorted_strings = collator.sort(input_strings)
    assert sorted_strings == expected_result


@pytest.mark.parametrize(
    "c",
    [
        Collator_5_2_0(),
        Collator_6_3_0(),
        Collator_8_0_0(),
        Collator_9_0_0(),
        Collator_10_0_0(),
        Collator(),
    ],
)
def test_collator_against_unicode_full_test(c: Collator):
    test_lines = load_collation_test(c.UCA_VERSION)

    prev_sort_key: None | tuple[int, ...] = None

    for _, line in enumerate(test_lines):
        points = line.split("#", 1)[0].split(";", 1)[0].strip().split()

        if points:
            test_string = "".join(chr(int(point, 16)) for point in points)
            test_string_sort_key = c.sort_key(test_string)
            if prev_sort_key is not None:
                assert prev_sort_key <= test_string_sort_key
            prev_sort_key = test_string_sort_key
