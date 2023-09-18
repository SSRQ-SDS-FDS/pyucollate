# pyucollate: Unicode sorting in Python made simple.

This library is a modernized version of [James K. Taubers](https://github.com/jtauber) [pyuca](https://github.com/jtauber/pyuca) with some small changes in the API.

As the original library it's a Python implementation of the [Unicode Collation Algorithm (UCA)](http://unicode.org/reports/tr10/). It
passes 100% of the UCA conformance tests with a variable-weighting setting of Non-ignorable.

## What do you use it for?

In short, sorting non-English strings properly.

The core of the algorithm involves multi-level comparison. For example,
``café`` comes before ``caff`` because at the primary level, the accent is
ignored and the first word is treated as if it were ``cafe``. The secondary
level (which considers accents) only applies then to words that are equivalent
at the primary level.

The Unicode Collation Algorithm and pyuca also support contraction and
expansion. **Contraction** is where multiple letters are treated as a single
unit. In Spanish, ``ch`` is treated as a letter coming between ``c`` and ``d``
so that, for example, words beginning ``ch`` should sort after all other words
beginnings with ``c``. **Expansion** is where a single letter is treated as
though it were multiple letters. In German, ``ä`` is sorted as if it were
``ae``, i.e. after ``ad`` but before ``af``.

## How does it differ from the original library and why did you fork it?

`pyuca` is a well working python library, but apparently it is no longer actively maintained (see the open PRs and issues). So we decided to create our own fork with some minor changes:

1. We added some modern python tooling like `pytest`, `ruff` or `mypy`
2. Type hints were added to all functions and classes.
3. A `sort()`-function was added to the collator interface (just a wrapper around Python's `sorted()`, which uses the `Collator` to generate sorting-keys).

## How to use it

Here is how to use the ``pyuca`` module.

```sh
pip install install git+https://github.com/SSRQ-SDS-FDS/pyucollate.git
```

Usage example:

```python
from pyucollate import Collator
c = Collator()

assert c.sort(["cafe", "caff", "café"]) == ["cafe", "caff", "café"]
```

## License

Python code is made available under an MIT license (see `LICENSE`).
`allkeys.txt` is made available under the similar license defined in
`LICENSE-allkeys`.
