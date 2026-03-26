import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode(
            "a",
            "Click me!",
            None,
            {"href": "https://www.google.com", "target": "_blank"},
        )
        # Check if attributes are formatted correctly with a leading space
        expected = ' href="https://www.google.com" target="_blank"'
        self.assertEqual(node.props_to_html(), expected)

    def test_values(self):
        node = HTMLNode("p", "Hello, world!")
        self.assertEqual(node.tag, "p")
        self.assertEqual(node.value, "Hello, world!")
        self.assertEqual(node.children, None)
        self.assertEqual(node.props, None)

    def test_repr(self):
        node = HTMLNode("h1", "Title", None, {"class": "header"})
        # Just verifying that it returns a string and contains the tag
        self.assertIn("h1", repr(node))
        self.assertIn("Title", repr(node))
        self.assertIn("header", repr(node))

    def test_leaf_to_html_p(self):
    	node = LeafNode("p", "This is a paragraph of text.")
    	self.assertEqual(node.to_html(), "<p>This is a paragraph of text.</p>")

    def test_leaf_to_html_a(self):
    	node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
    	self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me!</a>')

    def test_leaf_raw_text(self):
    	node = LeafNode(None, "Just some raw text.")
    	self.assertEqual(node.to_html(), "Just some raw text.")

    def test_to_html_with_children(self):
    	child_node = LeafNode("span", "child")
    	parent_node = ParentNode("div", [child_node])
    	self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
    	grandchild_node = LeafNode("b", "grandchild")
    	child_node = ParentNode("span", [grandchild_node])
    	parent_node = ParentNode("div", [child_node])
    	self.assertEqual(
        	parent_node.to_html(), 
        	"<div><span><b>grandchild</b></span></div>"
    	)

    def test_to_html_many_children(self):
    	node = ParentNode(
        	"p",
        	[
            	LeafNode("b", "Bold text"),
            	LeafNode(None, "Normal text"),
            	LeafNode("i", "italic text"),
            	LeafNode(None, "Normal text"),
        	],
    	)
    	expected = "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"
    	self.assertEqual(node.to_html(), expected)

if __name__ == "__main__":
    unittest.main()
