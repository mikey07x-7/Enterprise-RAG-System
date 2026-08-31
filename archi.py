import os

def generate_tree(root_dir, prefix=""):
    lines = []

    try:
        entries = sorted(
            os.listdir(root_dir),
            key=lambda x: (
                not os.path.isdir(os.path.join(root_dir, x)),
                x.lower()
            )
        )
    except PermissionError:
        return [prefix + "└── [Permission Denied]"]

    for index, entry in enumerate(entries):
        path = os.path.join(root_dir, entry)
        is_last = index == len(entries) - 1

        connector = "└── " if is_last else "├── "
        lines.append(prefix + connector + entry)

        if os.path.isdir(path):
            extension = "    " if is_last else "│   "
            lines.extend(generate_tree(path, prefix + extension))

    return lines


root_folder = os.path.dirname(os.path.abspath(__file__))

tree = [os.path.basename(root_folder)]
tree.extend(generate_tree(root_folder))

output_file = os.path.join(root_folder, "folder_structure.txt")

with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(tree))

print("\n".join(tree))
print(f"\nSaved to: {output_file}")