import re
from enum import Enum
from htmlnode import LeafNode, ParentNode

class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        return (
            self.text == other.text and
            self.text_type == other.text_type and
            self.url == other.url
            )

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"


def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
    else:
        raise ValueError(f"Invalid text type: {text_node.text_type}")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        split_nodes = []
        parts = old_node.text.split(delimiter)

        if len(parts) % 2 == 0:
            raise ValueError(f"Invalid Markdown syntax: no closing delimiter '{delimiter}' found.")

        for i in range(len(parts)):
            if parts[i] == "":
                continue
            if i % 2 == 0:
                split_nodes.append(TextNode(parts[i], TextType.TEXT))
            else:
                split_nodes.append(TextNode(parts[i], text_type))
        new_nodes.extend(split_nodes)

    return new_nodes


def extract_markdown_images(text):
    # Regex breakdown:
    # !         -> literal exclamation mark
    # \[(.*?)\] -> capture group 1: anything inside square brackets (alt text)
    # \((.*?)\) -> capture group 2: anything inside parentheses (url)
    pattern = r"!\[(.*?)\]\((.*?)\)"
    return re.findall(pattern, text)

def extract_markdown_links(text):
    # Regex breakdown:
    # (?<!!)    -> negative lookbehind: do NOT match if preceded by '!'
    # \[(.*?)\] -> capture group 1: anchor text
    # \((.*?)\) -> capture group 2: url
    pattern = r"(?<!!)\[(.*?)\]\((.*?)\)"
    return re.findall(pattern, text)


def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        original_text = old_node.text
        images = extract_markdown_images(original_text)

        if len(images) == 0:
            new_nodes.append(old_node)
            continue

        for image in images:
            sections = original_text.split(f"![{image[0]}]({image[1]})", 1)
            if len(sections) != 2:
                raise ValueError("Invalid markdown, image section not closed")

            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))

            new_nodes.append(TextNode(image[0], TextType.IMAGE, image[1]))
            original_text = sections[1]

        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))

    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        original_text = old_node.text
        links = extract_markdown_links(original_text)

        if len(links) == 0:
            new_nodes.append(old_node)
            continue

        for link in links:
            sections = original_text.split(f"[{link[0]}]({link[1]})", 1)
            if len(sections) != 2:
                raise ValueError("Invalid markdown, link section not closed")

            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))

            new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
            original_text = sections[1]

        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))

    return new_nodes


def text_to_textnodes(text):
    # Start with a single node containing the entire raw string
    nodes = [TextNode(text, TextType.TEXT)]

    # Chain the splitting functions
    # Bold must come before Italic if both use variations of * or _
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)

    # Extract links and images
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)

    return nodes


def markdown_to_blocks(markdown):
    # Split the document by double newlines
    raw_blocks = markdown.split("\n\n")
    blocks = []

    for block in raw_blocks:
        # Strip leading/trailing whitespace
        cleaned_block = block.strip()

        # Only add to the list if the block isn't just empty space
        if cleaned_block != "":
            blocks.append(cleaned_block)

    return blocks


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def block_to_block_type(block):
    lines = block.split("\n")

    # Heading check: 1-6 # followed by a space
    if re.match(r"^#{1,6} ", block):
        return BlockType.HEADING

    # Code block check: starts and ends with ```
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE

    # Quote block check: every line starts with >
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    # Unordered list check: every line starts with "- "
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    # Ordered list check: starts at 1. and increments
    if block.startswith("1. "):
        is_ordered = True
        for i, line in enumerate(lines):
            expected_start = f"{i + 1}. "
            if not line.startswith(expected_start):
                is_ordered = False
                break
        if is_ordered:
            return BlockType.ORDERED_LIST

    # Default case
    return BlockType.PARAGRAPH

def text_to_children(text):
    # 1. Convert raw text to a list of TextNode objects (handles bold, italic, etc.)
    # This assumes you have a previously built text_to_textnodes function
    text_nodes = text_to_textnodes(text)
    
    # 2. Convert those TextNodes into HTMLNodes (LeafNodes)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children

def markdown_to_html_node(markdown):
    # 1. Split into blocks
    blocks = markdown_to_blocks(markdown)
    children = []

    # 2. Loop over blocks
    for block in blocks:
        block_type = block_to_block_type(block)

        # 3. Create HTMLNode based on type
        if block_type == BlockType.HEADING:
            level = 0
            for char in block:
                if char == "#":
                    level += 1
                else:
                    break
            # Strip hashes and the space
            content = block[level + 1:]
            children.append(ParentNode(f"h{level}", text_to_children(content)))

        elif block_type == BlockType.CODE:
            # Code blocks are special: no inline parsing, nested <code> inside <pre>
            # Remove the backticks (top and bottom)
            content = block.strip("`").strip("\n")
            code_node = ParentNode("code", [LeafNode(None, content)])
            children.append(ParentNode("pre", [code_node]))

        elif block_type == BlockType.QUOTE:
            # Strip the '>' from each line
            lines = block.split("\n")
            new_lines = []
            for line in lines:
                new_lines.append(line.lstrip(">").strip())
            content = " ".join(new_lines)
            children.append(ParentNode("blockquote", text_to_children(content)))

        elif block_type == BlockType.UNORDERED_LIST:
            # Each line becomes an <li>
            items = block.split("\n")
            li_nodes = []
            for item in items:
                # Remove "- "
                content = item[2:]
                li_nodes.append(ParentNode("li", text_to_children(content)))
            children.append(ParentNode("ul", li_nodes))

        elif block_type == BlockType.ORDERED_LIST:
            # Each line becomes an <li>
            items = block.split("\n")
            li_nodes = []
            for item in items:
                # Remove "1. " or "2. " (find the first space)
                content = item[item.find(" ") + 1:]
                li_nodes.append(ParentNode("li", text_to_children(content)))
            children.append(ParentNode("ol", li_nodes))

        else: # Paragraph
            children.append(ParentNode("p", text_to_children(block)))

    # 4. Wrap everything in a div parent
    return ParentNode("div", children)
