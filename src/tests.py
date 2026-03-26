import unittest
from textnode import TextNode, TextType, text_node_to_html_node

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_eq_with_url(self):
        node = TextNode("Link node", TextType.LINK, "https://www.google.com")
        node2 = TextNode("Link node", TextType.LINK, "https://www.google.com")
        self.assertEqual(node, node2)

    def test_not_eq_text(self):
        node = TextNode("This is text", TextType.TEXT)
        node2 = TextNode("This is different text", TextType.TEXT)
        self.assertNotEqual(node, node2)

    def test_not_eq_type(self):
        node = TextNode("Same text", TextType.BOLD)
        node2 = TextNode("Same text", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_url_none_vs_string(self):
        node = TextNode("Link", TextType.LINK, None)
        node2 = TextNode("Link", TextType.LINK, "https://www.boot.dev")
        self.assertNotEqual(node, node2)

    def test_text_node_to_html_node_bold(self):
    	node = TextNode("This is bold", TextType.BOLD)
    	html_node = text_node_to_html_node(node)
    	self.assertEqual(html_node.tag, "b")
    	self.assertEqual(html_node.value, "This is bold")

    def test_text_node_to_html_node_image(self):
    	node = TextNode("alt text", TextType.IMAGE, "https://www.google.com/logo.png")
    	html_node = text_node_to_html_node(node)
    	self.assertEqual(html_node.tag, "img")
    	self.assertEqual(html_node.value, "")
    	self.assertEqual(
        	html_node.props, 
        	{"src": "https://www.google.com/logo.png", "alt": "alt text"}
    	)

if __name__ == "__main__":
    unittest.main()
