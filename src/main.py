import os
import shutil
from gencontent import generate_page, generate_pages_recursive

def main():
    dir_path_static = "./static"
    dir_path_public = "./public"
    dir_path_content = "./content"
    template_path = "template.html"

    print("Starting build process...")

    clean_and_copy(dir_path_static, dir_path_public)

    generate_pages_recursive(dir_path_content, template_path, dir_path_public)
    
    print("Build complete! All pages generated.")

def clean_and_copy(src, dst):
    if os.path.exists(dst):
        print(f"Cleaning destination: {dst}...")
        shutil.rmtree(dst)

    os.mkdir(dst)

    if not os.path.exists(src):
        raise Exception(f"Source directory {src} does not exist!")

    copy_recursive(src, dst)

def copy_recursive(src_path, dst_path):
    nodes = os.listdir(src_path)

    for node in nodes:
        source_node_path = os.path.join(src_path, node)
        dest_node_path = os.path.join(dst_path, node)

        if os.path.isfile(source_node_path):
            print(f"Copying file: {source_node_path} -> {dest_node_path}")
            shutil.copy(source_node_path, dest_node_path)
        else:
            print(f"Creating directory: {dest_node_path}")
            if not os.path.exists(dest_node_path):
                os.mkdir(dest_node_path)
            copy_recursive(source_node_path, dest_node_path)

if __name__ == "__main__":
    main()
