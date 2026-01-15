import os
from pathlib import Path


def get_all_by_extension(start, extension="md"):
    md_files = []
    for dirpath, dirnames, filenames in os.walk(start):
        if ".obsidian" in dirnames:
            dirnames.remove(".obsidian")
        for filename in filenames:
            if filename.endswith(f".{extension}"):
                # Compute relative path to root_dir
                relative_path = os.path.relpath(os.path.join(dirpath, filename), start)
                md_files.append(relative_path)
    return md_files


def read_md(path) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"UTF-8 failed, trying utf-8-sig for {path}")
        with open(path, "r", encoding="utf-8-sig") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return ""

    return content
