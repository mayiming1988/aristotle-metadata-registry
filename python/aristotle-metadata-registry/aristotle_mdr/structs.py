from typing import Optional, List, Dict, Tuple, Any
from collections import defaultdict


class Node:
    """A single node in the tree"""

    def __init__(self, parent=None, data=None):
        self.identifier = id(self)

        self.parent: Node = parent
        self.data = data

    def __str__(self):
        return str(self.data)


class Tree:
    """Tree data structure composed of nodes"""

    # Characters used for building string representation
    data_start = '- '
    spacing_char = ' '
    end_char = '\n'

    def __init__(self, root: Node):
        self.root: Node = root
        self.nodes: Dict[int, Node] = {}
        self.children: Dict[int, List[int]] = defaultdict(list)

    def add_node(self, node):
        self.nodes[node.identifier] = node
        # Add relationship to parent
        self.children[node.parent.identifier].append(node.identifier)

    def add_bulk_relations(self, start: Node, relations: List[Tuple[int, int]], datadict: Dict[int, Any]):
        """
        Add's relations in bulk from (parent, child) tuples
        To maintain tree structure id's that appear multiple times in tree will have new nodes created
        """
        # Build dict of parent -> list of children
        relation_dict: Dict[int, List[int]] = defaultdict(list)
        for pair in relations:
            relation_dict[pair[0]].append(pair[1])

        node_stack = [start]

        while node_stack:
            # Pop node off stack
            next_node = node_stack.pop()
            # Add to tree if not root
            if next_node != start:
                self.add_node(next_node)
            # Create child nodes and add to stack
            children = relation_dict.pop(next_node.data.id, [])
            for child_id in children:
                node_stack.append(
                    Node(next_node, datadict.get(child_id, None))
                )

    def get_node_children(self, identifier) -> List[Node]:
        return [self.nodes[i] for i in self.children[identifier]]

    def get_string(self, node, level=0) -> str:
        s = (self.spacing_char * level) + self.data_start + str(node) + self.end_char
        for sub_node in self.get_node_children(node.identifier):
            s += self.get_string(sub_node, level + 1)
        return s

    def get_string_list(self, node):
        slist = [str(node)]
        sublist = []

        for sub_node in self.get_node_children(node.identifier):
            sublist.extend(self.get_string_list(sub_node))

        if sublist:
            slist.append(sublist)

        return slist

    @property
    def string_list(self):
        return self.get_string_list(self.root)

    def __str__(self):
        return self.get_string(self.root)
