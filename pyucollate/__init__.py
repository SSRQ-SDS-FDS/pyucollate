"""This is a Python 3 implementation of the Unicode Collation Algorithm (UCA).

It passes 100% of the UCA conformances tests for Unicode 6.3.0 with a
variable-weighting setting of Non-ignorable.

Usage example:

    from pyucollate import Collator
    c = Collator()

    sorted_words = sorted(words, key=c.sort_key)

Collator can also take an optional filename for specifying a custom collation
element table.
"""

from pyucollate.collator import (
    Collator,
    Collator_5_2_0,
    Collator_6_3_0,
    Collator_8_0_0,
    Collator_9_0_0,
    Collator_10_0_0,
)

__all__ = ["Collator", "Collator_5_2_0", "Collator_6_3_0", "Collator_8_0_0", "Collator_9_0_0", "Collator_10_0_0"]
