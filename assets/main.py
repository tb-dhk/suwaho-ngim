import os

def edit_svgs(input_folder, output_folder=None):
    if output_folder is None:
        output_folder = input_folder
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".svg"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            with open(input_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            # insert background rect right after <svg ...>
            if "<rect" not in content:
                if "<svg" in content and ">" in content:
                    svg_open_end = content.find(">") + 1
                    rect = '<rect width="100%" height="100%" fill="#000"/>'
                    content = content[:svg_open_end] + rect + content[svg_open_end:]

            # replace colors
            content = content.replace("#fff0", "#000")
            content = content.replace("black", "white")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"edited {filename}")

# usage
edit_svgs(".")
