import os
import shutil
import sys 
from gencontent import generate_page, generate_pages_recursive

def main():
    basepath = "/"
    if len(sys.argv) > 1:
        basepath = sys.argv[1]

    dir_path_static = "./static"
    dir_path_content = "./content"
    template_path = "template.html"
    dir_path_docs = "./docs"

    print(f"Starting build process to {dir_path_docs} with basepath: {basepath}")

    clean_and_copy(dir_path_static, dir_path_docs)

    generate_pages_recursive(dir_path_content, template_path, dir_path_docs, basepath)

    print("Build complete!")

def clean_and_copy(src, dst):
    if os.path.exists(dst):
        print(f"Cleaning {dst} directory...")
        shutil.rmtree(dst)

    os.mkdir(dst)

    if not os.path.exists(src):
        raise Exception(f"Source directory {src} does not exist!")

def copy_recursive(src_path, dst_path):
    nodes = os.listdir(src_path)
    for node in nodes:
        source_node_path = os.path.join(src_path, node)
        dest_node_path = os.path.join(dst_path, node)
        if os.path.isfile(source_node_path):
            shutil.copy(source_node_path, dest_node_path)
        else:
            os.makedirs(dest_node_path, exist_ok=True)
            copy_recursive(source_node_path, dest_node_path)


if __name__ == "__main__":
    main()
