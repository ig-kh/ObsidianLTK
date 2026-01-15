BACKLINK = r"(?<!\!)(\[\[([^\]\|]+?)(?:\|([^\]]+?))?\]\])"
IMPUTED_BACKLINK = r""
NOTE_HEADER = r"^---\s*\n(.*?)\n---\s*\n"
# INBODY_TAG
# INBODY_PROPERTY
# HEADING
TEMPLATER_EXPR = r"<%[^>]+%>"
JINJA_EXPR = r"\{\{[^}]+\}\}|\{%[^%]+%-?%\}|\{#[^#]*#\}"
