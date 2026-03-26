import unittest

from textnode import TextNode, TextType, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

class TestSplitNodes(unittest.TestCase):
    def test_delim_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_delim_bold(self):
        node = TextNode("This is **bold** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" text", TextType.TEXT),
            ],
        )

    def test_delim_italic(self):
        node = TextNode("I love _italic_ words", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(
            new_nodes,
            [
                TextNode("I love ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" words", TextType.TEXT),
            ],
        )

    def test_multiple_delimiters(self):
        node = TextNode("Go `code` and `more code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            len(new_nodes),
            4 # ["Go ", "code", " and ", "more code"]
        )

    def test_unclosed_delimiter(self):
        node = TextNode("This is `invalid code", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_chained_delimiters(self):
        node = TextNode("Text with **bold** and `code`", TextType.TEXT)
        bold_split = split_nodes_delimiter([node], "**", TextType.BOLD)
        final_split = split_nodes_delimiter(bold_split, "`", TextType.CODE)
        self.assertEqual(len(final_split), 4)
        self.assertEqual(final_split[1].text_type, TextType.BOLD)
        self.assertEqual(final_split[3].text_type, TextType.CODE)


class TestMarkdownExtraction(unittest.TestCase):
    def test_extract_markdown_images(self):
        text = "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and ![another](https://link.com/pic.jpg)"
        matches = extract_markdown_images(text)
        self.assertListEqual(
            [("image", "https://i.imgur.com/zjjcJKZ.png"), ("another", "https://link.com/pic.jpg")], 
            matches
        )

    def test_extract_markdown_links(self):
        text = "Check [Boot.dev](https://www.boot.dev) and [Google](https://www.google.com)"
        matches = extract_markdown_links(text)
        self.assertListEqual(
            [("Boot.dev", "https://www.boot.dev"), ("Google", "https://www.google.com")], 
            matches
        )

    def test_links_ignore_images(self):
        # Links should NOT pick up image syntax
        text = "This is a ![image](https://url.com) and a [link](https://boot.dev)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("link", "https://boot.dev")], matches)

    def test_images_ignore_links(self):
        # Images should NOT pick up link syntax
        text = "This is a ![image](https://url.com) and a [link](https://boot.dev)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("image", "https://url.com")], matches)

    def test_no_matches(self):
        text = "Just some plain text here."
        self.assertEqual(extract_markdown_images(text), [])
        self.assertEqual(extract_markdown_links(text), [])


class TestSplitNodes(unittest.TestCase):
    def test_split_image(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            ],
            new_nodes,
        )

    def test_split_images_multiple(self):
        node = TextNode(
            "![img1](url1) and ![img2](url2) trailing",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertEqual(len(new_nodes), 4)
        self.assertEqual(new_nodes[0].text, "img1")
        self.assertEqual(new_nodes[3].text, " trailing")

    def test_split_link_single(self):
        node = TextNode("Check [Boot.dev](https://www.boot.dev) now!", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("Check ", TextType.TEXT),
                TextNode("Boot.dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" now!", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_links_no_text_between(self):
        node = TextNode("[one](url1)[two](url2)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].text, "one")
        self.assertEqual(new_nodes[1].text, "two")

class TestTextToTextNodes(unittest.TestCase):
    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertListEqual(expected, nodes)

    def test_only_text(self):
        text = "Just plain text here"
        nodes = text_to_textnodes(text)
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].text, "Just plain text here")

    def test_multiple_bold(self):
        text = "This is **bold** and **more bold**"
        nodes = text_to_textnodes(text)
        self.assertEqual(len(nodes), 4)
        self.assertEqual(nodes[1].text_type, TextType.BOLD)
        self.assertEqual(nodes[3].text_type, TextType.BOLD)


if __name__ == "__main__":
    unittest.main()
