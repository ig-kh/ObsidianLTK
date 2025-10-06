import re
import yaml

def extract_backlinks(content):
    backlinks = []

    backlink_matches = re.findall(
        r"(?<!\!)(\[\[([^\]\|]+?)(?:\|([^\]]+?))?\]\])", content, re.UNICODE
    )

    for match in backlink_matches:
        node = match[1].strip().split("#")[0]
        alias = match[2].strip() if match[2] else None
        backlinks.append((node, alias))

    return backlinks

def extract_header_props(content):
    md_yaml_props = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)

    if md_yaml_props:
        props = yaml.safe_load(md_yaml_props.group(1))
    else:
        props = dict()

    return props

# def extract_body_props(content)
# def run_rb_ner(content, rules_cfg)