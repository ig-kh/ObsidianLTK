from pathlib import Path

def list_shallow_dir(dir):
    directory = Path(dir)
    if not directory.exists():
        print(f"Directory {directory} does not exist.")

    md_files = list(directory.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {directory}")

    return md_files

def read_md(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"UTF-8 failed, trying utf-8-sig for {path}")
        with open(path, "r", encoding="utf-8-sig") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None
    
    return content