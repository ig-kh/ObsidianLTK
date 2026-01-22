from ..utils.re_constants import BACKLINK
import re


def dereference_backlinks(content: str) -> str:

    prev_end = 0
    derefernced_content = ""

    for match in re.finditer(BACKLINK, content, re.UNICODE):
        node_alias = match[3].strip() if match[3] else None
        impute_val = node_alias if node_alias else match[2].strip()
        derefernced_content += content[prev_end : match.start()] + impute_val
        prev_end = match.end()

    derefernced_content += content[prev_end:]
    return derefernced_content
