from __future__ import annotations

import re
from dataclasses import dataclass
from html import escape as html_escape

from bs4 import BeautifulSoup, Tag

_BLOCK_TAGS = {"p", "div", "td", "li", "h1", "h2", "h3", "h4", "h5", "h6"}

_EMBED_MARKER_RE = re.compile(r"embed your youtube video here", re.IGNORECASE)
_DESCRIPTION_MARKER_RE = re.compile(r"watch this\s*\(", re.IGNORECASE)
_SUGGESTED_SEARCH_RE = re.compile(
    r"suggested search:\s*[\"“]*(.*?)[\"”]*\]", re.IGNORECASE | re.DOTALL
)
_YOUTUBE_IFRAME_SRC_RE = re.compile(r"(?:youtube\.com/embed/|youtu\.be/)", re.IGNORECASE)
_ISO8601_DURATION_RE = re.compile(
    r"^PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?$"
)

_IFRAME_TEMPLATE = (
    '<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" '
    'title="{title}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; '
    'encrypted-media; gyroscope; picture-in-picture; web-share" '
    'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'
)


@dataclass
class VideoSlot:
    index: int
    description_tag: Tag | None
    embed_tag: Tag
    suggested_search: str
    original_description_text: str
    already_filled: bool = False


def _closest_block(node: object) -> Tag | None:
    tag = getattr(node, "parent", None)
    while tag is not None and getattr(tag, "name", None) not in _BLOCK_TAGS:
        tag = tag.parent
    return tag


def _find_slots_in_soup(soup: BeautifulSoup) -> list[VideoSlot]:
    position_by_id: dict[int, int] = {}
    for position, node in enumerate(soup.descendants):
        if isinstance(node, Tag):
            position_by_id[id(node)] = position

    embed_blocks: list[Tag] = []
    seen_embed_ids: set[int] = set()
    for text_node in soup.find_all(string=_EMBED_MARKER_RE):
        block = _closest_block(text_node)
        if block is None or id(block) in seen_embed_ids:
            continue
        seen_embed_ids.add(id(block))
        embed_blocks.append(block)

    description_blocks: list[Tag] = []
    seen_description_ids: set[int] = set()
    for text_node in soup.find_all(string=_DESCRIPTION_MARKER_RE):
        block = _closest_block(text_node)
        if block is None or id(block) in seen_description_ids or id(block) in seen_embed_ids:
            continue
        seen_description_ids.add(id(block))
        description_blocks.append(block)

    embed_blocks.sort(key=lambda b: position_by_id.get(id(b), 0))
    description_blocks.sort(key=lambda b: position_by_id.get(id(b), 0))

    used_description_ids: set[int] = set()
    slots: list[VideoSlot] = []
    for index, embed_block in enumerate(embed_blocks):
        embed_pos = position_by_id.get(id(embed_block), 0)
        best: Tag | None = None
        best_pos = -1
        for desc_block in description_blocks:
            if id(desc_block) in used_description_ids:
                continue
            desc_pos = position_by_id.get(id(desc_block), 0)
            if desc_pos < embed_pos and desc_pos > best_pos:
                best = desc_block
                best_pos = desc_pos
        if best is not None:
            used_description_ids.add(id(best))

        embed_text = embed_block.get_text(" ", strip=True)
        match = _SUGGESTED_SEARCH_RE.search(embed_text)
        suggested_search = match.group(1).strip(' "“”') if match else ""

        slots.append(VideoSlot(
            index=index,
            description_tag=best,
            embed_tag=embed_block,
            suggested_search=suggested_search,
            original_description_text=best.get_text(" ", strip=True) if best else "",
        ))

    # Second pass: description blocks left over from a *previous* push (still say
    # "Watch this (...)" since that's the fixed phrasing we generate) that no longer
    # have an unfilled placeholder next to them, but do have a real YouTube iframe
    # nearby in a later column - i.e. a video was already suggested and embedded here
    # before, and the page no longer carries the original placeholder marker either.
    remaining_description_blocks = sorted(
        (b for b in description_blocks if id(b) not in used_description_ids),
        key=lambda b: position_by_id.get(id(b), 0),
    )
    iframe_tags = [
        tag for tag in soup.find_all("iframe")
        if _YOUTUBE_IFRAME_SRC_RE.search(tag.get("src") or "")
    ]
    used_iframe_ids: set[int] = set()
    for desc_block in remaining_description_blocks:
        desc_pos = position_by_id.get(id(desc_block), 0)
        best_iframe: Tag | None = None
        best_iframe_pos = None
        for iframe in iframe_tags:
            if id(iframe) in used_iframe_ids:
                continue
            iframe_pos = position_by_id.get(id(iframe))
            if iframe_pos is None or iframe_pos <= desc_pos:
                continue
            if best_iframe_pos is None or iframe_pos < best_iframe_pos:
                best_iframe = iframe
                best_iframe_pos = iframe_pos
        if best_iframe is None:
            continue
        embed_block = _closest_block(best_iframe)
        if embed_block is None:
            continue
        used_iframe_ids.add(id(best_iframe))
        slots.append(VideoSlot(
            index=len(slots),
            description_tag=desc_block,
            embed_tag=embed_block,
            suggested_search="",
            original_description_text=desc_block.get_text(" ", strip=True),
            already_filled=True,
        ))

    return slots


def find_video_slots(html: str) -> list[VideoSlot]:
    """Locate every "Watch this (X:XX mins)... / *Embed your YouTube video here..." pair in a Canvas page body."""
    soup = BeautifulSoup(html or "", "html.parser")
    return _find_slots_in_soup(soup)


def format_duration(iso8601: str) -> str:
    """Convert a YouTube contentDetails duration ("PT12M45S") into "12:45" / "1:02:03"."""
    match = _ISO8601_DURATION_RE.match((iso8601 or "").strip())
    if not match:
        return "0:00"
    hours = int(match.group("hours") or 0)
    minutes = int(match.group("minutes") or 0)
    seconds = int(match.group("seconds") or 0)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def render_slot_html(slot: VideoSlot, videos: list[dict], descriptions: list[str]) -> tuple[str, str]:
    """Build plain replacement content for the description column and the embed column.

    This deliberately invents no layout of its own: the template already provides two
    columns (sized by Canvas's own theme CSS, not anything of ours) and expects exactly
    what a human would put in them by hand - description text in one, YouTube's own
    default embed code in the other. Each is returned separately so apply_slot can place
    it in its own column rather than both ending up in one.
    """
    description_tag_name = slot.description_tag.name if slot.description_tag else "p"
    embed_tag_name = slot.embed_tag.name if slot.embed_tag.name != "table" else "p"

    description_html = "".join(
        f"<{description_tag_name}>{html_escape(description)}</{description_tag_name}>"
        for description in descriptions
    )
    embed_html = "".join(
        f"<{embed_tag_name}>"
        + _IFRAME_TEMPLATE.format(
            video_id=html_escape(video.get("id") or "", quote=True),
            title=html_escape(video.get("title") or "Embedded video", quote=True),
        )
        + f"</{embed_tag_name}>"
        for video in videos
    )
    return description_html, embed_html


def wrap_for_preview(description_html: str, embed_html: str) -> str:
    """Wrap a slot's two replacement pieces into a standalone document for a preview iframe.

    This side-by-side arrangement is for visualising the two columns only - it is not
    what gets pushed to Canvas (apply_slot inserts each piece into its own real column
    there, sized by the page's own theme CSS).
    """
    return (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        "<style>body{margin:0;padding:12px;font-family:-apple-system,Segoe UI,Roboto,sans-serif;"
        "box-sizing:border-box;} *{box-sizing:inherit;} .preview-row{display:flex;gap:16px;"
        "align-items:flex-start;flex-wrap:wrap;} .preview-row > div{flex:1 1 33%;min-width:200px;}"
        "</style></head><body><div class=\"preview-row\">"
        f"<div>{description_html}</div><div>{embed_html}</div>"
        "</div></body></html>"
    )


def apply_slot(html: str, slot_index: int, description_html: str, embed_html: str) -> str:
    """Return the full page body with the slot's two columns filled in, each in its own place."""
    soup = BeautifulSoup(html or "", "html.parser")
    slots = _find_slots_in_soup(soup)
    if slot_index < 0 or slot_index >= len(slots):
        raise ValueError(f"Video slot {slot_index} was not found on this page.")
    slot = slots[slot_index]

    embed_fragment = BeautifulSoup(embed_html, "html.parser")
    for child in list(embed_fragment.contents):
        slot.embed_tag.insert_before(child)
    slot.embed_tag.decompose()

    if slot.description_tag is not None:
        description_fragment = BeautifulSoup(description_html, "html.parser")
        for child in list(description_fragment.contents):
            slot.description_tag.insert_before(child)
        slot.description_tag.decompose()

    return str(soup)
