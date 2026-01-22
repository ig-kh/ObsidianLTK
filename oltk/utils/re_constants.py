# Links
BACKLINK = r"(?<!\!)(\[\[([^\]\|]+?)(?:\|([^\]]+?))?\]\])"

# Explicit features
NOTE_HEADER = r"^---\s*\n(.*?)\n---\s*\n"

# Special cases - permissive regexps for embedded expressions syntax
MATHJAX_EXPR = r""
TEMPLATER_EXPR = r"<%[^>]+%>"
JINJA_EXPR = r"\{\{[^}]+\}\}|\{%[^%]+%-?%\}|\{#[^#]*#\}"
