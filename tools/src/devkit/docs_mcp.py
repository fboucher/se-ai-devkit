"""MCP tools for searching and reading the developer kit's documentation."""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from mcp.server.fastmcp import FastMCP

from devkit import llms
from devkit.search_engine import search

BUNDLED_DOCS = Path(__file__).resolve().parent / "_bundled_docs"


def resolve_docs_root(
    docs: str | Path | None = None, environ: dict[str, str] | None = None
) -> Path:
    """Resolve docs root from CLI, environment, then bundled snapshot."""
    env = os.environ if environ is None else environ
    selected = docs if docs is not None else env.get("SE_DEVKIT_DOCS")
    if selected:
        return Path(selected).expanduser().resolve()
    if BUNDLED_DOCS.is_dir():
        return BUNDLED_DOCS.resolve()
    return (Path(__file__).resolve().parents[3] / "docs").resolve()


def _validate_docs_root(docs_root: Path) -> Path:
    root = docs_root.expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"docs root '{root}' does not exist or is not a directory")
    return root


def _read_page(root: Path, page_path: str) -> str:
    normalized = page_path.replace("\\", "/")
    posix_path = PurePosixPath(normalized)
    windows_path = PureWindowsPath(page_path)
    if (
        not page_path
        or posix_path.is_absolute()
        or windows_path.is_absolute()
        or windows_path.drive
        or ".." in posix_path.parts
    ):
        raise ValueError(f"Invalid docs page path: {page_path!r}")

    candidate = (root / Path(*posix_path.parts)).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Invalid docs page path: {page_path!r}") from exc
    if candidate.suffix.lower() != ".md" or not candidate.is_file():
        raise ValueError(f"Unknown docs page: {page_path}")
    return candidate.read_text(encoding="utf-8")


def _page_tree(root: Path, section: str | None = None) -> list[dict[str, Any]]:
    entries = llms.collect(root)
    tree: list[dict[str, Any]] = []
    nodes: dict[str, dict[str, Any]] = {}
    section_filter = section.strip().casefold() if section else ""

    for entry in entries:
        relative = entry.path.removeprefix("docs/")
        area = relative.split("/", 1)[0].casefold()
        if section_filter and section_filter not in {
            entry.section.casefold(),
            area,
        }:
            continue

        parts = relative.split("/")
        current_nodes = nodes
        current_list = tree
        for index, part in enumerate(parts[:-1]):
            path = "/".join(parts[: index + 1])
            if path not in current_nodes:
                node = {"name": part, "path": path, "children": []}
                current_nodes[path] = node
                current_list.append(node)
            node = current_nodes[path]
            current_nodes = node.setdefault("_nodes", {})
            current_list = node["children"]

        leaf_path = relative
        current_list.append(
            {
                "name": parts[-1],
                "path": leaf_path,
                "title": entry.title,
                "children": [],
            }
        )

    def remove_internal_nodes(nodes_to_clean: list[dict[str, Any]]) -> None:
        for node in nodes_to_clean:
            node.pop("_nodes", None)
            remove_internal_nodes(node["children"])

    remove_internal_nodes(tree)
    return tree


def create_server(docs_root: str | Path) -> FastMCP:
    """Create the server and its tools without selecting a transport."""
    root = _validate_docs_root(Path(docs_root))
    server = FastMCP("se-ai-devkit-docs")

    @server.tool()
    def docs_search(query: str, limit: int = 5, section: str | None = None) -> list[dict[str, Any]]:
        """Search documentation and return paths, titles, scores, and matching lines."""
        if not 1 <= limit <= 50:
            raise ValueError("limit must be between 1 and 50")
        return [
            {
                "path": result.path,
                "title": result.title,
                "score": result.score,
                "matches": [{"line": number, "text": line} for number, line in result.lines],
            }
            for result in search(root, query, limit, section)
        ]

    @server.tool()
    def docs_get_page(path: str) -> str:
        """Read a Markdown documentation page by its path relative to the docs root."""
        return _read_page(root, path)

    @server.tool()
    def docs_list(section: str | None = None) -> list[dict[str, Any]]:
        """List documentation pages as a directory tree with page titles."""
        return _page_tree(root, section)

    return server


def run_server(server: FastMCP) -> None:
    """Run an already-created server over stdio."""
    server.run(transport="stdio")
