import os


def get_all_by_extension(start, extension="md"):
    md_files = []
    for dirpath, dirnames, filenames in os.walk(start):
        if ".obsidian" in dirnames:
            dirnames.remove(".obsidian")
        for filename in filenames:
            if filename.endswith(f".{extension}"):
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

def norm_abs(p: str) -> str:
    """Absolute, normalized filesystem path."""
    return os.path.normpath(os.path.abspath(p))


def abs_under_root(root: str, rel: str) -> str:
    """Resolve a canvas-relative file path to an absolute path."""
    return norm_abs(os.path.join(root, rel))


def strip_md_suffix(ref: str) -> str:
    """Remove a trailing '.md' if present (case-sensitive, matches VaultDataset)."""
    if ref.endswith(".md"):
        return ref[: -len(".md")]
    return ref


def norm_ref(ref: str) -> str:
    """Normalize a wikilink handler into canonical ref space."""
    return strip_md_suffix(ref.replace("\\", "/"))


def to_ref(root: str, abs_path: str) -> str:
    """Absolute path → canonical vault-relative ref (no separators, no .md)."""
    rel = os.path.relpath(norm_abs(abs_path), norm_abs(root))
    return norm_ref(rel)