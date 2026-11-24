"""Reusable BM25 search over Markdown documentation pages."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path

WORD = re.compile(r"[a-z0-9_]+")


@dataclass(frozen=True)
class SearchResult:
    path: str
    title: str
    score: float
    lines: list[tuple[int, str]]
    section: str


def _stem(word: str) -> str:
    """Tiny plural folding so "mutation" matches "mutations" and "values" matches "value"."""
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _tokens(text: str) -> list[str]:
    return [_stem(word) for word in WORD.findall(text.lower())]


def _title(text: str, path: Path) -> str:
    match = re.search(r"^title:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip().strip("'\"") if match else path.stem


def _section(text: str, path: Path, root: Path) -> str:
    match = re.search(r"^section:\s*(.+)$", text, re.MULTILINE)
    if match:
        return match.group(1).strip().strip("'\"")
    relative = path.relative_to(root)
    return relative.parts[0].title() if len(relative.parts) > 1 else "Docs"


def _best_lines(text: str, terms: list[str], keep: int = 3) -> list[tuple[int, str]]:
    """Body lines (front matter and headings skipped) matching the most terms."""
    lines = text.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), 0)
        start = end + 1
    scored = []
    for number in range(start, len(lines)):
        line = lines[number].strip()
        if not line or line.startswith("#"):
            continue
        hits = len(set(_tokens(line)) & set(terms))
        if hits:
            scored.append((-hits, number + 1, line))
    best = sorted(scored)[:keep]
    return [(number, line) for _, number, line in sorted(best, key=lambda item: item[1])]


def _matches_section(page_section: str, path: str, requested: str | None) -> bool:
    if requested is None:
        return True
    requested = requested.strip().casefold()
    if not requested:
        return True
    return page_section.casefold() == requested or path.split("/", 1)[0].casefold() == requested


def search(
    docs_root: Path, query: str, limit: int = 5, section: str | None = None
) -> list[SearchResult]:
    """Rank Markdown pages with BM25 and a boost for matches in titles and file names."""
    terms = sorted(set(_tokens(query)))
    if not terms or limit <= 0:
        return []

    root = docs_root.resolve()
    pages = []
    for path in sorted(root.rglob("*.md")):
        resolved = path.resolve()
        if not resolved.is_relative_to(root):
            continue
        text = path.read_text(encoding="utf-8")
        words = _tokens(text)
        if not words:
            continue
        rel = path.relative_to(root).as_posix()
        title = _title(text, path)
        page_section = _section(text, path, root)
        if _matches_section(page_section, rel, section):
            pages.append((rel, path, text, title, page_section, words))
    if not pages:
        return []

    avg_len = sum(len(page[5]) for page in pages) / len(pages)
    doc_freq = {term: sum(1 for page in pages if term in set(page[5])) for term in terms}
    idf = {
        term: math.log(1 + (len(pages) - doc_freq[term] + 0.5) / (doc_freq[term] + 0.5))
        for term in terms
    }
    k1, b = 1.2, 0.75
    results = []
    for rel, path, text, title, page_section, words in pages:
        counts = {term: words.count(term) for term in terms}
        matched = [term for term in terms if counts[term]]
        if not matched:
            continue
        norm = k1 * (1 - b + b * len(words) / avg_len)
        score = sum(idf[term] * counts[term] * (k1 + 1) / (counts[term] + norm) for term in matched)
        title_words = set(_tokens(title)) | set(_tokens(path.stem.replace("-", " ")))
        score += sum(1.5 * idf[term] for term in terms if term in title_words)
        results.append(SearchResult(rel, title, score, _best_lines(text, matched), page_section))
    results.sort(key=lambda result: (-result.score, result.path))
    return results[:limit]
