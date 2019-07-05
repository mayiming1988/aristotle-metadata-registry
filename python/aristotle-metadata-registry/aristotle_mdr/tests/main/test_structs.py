from django.test import TestCase
from aristotle_mdr.structs import Tree, Node


class TestTree(TestCase):

    def setUp(self):
        self.root = Node(data='1')
        self.tree = Tree(self.root)

        self.left = Node(self.root, data='11')
        self.right = Node(self.root, data='12')
        self.tree.add_node(self.left)
        self.tree.add_node(self.right)

        self.last = Node(self.left, '111')
        self.tree.add_node(self.last)

    def test_children(self):
        self.assertCountEqual(
            self.tree.children[self.root.identifier],
            [self.left.identifier, self.right.identifier]
        )
        self.assertCountEqual(
            self.tree.children[self.left.identifier],
            [self.last.identifier]
        )

    def test_string(self):
        s = str(self.tree)
        self.assertEqual(s, '- 1\n - 11\n  - 111\n - 12\n')

    def test_string_list(self):
        s = self.tree.string_list
        self.assertCountEqual(
            s,
            ['1', ['11', ['111'], '12']]
        )
