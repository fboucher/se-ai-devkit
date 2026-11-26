import asyncio
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from devkit import docs_mcp
from devkit.search_engine import search

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"


@pytest.fixture
def docs(tmp_path: Path) -> Path:
    root = tmp_path / "docs"
    pages = {
        "api/historical-values.md": (
            "---\ntitle: Historical Values\nsection: REST API / Endpoints\n---\n\n"
            "# Historical Values\n\nUse pagination to read historical values with page tokens.\n"
            "Historical values support pagination and stable ordering.\n"
        ),
        "api/overview.md": (
            "---\ntitle: API Overview\nsection: REST API / Overview\n---\n\n"
            "# API Overview\n\nThe API exposes sites and devices.\n"
        ),
        "guides/pagination.md": (
            "---\ntitle: Pagination Guide\n---\n\n"
            "# Pagination Guide\n\nPagination uses a continuation token.\n"
        ),
    }
    for relative, content in pages.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root


def test_search_ranks_pages_and_filters_sections(docs: Path) -> None:
    results = search(docs, "historical values pagination")
    assert results[0].path == "api/historical-values.md"
    assert results[0].title == "Historical Values"
    assert results[0].lines

    filtered = search(docs, "pagination", section="guides")
    assert [result.path for result in filtered] == ["guides/pagination.md"]
    assert search(docs, "historical", section="guides") == []


def test_docs_page_rejects_traversal_and_unknown_pages(docs: Path) -> None:
    root = docs.resolve()
    for invalid in ("../outside.md", "api/../../outside.md", "C:\\outside.md", "/outside.md"):
        with pytest.raises(ValueError, match="Invalid docs page path"):
            docs_mcp._read_page(root, invalid)

    with pytest.raises(ValueError, match="Unknown docs page"):
        docs_mcp._read_page(root, "api/missing.md")
    assert "page tokens" in docs_mcp._read_page(root, "api/historical-values.md")


def test_docs_list_returns_tree_and_filters_sections(docs: Path) -> None:
    tree = docs_mcp._page_tree(docs)
    api = next(node for node in tree if node["name"] == "api")
    assert [node["title"] for node in api["children"]] == ["Historical Values", "API Overview"]

    filtered = docs_mcp._page_tree(docs, "guides")
    assert [node["name"] for node in filtered] == ["guides"]


def test_docs_root_resolution_order(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    explicit = tmp_path / "explicit"
    from_env = tmp_path / "environment"
    bundled = tmp_path / "bundled"
    bundled.mkdir()
    monkeypatch.setattr(docs_mcp, "BUNDLED_DOCS", bundled)
    env = {"SE_DEVKIT_DOCS": str(from_env)}

    assert docs_mcp.resolve_docs_root(explicit, env) == explicit.resolve()
    assert docs_mcp.resolve_docs_root(None, env) == from_env.resolve()
    assert docs_mcp.resolve_docs_root(None, {}) == bundled.resolve()


def test_docs_mcp_tools_over_stdio_from_built_wheel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundled_page = REPO_ROOT / "docs" / "api" / "wheel-packaging-fixture.md"
    bundled_page.parent.mkdir(parents=True, exist_ok=True)
    bundled_page.write_text(
        "---\ntitle: Wheel Fixture\n---\n\nWheel packaged documentation search marker.\n",
        encoding="utf-8",
    )
    try:
        build = subprocess.run(
            [
                "uv",
                "build",
                "--project",
                str(TOOLS_ROOT),
                "--wheel",
                "--out-dir",
                str(tmp_path),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert build.returncode == 0, build.stderr
        wheel_path = next(tmp_path.glob("*.whl"))
        extraction = tmp_path / "wheel"
        with zipfile.ZipFile(wheel_path) as wheel:
            assert "devkit/_bundled_docs/api/wheel-packaging-fixture.md" in wheel.namelist()
            wheel.extractall(extraction)

        env = os.environ.copy()
        env.pop("SE_DEVKIT_DOCS", None)
        env["PYTHONPATH"] = str(extraction)
        monkeypatch.chdir(tmp_path)

        async def list_and_search_tools(
            args: list[str], query: str, expected_page: str
        ) -> list[str]:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client

            params = StdioServerParameters(
                command=sys.executable,
                args=["-m", "devkit.cli", *args],
                env=env,
            )
            async with (
                stdio_client(params) as (read_stream, write_stream),
                ClientSession(read_stream, write_stream) as client,
            ):
                await client.initialize()
                tools = await client.list_tools()
                result = await client.call_tool("docs_search", {"query": query})
                assert expected_page in str(result)
                return [tool.name for tool in tools.tools]

        tool_names = [
            "docs_search",
            "docs_get_page",
            "docs_list",
        ]
        assert (
            asyncio.run(
                list_and_search_tools(
                    ["docs-mcp"],
                    "packaged documentation marker",
                    "wheel-packaging-fixture.md",
                )
            )
            == tool_names
        )

        alternate_docs = tmp_path / "alternate-docs"
        alternate_docs.mkdir()
        (alternate_docs / "custom.md").write_text(
            "---\ntitle: Custom Docs\n---\n\nCustom docs root marker.\n", encoding="utf-8"
        )
        assert (
            asyncio.run(
                list_and_search_tools(
                    ["docs-mcp", "--docs", str(alternate_docs)],
                    "custom docs root marker",
                    "custom.md",
                )
            )
            == tool_names
        )
    finally:
        bundled_page.unlink(missing_ok=True)
        if bundled_page.parent.is_dir() and not any(bundled_page.parent.iterdir()):
            shutil.rmtree(bundled_page.parent)
