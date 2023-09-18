import os.path
import re
import sys
import unicodedata
from collections.abc import Iterable
from pathlib import Path
from typing import ClassVar

from pyucollate.trie import Trie
from pyucollate.utils import hexstrings2int

COLL_ELEMENT_PATTERN = re.compile(
    r"""
    \[
    (?:\*|\.)
    ([0-9A-Fa-f]{4})
    \.
    ([0-9A-Fa-f]{4})
    \.
    ([0-9A-Fa-f]{4})
    (?:\.[0-9A-Fa-f]{4,5})?
\]
""",
    re.X,
)


def sort_key_from_collation_elements(collation_elements: list[list[int]]) -> tuple[int, ...]:
    """Convert a list of collation elements to a sort key.

    Args:
    ----
        collation_elements (list[list[int]]): The collation elements to convert.

    Returns:
    -------
        tuple[int, ...]: The sort key.
    """
    sort_key = [
        ce_l
        for level in range(4)
        for element in collation_elements
        if len(element) > level
        for ce_l in [0, element[level]]
        if ce_l
    ]

    return tuple(sort_key)


class BaseCollator:
    """Base class for collators."""

    CJK_IDEOGRAPHS_8_0_0: ClassVar[bool] = False
    CJK_IDEOGRAPHS_10_0_0: ClassVar[bool] = False
    CJK_IDEOGRAPHS_EXT_A: ClassVar[bool] = True  # 3.0
    CJK_IDEOGRAPHS_EXT_B: ClassVar[bool] = True  # 3.1
    CJK_IDEOGRAPHS_EXT_C: ClassVar[bool] = True  # 5.2 (supposedly)
    CJK_IDEOGRAPHS_EXT_D: ClassVar[bool] = True  # 6.0
    CJK_IDEOGRAPHS_EXT_E: ClassVar[bool] = False  # 8.0
    CJK_IDEOGRAPHS_EXT_F: ClassVar[bool] = False  # 10.0

    table: Trie
    implicit_weights: list[list[int]]

    def __init__(self, collation_table: str | Path) -> None:
        """Initialize the collator.

        Args:
        ----
            collation_table (str | Path): The path to the collation table to use.
                If a string is passed, it is assumed to be the name of a table
                in the tables directory.
        """
        if isinstance(collation_table, str):
            file = os.path.join(
                os.path.dirname(__file__), "tables", f"allkeys-{collation_table}.txt"
            )
        else:
            file = str(collation_table.absolute())
        self.table = Trie()
        self.implicit_weights = []
        self.load(file)

    def load(self, filename: str) -> None:
        """Load a collation table from a file.

        Args:
        ----
            filename (str): The path to the collation table to use.
        """
        with open(filename) as keys_file:
            for source_line in keys_file:
                line = source_line.split("#", 1)[0].rstrip()

                if not line or line.startswith("@version"):
                    continue

                if line.startswith("@implicitweights"):
                    ch_range, base = line[len("@implicitweights") :].split(";")
                    range_start, range_end = ch_range.split("..")
                    self.implicit_weights.append(
                        [int(range_start, 16), int(range_end, 16), int(base, 16)]
                    )
                    continue

                a, b = line.split(";", 1)
                char_list = hexstrings2int(a.split())
                coll_elements = []
                for x in COLL_ELEMENT_PATTERN.finditer(b.strip()):
                    weights = x.groups()
                    coll_elements.append(hexstrings2int(weights))
                self.table.add(char_list, coll_elements)

    def collation_elements(self, normalized_string: str) -> list[list[int]]:
        """ToDo: Add docstring and refactor this method."""
        collation_elements = []

        lookup_key = self.build_lookup_key(normalized_string)
        while lookup_key:
            S, value, lookup_key = self.table.find_prefix(lookup_key)

            # handle non-starters

            last_class = None
            for i, C in enumerate(lookup_key):
                combining_class = unicodedata.combining(chr(C))
                if combining_class == 0 or combining_class == last_class:
                    break
                last_class = combining_class
                # C is a non-starter that is not blocked from S
                x, y, z = self.table.find_prefix([*S, C])
                if z == [] and y is not None:
                    lookup_key = lookup_key[:i] + lookup_key[i + 1 :]
                    value = y
                    break  # ???

            if not value:
                codepoint = lookup_key.pop(0)
                value = self.implicit_weight(codepoint)

            collation_elements.extend(value)

        return collation_elements

    def sort_key(self, string: str) -> tuple[int, ...]:
        """Calculate the sort key for a string.

        Args:
        ----
            string (str): The string to calculate the sort key for.

        Returns:
        -------
            tuple[int, ...]: The sort key.
        """
        normalized_string = unicodedata.normalize("NFD", string)
        collation_elements = self.collation_elements(normalized_string)
        return sort_key_from_collation_elements(collation_elements)

    def sort(self, values: Iterable[str]) -> list[str]:
        """Sort a list of strings. The strings are sorted according to the Unicode Collation Algorithm.

        This is just a convenience method that calls `sort_key` on each string and then sorts the
        strings according to the sort keys.

        Args:
        ----
            values (Iterable[str]): The strings to sort.

        Returns:
        -------
            list[str]: The sorted strings.
        """
        return sorted(values, key=self.sort_key)

    def implicit_weight(self, cp: int) -> list[list[int]]:
        """Calculate the implicit weight for a codepoint.

        Args:
        ----
            cp (int): The codepoint to calculate the implicit weight for.

        Returns:
        -------
            list[list[int]]: The implicit weight.
        """
        if (unicodedata.category(chr(cp)) != "Cn") and (
            0x4E00 <= cp <= 0x9FCC  # noqa: PLR2004
            or (self.CJK_IDEOGRAPHS_8_0_0 and 0x9FCD <= cp <= 0x9FD5)  # noqa: PLR2004
            or (self.CJK_IDEOGRAPHS_10_0_0 and 0x9FD6 <= cp <= 0x9FEA)  # noqa: PLR2004
            or cp
            in [
                0xFA0E,
                0xFA0F,
                0xFA11,
                0xFA13,
                0xFA14,
                0xFA1F,
                0xFA21,
                0xFA23,
                0xFA24,
                0xFA27,
                0xFA28,
                0xFA29,
            ]
        ):
            base = 0xFB40
            aaaa = base + (cp >> 15)
            bbbb = (cp & 0x7FFF) | 0x8000
        elif (unicodedata.category(chr(cp)) != "Cn") and (
            (self.CJK_IDEOGRAPHS_EXT_A and 0x3400 <= cp <= 0x4DB5)  # noqa: PLR2004
            or (self.CJK_IDEOGRAPHS_EXT_B and 0x20000 <= cp <= 0x2A6D6)  # noqa: PLR2004
            or (self.CJK_IDEOGRAPHS_EXT_C and 0x2A700 <= cp <= 0x2B734)  # noqa: PLR2004
            or (self.CJK_IDEOGRAPHS_EXT_D and 0x2B740 <= cp <= 0x2B81D)  # noqa: PLR2004
            or (self.CJK_IDEOGRAPHS_EXT_E and 0x2B820 <= cp <= 0x2CEAF)  # noqa: PLR2004
            or (self.CJK_IDEOGRAPHS_EXT_F and 0x2CEB0 <= cp <= 0x2EBE0)  # noqa: PLR2004
        ):
            base = 0xFB80
            aaaa = base + (cp >> 15)
            bbbb = (cp & 0x7FFF) | 0x8000
        else:
            base = 0xFBC0
            aaaa = base + (cp >> 15)
            bbbb = (cp & 0x7FFF) | 0x8000

            for start, end, base in self.implicit_weights:
                if start <= cp <= end:
                    aaaa = base
                    bbbb = (cp - start) | 0x8000
                    break

        return [[aaaa, 0x0020, 0x002], [bbbb, 0x0000, 0x0000]]

    def build_lookup_key(self, text: str) -> list[int]:
        """Build a lookup key for the trie.

        Args:
        ----
            text (str): The text to build the lookup key for.

        Returns:
        -------
            list[int]: The lookup key.
        """
        return [ord(ch) for ch in text]


class Collator_6_3_0(BaseCollator):
    UCA_VERSION: ClassVar[str] = "6.3.0"

    def __init__(self) -> None:
        super().__init__(collation_table="6.3.0")


class Collator_8_0_0(BaseCollator):
    UCA_VERSION: ClassVar[str] = "8.0.0"
    CJK_IDEOGRAPHS_8_0_0: ClassVar[bool] = True
    CJK_IDEOGRAPHS_EXT_E: ClassVar[bool] = True

    def __init__(self) -> None:
        super().__init__(collation_table="8.0.0")


class Collator_9_0_0(BaseCollator):
    UCA_VERSION: ClassVar[str] = "9.0.0"
    CJK_IDEOGRAPHS_8_0_0: ClassVar[bool] = True
    CJK_IDEOGRAPHS_EXT_E: ClassVar[bool] = True

    def __init__(self) -> None:
        super().__init__(collation_table="9.0.0")


class Collator_10_0_0(BaseCollator):
    UCA_VERSION: ClassVar[str] = "10.0.0"
    CJK_IDEOGRAPHS_8_0_0: ClassVar[bool] = True
    CJK_IDEOGRAPHS_10_0_0: ClassVar[bool] = True
    CJK_IDEOGRAPHS_EXT_E: ClassVar[bool] = True
    CJK_IDEOGRAPHS_EXT_F: ClassVar[bool] = True

    def __init__(self) -> None:
        super().__init__(collation_table="10.0.0")


class Collator_5_2_0(BaseCollator):
    UCA_VERSION: ClassVar[str] = "5.2.0"
    # Supposedly, extension C *was* introduced in 5.2.0, but the tests show
    # otherwise. Treat the tests as king.
    CJK_IDEOGRAPHS_EXT_C: ClassVar[bool] = False
    CJK_IDEOGRAPHS_EXT_D: ClassVar[bool] = False

    non_char_code_points: list[int]

    def __init__(self) -> None:
        self.non_char_code_points = []
        for i in range(17):
            base = i << 16
            self.non_char_code_points.append(base + 0xFFFE)
            self.non_char_code_points.append(base + 0xFFFF)
        for i in range(32):
            self.non_char_code_points.append(0xFDD0 + i)
        super().__init__(collation_table="5.2.0")

    def _valid_char(self, ch: str) -> bool:
        category = unicodedata.category(ch)
        if category == "Cs":
            return False
        if category != "Cn":
            return True
        return ord(ch) not in self.non_char_code_points

    def build_lookup_key(self, text: str) -> list[int]:
        return [ord(ch) for ch in text if self._valid_char(ch)]


if sys.version_info[:2] == (3, 5):
    Collator = Collator_8_0_0
elif sys.version_info[:2] >= (3, 6):
    Collator = Collator_9_0_0
else:
    Collator = Collator_6_3_0
