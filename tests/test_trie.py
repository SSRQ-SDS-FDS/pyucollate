import pytest
from pyucollate.trie import Trie


def convert_lookup_result_to_string(
    result: tuple[list[int], list[list[int]] | None, list[int]]
) -> tuple[str | None, ...]:
    first, second, third = result
    first = "".join(chr(c) for c in first)
    second = "".join("".join(chr(c) for c in part) for part in second) if second else None
    third = "".join(chr(c) for c in third)
    return first, second, third


@pytest.mark.parametrize(
    ("key_value_pairs", "prefix", "expected_result"),
    [
        ([("foo", "bar")], "fo", ("", None, "fo")),
        ([("foo", "bar")], "foo", ("foo", "bar", "")),
        ([("foo", "bar")], "food", ("foo", "bar", "d")),
        ([("a", "yes"), ("abc", "yes")], "abdc", ("a", "yes", "bdc")),
    ],
)
def test_trie(
    key_value_pairs: list[tuple[str, str]], prefix: str, expected_result: tuple[str | None, ...]
):
    trie = Trie()
    for key_value in key_value_pairs:
        key, value = key_value
        trie.add(key=[ord(c) for c in key], value=[[ord(c) for c in value]])
    result = trie.find_prefix([ord(c) for c in prefix])  # type: ignore
    assert convert_lookup_result_to_string(result) == expected_result
