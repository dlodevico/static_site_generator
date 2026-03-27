import unittest

from textnode import TextNode, TextType, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, BlockType, block_to_block_type, markdown_to_html_node, ParentNode, text_to_children


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


class TestMarkdownToHTML(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_newlines(self):
        # Testing multiple newlines and leading/trailing whitespace
        md = """
# This is a heading


This is a paragraph with extra space.      

  
- List item
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "# This is a heading",
                "This is a paragraph with extra space.",
                "- List item",
            ],
        )


class TestBlockToBlockType(unittest.TestCase):
    def test_heading(self):
        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### Tiny Heading"), BlockType.HEADING)
        # Invalid heading (no space)
        self.assertEqual(block_to_block_type("###Invalid"), BlockType.PARAGRAPH)

    def test_code(self):
        code = "```\nprint('hello')\n```"
        self.assertEqual(block_to_block_type(code), BlockType.CODE)

    def test_quote(self):
        quote = "> Line 1\n> Line 2"
        self.assertEqual(block_to_block_type(quote), BlockType.QUOTE)
        # Mixed content
        bad_quote = "> Line 1\nLine 2"
        self.assertEqual(block_to_block_type(bad_quote), BlockType.PARAGRAPH)

    def test_unordered_list(self):
        ul = "- Item 1\n- Item 2"
        self.assertEqual(block_to_block_type(ul), BlockType.UNORDERED_LIST)
        # Missing space
        bad_ul = "-Item 1"
        self.assertEqual(block_to_block_type(bad_ul), BlockType.PARAGRAPH)

    def test_ordered_list(self):
        ol = "1. First\n2. Second\n3. Third"
        self.assertEqual(block_to_block_type(ol), BlockType.ORDERED_LIST)
        # Wrong increment
        bad_ol = "1. First\n3. Second"
        self.assertEqual(block_to_block_type(bad_ol), BlockType.PARAGRAPH)
        # Doesn't start with 1
        bad_ol_start = "2. First\n3. Second"
        self.assertEqual(block_to_block_type(bad_ol_start), BlockType.PARAGRAPH)

    def test_paragraph(self):
        para = "Just a normal paragraph of text."
        self.assertEqual(block_to_block_type(para), BlockType.PARAGRAPH)


class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_paragraph(self):
        md = "This is a simple paragraph."
        node = markdown_to_html_node(md)
        self.assertEqual(node.tag, "div")
        self.assertEqual(node.children[0].tag, "p")
        self.assertEqual(node.children[0].children[0].value, "This is a simple paragraph.")

    def test_heading(self):
        md = "### This is a level 3 heading"
        node = markdown_to_html_node(md)
        self.assertEqual(node.children[0].tag, "h3")
        self.assertEqual(node.children[0].children[0].value, "This is a level 3 heading")

    def test_code_block(self):
        md = "```\npython\nprint('hi')\n```"
        node = markdown_to_html_node(md)
        self.assertEqual(node.children[0].tag, "pre")
        self.assertEqual(node.children[0].children[0].tag, "code")
        # Ensure it didn't try to parse 'hi' as inline markdown
        self.assertEqual(node.children[0].children[0].children[0].value, "python\nprint('hi')")

    def test_lists(self):
        md = "- item 1\n- item 2"
        node = markdown_to_html_node(md)
        self.assertEqual(node.children[0].tag, "ul")
        self.assertEqual(len(node.children[0].children), 2)
        self.assertEqual(node.children[0].children[0].tag, "li")

    def test_complex_markdown(self):
        md = """
# Heading

This is a paragraph with **bold**.

- List item
"""
        node = markdown_to_html_node(md)
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[0].tag, "h1")
        self.assertEqual(node.children[1].tag, "p")
        self.assertEqual(node.children[2].tag, "ul")


if __name__ == "__main__":
    unittest.main()
