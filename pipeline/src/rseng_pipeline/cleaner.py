"""Clean parsed page bodies for reuse outside the Jekyll site.

Cleaning turns a raw RSQKit page body into plain portable markdown:
Liquid tool tags become markdown links (via the tool registry), remaining
Liquid logic and includes are dropped, Training sections that hold no real
content disappear, and site-relative links become absolute everse.software
URLs so fragments keep working wherever they are embedded. Fenced code
blocks pass through untouched - they may legitimately show Liquid or
markdown syntax as examples.
"""

from __future__ import annotations

import re
from collections.abc import Callable

from .parser import _TOOL_TAG_RE
from .registry import Tool

_LIQUID_TAG_RE = re.compile(r"\{%-?.*?-?%\}")
_LIQUID_VAR_RE = re.compile(r"\{\{.*?\}\}")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_FENCE_RE = re.compile(r"^(```|~~~)")
_INLINE_LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)(\s+\"[^\"]*\")?\)")
_REF_DEF_RE = re.compile(r"^(\[[^\]]+\]:\s*)(\S+)(.*)$")
_EXTERNAL_RE = re.compile(r"^(https?://|mailto:|#)")
_BLANK_RUN_RE = re.compile(r"\n{3,}")

# A line mapper may return None to delete the line.
_LineFn = Callable[[str], str | None]


def _map_unfenced(body: str, fn: _LineFn) -> str:
    """Apply ``fn`` to every line outside fenced code blocks."""
    lines = []
    in_fence = False
    for line in body.splitlines():
        if _FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            lines.append(line)
            continue
        if in_fence:
            lines.append(line)
            continue
        mapped = fn(line)
        if mapped is not None:
            lines.append(mapped)
    return "\n".join(lines)


def replace_tool_tags(body: str, tools: dict[str, Tool] | None = None) -> str:
    """Turn ``{% tool "x" %}`` tags into markdown links or plain names."""
    lookup = tools or {}

    def substitute(match: re.Match) -> str:
        tool_id = match.group(1)
        tool = lookup.get(tool_id)
        if tool is None:
            return tool_id
        if tool.url:
            return f"[{tool.name}]({tool.url})"
        return tool.name

    return _map_unfenced(body, lambda line: _TOOL_TAG_RE.sub(substitute, line))


def strip_liquid(body: str) -> str:
    """Remove Liquid logic tags and variables; drop lines they leave empty."""

    def strip_line(line: str) -> str | None:
        stripped = _LIQUID_TAG_RE.sub("", line)
        stripped = _LIQUID_VAR_RE.sub("", stripped)
        if stripped.strip() == "" and line.strip() != "":
            return None  # the line held nothing but Liquid
        return stripped

    return _map_unfenced(body, strip_line)


def drop_empty_training_sections(body: str) -> str:
    """Remove Training headings whose section holds no actual content.

    Upstream Training sections are mostly dynamic embeds that strip down to
    nothing; genuinely curated Training lists are kept.
    """
    lines = body.splitlines()
    result: list[str] = []
    index = 0
    while index < len(lines):
        heading = _HEADING_RE.match(lines[index])
        if heading and heading.group(2).strip().lower() == "training":
            level = len(heading.group(1))
            end = index + 1
            while end < len(lines):
                next_heading = _HEADING_RE.match(lines[end])
                if next_heading and len(next_heading.group(1)) <= level:
                    break
                end += 1
            if "\n".join(lines[index + 1 : end]).strip() == "":
                index = end
                continue
        result.append(lines[index])
        index += 1
    return "\n".join(result)


# First path segment ending in one of these TLDs marks a schema-less
# external link (upstream sometimes writes e.g. "workflowhub.eu").
_BARE_DOMAIN_RE = re.compile(
    r"^[a-z0-9-]+(\.[a-z0-9-]+)*\.(com|org|net|io|eu|uk|dev|ai|edu)(/|$)", re.I
)


def _absolute(target: str, base_url: str) -> str:
    if _EXTERNAL_RE.match(target):
        return target
    slug = target
    while slug.startswith(("./", "../")):
        slug = slug.split("/", 1)[1]
    slug = slug.lstrip("/")
    if _BARE_DOMAIN_RE.match(slug):
        return f"https://{slug}"
    # Site permalinks carry no .md extension; upstream links sometimes do.
    slug = slug.removesuffix(".md")
    return f"{base_url}/{slug}"


def resolve_internal_links(body: str, base_url: str) -> str:
    """Rewrite site-relative link targets to absolute source-site URLs."""

    def fix_inline(match: re.Match) -> str:
        bang, text, target, title = match.groups()
        return f"{bang}[{text}]({_absolute(target, base_url)}{title or ''})"

    def fix_line(line: str) -> str:
        ref_def = _REF_DEF_RE.match(line)
        if ref_def:
            prefix, target, rest = ref_def.groups()
            return f"{prefix}{_absolute(target, base_url)}{rest}"
        return _INLINE_LINK_RE.sub(fix_inline, line)

    return _map_unfenced(body, fix_line)


def clean_body(body: str, base_url: str, tools: dict[str, Tool] | None = None) -> str:
    """Full cleaning pass over a page body."""
    cleaned = replace_tool_tags(body, tools)
    cleaned = strip_liquid(cleaned)
    cleaned = drop_empty_training_sections(cleaned)
    cleaned = resolve_internal_links(cleaned, base_url)
    # Trailing whitespace is stripped everywhere (code fences included) so
    # generated files stay byte-stable under standard whitespace hooks.
    cleaned = "\n".join(line.rstrip() for line in cleaned.splitlines())
    return _BLANK_RUN_RE.sub("\n\n", cleaned).strip() + "\n"
