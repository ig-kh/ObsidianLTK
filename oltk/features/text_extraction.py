import re
from typing import Any, List, Mapping, Tuple

import yaml

from ..utils.re_constants import BACKLINK, NOTE_HEADER


def extract_backlinks(content) -> List[Tuple[str]]:
    backlinks = []

    backlink_matches = re.findall(BACKLINK, content, re.UNICODE)

    for match in backlink_matches:

        node_info_list = match[1].strip().split("#")
        node_path = node_info_list[0]

        if len(node_info_list) > 1:
            heading_path = "/".join(match[1].strip().split("#")[1:])
        else:
            heading_path = None

        node_alias = match[2].strip() if match[2] else None

        backlinks.append((node_path, heading_path, node_alias))

    return backlinks


def extract_header_props(content) -> Mapping[str, Any]:
    md_yaml_props = re.match(NOTE_HEADER, content, re.DOTALL)

    if md_yaml_props:
        props = yaml.safe_load(md_yaml_props.group(1))
    else:
        props = dict()

    return props
