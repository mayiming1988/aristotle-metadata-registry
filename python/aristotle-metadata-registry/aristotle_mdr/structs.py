from typing import Optional, List, Dict
from collections import defaultdict


class Node:

    def __init__(self, parent=None, data=None):
        self.identifier = id(self)

        self.parent: Node = parent
        self.data = data

    def __str__(self):
        return str(self.data)


class Tree:

    data_start = '- '
    spacing_char = ' '
    end_char = '\n'

    def __init__(self, root: Node):
        self.root: Node = root
        self.nodes: Dict[int, Node] = {}
        self.children: Dict[int, List[int]] = defaultdict(list)

    def add_node(self, node):
        self.nodes[node.identifier] = node
        self.children[node.parent.identifier].append(node.identifier)

    def get_node_children(self, identifier) -> List[Node]:
        return [self.nodes[i] for i in self.children[identifier]]

    def get_string(self, node, level=0) -> str:
        s = (self.spacing_char * level) + self.data_start + str(node) + self.end_char
        for sub_node in self.get_node_children(node.identifier):
            s += self.get_string(sub_node, level + 1)
        return s

    def __str__(self):
        return self.get_string(self.root)
