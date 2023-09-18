from typing import Self


class Node:
    value: list[list[int]] | None
    children: dict[int, Self] | None

    __slots__ = ("value", "children")

    def __init__(self) -> None:
        self.value = None
        self.children = None


class Trie:
    root: Node

    def __init__(self) -> None:
        self.root = Node()

    def add(self, key: list[int], value: list[list[int]]) -> None:
        curr_node = self.root
        for part in key:
            if curr_node.children is None:
                curr_node.children = {}
            curr_node = curr_node.children.setdefault(part, Node())
        curr_node.value = value

    def find_prefix(self, key: list[int]) -> tuple[list[int], list[list[int]] | None, list[int]]:
        curr_node = self.root
        success_index = 0
        success_value = None
        for i, part in enumerate(key):
            if curr_node.children is None or part not in curr_node.children:
                break
            curr_node = curr_node.children[part]
            if curr_node.value:
                success_index = i + 1
                success_value = curr_node.value
        return key[:success_index], success_value, key[success_index:]
