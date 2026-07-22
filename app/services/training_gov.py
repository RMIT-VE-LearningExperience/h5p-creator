from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser

import httpx


_BASE_URL = "https://training.gov.au"
_CODE_RE = re.compile(r"^[A-Z0-9]{5,14}$")
_UNIT_ROW_RE = re.compile(
    r"Code\s*([A-Z0-9]{5,14})\s*\|\s*Title\s*([^|]+?)(?:\s*\|\s*Usage recommendation\s*([^|]+?))?(?:\s*\|\s*Release\s*([^|]+?))?(?:\s*\|\s*Essential\s*([^|\n]+?))?(?=\s*(?:Code[A-Z0-9]{5,14}\s*\||##|\n|$))",
    re.IGNORECASE | re.DOTALL,
)


@dataclass
class TrainingProduct:
    code: str
    title: str = ""
    product_type: str = "training product"
    usage_recommendation: str = ""
    source_url: str = ""
    summary: str = ""
    units: list[dict[str, str]] = field(default_factory=list)
    raw_text: str = ""

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "title": self.title,
            "product_type": self.product_type,
            "usage_recommendation": self.usage_recommendation,
            "source_url": self.source_url,
            "summary": self.summary,
            "units": self.units,
            "raw_text": self.raw_text,
        }


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1
            return
        if tag in {"br", "p", "div", "section", "article", "tr", "li", "h1", "h2", "h3", "h4"}:
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if self._skip_depth and tag in {"script", "style", "noscript", "svg"}:
            self._skip_depth -= 1
            return
        if tag in {"p", "div", "section", "article", "tr", "li", "h1", "h2", "h3", "h4"}:
            self._chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            self._chunks.append(data)

    def text(self) -> str:
        text = html.unescape(" ".join(self._chunks))
        text = re.sub(r"[ \t\r\f\v]+", " ", text)
        text = re.sub(r"\n\s+", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


async def lookup_training_product(code: str) -> TrainingProduct:
    """Fetch and normalise a training.gov.au product by code.

    The public site exposes product details under stable detail URLs. This service
    keeps the app decoupled from the browser UI and extracts the content needed
    for prompt context.
    """
    clean_code = _normalise_code(code)
    urls = [
        f"{_BASE_URL}/training/details/{clean_code}",
        f"{_BASE_URL}/training/details/{clean_code}/qualdetails",
        f"{_BASE_URL}/Training/Details/{clean_code}",
    ]

    async with httpx.AsyncClient(
        base_url=_BASE_URL,
        timeout=httpx.Timeout(15.0, connect=8.0),
        follow_redirects=True,
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (compatible; H5PCreator/1.0; +https://training.gov.au)",
        },
    ) as client:
        try:
            product = await _lookup_training_product_api(client, clean_code)
            if product:
                return product
        except Exception:
            # Fall back to the public detail pages below. The JSON API is the
            # preferred source, but keeping a page fallback makes the lookup
            # resilient if the frontend API changes.
            pass

        last_error: Exception | None = None
        for url in urls:
            try:
                response = await client.get(url)
                if response.status_code == 404:
                    continue
                response.raise_for_status()
                product = _parse_training_page(clean_code, str(response.url), response.text)
                if product.title or product.raw_text:
                    return product
            except Exception as exc:
                last_error = exc

    if last_error:
        raise RuntimeError(f"training.gov.au lookup failed for {clean_code}: {last_error}") from last_error
    raise ValueError(f"No training.gov.au product found for {clean_code}")


def format_for_prompt(product: TrainingProduct) -> str:
    lines = [
        f"Code: {product.code}",
        f"Title: {product.title or 'Unknown'}",
        f"Type: {product.product_type}",
        f"Source: {product.source_url}",
    ]
    if product.usage_recommendation:
        lines.append(f"Usage recommendation: {product.usage_recommendation}")
    if product.summary:
        lines.extend(["", "Summary:", product.summary])
    if product.units:
        lines.append("")
        lines.append("Units of competency:")
        for unit in product.units[:80]:
            essential = f" [{unit['essential']}]" if unit.get("essential") else ""
            lines.append(f"- {unit['code']}: {unit['title']}{essential}")
    return "\n".join(lines).strip()


def _normalise_code(code: str) -> str:
    clean_code = re.sub(r"[^A-Za-z0-9]", "", code or "").upper()
    if not _CODE_RE.match(clean_code):
        raise ValueError("Enter a valid training.gov.au code")
    return clean_code


def _parse_training_page(code: str, url: str, body: str) -> TrainingProduct:
    text = _html_to_text(body)
    compact = re.sub(r"\s+", " ", text).strip()

    title = _extract_title(code, body, compact)
    product_type = _extract_product_type(compact)
    usage = _extract_usage(compact)
    units = _extract_units(compact)
    summary = _extract_summary(compact, product_type)

    return TrainingProduct(
        code=code,
        title=title,
        product_type=product_type,
        usage_recommendation=usage,
        source_url=url,
        summary=summary,
        units=units,
        raw_text=text[:30000],
    )


async def _lookup_training_product_api(client: httpx.AsyncClient, code: str) -> TrainingProduct | None:
    response = await client.get(f"/api/training/{code}", params={"api-version": "1.0", "include": "All"})
    if response.status_code == 404:
        return None
    response.raise_for_status()
    data = response.json()

    title = str(data.get("title") or "")
    product_type = _normalise_product_type(str(data.get("type") or ""))
    usage = str(data.get("usageRecommendationLabel") or data.get("usageRecommendation") or "")
    release = _select_release(data.get("releases") or [])
    source_url = f"{_BASE_URL}/training/details/{code}"

    summary_parts: list[str] = []
    units: list[dict[str, str]] = []

    if release and release.get("id"):
        release_response = await client.get(
            f"/api/training/{code}/releases/{release['id']}",
            params={"api-version": "1.0", "include": "All"},
        )
        release_response.raise_for_status()
        release_data = release_response.json()
        for bundle in release_data.get("contentBundles") or []:
            bundle_id = bundle.get("id")
            if not bundle_id:
                continue
            bundle_response = await client.get(
                f"/api/content/bundle/{bundle_id}",
                params={"api-version": "1.0"},
            )
            bundle_response.raise_for_status()
            bundle_data = bundle_response.json()
            items = bundle_data.get("items") or []
            summary_parts.extend(_summaries_from_content_items(items, product_type))
            units.extend(_units_from_content_items(items))

    if not summary_parts:
        summary_parts.extend(_summaries_from_mapping(data.get("mappingInformation") or []))

    return TrainingProduct(
        code=code,
        title=title,
        product_type=product_type,
        usage_recommendation=usage,
        source_url=source_url,
        summary="\n\n".join(part for part in summary_parts if part)[:4000],
        units=_dedupe_units(units),
        raw_text=_raw_text_from_api(data, summary_parts)[:30000],
    )


def _normalise_product_type(value: str) -> str:
    key = value.strip().lower()
    return {
        "unit": "unit of competency",
        "qualification": "qualification",
        "skillset": "skill set",
        "skill set": "skill set",
        "trainingpackage": "training package",
        "training package": "training package",
        "accreditedcourse": "accredited course",
        "accreditedunit": "accredited unit",
    }.get(key, key or "training product")


def _select_release(releases: list[dict]) -> dict | None:
    if not releases:
        return None
    for release in releases:
        if str(release.get("currency") or "").lower() == "current":
            return release
    return releases[0]


def _summaries_from_content_items(items: list[dict], product_type: str) -> list[str]:
    preferred = {
        "unit of competency": {"ApplicationOfUnit", "UnitDescriptor", "PerformanceEvidence", "KnowledgeEvidence"},
        "qualification": {"Description", "PackagingRules", "EntryRequirements"},
    }.get(product_type, {"Description", "ApplicationOfUnit", "PackagingRules"})
    summaries: list[str] = []
    for item in sorted(items, key=lambda i: i.get("sequence") or 0):
        content_type = str(item.get("contentType") or "")
        if content_type not in preferred:
            continue
        title = str(item.get("title") or content_type)
        text = _html_to_text(str(item.get("content") or ""))
        if text:
            summaries.append(f"{title}: {text[:2500]}")
    return summaries


def _units_from_content_items(items: list[dict]) -> list[dict[str, str]]:
    units: list[dict[str, str]] = []
    for item in items:
        content = str(item.get("content") or "")
        if not content:
            continue
        for match in re.finditer(
            r'data-nrt-code="([^"]+)"\s+data-nrt-title="([^"]+)"\s+data-nrt-type="unit"',
            content,
            flags=re.IGNORECASE,
        ):
            units.append({
                "code": html.unescape(match.group(1)).upper(),
                "title": html.unescape(match.group(2)),
                "usage_recommendation": "",
                "release": "",
                "essential": "",
            })
    return units


def _summaries_from_mapping(mapping: list[dict]) -> list[str]:
    summaries: list[str] = []
    for item in mapping[:4]:
        notes = item.get("notes")
        if notes:
            summaries.append(str(notes))
    return summaries


def _raw_text_from_api(data: dict, summary_parts: list[str]) -> str:
    lines = [
        str(data.get("code") or ""),
        str(data.get("title") or ""),
        str(data.get("usageRecommendationLabel") or ""),
    ]
    parent = data.get("parent") or {}
    if parent:
        lines.append(f"Parent training package: {parent.get('code', '')} {parent.get('title', '')}".strip())
    lines.extend(summary_parts)
    return "\n".join(line for line in lines if line)


def _dedupe_units(units: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    result: list[dict[str, str]] = []
    for unit in units:
        code = unit.get("code", "").upper()
        if not code or code in seen:
            continue
        seen.add(code)
        result.append({**unit, "code": code})
    return result


def _html_to_text(body: str) -> str:
    parser = _TextExtractor()
    parser.feed(body)
    return parser.text()


def _extract_title(code: str, body: str, text: str) -> str:
    title_match = re.search(r"<title[^>]*>(.*?)</title>", body, flags=re.IGNORECASE | re.DOTALL)
    candidates: list[str] = []
    if title_match:
        candidates.append(html.unescape(re.sub(r"\s+", " ", title_match.group(1))).strip())
    candidates.extend(re.findall(rf"\b{re.escape(code)}\b\s+([^|#\n\r]+)", text, flags=re.IGNORECASE))

    for candidate in candidates:
        cleaned = re.sub(r"^National Training Register\s*-\s*", "", candidate, flags=re.IGNORECASE)
        cleaned = re.sub(rf"^{re.escape(code)}\s*", "", cleaned, flags=re.IGNORECASE).strip(" -|")
        if cleaned and cleaned.lower() not in {"training.gov.au", "national training register"}:
            return cleaned[:220]
    return ""


def _extract_product_type(text: str) -> str:
    lowered = text.lower()
    if "unit of competency" in lowered:
        return "unit of competency"
    if "qualification details" in lowered or "packaging rules" in lowered:
        return "qualification"
    if "skill set" in lowered:
        return "skill set"
    if "accredited course" in lowered:
        return "accredited course"
    return "training product"


def _extract_usage(text: str) -> str:
    match = re.search(r"Usage recommendation\s+([^|#\n]+?)(?=\s+(?:Release|Code|Title|##|$))", text, re.IGNORECASE)
    return match.group(1).strip()[:120] if match else ""


def _extract_units(text: str) -> list[dict[str, str]]:
    seen: set[str] = set()
    units: list[dict[str, str]] = []
    chunks = re.split(r"(?=\bCode\s*[A-Z0-9]{5,14}\s*\|)", text)
    for chunk in chunks:
        match = re.match(r"\s*Code\s*([A-Z0-9]{5,14})\s*\|\s*Title\s*([^|]+)", chunk, re.IGNORECASE)
        if not match:
            continue
        unit_code = match.group(1).upper()
        title = _clean_cell(match.group(2))
        if not title or unit_code in seen:
            continue
        seen.add(unit_code)
        usage = _extract_cell(chunk, "Usage recommendation")
        release = _extract_cell(chunk, "Release")
        essential = _extract_cell(chunk, "Essential")
        units.append({
            "code": unit_code,
            "title": title,
            "usage_recommendation": usage,
            "release": release,
            "essential": essential,
        })
    return units


def _extract_summary(text: str, product_type: str) -> str:
    if product_type == "unit of competency":
        return _section_after(text, ["Application", "Unit descriptor", "Application of the unit"], ["Unit sector", "Elements and performance criteria", "Licensing", "Pre-requisites"])
    if product_type == "qualification":
        return _section_after(text, ["Packaging Rules", "Qualification Description"], ["Core units", "Units of competency", "Mapping", "Releases"])
    return _section_after(text, ["Description", "Application", "Summary"], ["Mapping", "Releases", "Classifications"])


def _section_after(text: str, starts: list[str], stops: list[str]) -> str:
    for start in starts:
        match = re.search(rf"\b{re.escape(start)}\b\s*(.*)", text, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            continue
        section = match.group(1)
        stop_positions = [
            m.start()
            for stop in stops
            if (m := re.search(rf"\b{re.escape(stop)}\b", section, flags=re.IGNORECASE))
        ]
        if stop_positions:
            section = section[: min(stop_positions)]
        section = re.sub(r"\s+", " ", section).strip(" -|")
        if section:
            return section[:2500]
    return ""


def _clean_cell(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" -|")


def _extract_cell(text: str, label: str) -> str:
    match = re.search(rf"\b{re.escape(label)}\s*([^|]+)", text, re.IGNORECASE)
    return _clean_cell(match.group(1)) if match else ""
