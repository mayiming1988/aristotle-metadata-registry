from django.test import TestCase
from aristotle_mdr.structs import Tree, Node


class TestTree(TestCase):

    def setUp(self):
        self.root = Node(identifier=1, data='1')
        self.tree = Tree(self.root)
        left = Node(self.root, 2, data='11')
        right = Node(self.root, 3, data='12')
        self.tree.add_node(left)
        self.tree.add_node(right)
        self.tree.add_node(Node(left, 4, '111'))

    def test_children(self):
        self.assertCountEqual(self.tree.children[1], [2, 3])
        self.assertCountEqual(self.tree.children[2], [4])

    def test_string(self):
        s = str(self.tree)
        self.assertEqual(s, '- 1\n - 11\n  - 111\n - 12\n')
